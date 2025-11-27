## Real-Time Sports Performance Tracking System – Documentación Técnica

### 1. Visión General

Este proyecto implementa un sistema de **analítica deportiva en tiempo real** usando:

- Backend en `FastAPI` (`app.py`).
- Dashboard HTML/JS (`index.html`) con Chart.js y Plotly.
- Redis como cache y para estructuras probabilísticas (`HyperLogLog`) y colas.
- Algoritmos de streaming, MapReduce y modelos probabilísticos/ML.

La idea central es recibir eventos de atletas, procesarlos con estructuras de datos eficientes y mostrar métricas y predicciones en un panel en vivo.

---

### 2. Arquitectura y Flujo de Datos

- **Frontend (`index.html`)**  
  - Conecta por WebSocket (`/ws`) para recibir:
    - `initial_data` (analytics cache inicial).
    - `athlete_processed` (nuevo atleta procesado).
    - `heartbeat` (estado de conexión).  
  - Consume APIs REST (`/api/analytics/summary`, `/api/streaming/stats`, `/api/prediction/monte_carlo`).
  - Tiene controles para generar datos de prueba y refrescar métricas.

- **Backend (`app.py`)**  
  - Mantiene:
    - `processed_athletes`: lista en memoria de todos los registros.
    - Instancias globales de algoritmos: Bloom, Count-Min, DGIM, AMS-F2, Markov, KNN, MinWise, RunningMoments, etc.
    - `analytics_cache`: cache de resultados para el dashboard.
  - Expone endpoints FastAPI:
    - `POST /api/athlete/process`: ingesta de un nuevo atleta.
    - `GET /api/analytics/summary`: devuelve ranking de jugadores, promedios por posición, Markov, etc.
    - `GET /api/streaming/stats`: estadísticas de estructuras de streaming (HLL, DGIM, AMS-F2, MinWise).
    - `POST /api/prediction/monte_carlo`: simulación Monte Carlo.
    - `GET /api/similarity/{athlete_id}`: KNN de atletas similares.

- **Redis**  
  - `HyperLogLog` para estimar jugadas únicas.
  - Lista `events:timeline` para eventos que se difunden por WebSocket.

**Flujo básico de un atleta:**
1. Llega un JSON a `POST /api/athlete/process`.
2. Se normaliza el esquema (snake_case ↔ camelCase).
3. Se almacena en `processed_athletes` y se lanza `process_athlete_record` como tarea en segundo plano.
4. `process_athlete_record` actualiza estructuras de streaming y modelo de Markov, y emite un evento por WebSocket.
5. Periódicamente `update_analytics_cache()` ejecuta los algoritmos MapReduce y actualiza `analytics_cache`.
6. El dashboard pide `/api/analytics/summary` y `/api/streaming/stats` para refrescar las gráficas.

---

### 3. Algoritmos de Streaming y Estructuras Probabilísticas

#### 3.1 Bloom Filter (`bloom_filter_module.py`)

- **Objetivo**: saber si una jugada (`sport:playType`) ya se analizó, sin guardar todas las jugadas.
- **Estructura**: bit array de tamaño fijo + `k` funciones hash.
- **Inserción**: para una jugada `x`, se calculan `k` hashes y se ponen a 1 las posiciones correspondientes.
- **Consulta**:
  - Si alguna posición está a 0 → el elemento **seguro** que no está.
  - Si todas son 1 → el elemento *probablemente* está (posibles falsos positivos, nunca falsos negativos).
- **Complejidad**: tiempo O(k) ≈ O(1); memoria O(m) bits.
- **Uso en el sistema**: evitar reprocesar tipos de jugadas en `process_athlete_record`.

#### 3.2 Count-Min Sketch (`count_min_sketch.py`)

- **Objetivo**: contar apariciones de cada atleta sin guardar todos los eventos.
- **Estructura**: matriz `depth × width` de contadores, una función hash por fila.
- **Actualización**: para cada atleta `id`, se calcula un hash por fila y se incrementan los buckets correspondientes.
- **Consulta**: frecuencia estimada
  \(\hat{f}(x) = \min_i\{ \text{counts}[i][h_i(x)] \}\).  
  No subestima (sesgo hacia arriba) y el error está acotado por `width`/`depth`.
- **Uso**: `cms.add(player_id, 1)` por cada registro procesado.

#### 3.3 HyperLogLog (Redis)

