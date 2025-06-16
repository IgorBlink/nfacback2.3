import webrtcvad
import numpy as np
from pydub import AudioSegment
from pydub.utils import make_chunks
import io
import logging
from typing import Optional, List

logger = logging.getLogger(__name__)

class AudioService:
    """Сервис для обработки аудио и детекции речи"""
    
    def __init__(self, sample_rate: int = 16000, frame_duration: int = 30):
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration  # мс
        self.frame_size = int(sample_rate * frame_duration / 1000)
        
        # Инициализация VAD
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(3)  # Самый агрессивный режим
        
        # Буфер для аудио
        self.audio_buffer = []
        self.speech_frames = []
        self.silence_frames = 0
        self.max_silence_frames = 30  # 30 фреймов тишины = ~900мс
        
    def add_audio_chunk(self, audio_data: bytes):
        """Добавляет аудио чанк в буфер"""
        try:
            # Конвертируем в AudioSegment
            audio = AudioSegment.from_raw(
                io.BytesIO(audio_data),
                sample_width=2,
                frame_rate=self.sample_rate,
                channels=1
            )
            
            # Добавляем в буфер
            self.audio_buffer.append(audio)
            
            # Проверяем на активность голоса
            self._check_voice_activity(audio)
            
        except Exception as e:
            logger.error(f"Ошибка добавления аудио чанка: {e}")
    
    def _check_voice_activity(self, audio: AudioSegment):
        """Проверяет активность голоса в аудио"""
        try:
            # Разбиваем на фреймы
            frames = make_chunks(audio, self.frame_duration)
            
            for frame in frames:
                if len(frame) < self.frame_duration:
                    continue
                
                # Конвертируем в PCM
                pcm_data = frame.raw_data
                
                # Проверяем с помощью VAD
                if len(pcm_data) == self.frame_size * 2:  # 2 байта на семпл
                    is_speech = self.vad.is_speech(pcm_data, self.sample_rate)
                    
                    if is_speech:
                        self.speech_frames.append(frame)
                        self.silence_frames = 0
                    else:
                        self.silence_frames += 1
                        
        except Exception as e:
            logger.error(f"Ошибка проверки активности голоса: {e}")
    
    def is_speech_detected(self) -> bool:
        """Проверяет, обнаружена ли речь"""
        return len(self.speech_frames) > 0
    
    def is_silence_detected(self) -> bool:
        """Проверяет, обнаружена ли тишина (пользователь закончил говорить)"""
        return self.silence_frames >= self.max_silence_frames
    
    def get_audio_buffer(self) -> Optional[bytes]:
        """Возвращает накопленное аудио как bytes"""
        if not self.audio_buffer:
            return None
            
        try:
            # Объединяем все чанки
            combined_audio = sum(self.audio_buffer)
            
            # Конвертируем в WAV
            output = io.BytesIO()
            combined_audio.export(output, format="wav")
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Ошибка получения аудио буфера: {e}")
            return None
    
    def clear_buffer(self):
        """Очищает аудио буфер"""
        self.audio_buffer.clear()
        self.speech_frames.clear()
        self.silence_frames = 0
    
    def get_duration(self) -> float:
        """Возвращает продолжительность накопленного аудио в секундах"""
        if not self.audio_buffer:
            return 0.0
        
        total_duration = sum(len(chunk) for chunk in self.audio_buffer)
        return total_duration / 1000.0  # Конвертируем в секунды 