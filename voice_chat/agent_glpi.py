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
from utils import registrar_turno,sys_prompt,consultar_turnos,chatbot_sys_glpi
from openai import OpenAI
from datetime import datetime,timezone
from typing import TypedDict
from livekit.agents import function_tool, RunContext

# Conexión inicial a Google Calendar (idéntica)
api_key = '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'
client = OpenAI(api_key=api_key)





@function_tool(
    name="escribir_json",
    description="Esta tool solo debe ser llamada en caso que el usuario explicitamente indique quiere dejar el reclamo asentado."
)
async def escribir_json(
    context: RunContext,
    titulo: str,
    nombre_usuario: str,
    fecha_creacion: datetime,        # ISO 8601 UTC
    grado_urgencia: str,            # "alta", "media" o "baja"
    area_usuario: str,
    perfil_usuario: str,
    resumen_conversacion: str,
    posibles_causas: str,
    comentarios_adicionales: str,
    requiere_contacto_telefonico: bool
) -> dict:
    """
    Crea el JSON del ticket de reclamo con los 10 campos obligatorios.
    """

    json_reclamo = {
        "titulo": titulo,
        "nombre_usuario": nombre_usuario,
        "fecha_creacion": fecha_creacion.astimezone(timezone.utc).isoformat(),
        "grado_urgencia": grado_urgencia,
        "area_usuario": area_usuario,
        "perfil_usuario": perfil_usuario,
        "resumen_conversacion": resumen_conversacion,
        "posibles_causas": posibles_causas,
        "comentarios_adicionales": comentarios_adicionales,
        "requiere_contacto_telefonico": requiere_contacto_telefonico
    }

    print(f"[TOOL] JSON del reclamo generado >>>>> {json_reclamo}")
    return json_reclamo



class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=chatbot_sys_glpi,
            tools=[escribir_json]
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
