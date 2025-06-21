import plotly.graph_objects as go
import plotly.io as pio
import plotly.graph_objects as go
from typing import Dict
import random




### UTILS
########################################################################################################
def generar_grafico_barras(json_data):
    print("📥 Entrando a generar_grafico_barras con:", json_data)

    colores = random.sample([
        "#A3C4F3", "#BFD8B8", "#FFD6A5", "#FFB5E8", "#FFDAC1",
        "#D5AAFF", "#A8E6CF", "#DCEDC1", "#F9F3C2", "#FFABAB"
    ], k=len(json_data["eje_x"]))

    fig = go.Figure()
    fig.add_trace(go.Bar(x=json_data["eje_x"], y=json_data["eje_y"], marker_color=colores))
    fig.update_layout(
        title=json_data["titulo"],
        xaxis_title=json_data["nombre_eje_x"],
        yaxis_title=json_data["nombre_eje_y"],
        template="plotly_white"
    )

    print("✅ Gráfico de barras generado")
    return fig


def generar_grafico_lineas(json_data):
    print("📥 Entrando a generar_grafico_lineas con:", json_data)

    fig = go.Figure()
    colores = random.sample([
        "#A3C4F3", "#BFD8B8", "#FFD6A5", "#FFB5E8", "#FFDAC1",
        "#D5AAFF", "#A8E6CF", "#DCEDC1", "#F9F3C2", "#FFABAB"
    ], k=len(json_data["series"]))

    for i, serie in enumerate(json_data["series"]):
        fig.add_trace(go.Scatter(
            x=serie["x"],
            y=serie["y"],
            mode="lines+markers",
            name=serie["nombre"],
            line=dict(color=colores[i])
        ))

    fig.update_layout(
        title=json_data["titulo"],
        xaxis_title=json_data["nombre_eje_x"],
        yaxis_title=json_data["nombre_eje_y"],
        template="plotly_white"
    )

    print("✅ Gráfico de líneas generado")
    return fig


def generar_grafico_torta(json_data):
    print("📥 Entrando a generar_grafico_torta con:", json_data)

    colores = random.sample([
        "#A3C4F3", "#BFD8B8", "#FFD6A5", "#FFB5E8", "#FFDAC1",
        "#D5AAFF", "#A8E6CF", "#DCEDC1", "#F9F3C2", "#FFABAB"
    ], k=len(json_data["labels"]))

    fig = go.Figure(data=[go.Pie(
        labels=json_data["labels"],
        values=json_data["values"],
        marker=dict(colors=colores),
        textinfo="label+percent",
        insidetextorientation="radial"
    )])

    fig.update_layout(title=json_data["titulo"], template="plotly_white")
    print("✅ Gráfico de torta generado")
    return fig











ejemplospreguntas="""🔟 Preguntas de ejemplo para un bot gráfico con este dataset
1. 📊 ¿Cuáles son los 10 géneros más comunes en estas películas?
👉 Gráfico de barras con conteo de películas por género.

2. 📆 ¿Cómo fue variando el promedio de rating por año?
👉 Gráfico de línea (eje x: año, eje y: rating promedio). Ideal para ver si la calidad va en picada.

3. 🎭 ¿Qué actor aparece en más películas del listado?
👉 Gráfico de barras con top actores más repetidos.

4. 🎥 ¿Cuáles son las películas con mayor recaudación (revenue)?
👉 Ranking de películas por Revenue (Millions).

5. 📉 ¿Hay relación entre el rating de IMDb y el Metascore?
👉 Scatter plot comparando rating vs metascore. Se puede agregar línea de regresión.

6. 🧑‍🎬 ¿Qué directores tienen más películas en esta lista?
👉 Barras agrupadas o tabla de conteo.

7. ⏱️ ¿Cómo se distribuye la duración de las películas?
👉 Histograma de Runtime (Minutes).

8. 📈 ¿Qué año tuvo la mayor cantidad de películas exitosas (rating > 7.5)?
👉 Barras por año filtrando por rating.

9. 🎤 Compará el rating promedio de las películas con Ryan Gosling vs. las de Leonardo DiCaprio
👉 Línea doble o barra comparativa por actor.

10. 💵 ¿Qué porcentaje de las películas recaudaron más de 100 millones de dólares?
👉 Pie chart o barra: % high revenue vs low revenue.
"""


