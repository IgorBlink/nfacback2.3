from fastapi import WebSocket
from typing import List, Dict
import logging
import json

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Менеджер для управления WebSocket соединениями"""
    
    def __init__(self):
        # Активные соединения
        self.active_connections: List[WebSocket] = []
        # Метаданные соединений
        self.connection_metadata: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Принимает новое WebSocket соединение"""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Инициализируем метаданные
        self.connection_metadata[websocket] = {
            "connected_at": self._get_current_timestamp(),
            "session_id": self._generate_session_id(),
            "is_recording": False,
            "last_activity": self._get_current_timestamp()
        }
        
        logger.info(f"Новое WebSocket соединение. Всего активных: {len(self.active_connections)}")
        
        # Отправляем приветственное сообщение
        await self.send_personal_message({
            "type": "connection_established",
            "message": "Соединение установлено. Можете начать говорить!",
            "session_id": self.connection_metadata[websocket]["session_id"]
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Отключает WebSocket соединение"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
        if websocket in self.connection_metadata:
            session_id = self.connection_metadata[websocket]["session_id"]
            del self.connection_metadata[websocket]
            logger.info(f"WebSocket соединение отключено. Session ID: {session_id}")
        
        logger.info(f"Всего активных соединений: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Отправляет личное сообщение конкретному клиенту"""
        try:
            if websocket in self.active_connections:
                await websocket.send_text(json.dumps(message, ensure_ascii=False))
                self._update_last_activity(websocket)
            else:
                logger.warning("Попытка отправить сообщение отключенному клиенту")
                
        except Exception as e:
            logger.error(f"Ошибка отправки сообщения: {e}")
            # Удаляем проблемное соединение
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Отправляет сообщение всем подключенным клиентам"""
        if not self.active_connections:
            return
            
        disconnected_clients = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message, ensure_ascii=False))
                self._update_last_activity(connection)
            except Exception as e:
                logger.error(f"Ошибка broadcast сообщения: {e}")
                disconnected_clients.append(connection)
        
        # Удаляем отключенные соединения
        for client in disconnected_clients:
            self.disconnect(client)
    
    def get_connection_info(self, websocket: WebSocket) -> dict:
        """Возвращает информацию о соединении"""
        return self.connection_metadata.get(websocket, {})
    
    def set_recording_status(self, websocket: WebSocket, is_recording: bool):
        """Устанавливает статус записи для соединения"""
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["is_recording"] = is_recording
            self._update_last_activity(websocket)
    
    def get_active_connections_count(self) -> int:
        """Возвращает количество активных соединений"""
        return len(self.active_connections)
    
    def get_connections_summary(self) -> dict:
        """Возвращает сводку по всем соединениям"""
        summary = {
            "total_connections": len(self.active_connections),
            "recording_connections": 0,
            "connections": []
        }
        
        for websocket, metadata in self.connection_metadata.items():
            if metadata["is_recording"]:
                summary["recording_connections"] += 1
            
            summary["connections"].append({
                "session_id": metadata["session_id"],
                "connected_at": metadata["connected_at"],
                "last_activity": metadata["last_activity"],
                "is_recording": metadata["is_recording"]
            })
        
        return summary
    
    def _update_last_activity(self, websocket: WebSocket):
        """Обновляет время последней активности"""
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]["last_activity"] = self._get_current_timestamp()
    
    def _get_current_timestamp(self) -> str:
        """Возвращает текущее время в формате ISO"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _generate_session_id(self) -> str:
        """Генерирует уникальный ID сессии"""
        import uuid
        return str(uuid.uuid4())[:8] 