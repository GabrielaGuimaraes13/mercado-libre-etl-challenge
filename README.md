# Mercado Libre - ETL Challenge

Proyecto desarrollado como solución al desafío técnico de automatización ETL utilizando Python y las APIs de Mercado Libre.

## Objetivo

El objetivo es analizar publicaciones de un modelo Samsung Galaxy en Mercado Libre Argentina.

Para este proyecto elegí el **Samsung Galaxy S24 FE** (`site_id = MLA`).

El pipeline busca productos relacionados con el modelo, identifica sus publicaciones activas de productos nuevos, transforma los datos necesarios para el análisis y guarda el resultado en una base PostgreSQL local.

Con los datos obtenidos se busca responder:

1. ¿Hay vendedores con múltiples publicaciones? ¿Cuántas?
2. ¿Cuál es el promedio de ventas por vendedor?
3. ¿Cuál es el precio promedio de las publicaciones en USD?
4. ¿Qué porcentaje de las publicaciones tiene garantía?
5. ¿Cuáles son los métodos de envío disponibles?

---

## Arquitectura

El proyecto utiliza un pipeline ETL ejecutado localmente:

```text
Mercado Libre API
        │
        ▼
     Extract
        │
        ├── Búsqueda de productos
        ├── Filtro del modelo
        ├── Búsqueda de publicaciones
        └── Conversión ARS → USD
        │
        ▼
    Transform
        │
        ├── Precio en USD
        ├── Garantía
        ├── Shipping
        └── JOB_RUN
        │
        ▼
       Load
        │
        ▼
    PostgreSQL
        │
        ▼
    Queries SQL
```

La arquitectura se mantuvo simple para el alcance del desafío: **API → Python → PostgreSQL → SQL**.

---

## Tecnologías utilizadas

- **Python 3**
- **Requests**
- **python-dotenv**
- **PostgreSQL**
- **psycopg2**
- **SQL**

---

## Estructura del proyecto

```text
mercado-livre-etl/
│
├── src/
│   ├── api_client.py
│   ├── extract.py
│   ├── transform.py
│   └── load.py
│
├── sql/
│   ├── schema.sql
│   └── queries.sql
│
├── config.py
├── generate_token.py
├── main.py
├── teste_api.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

| Archivo | Función |
|---|---|
| `src/api_client.py` | Centraliza las requests a la API y el tratamiento de los principales errores HTTP |
| `src/extract.py` | Busca productos, filtra el modelo, consulta publicaciones y obtiene el tipo de cambio |
| `src/transform.py` | Prepara los datos antes de cargarlos en la base |
| `src/load.py` | Realiza la conexión y la carga en PostgreSQL |
| `sql/schema.sql` | Contiene el DDL de la tabla |
| `sql/queries.sql` | Contiene las queries utilizadas para responder las preguntas del desafío |
| `config.py` | Centraliza la configuración de búsqueda, paginación y endpoints |
| `generate_token.py` | Genera el access token utilizado por la API |
| `main.py` | Ejecuta el pipeline completo |
| `teste_api.py` | Prueba los principales endpoints utilizados |
| `.env.example` | Ejemplo de las variables de entorno necesarias |
| `requirements.txt` | Dependencias de Python |

---

## Cómo ejecutar el proyecto

### Requisitos

Es necesario tener instalado:

- Python 3
- PostgreSQL
- Git
- una aplicación en Mercado Libre Developers para utilizar OAuth

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd mercado-livre-etl
```

### 2. Crear el entorno virtual

```bash
python -m venv .venv
```

En Windows:

```bash
.venv\Scripts\activate
```

En Linux/macOS:

```bash
source .venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar las variables de entorno

Crear un archivo `.env` en la raíz del proyecto usando `.env.example` como referencia:

```env
ML_CLIENT_ID=
ML_CLIENT_SECRET=
ML_REDIRECT_URI=
ML_AUTH_CODE=
ML_ACCESS_TOKEN=

