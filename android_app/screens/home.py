"""
Home Screen
Main screen with modern design matching web UI
"""
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDListItem
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton
from kivymd.uix.card import MDCardSwipe
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.imageloading import AsyncImage
from kivy.utils import get_color_from_hex
import os

Builder.load_string("""
<HomeScreen>:
    name: 'home'
    
    # Modern dark background
    md_bg_color: get_color_from_hex('#0F172A')  # slate-900
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(16)
        padding: dp(16)
        
        # Header with gradient accent
        MDBoxLayout:
            size_hint_y: None
            height: dp(60)
            spacing: dp(12)
            
            # Logo icon (Image widget for PNG)
            MDBoxLayout:
                size_hint: None, None
                size: dp(48), dp(48)
                canvas.before:
                    Color:
                        rgba: get_color_from_hex('#8B5CF6')  # violet
                    RoundedRectangle:
                        size: self.size
                        pos: self.pos
                        radius: [12]
                Image:
                    source: 'icon.png'
                    size_hint: 1, 1
                    allow_stretch: True
                    keep_ratio: True
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
            
            # Title container
            MDBoxLayout:
                orientation: 'vertical'
                spacing: 0
                
                MDLabel:
                    text: "Recap AI"
                    font_size: '22sp'
                    bold: True
                    font_name: 'Roboto'
                    theme_text_color: 'Custom'
                    text_color: get_color_from_hex('#F5F5F5')
                    halign: 'left'
                    valign: 'center'
                
                MDLabel:
                    text: "Video Recap Generator"
                    font_size: '11sp'
                    theme_text_color: 'Custom'
                    text_color: get_color_from_hex('#94A3B8')  # slate-400
                    halign: 'left'
                    valign: 'top'
            
            Widget:
                size_hint_x: 1
            
            # Settings button
            MDIconButton:
                icon: 'cog'
                pos_hint: {'right': 1}
                on_release: app.open_settings()
                theme_icon_color: 'Custom'
                icon_color: get_color_from_hex('#94A3B8')
        
        # GPU Status Card - Modern design
        ModernGPUCard:
            id: gpu_card
        
        # Quick Action Buttons - Grid style
        MDLabel:
            text: "Quick Actions"
            font_size: '16sp'
            bold: True
            size_hint_y: None
            height: dp(36)
            theme_text_color: 'Custom'
            text_color: get_color_from_hex('#CBD5E1')  # slate-300
        
        # Action Buttons Grid
        MDBoxLayout:
            size_hint_y: None
            height: dp(140)
            spacing: dp(12)
            
            # New Project Button
            ModernActionButton:
                icon: 'plus'
                title: 'New Project'
                subtitle: 'Start fresh'
                color: get_color_from_hex('#8B5CF6')  # violet
                on_release: root.show_new_project_menu()
            
            # Import Video Button
            ModernActionButton:
                icon: 'import'
                title: 'Import Video'
                subtitle: 'Upload from device'
                color: get_color_from_hex('#06B6D4')  # cyan
                on_release: root.show_file_manager()
        
        # Secondary Quick Actions - 4 column grid
        MDBoxLayout:
            size_hint_y: None
            height: dp(100)
            spacing: dp(8)
            
            SmallActionCard:
                icon: 'movie-edit'
                title: "Editor"
                subtitle: "Trim & effects"
                color: get_color_from_hex('#3B82F6')  # blue
                on_release: root.open_editor()
            
            SmallActionCard:
                icon: 'robot'
                title: "AI Recap"
                subtitle: "Generate script"
                color: get_color_from_hex('#8B5CF6')  # violet
                on_release: root.go_to_recap()
            
            SmallActionCard:
                icon: 'export'
                title: "Export"
                subtitle: "Share video"
                color: get_color_from_hex('#10B981')  # emerald
                on_release: root.go_to_export()
            
            SmallActionCard:
                icon: 'cloud'
                title: "Cloud"
                subtitle: "Upload/Sync"
                color: get_color_from_hex('#0EA5E9')  # sky
                on_release: root.show_cloud_menu()


<ModernGPUCard@MDCard>:
    elevation: 0
    padding: dp(16)
    radius: [16]
    md_bg_color: get_color_from_hex('#1E293B')  # slate-800/60
    line_color: get_color_from_hex('#334155')  # slate-700/50
    
    MDBoxLayout:
        spacing: dp(16)
        adaptive_height: True
        
        # GPU Icon Box
        MDBoxLayout:
            size_hint: None, None
            size: dp(48), dp(48)
            canvas.before:
                Color:
                    rgba: get_color_from_hex('#10B98133')  # emerald/20
                RoundedRectangle:
                    size: self.size
                    pos: self.pos
                    radius: [12]
                Color:
                    rgba: get_color_from_hex('#10B981')  # emerald
                Line:
                    rounded_rectangle: [self.x, self.y, self.width, self.height, 12]
                    width: 1
            MDIcon:
                icon: 'memory'
                font_size: '24sp'
                halign: 'center'
                valign: 'center'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#10B981')
        
        # Status text
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(4)
            size_hint_x: 1
            
            MDLabel:
                id: gpu_name
                text: "GPU Accelerated"
                font_size: '16sp'
                bold: True
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#10B981')  # emerald
            
            MDLabel:
                id: gpu_status
                text: "Ready for fast rendering"
                font_size: '13sp'
                theme_text_color: 'Custom'
                text_color: get_color_from_hex('#94A3B8')  # slate-400
        
        # Status badge
        MDChip:
            text: 'Active'
            chip_height: '28dp'
            md_bg_color: get_color_from_hex('#10B98133')  # emerald/20
            theme_text_color: 'Custom'
            text_color: get_color_from_hex('#10B981')
            elevation: 0


<ModernActionButton@MDRelativeLayout>:
    icon: ''
    title: ''
    subtitle: ''
    color: [1, 1, 1, 1]
    
    canvas.before:
        Color:
            rgba: get_color_from_hex('#1E293B')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [16]
        Color:
            rgba: root.color + [0.3]  # 30% opacity
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [16]
        Color:
            rgba: root.color
        Line:
            rounded_rectangle: [self.x, self.y, self.width, self.height, 16]
            width: 1
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(8)
        padding: dp(16)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint: 1, 1
        
        MDIcon:
            icon: root.icon
            font_size: '32sp'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: root.color
        
        MDLabel:
            text: root.title
            font_size: '14sp'
            bold: True
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: get_color_from_hex('#F5F5F5')
        
        MDLabel:
            text: root.subtitle
            font_size: '11sp'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: get_color_from_hex('#64748B')  # slate-500


<SmallActionCard@MDRelativeLayout>:
    icon: ''
    title: ''
    subtitle: ''
    color: [1, 1, 1, 1]
    
    canvas.before:
        Color:
            rgba: get_color_from_hex('#1E293B')
        RoundedRectangle:
            size: self.size
            pos: self.pos
            radius: [12]
    
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(4)
        padding: dp(8)
        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        size_hint: 1, 1
        
        MDIcon:
            icon: root.icon
            font_size: '22sp'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: root.color
        
        MDLabel:
            text: root.title
            font_size: '11sp'
            bold: True
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: get_color_from_hex('#F5F5F5')
        
        MDLabel:
            text: root.subtitle
            font_size: '9sp'
            halign: 'center'
            theme_text_color: 'Custom'
            text_color: get_color_from_hex('#64748B')  # slate-500
""")


