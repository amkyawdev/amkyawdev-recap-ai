"""
WebSocket Manager for Real-time Updates
Handles render progress and notifications
"""
import json
import logging
from typing import Callable, Dict, Optional
from threading import Thread, Event

logger = logging.getLogger(__name__)

# WebSocket support
try:
    from websocket import create_connection, WebSocketException
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    logger.warning("websocket-client not installed")


class WebSocketManager:
    """
    WebSocket connection manager
    
    Handles real-time updates for:
    - Render progress
    - GPU status changes
    - Job completion notifications
    """
    
    def __init__(self, ws_url: Optional[str] = None):
        """
        Initialize WebSocket manager
        
        Args:
            ws_url: WebSocket server URL
        """
        self.ws_url = ws_url or "ws://localhost:8000/ws"
        self._ws = None
        self._connected = False
        self._reconnect_thread = None
        self._stop_event = Event()
        
        # Event callbacks
        self._callbacks: Dict[str, list] = {
            'render_progress': [],
            'render_complete': [],
            'render_error': [],
            'gpu_status': [],
            'connection_status': [],
        }
    
    @property
    def connected(self) -> bool:
        """Check if connected"""
        return self._connected
    
    def connect(self):
        """Connect to WebSocket server"""
        if not WEBSOCKET_AVAILABLE:
            logger.warning("WebSocket not available")
            return
        
        if self._connected:
            return
        
        try:
            self._ws = create_connection(
                self.ws_url,
                timeout=30,
                enable_multithread=True
            )
            self._connected = True
            logger.info(f"WebSocket connected: {self.ws_url}")
            
            self._emit('connection_status', {'connected': True})
            
            # Start listening thread
            self._start_listener()
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            self._schedule_reconnect()
    
    def disconnect(self):
        """Disconnect from WebSocket server"""
        self._stop_event.set()
        
        if self._ws:
            try:
                self._ws.close()
            except:
                pass
            self._ws = None
        
        self._connected = False
        self._emit('connection_status', {'connected': False})
    
    def _start_listener(self):
        """Start listening for messages"""
        def listen():
            while not self._stop_event.is_set() and self._connected:
                try:
                    if self._ws:
                        message = self._ws.recv()
                        self._handle_message(message)
                except Exception as e:
                    logger.error(f"WebSocket receive error: {e}")
                    self._connected = False
                    self._schedule_reconnect()
                    break
        
        thread = Thread(target=listen, daemon=True)
        thread.start()
    
    def _handle_message(self, message: str):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            event_type = data.get('type')
            
            if event_type == 'render_progress':
                self._emit('render_progress', data)
            elif event_type == 'render_complete':
                self._emit('render_complete', data)
            elif event_type == 'render_error':
                self._emit('render_error', data)
            elif event_type == 'gpu_status':
                self._emit('gpu_status', data)
                
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON: {message}")
    
    def _schedule_reconnect(self):
        """Schedule reconnection attempt"""
        import time
        time.sleep(5)
        if not self._connected and not self._stop_event.is_set():
            self.connect()
    
    def _emit(self, event: str, data: dict):
        """Emit event to callbacks"""
        for callback in self._callbacks.get(event, []):
            try:
                callback(data)
            except Exception as e:
                logger.error(f"Callback error: {e}")
    
    def on(self, event: str, callback: Callable):
        """
        Register event callback
        
        Args:
            event: Event name
            callback: Callback function
        """
        if event not in self._callbacks:
            self._callbacks[event] = []
        self._callbacks[event].append(callback)
    
    def off(self, event: str, callback: Callable):
        """Remove event callback"""
        if event in self._callbacks:
            try:
                self._callbacks[event].remove(callback)
            except ValueError:
                pass
    
    def send(self, event: str, data: dict):
        """Send message to server"""
        if not self._connected or not self._ws:
            logger.warning("WebSocket not connected")
            return
        
        try:
            message = json.dumps({'type': event, **data})
            self._ws.send(message)
        except Exception as e:
            logger.error(f"WebSocket send error: {e}")
    
    # Convenience methods
    
    def subscribe_render(self, job_id: str):
        """Subscribe to render job updates"""
        self.send('subscribe_render', {'job_id': job_id})
    
    def unsubscribe_render(self, job_id: str):
        """Unsubscribe from render job updates"""
        self.send('unsubscribe_render', {'job_id': job_id})
    
    def subscribe_gpu(self):
        """Subscribe to GPU status updates"""
        self.send('subscribe_gpu', {})
    
    def unsubscribe_gpu(self):
        """Unsubscribe from GPU status updates"""
        self.send('unsubscribe_gpu', {})


# Global instance
ws_manager = WebSocketManager()
