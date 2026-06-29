"""
Home Screen
Main screen with project list and actions
"""
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import MDListItem
from kivymd.uix.button import MDFloatingActionButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.snackbar import Snackbar

Builder.load_string("""
<HomeScreen>:
    name: 'home'
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(16)
        padding: dp(16)
        
        # Header
        MDBoxLayout:
            size_hint_y: None
            height: dp(56)
            
            MDLabel:
                text: "Recap AI"
                font_style: 'Headline'
                halign: 'left'
                valign: 'middle'
            
            MDIconButton:
                icon: 'cog'
                pos_hint: {'right': 1}
                on_release: app.open_settings()
        
        # GPU Status Card
        GPUStatusCard:
            id: gpu_card
            size_hint_y: None
            height: dp(80)
        
        # Recent Projects
        MDLabel:
            text: "Recent Projects"
            font_style: 'Title'
            size_hint_y: None
            height: dp(40)
        
        # Project List
        ScrollView:
            do_scroll_x: False
            
            MDList:
                id: project_list
        
        # Action Buttons
        MDBoxLayout:
            size_hint_y: None
            height: dp(80)
            spacing: dp(16)
            padding: dp(16, 0)
            
            MDRaisedButton:
                text: "New Project"
                icon: 'plus'
                on_release: root.show_new_project_menu()
                size_hint_x: 1
            
            MDRaisedButton:
                text: "Import Video"
                icon: 'import'
                on_release: root.show_file_manager()
                size_hint_x: 1
        
        # Quick Actions
        MDBoxLayout:
            size_hint_y: None
            height: dp(100)
            spacing: dp(12)
            
            QuickActionCard:
                icon: 'movie-edit'
                title: "Edit"
                subtitle: "Trim & effects"
                on_release: root.open_editor()
            
            QuickActionCard:
                icon: 'robot'
                title: "AI Recap"
                subtitle: "Generate script"
                on_release: root.go_to_recap()
            
            QuickActionCard:
                icon: 'export'
                title: "Export"
                subtitle: "Share video"
                on_release: root.go_to_export()
            
            QuickActionCard:
                icon: 'cloud'
                title: "Cloud"
                subtitle: "Upload/Sync"
                on_release: root.show_cloud_menu()


<GPUStatusCard@MDCard>:
    elevation: 2
    padding: dp(12)
    
    MDBoxLayout:
        spacing: dp(12)
        adaptive_height: True
        
        MDIcon:
            icon: 'memory'
            halign: 'center'
            valign: 'middle'
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: dp(4)
            
            MDLabel:
                id: gpu_name
                text: "GPU: Checking..."
                font_style: 'Body1'
            
            MDLabel:
                id: gpu_status
                text: "Ready"
                font_style: 'Body2'
                theme_text_color: 'Secondary'


<QuickActionCard@MDCard>:
    elevation: 1
    padding: dp(8)
    on_release: None  # Set in Python
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(4)
        halign: 'center'
        
        MDIcon:
            icon: root.icon
            font_size: '32sp'
            halign: 'center'
        
        MDLabel:
            text: root.title
            font_style: 'Caption'
            halign: 'center'
        
        MDLabel:
            text: root.subtitle
            font_style: 'Overline'
            theme_text_color: 'Secondary'
            halign: 'center'
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