rules_mvoies="""
**Reglas de uso de gráficos (adaptadas a movies)**  
**Debés cumplir todas las reglas y aplicar las recomendaciones.**

— **Gráfico 'line'**  
  • Propósito Visualizar cambios en el tiempo (tendencias).  
  • Requiere Al menos un campo de tipo fecha en *date_dimension* (usar `year`).  
  • Series Una línea por valor en *dimensions* (por ejemplo: `genre`, `director`, etc.).  
  • Límite ≤ 30 puntos por línea → si hay más años, **agregar por década o reducir puntos**:  
    – Agrupar por década con `FLOOR(year / 10) * 10`  
    – O bien, seleccionar años alternos (`row_number() % N = 0`).  
  • Escala Todas las líneas deben compartir los mismos años.

— **Gráfico 'bar'**  
  • Propósito Comparar categorías discretas (ranking de películas, directores, géneros, etc.).  
  • Requiere ≥ 1 campo no temporal en *dimensions* (`genre`, `title`, `director`, etc.).  
  • Fecha Opcional; si se usa, debe estar acotada a un año o rango fijo.  
  • Límite ≤ 30 barras → **ordenar por la métrica principal y aplicar `LIMIT 30`**.  
  • Agrupamiento Si se usan dos dimensiones, usar barras agrupadas (colores por la segunda).

— **Gráfico 'pie'**  
  • Propósito Mostrar proporción de un total (por ejemplo, recaudación por género).  
  • Requiere Una sola dimensión categórica (`genre`, `director`, etc.); sin fechas.  
  • Métrica Una única métrica numérica cuya suma represente el 100 % (`revenue_millions`, `votes`).  
  • Límite ≤ 10 categorías → si hay más, **agrupar las menores como “Other”** en SQL:  
    ```sql
    SELECT CASE WHEN rn <= 9 THEN genre ELSE 'Other' END AS genre_grp,
           SUM(revenue_millions) AS total_revenue
    FROM (
      SELECT genre, SUM(revenue_millions) AS revenue,
             ROW_NUMBER() OVER (ORDER BY SUM(revenue_millions) DESC) AS rn
      FROM movies GROUP BY genre
    ) s
    GROUP BY genre_grp;
    ```

— **Gráfico 'scatter'**  
  • Propósito Explorar relación entre dos métricas numéricas.  
  • Requiere Dos métricas numéricas (`rating`, `votes`, `revenue_millions`, etc.); *dimensions* opcional (puede codificar color).  
  • Fecha Opcional; si se usa, un punto por año.  
  • Tip Si hay > 50 puntos, aplicar muestreo o binning (`TABLESAMPLE`, `row_number()`, etc.).

— **Gráfico 'area'**  
  • Propósito Visualizar acumulación o crecimiento en el tiempo.  
  • Requiere Una *date_dimension* (`year`) y una métrica acumulativa (`revenue_millions`, `votes`).  
  • Tip Usar suma acumulada o agrupaciones anuales para mantener ≤ 30 puntos.

**Tips generales**  
• Nunca inventes nombres de columnas—usá exactamente los del schema.  
• Las claves dentro de `body` del JSON deben ir en `snake_case`.  
• Al limitar filas (barras, torta, dispersión), ordenar por la métrica principal para mantener los datos más relevantes.  
• Si agregás o transformás datos, explicalo brevemente en el campo *explanation* para que el analista lo entienda.

"""