class HomeScreen(MDScreen):
    """Home screen with project management"""
    
    def on_enter(self):
        """Called when entering screen"""
        self.load_projects()
        self.update_gpu_status()
    
    def load_projects(self):
        """Load recent projects"""
        # TODO: Load from database/storage
        # For now, add sample
        pass
    
    def update_gpu_status(self):
        """Update GPU status display"""
        try:
            gpu_card = self.ids.gpu_card
            if gpu_card:
                from main import RecapAIApp
                app = RecapAIApp.get_running_instance()
                if app and app.gpu_available:
                    gpu_card.ids.gpu_name.text = "GPU: Available"
                    gpu_card.ids.gpu_status.text = "Ready for rendering"
                else:
                    gpu_card.ids.gpu_name.text = "CPU Mode"
                    gpu_card.ids.gpu_status.text = "GPU not available"
        except:
            pass
    
    def show_new_project_menu(self):
        """Show new project creation menu"""
        from kivymd.uix.menu import MDDropdownMenu
        
        menu_items = [
            {"text": "Blank Project", "icon": "file-plus"},
            {"text": "From Template", "icon": "file-document"},
            {"text": "Import Video", "icon": "import"},
        ]
        
        menu = MDDropdownMenu(
            caller=self,
            items=menu_items,
            width_mult=2
        )
        menu.open()
    
    def show_file_manager(self):
        """Show file manager for video import"""
        from main import RecapAIApp
        
        app = RecapAIApp.get_running_instance()
        
        self.file_manager = MDFileManager(
            exit_manager=self.exit_file_manager,
            select_path=self.select_video_file,
        )
        
        # Start from external storage
        if hasattr(app, 'external_storage'):
            self.file_manager.show(app.external_storage)
        else:
            self.file_manager.show("/storage/emulated/0")
    
    def exit_file_manager(self, *args):
        """Exit file manager"""
        if hasattr(self, 'file_manager'):
            self.file_manager.close()
    
    def select_video_file(self, path: str):
        """Handle video file selection"""
        self.exit_file_manager()
        
        Snackbar(
            text=f"Selected: {path}",
            duration=2
        ).open()
        
        # Navigate to editor
        self.manager.get_screen('editor').load_video(path)
        self.manager.current = 'editor'
    
    def open_editor(self):
        """Open video editor"""
        self.manager.current = 'editor'
    
    def go_to_recap(self):
        """Navigate to recap screen"""
        self.manager.current = 'recap'
    
    def go_to_export(self):
        """Navigate to export screen"""
        self.manager.current = 'export'
    
    def show_cloud_menu(self):
        """Show cloud storage options"""
        from kivymd.uix.menu import MDDropdownMenu
        
        menu_items = [
            {"text": "Upload to Cloud", "icon": "cloud-upload"},
            {"text": "Download from Cloud", "icon": "cloud-download"},
            {"text": "Sync Projects", "icon": "sync"},
        ]
        
        menu = MDDropdownMenu(
            caller=self,
            items=menu_items,
            width_mult=2
        )
        menu.open()
