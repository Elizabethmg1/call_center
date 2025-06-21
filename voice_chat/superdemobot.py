# app.py
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import openai
from livekit.plugins.silero import VAD
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from dotenv import load_dotenv
import os
from livekit.agents import Agent, AgentSession, function_tool
load_dotenv()
import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from livekit.agents import function_tool, RunContext
from utils import analizer_movies,registrar_turno,chart_sys,sys_second_chart,analizer_sys,extract_outer_json,validate_chart_json,sys_prompt,translated_prompt,verifier_sys,second_try_sys,bot_answer,get_schema_metadata,consultar_turnos,chatbot_sys_glpi,chatbot_ttd,database_description,charts_rules
from openai import OpenAI
from plotly_utils import chatbot_movies, mvdb_descripcion,rules_mvoies,movie_query,json_writer_barras,json_writer_torta,json_writer_lineas
from datetime import datetime,timezone
from typing import TypedDict
from livekit.agents import function_tool, RunContext
from app_db import AppDb
# Conexión inicial a Google Calendar (idéntica)
api_key = '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'
client = OpenAI(api_key=api_key)

from dbn2 import PostgreSQL
db = PostgreSQL() 

def guardar_json_en_db(json_chart: dict, chart_type: str):
    json_str = json.dumps(json_chart)
    print("JSON que se va a guardar >>>>", json_str)
    try:
        db.execute(
            "INSERT INTO chart_results (json_data, chart_type) VALUES (%s, %s);",
            (json_str, chart_type)
        )
        db.conn.commit()
        print("✅ Inserción exitosa")
    except Exception as e:
        print("❌ Error al insertar:", e)


@function_tool(
    name="escribir_consulta_usuario",
    description="Esta tool solo debe ser llamada en caso que el agente considere que los datos son suficientes para renderizar el gráfico según todos los parámetros establecidos."
)
async def escribir_consulta_usuario(resumen: str) -> str:
    chatbot_summary = resumen
    query_answer = bot_answer(sys_prompt=movie_query.replace("\n", " ").format(user_query=chatbot_summary,rules=rules_mvoies,database_description=mvdb_descripcion), )
    chart_type = next((c for c in ['line', 'bar', 'pie'] if c in query_answer), None)
    print(f'QUERY ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {query_answer}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    sql_query = query_answer.split("//")[1].strip()
    data = db.query(sql_query)
    data_dict = str(data)
    print(f'GFDSGFDSGFDS GFDS G data_dict >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {data_dict}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

    if 'pie' in chart_type:
        prompt_jsonwr=json_writer_torta
    elif 'bar' in chart_type:
        prompt_jsonwr=json_writer_barras
    elif 'line' in chart_type:
        prompt_jsonwr=json_writer_lineas
    else:
        prompt_jsonwr='hace lo que puedas negri.'
    print(prompt_jsonwr)
    chart_answer = bot_answer(sys_prompt=prompt_jsonwr.replace("\n", " ").format(query = sql_query, datos=data_dict))
    
    
    
    print(f'chart_answer ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {chart_answer}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    chart_json = extract_outer_json(chart_answer)
    analizer_answer = bot_answer(sys_prompt=analizer_movies.replace("\n", " ").format(data=data_dict,query=sql_query,user_prompt=resumen))
    print(f'analizer_answer ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {analizer_answer}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
    result = {
        "state": "finished",
        "json_chart": chart_json,
        "analysis": analizer_answer
    }
    guardar_json_en_db(chart_json,chart_type)
    print(f'ESTE ES EL RESULTADOOOOOOO >>>>>>> {result}<<<<<<<<<<<<<<')
    return result 













class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=chatbot_movies,
            tools=[escribir_consulta_usuario]
        )






async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(model="gpt-4o-mini"),

        # tts=openai.TTS(
        #     model="gpt-4o-mini-tts",
        #     voice="echo",
        #     instructions="Hablá claro y despacio en español argentino, tono muy amable y paciente, usando expresiones como 'cómo te puedo ayudar?', 'dale', 'perfecto'."
        # ),
        tts = openai.TTS(
            model="gpt-4o-mini-tts",
            voice="echo",
            instructions="Hablá claro y despacio en español argentino, tono muy amable y paciente, usando expresiones como 'cómo te puedo ayudar?', 'dale', 'perfecto'."
        ),

        # tts=openai.TTS(
        #                 model="gpt-4o-mini-tts",
        #                 voice="nova",
        #                 instructions="Habla en un español rioplatense elegante, neutro, con voseo pero sin lunfardo fuerte, para sonar cordial y profesional."
        #             ),



        # tts=openai.TTS(
        #                 model="gpt-4o-mini-tts",
        #                 voice="ash",
        #                 instructions="Hablá amigable en español rioplatense, con modismos argentinos."
        #             ),  # La voz más expresiva
        vad=VAD.load(),
        turn_detection=MultilingualModel())



    await session.start(
        room=ctx.room,
        agent=Assistant(),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Saluda amablemente al usuario ofreciendo y describiendo el servicio."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