DB_HOST=localhost
DB_PORT=5432
DB_NAME=mercado_livre_etl
DB_USER=postgres
DB_PASSWORD=
```

El archivo `.env` contiene credenciales y no debe subirse al repositorio.

### 5. Generar el access token

Después de obtener un authorization code válido y configurar `ML_AUTH_CODE`, ejecutar:

```bash
python generate_token.py
```

El script solicita un nuevo access token y actualiza `ML_ACCESS_TOKEN` en el `.env`.

Si el authorization code ya fue utilizado o expiró, es necesario obtener uno nuevo antes de ejecutar el script.

### 6. Crear la base de datos

En PostgreSQL:

```sql
CREATE DATABASE mercado_livre_etl;
```

Después, ejecutar el DDL disponible en:

```text
sql/schema.sql
```

Los datos de conexión se leen desde las variables configuradas en `.env`.

### 7. Probar la API

Antes de ejecutar el pipeline completo:

```bash
python teste_api.py
```

### 8. Ejecutar la ETL

```bash
python main.py
```

Una ejecución de referencia durante el desarrollo produjo:

```text
Iniciando ETL...
Extraindo dados do Mercado Libre...
100 produtos encontrados na busca.
22 produtos correspondem ao modelo selecionado.
51 publicações novas encontradas.
Transformando dados...
51 registros transformados.
Carregando dados no PostgreSQL...
ETL finalizada com sucesso.
```

Los valores pueden cambiar entre ejecuciones porque los datos se consultan directamente desde la API.

---

## Flujo ETL

### Extract

La extracción comienza buscando:

```text
Samsung Galaxy S24 FE
```

en Mercado Libre Argentina (`MLA`).

La API se consulta con páginas de hasta 50 registros. El límite total utilizado en el proyecto se encuentra en `config.py`:

```python
PAGE_SIZE = 50
MAX_PRODUCTS = 100
```

#### Selección del modelo

Durante las pruebas, la búsqueda por `Samsung Galaxy S24 FE` también devolvió otros modelos Samsung, incluyendo productos de las líneas S25, S24 Ultra y Galaxy A.

Usar todos esos resultados afectaba la población analizada y, principalmente, el cálculo del precio promedio.

Por eso se agregó una validación antes de buscar las publicaciones. El filtro verifica:

- marca Samsung;
- presencia de `S24 FE` en el nombre normalizado del producto.

En la ejecución de referencia:

```text
100 resultados
      ↓
22 productos S24 FE
      ↓
51 publicaciones nuevas
```

También se evaluó utilizar únicamente el atributo `MODEL`, pero los valores devueltos no tenían un formato único. Se encontraron variantes como `Galaxy-S24 FE`, `S24 FE`, `GALAXY S24FE` y códigos de modelo.

Para este caso, la combinación de marca y nombre normalizado resultó más simple.

#### Publicaciones

Después de seleccionar los productos, se consultan sus publicaciones.

Solo se mantienen publicaciones con:

```text
condition = new
```

Si un producto no tiene publicaciones disponibles, se continúa con los demás sin interrumpir la ETL.

#### Conversión ARS → USD

La tasa de conversión también se consulta en la API durante cada ejecución.

De esta forma, el cálculo no depende de una tasa fija guardada en el código.

---

### Transform

La transformación prepara los campos necesarios para el análisis.

Entre ellos:

- vendedor;
- precio en ARS;
- tasa de conversión;
- precio en USD;
- garantía;
- información de envío;
- condición;
- `JOB_RUN`.

El precio en USD se calcula como:

```text
price_usd = price_ars × exchange_rate
```

Se genera un único `JOB_RUN` para cada ejecución y ese mismo timestamp se utiliza en todos los registros procesados.

---

### Load

Los registros transformados se insertan en PostgreSQL.

La carga se ejecuta dentro de una transacción. Si termina correctamente se realiza `commit`; si ocurre un error se realiza `rollback`.

Las credenciales de conexión se obtienen desde las variables de entorno.

---

## Modelo de datos

Para el alcance del desafío se utilizó una única tabla: `mercado_livre_items`.

| Campo | Tipo | Descripción |
|---|---|---|
| `item_id` | VARCHAR(30) | ID de la publicación |
| `product_id` | VARCHAR(30) | ID del producto |
| `product_name` | TEXT | Nombre del producto |
| `seller_id` | BIGINT | ID del vendedor |
| `price_ars` | NUMERIC(14,2) | Precio en ARS |
| `exchange_rate` | NUMERIC(15,8) | Tasa ARS → USD utilizada |
| `price_usd` | NUMERIC(14,2) | Precio convertido a USD |
| `sold_quantity` | INTEGER | Cantidad vendida, cuando está disponible |
| `warranty` | TEXT | Información de garantía |
| `has_warranty` | BOOLEAN | Indica si la publicación tiene información de garantía |
| `shipping_mode` | VARCHAR(50) | Modalidad de envío |
| `logistic_type` | VARCHAR(50) | Tipo de logística |
| `free_shipping` | BOOLEAN | Indica si tiene envío gratis |
| `condition` | VARCHAR(20) | Condición del producto |
| `job_run` | TIMESTAMP | Timestamp de la ejecución |

El DDL completo está disponible en `sql/schema.sql`.

La clave primaria es:

```text
(item_id, job_run)
```

Esto permite guardar una misma publicación en ejecuciones diferentes sin sobrescribir el histórico.

Para consultar la última ejecución, las queries utilizan:

```sql
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
)
```

---

## Resultados

Las queries completas están disponibles en `sql/queries.sql`.

Los resultados a continuación corresponden a una ejecución de referencia y pueden cambiar con nuevas ejecuciones.

### 1. Vendedores con múltiples publicaciones

```sql
SELECT
    seller_id,
    COUNT(*) AS publications
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
)
GROUP BY seller_id
HAVING COUNT(*) > 1
ORDER BY publications DESC;
```

Se encontraron **51 publicaciones de 47 vendedores diferentes**.

Cuatro vendedores tenían más de una publicación:

| seller_id | publicaciones |
|---:|---:|
| 3135574 | 2 |
| 50034844 | 2 |
| 4529954 | 2 |
| 214988544 | 2 |

### 2. Promedio de ventas por vendedor

La query preparada es:

```sql
SELECT
    seller_id,
    ROUND(AVG(sold_quantity), 2) AS average_sales
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
)
AND sold_quantity IS NOT NULL
GROUP BY seller_id
ORDER BY average_sales DESC;
```

Durante las pruebas, las consultas realizadas para obtener los detalles de los ítems devolvieron `HTTP 403 (Access Denied)` con la autenticación utilizada. Por eso no fue posible obtener `sold_quantity` de forma confiable.

El campo se guarda como `NULL` y no como `0`, porque cero significaría que la publicación no tuvo ventas, mientras que en este caso el dato no está disponible.

Tampoco se utilizó `available_quantity` u otro campo como aproximación, ya que representaría una métrica diferente.

La query queda preparada para utilizarse si `sold_quantity` está disponible con otro nivel de acceso.

### 3. Precio promedio en USD

```sql
SELECT
    ROUND(AVG(price_usd), 2) AS average_price_usd
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
);
```

Resultado de la ejecución de referencia:

```text
USD 821.91
```

### 4. Porcentaje de publicaciones con garantía

```sql
SELECT
    COUNT(*) AS total_items,
    COUNT(*) FILTER (
        WHERE has_warranty = TRUE
    ) AS items_with_warranty,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE has_warranty = TRUE
        ) / COUNT(*),
        2
    ) AS warranty_percentage
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
);
```

Resultado:

```text
Total de publicaciones: 51
Con garantía: 50
Porcentaje: 98.04%
```

### 5. Métodos de envío

```sql
SELECT
    shipping_mode,
    logistic_type,
    COUNT(*) AS publications