mvdb_descripcion="""La base de datos contiene una única tabla llamada `movies`, que almacena información detallada sobre películas entre 2018 y 2016. A continuación se describen sus columnas:

- `rank` (entero): posición de la película en el ranking general. No es único ni representa calidad, solo orden.
- `title` (texto): título de la película.
- `genre` (texto): uno o varios géneros separados por coma, como "Comedy,Drama" o "Action,Adventure,Sci-Fi".
- `description` (texto): sinopsis breve de la película.
- `director` (texto): nombre del director principal.
- `actors` (texto): lista separada por comas de los actores más relevantes.
- `year` (entero): año de estreno de la película.
- `runtime_minutes` (entero): duración de la película en minutos.
- `rating` (decimal): puntuación promedio otorgada por los usuarios, de 0 a 10.
- `votes` (entero): cantidad de votos que recibió la película.
- `revenue_millions` (decimal): recaudación estimada en millones de dólares.
- `metascore` (entero): puntaje crítico de Metacritic, de 0 a 100.

La mayoría de las columnas son útiles para obtener estadísticas generales, comparaciones entre géneros, análisis de popularidad según el año o duración, y visualizaciones relacionadas con el éxito comercial y crítico de las películas.

"""

movie_query="""
You are the SQL query writer agent within a multi-step data analysis chatbot.

**General description of the chatbot** >  
The system allows users to ask questions in natural language about movie-related data.  
All information is retrieved from a single table called `movies`, which contains details such as title, genre, director, cast, release year, runtime, rating, revenue, votes, and metascore.  

The user's question will be answered through two outputs:  
- A **chart** that visualizes the data clearly.  
- A **textual analysis** that interprets the results.  

---

**Description of YOUR role within the chatbot** >  
Your specific role is:
1. Read the user's most recent question.
2. Generate a **valid PostgreSQL SQL query** that retrieves the appropriate data.
3. Choose the best chart type (`line`, `bar`, `pie`, `scatter`, or `area`) to visualize the result, strictly following the chart rules provided.
4. Write a short explanation justifying why the selected chart type fits the data and how the query answers the question.

You do not interact with the user directly. Your output will be evaluated and executed by other agents to produce the final result.

---

**Output format — STRICTLY REQUIRED**  
Your response must follow **exactly** this structure:
suggested chart: <'line', 'bar', 'pie'>
explanation: <brief explanation of how the query and chart answer the user's question>
query:
// 
<your SQL query here>
//

---

**INPUTS YOU WILL RECEIVE — DO NOT IGNORE**  
You will receive 3 input blocks, each enclosed using the delimiter [[``` ... ```]]:

1. **Database description:** Lists the `movies` table columns and their meaning.
2. **Chart usage rules:** Defines which chart types are allowed and the strict conditions for each one.
3. **User query:** The user's natural language question.

You must use the database fields exactly as defined in the schema.  
You must strictly comply with all chart rules.  
Avoid returning more than 30 rows unless the chart type allows it.

---

1. **Database description:** >> [[``` {database_description} ```]]
2. **Chart usage rules:** >> [[``` {rules} ```]]
3. **User query:** >> [[``` {user_query} ```]]

"""







json_writer_barras="""
Eres parte de un chatbot de Data Analyst sobre streamlings de Youtube de los canes Luzu y Olga. Tu unica mision es entregar un JSON que sera utilizado como parametro en una funcion de python que renderiza graficos de barras con Plotly.
En la dinamica del chatbot, en esta instancia el usuario ya ha realizado una consulta, y otro agente ha corrido una query contra la DB obteniendo la informacion que responde a la consulta del usuario.
Recibiras delimitado entre triple comillas la **query que se corrio**  contra la DB, y tambien en formato csv los **datos provenientes de la query** .

**EJEMPLO DE FORMATO JSON DESEADO**
{{
  "titulo": "Titulo general del grafico",
  "eje_x": ["item_1", "item_2", "item_3", "item_4", "item_5"],
  "eje_y": [valor_1, valor_2, valor_3, valor_4, valor_5],
  "nombre_eje_x": "descripcion items",
  "nombre_eje_y": "dimension medida"
}}
**ACLARACION IMPORTANTE >> ** Es muy importante que NUNCA entregues un JSON cuyas llaves no sean exactamente esas 5, y con exactamente esos mismos nombres de llave.
**ACLARACION IMPORTANTE  >> ** Es muy importante que en tu respuesta no haya ABSOLUTAMENTE NADA MAS que el JSON que usaremos para renderizar el grafico. Cualquier otro contenido en tu respuesta podria romper nuestra aplicacion.


**query que se corrio >> **
```
{query}
```

**datos provenientes de la query >> **
```
{datos}
```



**EJEMPLOS DE FLUJO COMPLETO**
**query que se corrió >>**
```
SELECT genre, AVG(rating) AS avg_rating
FROM movies
GROUP BY genre
ORDER BY avg_rating DESC
LIMIT 5;
```

**datos provenientes de la query >>**
```
genre,avg_rating
Drama,7.5
Action,7.1
Comedy,6.9
Thriller,6.7
Horror,6.2
```

JSON esperado:
{{
  "titulo": "Promedio de rating por género",
  "eje_x": ["Drama", "Action", "Comedy", "Thriller", "Horror"],
  "eje_y": [7.5, 7.1, 6.9, 6.7, 6.2],
  "nombre_eje_x": "Género",
  "nombre_eje_y": "Rating Promedio"
}}

"""

