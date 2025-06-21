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
from google.oauth2 import service_account
from googleapiclient.discovery import build
from livekit.agents import function_tool, RunContext
from utils import registrar_turno,sys_prompt,consultar_turnos
from openai import OpenAI

# Conexión inicial a Google Calendar (idéntica)
api_key = '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'
client = OpenAI(api_key=api_key)
SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "jsoncred.json"
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=creds)

from datetime import datetime
from typing import TypedDict
from livekit.agents import function_tool, RunContext










@function_tool(
    name="consultar_turnos",
    description="Devuelve todos los turnos ya agendados en un rango de fechas y horas, para saber qué espacios ya están ocupados. Esta tool debe ser llamada en los que casos que haya una consulta y esten aclaradas las fechas. y ademas en los casos que el usuario desea confirmar un turno, es obligatorio validar con este metodo que este disponible antes de confirmarlo."
)
async def consultar_turnos_tool(
    context: RunContext,
    fecha_inicio: datetime,  # Requiere formato ISO: "2025-06-11T10:00:00"
    fecha_fin: datetime      # Requiere formato ISO: "2025-06-11T18:00:00"
) -> dict:
    json_consulta = {
        "fecha_inicio": fecha_inicio.isoformat(),
        "fecha_fin": fecha_fin.isoformat()
    }
    print(f"[TOOL] Consultando turnos json >>>>>>>>> {json_consulta}")
    turnos = consultar_turnos(service, json_consulta)
    print(f"[TOOL] Turnos encontrados: {len(turnos)}")
    return {"turnos": turnos}


@function_tool(
    name="registrar_turno",
    description="Registra un nuevo turno en Google Calendar si la fecha y hora elegidas están disponibles. Esta tool solo debe ser llamada si el usuario ha entregado todos los datos necesarios para el registro. "
)
async def registrar_turno_tool(
    context: RunContext,
    nombre_paciente: str,
    inicio: datetime,  # Formato ISO requerido
    fin: datetime,     # Formato ISO requerido
    titulo: str = "Turno Reparación Auto",
    ubicacion: str = "",
) -> dict[str, str]:
    datos_turno = {
        "titulo": titulo,
        "ubicacion": ubicacion,
        "nombre_paciente": nombre_paciente,
        "inicio": inicio.isoformat(),
        "fin": fin.isoformat(),
    }
    print(f"[TOOL] Registrando turno: {datos_turno}")
    url = registrar_turno(service, datos_turno)
    return {"url_evento": url}


# @function_tool(
#     name="consultar_turnos",
#     description="Consulta los turnos agendados en Google Calendar en un rango de fechas especificado."
# )
# async def consultar_turnos_tool(
#     context: RunContext,
#     fecha_inicio: str,
#     fecha_fin: str,
# ) -> dict:
#     json_consulta = {
#         "fecha_inicio": fecha_inicio,
#         "fecha_fin": fecha_fin
#     }
#     print(f"[TOOL] Consultando turnos desde {fecha_inicio} hasta {fecha_fin}")
#     turnos = consultar_turnos(service, json_consulta)
#     print(f"[TOOL] Turnos encontrados: {len(turnos)}")
#     return {"turnos": turnos}










# @function_tool(
#     name="registrar_turno",
#     description="Registra un turno en Google Calendar."
# )
# async def registrar_turno_tool(
#     context: RunContext,
#     nombre_paciente: str,
#     inicio: str,
#     fin: str,
#     titulo: str = "Turno Reparación Auto",
#     ubicacion: str = "",
# ) -> dict[str, str]:
#     datos_turno = {
#         "titulo": titulo,
#         "ubicacion": ubicacion,
#         "nombre_paciente": nombre_paciente,
#         "inicio": inicio,
#         "fin": fin,
#     }
#     url = registrar_turno(service, datos_turno)
#     return {"url_evento": url}


# class Assistant(Agent):
#     def __init__(self) -> None:
#         super().__init__(instructions=sys_prompt)








class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=sys_prompt,
            tools=[registrar_turno_tool, consultar_turnos_tool]
        )






async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=openai.STT(model="whisper-1"),
        llm=openai.LLM(model="gpt-4o-mini"),

        tts=openai.TTS(
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
        instructions="Saludá al usuario amablemente para intentar registrar su turno."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
