from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import asyncio
import json
import base64
import logging
from typing import Dict, List

from services.audio_service import AudioService
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

# Аудио сервисы для каждого соединения
audio_services = {}

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
    
    # Создаем отдельный audio_service для каждого соединения
    audio_services[websocket] = AudioService()
    
    try:
        while True:
            # Получаем аудио данные от клиента
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "audio_chunk":
                # Обрабатываем аудио чанк
                audio_data = base64.b64decode(message["data"])
                await process_audio_chunk(websocket, audio_data)
                
            elif message["type"] == "audio_end":
                # Завершаем обработку аудио
                await process_audio_end(websocket)
                
            elif message["type"] == "clear_history":
                # Очищаем историю разговора
                gemini_service.clear_history()
                await websocket.send_text(json.dumps({
                    "type": "history_cleared"
                }))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        # Удаляем audio_service при отключении
        if websocket in audio_services:
            del audio_services[websocket]
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        # Удаляем audio_service при ошибке
        if websocket in audio_services:
            del audio_services[websocket]
        manager.disconnect(websocket)

async def process_audio_chunk(websocket: WebSocket, audio_data: bytes):
    """Обработка аудио чанка"""
    try:
        # Получаем audio_service для этого соединения
        audio_service = audio_services.get(websocket)
        if not audio_service:
            return
            
        # Добавляем аудио в буфер
        audio_service.add_audio_chunk(audio_data)
        
        # Проверяем активность голоса
        if audio_service.is_speech_detected():
            await websocket.send_text(json.dumps({
                "type": "speech_detected",
                "status": "listening"
            }))
        
    except Exception as e:
        logger.error(f"Error processing audio chunk: {e}")

async def process_audio_end(websocket: WebSocket):
    """Обработка завершения аудио"""
    try:
        # Получаем audio_service для этого соединения
        audio_service = audio_services.get(websocket)
        if not audio_service:
            logger.error("Audio service not found for websocket")
            return
            
        # Получаем накопленное аудио
        audio_buffer = audio_service.get_audio_buffer()
        
        logger.info(f"Audio buffer size: {len(audio_buffer) if audio_buffer else 0}")
        
        if not audio_buffer:
            await websocket.send_text(json.dumps({
                "type": "error",
                "message": "Не удалось записать аудио"
            }))
            return
            
        # Конвертируем речь в текст
        text = await speech_service.speech_to_text(audio_buffer)
        
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
        
        # Очищаем буфер
        audio_service.clear_buffer()
        
    except Exception as e:
        logger.error(f"Error processing audio end: {e}")
        await websocket.send_text(json.dumps({
            "type": "error",
            "message": "Ошибка обработки аудио"
        }))

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 