- **Objetivo**: estimar cuántas jugadas únicas ha habido (cardinalidad) con poca memoria.
- **Idea**: utiliza hashes de las jugadas y cuenta el número máximo de ceros a la izquierda en la representación binaria para estimar cardinalidad.
- **Uso**:
  - Inserción: `PFADD hll:plays "<sport>|<playType>|<player_id>"`.
  - Consulta: `PFCOUNT hll:plays` devuelve aproximación de jugadas únicas.
- **Relación con el dashboard**: métrica “Unique Plays (HLL)”.

#### 3.4 DGIM (`dgim.py`)

- **Objetivo**: contar cuántos 1s (picos de rendimiento) hay en una ventana deslizante reciente sin guardar toda la secuencia.
- **Estrategia** (algoritmo DGIM):
  - Agrupa bits en *buckets* de tamaño potencia de dos (1, 2, 4, 8, …).
  - Mantiene como máximo *dos* buckets de cada tamaño.
  - Descarta buckets cuando quedan fuera de la ventana de tiempo.
- **Consulta**: suma los tamaños de los buckets activos; el bucket más antiguo se cuenta parcialmente.
- **Uso**:
  - Al procesar un atleta: `dgim_global.add_bit(1 if record.get("performancePeak") else 0)`.
  - En `/api/streaming/stats`: `dgim_peaks = dgim_global.query()`.
- **Dashboard**: métrica “Peak Performance (DGIM)”.

#### 3.5 AMS-F2 (`ams_f2.py`)

- **Objetivo**: estimar el segundo momento \( F_2 = \sum_x f_x^2 \) de la distribución de velocidades (relacionado con varianza y concentración).
- **Algoritmo AMS (Alon–Matias–Szegedy)**:
  - Mantiene `k` muestras aleatorias del flujo.
  - Cada muestra contribuye con un estimador de \( F_2 \).
  - Se promedian las estimaciones de las `k` muestras.
- **Uso**:
  - Se discretiza la velocidad: `speed_bin = int(speed)`.
  - `ams_speed.update(speed_bin, 1)` por cada registro.
  - `/api/streaming/stats` llama `ams_speed.estimate_F2()`.
- **Dashboard**: métrica “Speed Variance (AMS-F2)”.  

#### 3.6 MinWise Sampling (`minwise_sampler.py`)

- **Objetivo**: mantener una muestra representativa de registros “interesantes” (por ejemplo, picos de rendimiento) sin guardar todos.
- **Idea**:
  - Para cada elemento se calcula un hash.
  - Se guardan solo los `k` elementos con hash mínimo (min-wise hashing).
- **Uso**:
  - Si `performancePeak` es verdadero, se llama `minwise.consider(record)`.
  - La función `minwise.sample()` devuelve la muestra actual.

#### 3.7 Running Moments (`online_moments.py`)

- **Objetivo**: calcular media, varianza y otros momentos de manera incremental.
- **Técnica**: utiliza fórmulas tipo Welford para evitar errores numéricos:
  \[
  \mu_n = \mu_{n-1} + \frac{x_n - \mu_{n-1}}{n}
  \]
- **Uso**:
  - `player_moments[player_id]["speed"].update(speed)`.
  - `player_moments[player_id]["accuracy"].update(accuracy)`.
  - Permite tener estadísticas por jugador sin guardar todos los valores.

---

### 4. Modelo de Markov (`markov_module.py`)

- **Estados**: `["peak", "good", "average", "declining", "injured"]`.
- **Tipo de modelo**: cadena de Markov de primer orden.
  - La probabilidad del siguiente estado depende solo del estado actual.
- **Matriz de transición**:
  \[
  P_{ij} = P(\text{estado}_\text{destino}=j \mid \text{estado}_\text{origen}=i)
  \]
- **Actualización de conteos**:
  - Al procesar un atleta:
    - Se lee `previousPerformanceState` y `performanceState`.
    - `markov.observe_transition(prev_state, current_state)` incrementa la celda correspondiente en una matriz de conteos `counts[i, j]`.
- **Cálculo de probabilidades**:
  - Se aplica suavizado aditivo para evitar ceros:
    \[
    P_{ij} = \frac{\text{counts}_{ij} + \epsilon}{\sum_j (\text{counts}_{ij} + \epsilon)}
    \]
- **Distribución estacionaria**:
  - Se calcula por el método de la potencia: se itera \( v_{k+1} = v_k P \) hasta converger.
  - Representa la probabilidad a largo plazo de estar en cada estado.
