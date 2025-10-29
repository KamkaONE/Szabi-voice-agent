import os
import asyncio
import aiohttp
import inspect
from typing import AsyncIterable
from dotenv import load_dotenv

# Default LIVEKIT_URL if not provided
os.environ["LIVEKIT_URL"] = os.environ.get("LIVEKIT_URL", "ws://127.0.0.1:7880")

print("FORCED LIVEKIT_URL =", os.environ["LIVEKIT_URL"])
print("LIVEKIT_API_KEY set?", bool(os.environ.get("LIVEKIT_API_KEY")))
print("LIVEKIT_API_SECRET set?", bool(os.environ.get("LIVEKIT_API_SECRET")))
print("AGENT_MODE value:", os.environ.get('AGENT_MODE'))

from livekit import agents, rtc, api
from livekit.agents import (
    Agent, AgentSession, ChatContext,
    JobContext, AutoSubscribe,
    RoomInputOptions, ModelSettings,
    ConversationItemAddedEvent,
)
from livekit.plugins import deepgram, silero, groq
from livekit.plugins.turn_detector.english import EnglishModel
from deepinfra_tts import DeepInfraTTS

from memory_sql import SQLiteMemory

load_dotenv()

def _http_kwarg_for(klass, http):
    # Some plugin constructors use http_session, others use session, some neither
    try:
        params = inspect.signature(klass.__init__).parameters
        if "http_session" in params:
            return {"http_session": http}
        if "session" in params:
            return {"session": http}
    except Exception:
        pass
    return {}

def truncate(s: str, marker="<truncated>"):
    if len(s) <= 100:
        return s
    return f"{s[:50]}{marker}{s[-50:]}"

DEEPINFRA_API_KEY = os.environ.get("DEEPINFRA_API_KEY")

BASE_INSTRUCTIONS = """
You are a warm, witty voice companion. Speak in short, natural sentences.
Avoid lists, headings, emojis, or formal tone. Keep it conversational and brief.
"""

class Operator(Agent):
    async def tts_node(
        self,
        text: AsyncIterable[str],
        model_settings: ModelSettings,
    ) -> AsyncIterable[rtc.AudioFrame]:
        async for frame in Agent.default.tts_node(self, text, model_settings):
            yield frame

