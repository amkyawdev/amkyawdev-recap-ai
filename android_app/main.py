"""
Recap AI - Android Video Editor App
Kivy/KivyMD based mobile application
"""
import os
import sys
from pathlib import Path

# Add backend API path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from kivy import Config
from kivy.core.window import Window
from kivy.utils import platform

# Mobile configuration
if platform in ('android', 'ios'):
    Config.set('graphics', 'width', '360')
    Config.set('graphics', 'height', '640')
    Config.set('graphics', 'mult Samples', '4')

# App configuration
Config.set('kivy', 'version', '2.2.1')
Config.set('kivy', 'log_level', 'info')
Config.set('kivy', 'log_enable', 1)
Config.set('kivy', 'default_font', [
    'Roboto',
    'data/fonts/Roboto-Regular.ttf',
    'data/fonts/Roboto-Bold.ttf',
    'data/fonts/Roboto-Italic.ttf',
])

from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.theming import ThemeManager
from kivymd.font_definitions import theme_font_styles

from screens.loading_screen import LoadingScreen
from screens.home import HomeScreen
from screens.editor.timeline_widget import TimelineWidget
from screens.editor.preview_widget import PreviewWidget
from screens.editor.tools_panel import ToolsPanel
from screens.editor.gpu_status import GPUStatusPanel
from screens.recap import RecapScreen
from screens.export import ExportScreen
from services.api_client import APIClient
from services.websocket import WebSocketManager


class RecapAIApp(MDApp):
    """Main Application Class"""
    
    title = "Recap AI"
    theme_cls = ThemeManager()
    
    # Theme colors - matching web design with violet/fuchsia gradient
    theme_colors = {
        # Modern violet/fuchsia theme matching web
        'primary': '#8B5CF6',        # violet-500
        'secondary': '#A855F7',      # purple-500
        'accent': '#D946EF',         # fuchsia-500
        'background': '#0F0F1A',     # slate-950
        'surface': '#1E1E2E',        # slate-800/60
        'surface_variant': '#27273A', # slate-700/50
        'error': '#F43F5E',          # rose-500
        'success': '#10B981',        # emerald-500
        'on_primary': '#FFFFFF',
        'on_secondary': '#FFFFFF',
        'on_background': '#FFFFFF',
        'on_surface': '#FFFFFF',
        # Gradient colors
        'violet': '#8B5CF6',
        'fuchsia': '#D946EF',
        'purple': '#A855F7',
        'emerald': '#10B981',
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Services
        self.api_client = APIClient()
        self.ws_manager = WebSocketManager()
        
        # App state
        self.current_project = None
        self.gpu_available = False
        self.is_loading = True
        
    def build(self):
        """Build the application"""
        self.setup_theme()
        
        # Screen manager
        sm = MDScreenManager()
        
        # Add loading screen first
        sm.add_widget(LoadingScreen(name='loading'))
        
        # Add main screens
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(RecapScreen(name='recap'))
        sm.add_widget(ExportScreen(name='export'))
        
        # Editor screen (complex, built separately)
        from screens.editor.editor_screen import EditorScreen
        sm.add_widget(EditorScreen(name='editor'))
        
        return sm
    
    def setup_theme(self):
        """Setup app theme with modern violet/fuchsia colors"""
        self.theme_cls.primary_palette = 'DeepPurple'
        self.theme_cls.accent_palette = 'Purple'
        self.theme_cls.theme_style = 'Dark'
        
        # Update colors with custom violet/fuchsia theme
        self.theme_cls.colors.update({
            'Primary': self.theme_colors['primary'],
            'Secondary': self.theme_colors['secondary'],
            'Accent': self.theme_colors['accent'],
            'Background': self.theme_colors['background'],
            'Surface': self.theme_colors['surface'],
            'Error': self.theme_colors['error'],
        })
    
    def on_start(self):
        """App startup"""
        super().on_start()
        
        # Initialize services
        self.check_gpu_status()
        self.connect_websocket()
    
    def on_pause(self):
        """App pause (mobile)"""
        # Save project state
        if self.current_project:
            self.save_project_state()
        return True
    
    def on_resume(self):
        """App resume (mobile)"""
        self.reconnect_websocket()
    
    def on_stop(self):
        """App shutdown"""
        self.ws_manager.disconnect()
    
    def check_gpu_status(self):
        """Check GPU availability"""
        try:
            status = self.api_client.get_gpu_status()
            self.gpu_available = status.get('available', False)
        except Exception as e:
            print(f"GPU status check failed: {e}")
            self.gpu_available = False
    
    def connect_websocket(self):
        """Connect to WebSocket for real-time updates"""
        try:
            self.ws_manager.connect()
        except Exception as e:
            print(f"WebSocket connection failed: {e}")
    
    def reconnect_websocket(self):
        """Reconnect WebSocket"""
        if not self.ws_manager.connected:
            self.connect_websocket()
    
    def save_project_state(self):
        """Save current project state"""
        # TODO: Implement project state persistence
        pass
    
    def get_api_client(self) -> APIClient:
        """Get API client instance"""
        return self.api_client
    
    def get_ws_manager(self) -> WebSocketManager:
        """Get WebSocket manager instance"""
        return self.ws_manager


if __name__ == '__main__':
    # Mobile or desktop
    if platform == 'android':
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.INTERNET,
            Permission.CAMERA,
        ])
    
    RecapAIApp().run()
