from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions,function_tool, RunContext
from livekit.plugins import (
    openai,
    noise_cancellation,
)
from utils import registrar_turno,consultar_turnos,chatbot_sys,registrar_turno_tool_descripcion,consultar_turno_tool_descripcion
from google.oauth2 import service_account

from datetime import datetime
from typing import TypedDict
from googleapiclient.discovery import build
from zoneinfo import ZoneInfo


SCOPES = ["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE = "jsoncred.json"
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("calendar", "v3", credentials=creds)
load_dotenv()
ZONA_ARG = ZoneInfo("America/Argentina/Buenos_Aires")




@function_tool(
    name="registrar_turno",
    description=registrar_turno_tool_descripcion
)
async def registrar_turno_tool(
    context: RunContext,
    sede: str,
    inicio: datetime, 
    fin: datetime,     
    detalles: str,
    ubicacion_exacta: str = "",
) -> dict[str, str]:

    datos_turno = {
        "sede": sede,
        "detalles": detalles,
        "ubicacion_exacta": ubicacion_exacta,
        "inicio": inicio.astimezone(ZONA_ARG).isoformat(),
        "fin": fin.astimezone(ZONA_ARG).isoformat(),
    }

    try:
        registrar_turno(service, datos_turno)
    except:
        return 'no se pudo registrar el turno'
    return 'turno registrado exitosamente'


@function_tool(
    name="consultar_turnos",
    description=consultar_turno_tool_descripcion
)
async def consultar_turnos_tool(
    context: RunContext,
    fecha_inicio: datetime, 
    fecha_fin: datetime      
) -> dict:

    json_consulta = {
        "fecha_inicio": fecha_inicio.astimezone(ZONA_ARG).isoformat(),
        "fecha_fin": fecha_fin.astimezone(ZONA_ARG).isoformat()
    }

    try:
        turnos = consultar_turnos(service, json_consulta)
    except Exception as e:
        return "Error. No pude consultar los turnos."
    
    return f"Los turnos reservados entre {json_consulta['fecha_inicio']} y {json_consulta['fecha_fin']} son los siguientes: >>>>> {str(turnos)} <<<<<. Recuerda que cada turno dura media hora; todas las opciones ausentes están disponibles."



class Turnero_loko(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=chatbot_sys,
                        tools=[registrar_turno_tool,consultar_turnos_tool])
        


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=openai.realtime.RealtimeModel(
            #model="gpt-4o",#gpt-4o gpt-4o-realtime-preview
            #temperature=0.8
            #tool_choice= 'auto', 'required' o 'none', siendo "auto"
            #TurnDetection= "server_vad" o "semantic_vad" # agregar parametros extra? 
            speed=1.2,   # de 0.25 a 4.0
            voice="echo"#'alloy', 'ash', 'ballad', 'coral', 'echo', 'sage', 'shimmer', and 'verse'
        ),
        allow_interruptions=True,
        min_endpointing_delay=0.5,
        max_endpointing_delay=4,
        max_tool_steps=3,
        user_away_timeout=15
    )
    
    await session.start(
        room=ctx.room,
        agent = Turnero_loko(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
            #noise_cancellation=noise_cancellation.BVCTelephony()
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="""
        Recibí al usuario diciendo exactamente lo siguiente:
        '¡Hola! Bienvenido al servicio de instalación de equipos de localización satelital para autos y motos de STRIX. 
        Te puedo ayudar a reservar rápidamente tu turno de instalacion, ya sea en tu domicilio o en alguna de nuestras sedes en Belgrano, Balvanera o Devoto. 
        Decime cuándo y dónde preferís hacer la instalación, y lo coordinamos enseguida. Las instalaciones se realizan de lunes a viernes de 10 a 18hs.'
        """
    )

if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))