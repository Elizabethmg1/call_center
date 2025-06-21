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
from utils import registrar_turno,chart_sys,sys_second_chart,analizer_sys,extract_outer_json,validate_chart_json,sys_prompt,translated_prompt,verifier_sys,second_try_sys,bot_answer,get_schema_metadata,consultar_turnos,chatbot_sys_glpi,chatbot_ttd,database_description,charts_rules
from openai import OpenAI
from datetime import datetime,timezone
from typing import TypedDict
from livekit.agents import function_tool, RunContext
from app_db import AppDb
# Conexión inicial a Google Calendar (idéntica)
api_key = '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'
client = OpenAI(api_key=api_key)

os.environ["DB_PORT"] = "5432"
os.environ["DB_HOST"] = "88.99.166.175"
os.environ["DB_USER"] = "postgres"
os.environ["DB_PASS"] = "example1"
os.environ["DB_NAME"] = "postgres"

db = AppDb()

@function_tool(
    name="escribir_consulta_usuario",
    description="Esta tool solo debe ser llamada en caso que el agente considere que los datos son suficientes para renderizar el gráfico según todos los parámetros establecidos."
)
async def escribir_consulta_usuario(resumen: str) -> str:
        chatbot_summary = resumen
        schema = get_schema_metadata()
        query_answer = bot_answer(sys_prompt=translated_prompt.replace("\n", " ").format(schema=schema,user_query=chatbot_summary,rules=charts_rules,database_description=database_description), )
        # PRINT_JODA = bot_answer(temperature=0.8,sys_prompt=sql_writer_sys_short_version.replace("\n", " "), user_prompt=prompt)
        # print(f'PRINT_JODA >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {PRINT_JODA}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

        print(f'QUERY ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {query_answer}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        preset=''
        # print(f'schema ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {schema}')
        verifier_answer = bot_answer(sys_prompt=verifier_sys.replace("\n", " ").format(schema = schema, sql_writer_response = query_answer))
        print(f'verifier_answer ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {verifier_answer}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')


        if "QUERY OK" in verifier_answer:
            sql_query = verifier_answer.split("//")[1].strip()
            try:
                data = db.exec_query(sql_query)
            except Exception as e:
                recovery_prompt = f"The following SQL query failed when executed:\n\n{sql_query}\n\nDatabase error:\n{str(e)}\n\nPlease rewrite a corrected version of the query based on this error."
                new_query_answer = bot_answer(sys_prompt=second_try_sys.replace("\n", " ").format(schema=schema,recovery_prompt=recovery_prompt,user_query=prompt), model="o3-mini")
                sql_query = new_query_answer.split("//")[1].strip()
                try :
                    data = db.exec_query(sql_query)
                except Exception as e:
                    preset = 'it wasnt posible to get a valid SQL query.'
                    
        else:
            recovery_prompt = f"The SQL query failed when executed:\n\n{query_answer}. The SQL Verifier agent dont allow the query to run, and gave this message: ```{verifier_answer}``` "
            second_query_call = bot_answer(sys_prompt=second_try_sys.replace("\n", " ").format(schema=schema,recovery_prompt=recovery_prompt,user_query=prompt), model="o3-mini")
            sql_query_2= second_query_call.split("//")[1].strip()
            try :
                data = db.exec_query(sql_query_2)
            except Exception as e:
                preset = F'it wasnt posible to get a valid SQL query SECOND QUERY >>>>>{sql_query_2}.'


        data_dict = json.loads(data)
        print(f'GFDSGFDSGFDS GFDS G data_dict >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {data_dict}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')

        chart_answer = bot_answer(sys_prompt=chart_sys.replace("\n", " ").format(user_prompt = chatbot_summary,database_description=database_description, sql_writer_response = query_answer,rules=charts_rules, database_response=json.dumps(data_dict)))
        print(f'chart_answer ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {chart_answer}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        errors_v2=[]
        errors=[]
        chart_json = extract_outer_json(chart_answer)
        errors = validate_chart_json(chart_json)

        if len(errors) != 0:
            chart_json_2 = bot_answer(sys_prompt=sys_second_chart.replace("\n", " ").format(errors=str(errors),original_json=chart_json))
            chart_json = extract_outer_json(chart_json_2)
            errors_v2 = validate_chart_json(chart_json)
            if len(errors_v2) != 0:
                pre_return=f' A valid JSON could not be generated in 2 attempts. ERRORS --->>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<{str(errors_v2)}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'


        analizer_answer = bot_answer(sys_prompt=analizer_sys.replace("\n", " ").format(user_prompt=chatbot_summary,query=verifier_answer,data=data,chart=chart_json))
        print(f'analizer_answer ANSWER >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> {analizer_answer}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<')
        
        result = {
            "state": "finished",
            "json_chart": chart_json,
            "analysis": analizer_answer
        }
        print(f'ESTE ES EL RESULTADOOOOOOO >>>>>>> {result}<<<<<<<<<<<<<<')
        return result 













class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=chatbot_ttd,
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
            voice="shimmer",  # o "noca" si querés un timbre un poco más joven
            instructions="Speak fluent, natural American English. Use a warm, friendly tone with clear articulation and confident pacing. Sound helpful and engaging, as if guiding someone through a conversation step-by-step."
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
        instructions="Greet the user warmly and give a brief explanation of what this is about."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
