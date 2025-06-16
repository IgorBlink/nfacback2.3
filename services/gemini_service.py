import google.generativeai as genai
import os
import logging
from typing import Optional, List
import asyncio

logger = logging.getLogger(__name__)

class GeminiService:
    """Сервис для работы с Gemini API"""
    
    def __init__(self):
        # Инициализация Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY не найден в переменных окружения")
            # Можно установить дефолтный ключ или попросить пользователя
            
        genai.configure(api_key=api_key)
        
        # Настройка модели
        self.model = genai.GenerativeModel('gemini-pro')
        
        # История разговора
        self.conversation_history: List[dict] = []
        
        # Системный промпт
        self.system_prompt = """
        Ты дружелюбный голосовой ИИ-ассистент. Отвечай естественно, как в живом разговоре.
        Твои ответы должны быть:
        - Краткими и по делу (1-3 предложения)
        - Дружелюбными и вежливыми
        - Подходящими для голосового общения
        - На русском языке
        
        Если пользователь задает вопрос, отвечай четко и по существу.
        Если просто общается - поддерживай беседу.
        """
    
    async def get_response(self, user_input: str) -> str:
        """Получает ответ от Gemini на пользовательский ввод"""
        try:
            # Добавляем пользовательский ввод в историю
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Формируем промпт с контекстом
            prompt = self._build_prompt(user_input)
            
            # Получаем ответ от Gemini
            response = await self._generate_response(prompt)
            
            # Добавляем ответ в историю
            self.conversation_history.append({
                "role": "assistant", 
                "content": response
            })
            
            # Ограничиваем историю последними 10 сообщениями
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return response
            
        except Exception as e:
            logger.error(f"Ошибка получения ответа от Gemini: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса."
    
    def _build_prompt(self, user_input: str) -> str:
        """Формирует промпт с учетом истории разговора"""
        prompt_parts = [self.system_prompt]
        
        # Добавляем последние несколько сообщений для контекста
        recent_history = self.conversation_history[-6:]  # Последние 6 сообщений
        
        for message in recent_history:
            if message["role"] == "user":
                prompt_parts.append(f"Пользователь: {message['content']}")
            else:
                prompt_parts.append(f"Ассистент: {message['content']}")
        
        prompt_parts.append(f"Пользователь: {user_input}")
        prompt_parts.append("Ассистент:")
        
        return "\n".join(prompt_parts)
    
    async def _generate_response(self, prompt: str) -> str:
        """Генерирует ответ от Gemini"""
        try:
            # Используем asyncio для неблокирующего вызова
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Ошибка генерации ответа: {e}")
            raise
    
    def clear_history(self):
        """Очищает историю разговора"""
        self.conversation_history.clear()
    
    def get_conversation_summary(self) -> str:
        """Возвращает краткое содержание разговора"""
        if not self.conversation_history:
            return "Разговор еще не начался."
        
        summary = []
        for message in self.conversation_history[-5:]:  # Последние 5 сообщений
            role = "Вы" if message["role"] == "user" else "ИИ"
            content = message["content"][:100] + "..." if len(message["content"]) > 100 else message["content"]
            summary.append(f"{role}: {content}")
        
        return "\n".join(summary) 