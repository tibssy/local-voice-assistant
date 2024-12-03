import io
import numpy as np
import sounddevice as sd
import soundfile as sf
from faster_whisper import WhisperModel
from ollama import chat
from piper.voice import PiperVoice
from stream2sentence import generate_sentences


# Constants
FREQ = 16000  # Sampling rate
BLOCK_SIZE = 160  # Block size
SILENCE_THRESHOLD = 0.01  # Silence threshold
SILENCE_THRESHOLD_BLOCKS = int(0.5 * FREQ / BLOCK_SIZE)
WHISPER_MODEL = 'small.en'
OLLAMA_MODEL = 'assistant'
PIPER_MODEL_PATH = 'tts_models/en_US-hfc_female-medium.onnx'
AUDIO_FORMAT = 'ogg'


class AudioRecorder:
    def __init__(self, sample_rate: int, on_audio_callback):
        self.sample_rate = sample_rate
        self.audio_data = np.array([], dtype=np.float32)
        self.on_audio_callback = on_audio_callback
        self.silence_timer = 0

    def record_stream(self, data: np.ndarray):
        """Append incoming audio data to the audio buffer."""
        self.audio_data = np.append(self.audio_data, data.flatten())

    def audio_callback(self, indata: np.ndarray, frames: int, time, status):
        """Callback function to process audio input."""
        rms = np.sqrt(np.mean(indata ** 2))
        if rms < SILENCE_THRESHOLD:
            self._handle_possible_silence(indata)
        else:
            self._reset_silence_timer()
            self.record_stream(indata)

    def _handle_possible_silence(self, indata: np.ndarray):
        """Handle potential silence in the audio stream."""
        self.silence_timer += 1
        if self.silence_timer >= SILENCE_THRESHOLD_BLOCKS:
            self._handle_silence()
        else:
            self.record_stream(indata)

    def _handle_silence(self):
        """Handle the end of audio recording when silence is detected."""
        if callable(self.on_audio_callback) and self.audio_data.size:
            self.on_audio_callback(self.audio_data)
            self._reset_audio_data()
        sd.stop()

    def _reset_silence_timer(self):
        """Reset the silence timer."""
        self.silence_timer = 0

    def _reset_audio_data(self):
        """Reset the audio data buffer."""
        self.audio_data = np.array([], dtype=np.float32)

    def save_audio_as(self, audio: np.ndarray, audio_format: str = AUDIO_FORMAT) -> io.BytesIO:
        """Save the audio data to a file-like object."""
        audio_array = (audio * 32767 / np.max(np.abs(audio))).astype(np.int16)
        audio_buffer = io.BytesIO()
        audio_buffer.name = f'audio.{audio_format}'
        sf.write(audio_buffer, audio_array, self.sample_rate)
        audio_buffer.seek(0)
        return audio_buffer


class VoiceAssistant:
    def __init__(self):
        self.stt_model = WhisperModel(WHISPER_MODEL, device="cpu", compute_type="int8")
        self.chat_history = []
        self.recorder = AudioRecorder(sample_rate=FREQ, on_audio_callback=self.process_ai)
        self.stream = sd.InputStream(samplerate=FREQ, blocksize=BLOCK_SIZE, channels=1, callback=self.recorder.audio_callback)
        self.voice = PiperVoice.load(PIPER_MODEL_PATH)
        self.running = True

    def run(self):
        """Start the audio input stream."""
        with self.stream:
            print("Listening for audio input...")
            while self.running:
                sd.sleep(1000)

    def process_ai(self, audio: np.ndarray):
        """Process audio input and interact with AI."""
        if text := self.speech_to_text(audio).strip():
            print(f'\nUser: {text}\nAssistant: ', end='')
            text_stream = self.chat_with_ollama(text)
            self.synthesize_and_play(text_stream)
            self._check_for_exit_command(text)

    def _check_for_exit_command(self, text: str):
        """Check if the user wants to exit the conversation."""
        if 'bye' in text.lower():
            self.running = False
            sd.stop()

    def chat_with_ollama(self, text: str):
        """Engage in a chat with the Ollama model."""
        self.chat_history.append({'role': 'user', 'content': text})
        self.chat_history.append({'role': 'assistant', 'content': ''})

        for chunk in chat(model=OLLAMA_MODEL, messages=self.chat_history, stream=True):
            if (text_chunk := chunk.message.content) is not None:
                print(text_chunk, end='', flush=True)
                self.chat_history[-1]['content'] += text_chunk
                yield text_chunk

    def speech_to_text(self, audio: np.ndarray):
        """Convert audio to text using Whisper model."""
        if audio.size > 0:
            segments, _ = self.stt_model.transcribe(audio, beam_size=1)
            return ' '.join(segment.text for segment in segments)

    def synthesize_and_play(self, text_stream):
        """Synthesize and play text, but stop if user interrupts."""
        sentences = generate_sentences(text_stream)
        with sd.OutputStream(samplerate=self.voice.config.sample_rate, channels=1, dtype='int16') as stream:
            for sentence in sentences:
                for audio_bytes in self.voice.synthesize_stream_raw(sentence):
                    # Check if user input is detected
                    if self.is_user_interrupting():
                        print("User interruption detected. Stopping playback.")
                        return  # Stop speaking and return control
                    int_data = np.frombuffer(audio_bytes, dtype=np.int16)
                    stream.write(int_data)

    def is_user_interrupting(self) -> bool:
        """Check if the user is interrupting the assistant."""
        with sd.InputStream(samplerate=FREQ, blocksize=BLOCK_SIZE, channels=1) as mic_stream:
            data, _ = mic_stream.read(BLOCK_SIZE)
            rms = np.sqrt(np.mean(data ** 2))
            if rms > SILENCE_THRESHOLD:  # User starts speaking
                print("Voice detected, interrupting.")
                return True
        return False




if __name__ == "__main__":
    VoiceAssistant().run()