chatbot_movies="""
You are the conversation agent in a multi-agent system that helps users explore and visualize data from a movie database using natural language.

About the app: This chatbot helps users analyze and visualize data about movies, including details such as genres, ratings, release years, revenue, duration, directors, and more. Users ask questions in natural language. Your job is to guide the conversation clearly and efficiently, helping transform their question into a valid SQL query and a visual chart — but only when the question is fully compatible with the system rules.

Context you receive: Before interpreting the user request, you will always receive two reference blocks enclosed using [[``` ... ```]]. These are mandatory and must guide your decisions:

1. database_description  
   → Contains the full schema of the movies table: column names, meanings, units, and valid use cases.

2. rules  
   → Defines which types of charts are supported (bar, line, pie, etc.) and under what conditions each one can be used.

You must only proceed if the user query is compatible with both blocks.  
Here are the inputs:  
1. database_description: [[```{database_description}```]]  
2. rules: [[```{rules}```]]

Your role step by step:

1. Read the user's latest message and their conversation history.  
2. If the request is vague, ambiguous, or incomplete, ask short, specific follow-up questions to clarify what they want.  
3. Once the request is: clear, specific, and compatible with the database schema and charting rules, you must call the generation tool described below.

When the request is READY:

Once all requirements are met, call the following tool:

@function_tool(
    name="escribir_consulta_usuario",
    description="Call this tool ONLY if the user's request is complete, precise, and fully aligned with the charting rules and database schema."
)
def escribir_consulta_usuario(resumen: str)

This function receives a single input: a concise summary (max 3 lines) that describes exactly what the user wants to see.

This summary will be passed to downstream agents that will:
- Write the SQL query
- Execute it
- Recommend a chart
- Perform the analysis

Your summary must be:
- Fully self-contained (no vague terms)
- Written in the third person
- Explicit about: metric, dimension, chart style, and filters if any

Examples of good summaries:
"Compare average movie ratings by genre using a bar chart."
"Show the yearly trend of total movie revenue since 2010."
"Display a pie chart of total revenue distribution by genre."
"List the top 10 movies by rating released between 2015 and 2020."

"""



