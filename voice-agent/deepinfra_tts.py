import aiohttp
from typing import Optional, Any
from livekit.agents import tts
import uuid
import logging

print("=" * 80)
print("DEEPINFRA_TTS.PY MODULE LOADED - NEW VERSION WITH FLUSH FIX")
print("=" * 80)

logger = logging.getLogger(__name__)

class DeepInfraTTS(tts.TTS):
    def __init__(
        self,
        api_key: str,
        voice: str = "af_sky",
        model: str = "hexgrad/Kokoro-82M",
        sample_rate: int = 24000,
    ):
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),  # Correctly set to False
            sample_rate=sample_rate,
            num_channels=1,
        )
        self._api_key = api_key
        self._voice = voice
        self._model = model
        self._api_url = "https://api.deepinfra.com/v1/openai/audio/speech"
        print(f"[DeepInfraTTS] Initialized with voice={voice}, model={model}, sample_rate={sample_rate}")
        logger.info(f"[DeepInfraTTS] Initialized with voice={voice}, model={model}, sample_rate={sample_rate}")

    def synthesize(
        self,
        text: str,
        *,
        conn_options: Optional[Any] = None,
    ) -> "DeepInfraStream":
        print(f"[DeepInfraTTS] synthesize() called with text: {text[:100]}...")
        logger.info(f"[DeepInfraTTS] synthesize() called with text: {text[:100]}...")
        return DeepInfraStream(
            input_text=text,  # Changed from text= to input_text=
            tts=self,
            conn_options=conn_options,
        )


class DeepInfraStream(tts.ChunkedStream):  # Changed from SynthesizeStream to ChunkedStream
    def __init__(self, *, input_text: str, tts: DeepInfraTTS, conn_options: Optional[Any] = None):
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts = tts

    async def _run(self, output_emitter: tts.AudioEmitter):
        request_id = str(uuid.uuid4())

        print(f"[DeepInfraTTS] _run() called! Starting TTS synthesis for text: {self._input_text[:100]}...")
        logger.info(f"[DeepInfraTTS] Starting TTS synthesis for text: {self._input_text[:100]}...")

        # 1. Initialize the emitter before making the API call
        print(f"[DeepInfraTTS] About to initialize emitter with MP3 format...")
        output_emitter.initialize(
            request_id=request_id,
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/mpeg",  # MP3 format - let LiveKit decode it
        )
        print(f"[DeepInfraTTS] Emitter initialized successfully!")
        logger.info(f"[DeepInfraTTS] Output emitter initialized with MP3 format")
        
        headers = {
            "Authorization": f"Bearer {self._tts._api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self._tts._model,
            "input": self._input_text,
            "voice": self._tts._voice,
            "response_format": "mp3",  # Try MP3 instead of WAV
        }

        try:
            print(f"[DeepInfraTTS] About to make API request to DeepInfra...")
            logger.info(f"Requesting TTS from DeepInfra for text: {self._input_text[:50]}...")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._tts._api_url,
                    json=payload,
                    headers=headers,
                ) as response:
                    print(f"[DeepInfraTTS] Got response with status: {response.status}")
                    if not response.ok:
                        error_text = await response.text()
                        print(f"[DeepInfraTTS] ERROR: {response.status} - {error_text}")
                        logger.error(f"DeepInfra API Error: {response.status} - {error_text}")
                        response.raise_for_status()

                    print(f"[DeepInfraTTS] Reading response bytes...")
                    audio_bytes = await response.read()
                    print(f"[DeepInfraTTS] Received {len(audio_bytes)} bytes of MP3 data from DeepInfra")
                    logger.info(f"Received {len(audio_bytes)} bytes from DeepInfra")

                    if len(audio_bytes) == 0:
                        print(f"[DeepInfraTTS] ERROR: No audio data received!")
                        logger.error("Received empty audio data")
                        return

                    # Push entire MP3 data - LiveKit will decode it
                    print(f"[DeepInfraTTS] About to push {len(audio_bytes)} bytes of MP3 data...")
                    output_emitter.push(audio_bytes)
                    print(f"[DeepInfraTTS] Successfully pushed {len(audio_bytes)} bytes of MP3 data")

                    # Flush the emitter to signal completion
                    print(f"[DeepInfraTTS] About to flush emitter...")
                    output_emitter.flush()
                    print(f"[DeepInfraTTS] Emitter flushed successfully!")
                    logger.info(f"Audio synthesis complete: {len(audio_bytes)} bytes pushed")

        except Exception as e:
            print(f"[DeepInfraTTS] EXCEPTION CAUGHT: {type(e).__name__}: {e}")
            logger.error(f"DeepInfra TTS Synthesis Error: {e}", exc_info=True)
            raise