FROM mercado_livre_items
WHERE job_run = (
    SELECT MAX(job_run)
    FROM mercado_livre_items
)
GROUP BY
    shipping_mode,
    logistic_type
ORDER BY publications DESC;
```

Resultado:

| shipping_mode | logistic_type | publicaciones |
|---|---|---:|
| me2 | drop_off | 27 |
| me2 | xd_drop_off | 20 |
| me2 | cross_docking | 4 |

El método de envío encontrado fue `me2`. Dentro de ese método se identificaron tres tipos de logística: `drop_off`, `xd_drop_off` y `cross_docking`.

---

## Decisiones y problemas encontrados

### La búsqueda devolvía otros modelos

La búsqueda textual no devolvía únicamente el S24 FE.

En las primeras ejecuciones esto llegó a afectar el precio promedio porque entraban productos que no pertenecían a la población analizada.

En lugar de eliminar precios altos utilizando un límite arbitrario, primero revisé qué productos estaban entrando en el análisis.

El problema estaba en la selección de los productos, por lo que agregué el filtro de marca y modelo antes de consultar las publicaciones.

### Productos sin publicaciones

Algunos productos del catálogo no tenían publicaciones disponibles y devolvían `404` al consultar sus publicaciones.

En ese caso se devuelve una lista vacía y la ETL continúa con el siguiente producto.

### `sold_quantity`

La principal limitación fue el acceso a la cantidad vendida.

Las consultas probadas para obtener ese dato devolvieron `403` con la autenticación utilizada.

Como no había una fuente confiable para completar esa información, el campo se mantuvo como `NULL` en lugar de estimarlo a partir de otra métrica.

### PostgreSQL local

El desafío permitía utilizar una base local o cloud.

Se utilizó PostgreSQL local porque era suficiente para el volumen procesado y permitía realizar la carga y las consultas SQL sin agregar infraestructura innecesaria.

---

## Overengineering: qué podría haber agregado y no agregué

Durante el desarrollo se consideraron algunas soluciones que serían útiles en un pipeline mayor o en producción, pero que para este desafío agregarían más complejidad que beneficio.

### Docker

Se podría utilizar Docker y Docker Compose para levantar la aplicación y PostgreSQL de forma estandarizada.

Para una ejecución local, el entorno virtual y PostgreSQL fueron suficientes. Docker tendría más sentido si el proyecto necesitara ejecutarse en diferentes ambientes o distribuirse a otros equipos.

### Airflow o Prefect

Un orquestador podría encargarse del scheduling, retries y seguimiento de las ejecuciones.

En este proyecto el flujo es corto y lineal:

```text
Extract → Transform → Load
```

Agregar un orquestador para una ejecución manual de tres pasos no resolvería un problema actual.

### Retry y exponential backoff

El cliente trata errores HTTP y timeouts, pero no repite automáticamente una request que falla.

En un pipeline recurrente se podrían agregar retries con intervalos progresivos para errores temporales y rate limits.

### Logging y monitoreo

Actualmente el seguimiento se realiza mediante mensajes en la terminal.

En producción se podría utilizar logging estructurado y métricas como duración de cada etapa, cantidad de registros procesados, errores por endpoint y variaciones de volumen entre ejecuciones.

### Renovación automática del token

`generate_token.py` permite generar el access token, pero el proceso todavía depende de un authorization code válido.

En una ejecución recurrente se podría utilizar `refresh_token` para automatizar la renovación y un servicio de secrets para almacenar las credenciales.

### Tests automatizados

`teste_api.py` funciona como una validación simple de los endpoints principales.

En un proyecto con mantenimiento continuo se podrían agregar tests con `pytest`, principalmente para el filtro del modelo, las transformaciones, el tratamiento de las respuestas de la API y la carga.

### Carga incremental

Actualmente cada ejecución se identifica con un nuevo `JOB_RUN`.

Con un volumen mayor se podrían procesar únicamente registros nuevos o modificados utilizando una estrategia incremental y `UPSERT`.

### Bulk insert

Para las 51 publicaciones de la ejecución de referencia, la carga actual es suficiente.

Con un volumen mucho mayor se podrían utilizar mecanismos como `execute_values` o `COPY`.

### Extracción concurrente

Las publicaciones se consultan de forma secuencial.

Con muchos más productos, las requests independientes podrían ejecutarse de forma concurrente, respetando los límites de la API.

### Cloud

Para este volumen, PostgreSQL local es suficiente.

Si el pipeline creciera, integrara otras fuentes o alimentara análisis compartidos, una solución como BigQuery podría ser una alternativa.

### Modelo normalizado

También sería posible separar productos, vendedores, publicaciones, ejecuciones y tasas de cambio en tablas diferentes.

Para las preguntas de este desafío, una sola tabla mantiene las consultas y la carga más simples. Con más fuentes, mayor histórico o reutilización de esas entidades, tendría sentido revisar el modelo.

### Validaciones de calidad

Actualmente existe una validación específica para marca y modelo porque fue un problema encontrado durante el desarrollo.

En un pipeline mayor se podrían agregar controles para campos obligatorios, duplicados, precios fuera de rango, cambios de schema y variaciones inesperadas en la cantidad de registros.

### CI/CD

GitHub Actions podría ejecutar tests y validaciones automáticamente con cada cambio.

No se agregó porque el proyecto tiene un alcance pequeño y no existe un flujo continuo de deploy.

---

## Limitaciones

La principal limitación de esta implementación es que `sold_quantity` no estuvo disponible con el acceso utilizado.

Por eso fue posible responder cuatro de las cinco preguntas con los datos extraídos. La query para calcular el promedio de ventas quedó implementada, pero no se presenta un resultado que no pueda ser respaldado por los datos.

Los resultados también representan el estado del marketplace en el momento de la ejecución. Precios, vendedores, publicaciones, garantías y opciones de envío pueden cambiar con el tiempo.

---

## Conclusión

El proyecto implementa un flujo ETL completo para analizar publicaciones del Samsung Galaxy S24 FE en Mercado Libre Argentina.

Durante el desarrollo fue necesario agregar una validación adicional porque la búsqueda textual incluía otros modelos. También se mantuvieron como `NULL` los datos que no pudieron obtenerse de forma confiable, en lugar de estimarlos con otras variables.

La solución final mantiene un flujo simple:

```text
Mercado Libre API → Python → PostgreSQL → SQL
```

Para el alcance actual fue suficiente para extraer los datos, transformarlos, mantener el histórico por ejecución y responder las preguntas soportadas por la información disponible.