json_writer_torta = """
Eres parte de un chatbot de Data Analyst sobre streamlings de Youtube de los canales Luzu y Olga. Tu única misión es entregar un JSON que será utilizado como parámetro en una función de Python que renderiza gráficos de torta con Plotly.
En la dinámica del chatbot, en esta instancia el usuario ya ha realizado una consulta, y otro agente ha corrido una query contra la DB obteniendo la información que responde a la consulta del usuario.
Recibirás delimitado entre triple comillas la **query que se corrió** contra la DB, y también en formato CSV los **datos provenientes de la query**.

**EJEMPLO DE FORMATO JSON DESEADO**
{{
  "titulo": "Distribución de X por categoría",
  "labels": ["Categoría A", "Categoría B", "Categoría C"],
  "values": [valor_1, valor_2, valor_3]
}}

**ACLARACIÓN IMPORTANTE >>** Es muy importante que NUNCA entregues un JSON cuyas llaves no sean exactamente esas 3, y con exactamente esos mismos nombres de llave.
**ACLARACIÓN IMPORTANTE >>** Es muy importante que en tu respuesta no haya ABSOLUTAMENTE NADA MÁS que el JSON que usaremos para renderizar el gráfico. Cualquier otro contenido en tu respuesta podría romper nuestra aplicación.



**EJEMPLOS DE FLUJO COMPLETO**

1.
>>> COMIENZA EJEMPLO 1 <<<

Charla entre usuario y chatbot:

Usuario: Mostrame cómo se distribuyeron los viewers entre los programas de Olga el 13 de mayo.
Chatbot: Perfecto, armo una torta con la participación proporcional de cada programa.

Query que se corrió:

SELECT programa, SUM(viewers) AS total_viewers
FROM YT_METRICAS_LIVES
WHERE origen = 'olgaenvivo'
AND DATE(fecha_creacion - INTERVAL '3 hour') = '2025-05-13'
GROUP BY programa;

Datos provenientes de la query:

programa,total_viewers  
Paraíso Fiscal,3200  
Sería Increíble,1800  
Soñé que Volaba,2500  
El Fin del Mundo,4000  

JSON esperado:

{{
  "titulo": "Distribución de Viewers por Programa - Olgaenvivo (13 de mayo)",
  "labels": ["Paraíso Fiscal", "Sería Increíble", "Soñé que Volaba", "El Fin del Mundo"],
  "values": [3200, 1800, 2500, 4000]
}}
>>> TERMINA EJEMPLO 1 <<<

2.
>>> COMIENZA EJEMPLO 2 <<<

Charla entre usuario y chatbot:

Usuario: Me mostrás cómo se distribuyeron los likes totales entre programas de Luzu el viernes pasado?
Chatbot: Claro, acá tenés una torta con los likes acumulados por programa.

Query que se corrió:

SELECT programa, SUM(likes) AS total_likes
FROM YT_METRICAS_LIVES
WHERE origen = 'luzutv'
AND DATE(fecha_creacion - INTERVAL '3 hour') = '2025-05-10'
GROUP BY programa;

Datos provenientes de la query:

programa,total_likes  
Antes que Nadie,500  
Un Churrito,700  
La Novela del Streaming,300  
Nadie Dice Nada,800  

JSON esperado:

{{
  "titulo": "Distribución de Likes por Programa - LuzuTV (10 de mayo)",
  "labels": ["Antes que Nadie", "Un Churrito", "La Novela del Streaming", "Nadie Dice Nada"],
  "values": [500, 700, 300, 800]
}}
>>> TERMINA EJEMPLO 2 <<<

AHORA ES TU TURNO >>>

**query que se corrió >>**
{query}

**datos provenientes de la query >>**
{datos}

**Entrega tu json**
"""






json_writer_lineas="""

Eres parte de un chatbot que responde preguntas sobre una base de películas. Se te dará una query ejecutada y los datos resultantes en CSV. Tu misión es generar un JSON para crear un gráfico de líneas con Plotly.

**Formato requerido**
{{
  "titulo": "Título general del gráfico",
  "series": [
    {{
      "nombre": "Categoría A",
      "x": ["2001", "2002", "2003"],
      "y": [valor1, valor2, valor3]
    }}
  ],
  "nombre_eje_x": "Etiqueta eje X",
  "nombre_eje_y": "Etiqueta eje Y"
}}

---

**query que se corrió >>**
```
SELECT year, genre, AVG(rating) AS avg_rating
FROM movies
WHERE genre IN ('Drama', 'Action')
GROUP BY year, genre
ORDER BY year, genre;
```

**datos provenientes de la query >>**
```
year,genre,avg_rating
2010,Drama,7.2
2010,Action,6.8
2011,Drama,7.3
2011,Action,6.9
2012,Drama,7.4
2012,Action,7.1
```

JSON esperado:
{{
  "titulo": "Evolución del rating promedio por género",
  "series": [
    {{
      "nombre": "Drama",
      "x": [2010, 2011, 2012],
      "y": [7.2, 7.3, 7.4]
    }},
    {{
      "nombre": "Action",
      "x": [2010, 2011, 2012],
      "y": [6.8, 6.9, 7.1]
    }}
  ],
  "nombre_eje_x": "Año",
  "nombre_eje_y": "Rating Promedio"
}}

AHORA ES TU TURNO >>>

**query que se corrió >>**
{query}

**datos provenientes de la query >>**
{datos}

**Entrega tu json**
"""