- **Propiedades adicionales**:
  - `is_aperiodic()`: comprueba, de forma práctica, si la cadena es aperiódica.
  - `is_irreducible()`: verifica si todos los estados son alcanzables.
  - `mixing_time_approx()`: estima el tiempo de mezcla, es decir, cuántos pasos tarda en aproximarse a la distribución estacionaria.
- **Dashboard**:
  - Se expone `transition_prob_matrix_readable()` y se convierte en un mapa de calor:
    - Eje Y: estado origen (*From State*).
    - Eje X: estado destino (*To State*).
    - Color: probabilidad de transición \( P_{ij} \).

---

### 5. Machine Learning y Predicciones

#### 5.1 KNN – Similaridad de Atletas (`knn_athlete_similarity.py`)

- **Objetivo**: dado un atleta, encontrar otros con características similares.
- **Representación**: cada atleta se transforma en un vector de características (velocidad, precisión, stamina, puntos, etc.).
- **Modelo**:
  - Se usa K-Nearest Neighbors (KNN):
    - Distancia típica: euclídea.
    - `n_neighbors` configurable (por defecto 5).
- **Flujo**:
  - `knn_analyzer.fit(processed_athletes)` entrena el modelo.
  - `find_similar_athletes(target_athlete)` devuelve los vecinos más cercanos.
  - Endpoint `GET /api/similarity/{athlete_id}` expone esta funcionalidad.

#### 5.2 Monte Carlo (`monte_carlo_predict.py`)

- **Objetivo**: estimar la probabilidad de éxito de una jugada o acción deportiva usando simulación Monte Carlo.
- **Entrada**:
  - `speed`, `accuracy`, `stamina`, y número de simulaciones (`simulation_count`).
- **Técnica**:
  - Se generan múltiples simulaciones donde se perturban estos parámetros según ciertas distribuciones.
  - Se contabiliza en cuántas simulaciones se supera un umbral de “éxito”.
  - Probabilidad estimada:
    \[
    \hat{p} = \frac{\text{simulaciones exitosas}}{\text{simulaciones totales}}
    \]
- **Uso**:
  - Expuesto en `POST /api/prediction/monte_carlo`.
  - El dashboard permite jugar con los parámetros y muestra el porcentaje de éxito resultante.

---

### 6. MapReduce (`mapreduce_algorithms.py`)

Todas las clases heredan de `MapReduceEngine`, que define:

- `emit(key, value)`: almacena pares `(key, value)` en `intermediate_data`.
- `clear_intermediate()`: limpia datos para iniciar un nuevo job.

Actualmente los jobs son **secuenciales**, no distribuidos: el patrón MapReduce se usa de forma local.

#### 6.1 PlayerPerformanceCounter

- **Objetivo**: contar el número total de “juegos” por jugador y obtener los más activos.
- **Map**:
  - Lee `_id` y `performanceData.gamesPlayed` (si falta, asume 1).
  - Emite `(player_id, gamesPlayed)`.
- **Reduce**:
  - Suma las listas de valores por player: total de juegos.
- **Salida**: diccionario `{player_id: total_juegos}`, ordenado de mayor a menor.
- **Dashboard**:
  - Se usan los 10 primeros en `analytics_cache["player_rankings"]`.
  - Alimenta la gráfica “Performance Analytics” (eje X jugadores, eje Y juegos).

#### 6.2 AverageScoreCalculator

- **Objetivo**: calcular el **promedio de puntos anotados por posición**.
- **Map**:
  - `(position, performanceData.pointsScored)`.
- **Reduce**:
  - Calcula para cada posición:
    - `total`, `count`, `average = total / count`.
    - Además `max` y `min`.
- **Salida**:
  ```json
  {
    "Forward":  {"average": 15.5, "count": 10, "total": 155, "max": 25, "min": 5},
    "Defender": {"average":  8.2, "count":  5, "total":  41, "max": 12, "min": 3}
  }
  ```
- **Dashboard**:
  - Gráfica “MapReduce Analytics Results”: barras por posición (Forward, Midfielder, etc.), altura = promedio de puntos.

#### 6.3 SportsReportGenerator

- **Objetivo**: unir datos de jugador y datos de equipo (tipo “join” lógico).
- **Map**:
  - Para cada registro, emite:
    - `(player_id, {type: "player_stats", ...})`.
    - `(player_id, {type: "team_info", ...})`.
