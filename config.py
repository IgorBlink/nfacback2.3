import os
from typing import Optional

class Config:
    """Конфигурация приложения"""
    
    # Gemini API
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    
    # Сервер
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # Аудио
    SAMPLE_RATE: int = int(os.getenv("SAMPLE_RATE", "16000"))
    FRAME_DURATION: int = int(os.getenv("FRAME_DURATION", "30"))
    MAX_SILENCE_FRAMES: int = int(os.getenv("MAX_SILENCE_FRAMES", "30"))
    
    # Логирование
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Пути
    STATIC_DIR: str = "static"
    TEMPLATES_DIR: str = "templates"
    
    # Валидация конфигурации
    @classmethod
    def validate(cls):
        """Проверяет конфигурацию на корректность"""
        errors = []
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY не установлен")
        
        if cls.PORT < 1 or cls.PORT > 65535:
            errors.append("PORT должен быть от 1 до 65535")
            
        if cls.SAMPLE_RATE not in [8000, 16000, 44100, 48000]:
            errors.append("SAMPLE_RATE должен быть 8000, 16000, 44100 или 48000")
        
        if errors:
            raise ValueError("Ошибки конфигурации:\n" + "\n".join(errors))
        
        return True

# Инстанс конфигурации
config = Config() 