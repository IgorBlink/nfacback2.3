from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import json
import base64
import logging
from typing import Dict, List

from services.gemini_service import GeminiService
from services.speech_service import SpeechService
from utils.connection_manager import ConnectionManager

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Voice-to-Voice AI Agent", version="1.0.0")

# Статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Сервисы (общие для всех соединений)
gemini_service = GeminiService()
speech_service = SpeechService()
manager = ConnectionManager()

@app.get("/")
async def get():
    """Главная страница приложения"""
    with open("templates/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint для голосового чата"""
    await manager.connect(websocket)
    
    try:
        while True:
            # Получаем аудио данные от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "complete_audio":
                # Обрабатываем полное аудио ОДНИМ куском
                audio_data = base64.b64decode(message["data"])
                await process_complete_audio(websocket, audio_data)
                
            elif message["type"] == "clear_history":
                # Очищаем историю разговора
                gemini_service.clear_history()
                await websocket.send_text(json.dumps({
                    "type": "history_cleared"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

async def process_complete_audio(websocket: WebSocket, audio_data: bytes):
    """Обработка полного аудио файла"""
    try:
        logger.info(f"Received complete audio: {len(audio_data)} bytes")
        
        if not audio_data or len(audio_data) == 0:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Не удалось записать аудио"
            }))
            return
            
        # Конвертируем речь в текст НАПРЯМУЮ
        text = await speech_service.speech_to_text(audio_data)
        
        if text:
            logger.info(f"Transcribed text: {text}")
            await websocket.send_text(json.dumps({
                "type": "transcription",
                "text": text
            }))
            
            # Получаем ответ от Gemini
            response = await gemini_service.get_response(text)
            logger.info(f"Gemini response: {response}")
            
            await websocket.send_text(json.dumps({
                "type": "ai_response",
                "text": response
            }))
            
            # Конвертируем ответ в речь
            audio_response = await speech_service.text_to_speech(response)
            
            # Отправляем аудио ответ
            audio_base64 = base64.b64encode(audio_response).decode()
            await websocket.send_text(json.dumps({
                "type": "audio_response",
                "data": audio_base64
            }))
        else:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Не удалось распознать речь"
            }))
        
    except Exception as e:
        logger.error(f"Error processing complete audio: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Ошибка обработки аудио"
        }))

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 