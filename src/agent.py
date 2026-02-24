import asyncio
import time
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.multilingual import MultilingualModel

load_dotenv(".env.local")



# Assistant Definition

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=(
                "You are a helpful voice AI assistant. "
                "Keep responses concise and natural. "
                "Avoid complex formatting or technical jorgans."
            ),
        )



# Agent Server

server = AgentServer()


@server.rtc_session(agent_name="RigRav-Agent")
async def my_agent(ctx: agents.JobContext):

    session = AgentSession(
        stt="deepgram/nova-3:multi",
        llm="openai/gpt-4.1-mini",
        tts="cartesia/sonic-3:9626c31c-bec5-4cca-baa8-f8ba9e84c8bc",
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )


    # State Management

    user_speaking = False
    agent_speaking = False
    reminder_active = False
    last_speech_time = time.time()
    silence_lock = asyncio.Lock()


    # Speech Event Handlers


    def handle_user_speech_started():
        asyncio.create_task(_on_user_speech_started())

    async def _on_user_speech_started():
        nonlocal user_speaking, agent_speaking, last_speech_time

        user_speaking = True
        last_speech_time = time.time()

        if agent_speaking:
            try:
                await session.cancel_current_reply()
            except Exception:
                pass
            agent_speaking = False

    def handle_user_speech_ended():
        asyncio.create_task(_on_user_speech_ended())

    async def _on_user_speech_ended():
        nonlocal user_speaking, last_speech_time
        user_speaking = False
        last_speech_time = time.time()

    def handle_agent_speech_started():
        nonlocal agent_speaking
        agent_speaking = True

    def handle_agent_speech_ended():
        nonlocal agent_speaking
        agent_speaking = False

    # Register synchronous handlers
    session.on("user_speech_started", handle_user_speech_started)
    session.on("user_speech_ended", handle_user_speech_ended)
    session.on("agent_speech_started", handle_agent_speech_started)
    session.on("agent_speech_ended", handle_agent_speech_ended)


    # Silence Monitor

    async def silence_monitor():
        nonlocal last_speech_time, user_speaking, agent_speaking

        while True:
            await asyncio.sleep(5)

            async with silence_lock:
                if (
                    not user_speaking
                    and not agent_speaking
                    and not reminder_active
                    and time.time() - last_speech_time > 20
                ):
                    last_speech_time = time.time()

                    await session.generate_reply(
                        instructions=(
                            "The user has been silent for a while. "
                            "Politely remind them you are here and ask if they need anything."
                        )
                    )


    # Start Session

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params:
                noise_cancellation.BVCTelephony()
                if params.participant.kind
                == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                else noise_cancellation.BVC(),
            ),
        ),
    )

    # Start silence monitoring task
    asyncio.create_task(silence_monitor())

    # Initial greeting
    await session.generate_reply(
        instructions="Greet the user briefly and offer assistance."
    )


if __name__ == "__main__":
    agents.cli.run_app(server)