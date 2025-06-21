import streamlit as st
import json
import time
from dbn2 import PostgreSQL
from plotly_utils import generar_grafico_barras, generar_grafico_torta, generar_grafico_lineas
# from streamlit_echarts import st_echarts

# options = {
#     "title": {"text": "Top 10 movies by rating"},
#     "tooltip": {},
#     "xAxis": {"type": "category", "data": ["Inception", "Toy Story 3", "..."]},
#     "yAxis": {"type": "value"},
#     "series": [{"type": "bar", "data": [8.8, 8.3, ...]}]
# }

# st_echarts(options)
st.title("Panel de Visualización")

if st.button("Esperar nuevo gráfico"):
    db = PostgreSQL()

    with st.spinner("Esperando nuevo gráfico..."):
        while True:
            print("🔄 Esperando datos nuevos...")
            df = db.query("SELECT created_at, json_data, chart_type FROM chart_results ORDER BY created_at DESC LIMIT 1;")
            if not df.empty:
                row = df.iloc[0]
                chart_id = row["created_at"]
                print(f"🆕 Registro detectado: {chart_id}")

                try:
                    json_chart = json.loads(row["json_data"])
                    print("📦 JSON cargado:", json_chart)
                except Exception as e:
                    print("❌ Error al parsear JSON:", e)
                    st.error("Error al cargar el gráfico.")
                    break

                tipo = row.get("chart_type", "").lower()
                print("📊 Tipo de gráfico detectado:", tipo)

                st.success("Gráfico recibido")

                try:
                    if tipo == "bar":
                        graf = generar_grafico_barras(json_chart)
                    elif tipo == "pie":
                        graf = generar_grafico_torta(json_chart)
                    elif tipo == "line":
                        graf = generar_grafico_lineas(json_chart)
                    else:
                        print("⚠️ Tipo no reconocido:", tipo)
                        st.error("Tipo de gráfico no reconocido.")
                        break

                    st.plotly_chart(graf, use_container_width=True)
                    print("✅ Gráfico renderizado")

                    time.sleep(15)
                    db.execute("DELETE FROM chart_results WHERE created_at = %s;", (chart_id,))
                    st.info("Gráfico eliminado de la base.")
                    print("🗑️ Gráfico eliminado de la tabla chart_results.")
                    break

                except Exception as e:
                    print("❌ Error al renderizar gráfico:", e)
                    st.error("Error al generar el gráfico.")
                    break
            else:
                print("⏳ Sin nuevos registros...")
            time.sleep(1)