- **Reduce**:
  - Combina ambas entradas para formar un reporte consolidado por jugador.
- **Uso**: útil para informes más detallados, integrando rendimiento individual y dinámica de equipo.

#### 6.4 SportsSystemCostCalculator

- **Objetivo**: estimar los costos del sistema basándose en `resourceUsage`:
  - `dataStorageMB`, `processingTimeMS`, `networkBandwidthKbps`.
- **Cálculo**:
  - Multiplica cada recurso por su costo unitario (almacenamiento, CPU, red).
  - Devuelve:
    - `total_cost`, `storage_cost`, `processing_cost`, `bandwidth_cost` y `cost_per_player`.
- **Interpretación**: sirve para analizar la viabilidad económica del sistema.

#### 6.5 SportsProcessingPerformance

- **Objetivo**: simular el rendimiento del procesamiento con distintos tamaños de cluster.
- **Método**:
  - `test_cluster_performance(data, cluster_sizes)` divide los datos en `cluster_size` chunks.
  - Procesa cada chunk (simulado) y mide tiempos.
  - Devuelve métricas como `records_per_second` y `total_processing_time` por configuración.
- **Uso**: analizar cómo escalaría el sistema si se distribuyera en varios nodos.

---

### 7. Dashboard y Visualización (`index.html`)

#### 7.1 Métricas en Tarjetas

- **Total Athletes**: número total de atletas procesados (`len(processed_athletes)` + eventos WebSocket).
- **Unique Plays (HLL)**: cardinalidad estimada con `HyperLogLog` en Redis.
- **Peak Performance (DGIM)**: conteo aproximado de picos en ventana reciente (DGIM).
- **Speed Variance (AMS-F2)**: estimación del segundo momento de la distribución de velocidades.

#### 7.2 Performance Analytics (Line Chart)

- Usa `analytics.player_rankings` (salida de `PlayerPerformanceCounter`).
- **Eje X**: hasta 10 jugadores más activos (etiquetados como `Player 1`, `Player 2`, …).
- **Eje Y**: total de juegos procesados por jugador.

#### 7.3 MapReduce Analytics Results (Bar Chart)

- Usa `analytics.position_averages` (salida de `AverageScoreCalculator`).
- **Eje X**: posiciones fijas (`Forward`, `Midfielder`, `Defender`, `Goalkeeper`, `Guard`, `Center`).
- **Eje Y**: promedio de `pointsScored` por posición.

#### 7.4 Markov Chain Analysis (Heatmap)

- Usa `analytics.markov_predictions.transition_matrix`.
- **Eje Y**: estado origen (`peak`, `good`, `average`, `declining`, `injured`).  
- **Eje X**: estado destino.
- **Color**: probabilidad de transición \( P_{ij} \) (tonos de azul).

#### 7.5 Monte Carlo Prediction

- Formulario que envía `speed`, `accuracy`, `stamina` a `/api/prediction/monte_carlo`.

- Muestra `%` de éxito estimado en base a `simulation_count` simulaciones.

---

### 8. Despliegue

#### 8.1 Entorno Virtual (sin Docker)

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python app.py
```

Requiere tener Redis ejecutándose localmente.

#### 8.2 Docker (recomendado)

- `Dockerfile`: imagen `python:3.11-slim`, instala `requirements.txt` y arranca `uvicorn app:app`.
- `docker-compose.yml`: servicios `app` y `redis:7-alpine`.

```bash
docker compose up --build
```

Luego abrir `http://localhost:8000` para ver el dashboard.

---

### 9. Resumen Conceptual

- **Streaming**: estructuras probabilísticas (Bloom, Count-Min, HLL, DGIM, AMS-F2, MinWise, Running Moments) permiten manejar flujos grandes con memoria acotada.
- **Probabilidad y ML**: la cadena de Markov captura la dinámica de estados de rendimiento; KNN y Monte Carlo permiten análisis de similitud y predicciones de éxito.
- **MapReduce**: se aplica el patrón map/reduce para agregados por jugador, posición y análisis de costos, aunque en este proyecto se ejecuta de manera secuencial.
- **Dashboard**: integra todas las métricas en tiempo real ofreciendo una visión clara del rendimiento deportivo en un partido simulado.

Esta documentación puede usarse como base para presentaciones, reportes técnicos o comentarios dentro del repositorio.


