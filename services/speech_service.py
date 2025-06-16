import speech_recognition as sr
from gtts import gTTS
import io
import logging
import asyncio
from typing import Optional
from pydub import AudioSegment
import tempfile
import os

logger = logging.getLogger(__name__)

class SpeechService:
    """Сервис для работы с распознаванием и синтезом речи"""
    
    def __init__(self):
        # Инициализация распознавателя речи
        self.recognizer = sr.Recognizer()
        
        # Настройки для лучшего распознавания
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5
    
    async def speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Конвертирует аудио в текст"""
        try:
            # Создаем временный файл для аудио
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_file_path = tmp_file.name
            
            try:
                # Загружаем аудио в SpeechRecognition
                with sr.AudioFile(tmp_file_path) as source:
                    # Настройка для шумоподавления
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.record(source)
                
                # Распознаем речь с помощью Google Speech Recognition
                loop = asyncio.get_event_loop()
                text = await loop.run_in_executor(
                    None,
                    lambda: self.recognizer.recognize_google(
                        audio, 
                        language='ru-RU'
                    )
                )
                
                logger.info(f"Распознанный текст: {text}")
                return text
                
            finally:
                # Удаляем временный файл
                if os.path.exists(tmp_file_path):
                    os.unlink(tmp_file_path)
                    
        except sr.UnknownValueError:
            logger.warning("Не удалось распознать речь")
            return None
        except sr.RequestError as e:
            logger.error(f"Ошибка сервиса распознавания речи: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка при распознавании речи: {e}")
            return None
    
    async def text_to_speech(self, text: str, lang: str = 'ru') -> bytes:
        """Конвертирует текст в аудио"""
        try:
            # Создаем TTS объект
            tts = gTTS(text=text, lang=lang, slow=False)
            
            # Сохраняем в буфер
            audio_buffer = io.BytesIO()
            
            # Генерируем аудио в отдельном потоке
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: tts.write_to_fp(audio_buffer)
            )
            
            # Возвращаем в начало буфера
            audio_buffer.seek(0)
            audio_data = audio_buffer.getvalue()
            
            # Конвертируем MP3 в WAV для лучшей совместимости
            audio_segment = AudioSegment.from_mp3(io.BytesIO(audio_data))
            
            # Экспортируем как WAV
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format="wav")
            wav_buffer.seek(0)
            
            logger.info(f"Сгенерировано аудио для текста: {text[:50]}...")
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка при синтезе речи: {e}")
            # Возвращаем пустой аудио файл в случае ошибки
            return self._create_silence_audio()
    
    def _create_silence_audio(self, duration_ms: int = 1000) -> bytes:
        """Создает аудио файл с тишиной"""
        try:
            # Создаем тишину
            silence = AudioSegment.silent(duration=duration_ms)
            
            # Экспортируем как WAV
            buffer = io.BytesIO()
            silence.export(buffer, format="wav")
            buffer.seek(0)
            
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка создания аудио тишины: {e}")
            return b''
    
    async def test_microphone(self) -> bool:
        """Тестирует доступность микрофона"""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                return True
        except Exception as e:
            logger.error(f"Микрофон недоступен: {e}")
            return False
    
    def get_available_microphones(self) -> list:
        """Возвращает список доступных микрофонов"""
        try:
            return sr.Microphone.list_microphone_names()
        except Exception as e:
            logger.error(f"Ошибка получения списка микрофонов: {e}")
            return [] 