# ---------------- DIRECT MODE ----------------
async def run_direct():
    url = os.environ["LIVEKIT_URL"]
    api_key = os.environ["LIVEKIT_API_KEY"]
    api_secret = os.environ["LIVEKIT_API_SECRET"]

    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity("server_agent")
        .with_grants(api.VideoGrants(room_join=True, room="default"))
        .to_jwt()
    )

    room = rtc.Room()
    await room.connect(url, token)

    db = SQLiteMemory(db_path="/opt/Livekit/conversations.db")

    # Shared HTTP session for HTTP-based plugins in DIRECT mode
    http = aiohttp.ClientSession()

    try:
        # Build chat context from memory
        old = db.get_context_messages(50)
        chat_ctx = ChatContext()
        for m in old:
            role = m["role"]; content = m["content"]
            chat_ctx.add_message(role=role, content=truncate(content) if role != "user" else content)
        chat_ctx.add_message(role="assistant", content="New session begins here. Greet the user after they speak.")

        operator = Operator(chat_ctx=chat_ctx, instructions=BASE_INSTRUCTIONS)

        # Build kwargs that match each class' expected param name (or none)
        dg_kwargs  = _http_kwarg_for(deepgram.STT, http)
        llm_kwargs = _http_kwarg_for(groq.LLM, http)

        stt = deepgram.STT(
            model=os.getenv("DEEPGRAM_MODEL", "nova-3"),
            api_key=os.environ.get("DEEPGRAM_API_KEY"),
            **dg_kwargs,
        )

        tts = DeepInfraTTS(
            api_key=DEEPINFRA_API_KEY,
            voice=os.getenv("TTS_VOICE", "af_sky"),
        )

        llm = groq.LLM(
         model=os.getenv("LLM_MODEL", "openai/gpt-oss-120b"),
         temperature=float(os.getenv("LLM_TEMPERATURE", "1.0")),
         **llm_kwargs,  # will be {} if LLM doesn't support http/session
        )

        session = AgentSession(
            llm=llm,
            stt=stt,
            tts=tts,
            # turn_detection=EnglishModel(),  # Disabled: requires WORKER mode
            vad=silero.VAD.load(),
        )

        print("[DIRECT MODE] Starting agent session...")
        await session.start(
            room=room,
            agent=operator,
            room_input_options=RoomInputOptions(video_enabled=False, close_on_disconnect=False),  # Changed to False
        )
        print("[DIRECT MODE] Agent session started successfully, entering main loop...")

        # Keep process alive - catch any exceptions to prevent crashes
        try:
            await asyncio.Event().wait()
        except Exception as e:
            print(f"[DIRECT MODE] Main loop exception: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"[DIRECT MODE] Setup exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await http.close()
        print("[DIRECT MODE] Session ended, HTTP closed")

# ---------------- WORKER MODE ----------------
async def entrypoint(ctx: JobContext):
    # env-driven config
    url       = os.environ["LIVEKIT_URL"]
    api_key   = os.environ["LIVEKIT_API_KEY"]
    api_secret= os.environ["LIVEKIT_API_SECRET"]
    room_name = os.getenv("ROOM_NAME", "default")

    DG_MODEL  = os.getenv("DEEPGRAM_MODEL", "nova-3")
    TTS_MODEL = os.getenv("TTS_MODEL", "hexgrad/Kokoro-82M")
    TTS_BASE  = os.getenv("TTS_BASE_URL", "https://api.deepinfra.com/v1/openai")
    TTS_VOICE = os.getenv("TTS_VOICE", "af_heart")
    TTS_SPEED = float(os.getenv("TTS_SPEED", "1.0"))
    LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")
    LLM_TEMP  = float(os.getenv("LLM_TEMPERATURE", "1.0"))

    # mint a room-scoped token for this worker session
    token = (
        api.AccessToken(api_key, api_secret)
        .with_identity("server_agent")
        .with_grants(api.VideoGrants(room_join=True, room=room_name))
        .to_jwt()
    )

    # connect to LiveKit
    room = rtc.Room()
    await room.connect(url, token)
    ctx.room = room

    # build chat context from memory
    db = SQLiteMemory(db_path="/opt/Livekit/conversations.db")
    old = db.get_context_messages(50)
    chat_ctx = ChatContext()
    for m in old:
        role, content = m["role"], m["content"]
        chat_ctx.add_message(role=role, content=truncate(content) if role != "user" else content)
    chat_ctx.add_message(role="assistant", content="New session begins here. Greet the user after they speak.")

    operator = Operator(chat_ctx=chat_ctx, instructions=BASE_INSTRUCTIONS)

    # worker mode: plugins don't need explicit http_session
    session = AgentSession(
        llm=groq.LLM(model=LLM_MODEL, temperature=LLM_TEMP),
        stt=deepgram.STT(model=DG_MODEL, api_key=os.environ.get("DEEPGRAM_API_KEY")),
        tts=DeepInfraTTS(
            api_key=DEEPINFRA_API_KEY,
            voice=TTS_VOICE,
        ),
        turn_detection=EnglishModel(),
        vad=silero.VAD.load(),
    )

    # persist turns to SQLite
    turn_buf = []
    @session.on("conversation_item_added")
    def on_item(ev: ConversationItemAddedEvent):
        role = ev.item.role
        if role == "user":
            turn_buf.append(ev.item.text_content)
        elif role == "assistant":
            user_text = " ".join(turn_buf).strip()
            if user_text:
                db.add_message("user", user_text)
            turn_buf.clear()
            db.add_message("assistant", ev.item.text_content)

    await session.start(
        room=ctx.room,
        agent=operator,
        room_input_options=RoomInputOptions(video_enabled=False, close_on_disconnect=True),
    )

    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

# ---------------- MAIN ----------------
async def main():
    print("LIVEKIT_URL =", os.environ.get("LIVEKIT_URL"))
    print("LIVEKIT_API_KEY set?", bool(os.environ.get("LIVEKIT_API_KEY")))
    print("LIVEKIT_API_SECRET set?", bool(os.environ.get("LIVEKIT_API_SECRET")))

    if os.environ.get("AGENT_MODE", "worker") == "direct":
        print("Starting in DIRECT mode (no job system).")
        await run_direct()
        return

    print("Starting in WORKER mode (waiting for jobs).")
    from livekit.agents import Worker, WorkerOptions
    opts = WorkerOptions(entrypoint_fnc=entrypoint, initialize_process_timeout=30)
    worker = Worker(opts)
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
