"""
Export Screen
Video export with presets and settings
"""
from kivy.lang import Builder
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.progressloader import MDProgressLoader

Builder.load_string("""
<ExportScreen>:
    name: 'export'
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(16)
        padding: dp(16)
        
        # Header
        MDTopAppBar:
            title: "Export"
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
        
        # Video Preview
        MDCard:
            size_hint_y: 0.2
            padding: dp(12)
            
            MDBoxLayout:
                spacing: dp(12)
                
                BoxLayout:
                    size_hint_x: 0.3
                    canvas.before:
                        Color:
                            rgba: 0, 0, 0, 1
                        Rectangle:
                            pos: self.pos
                            size: self.size
                    
                    AsyncImage:
                        id: thumbnail
                        source: ''
                
                MDBoxLayout:
                    orientation: 'vertical'
                    
                    MDLabel:
                        id: video_name
                        text: "Video"
                        font_style: 'Body1'
                    
                    MDLabel:
                        id: video_info
                        text: "1920x1080 • 30fps"
                        font_style: 'Caption'
                        theme_text_color: 'Secondary'
        
        # Format Selection
        MDLabel:
            text: "Format"
            font_style: 'Subtitle'
        
        MDBoxLayout:
            spacing: dp(12)
            size_hint_y: None
            height: dp(80)
            
            FormatButton:
                id: format_mp4
                text: "MP4"
                selected: True
            
            FormatButton:
                id: format_webm
                text: "WebM"
            
            FormatButton:
                id: format_mov
                text: "MOV"
        
        # Quality Selection
        MDLabel:
            text: "Quality"
            font_style: 'Subtitle'
        
        MDBoxLayout:
            spacing: dp(12)
            size_hint_y: None
            height: dp(80)
            
            QualityButton:
                text: "Low"
                subtitle: "480p"
            
            QualityButton:
                text: "Medium"
                subtitle: "720p"
            
            QualityButton:
                text: "High"
                subtitle: "1080p"
                selected: True
            
            QualityButton:
                text: "Ultra"
                subtitle: "4K"
        
        # Export Location
        MDLabel:
            text: "Export Location"
            font_style: 'Subtitle'
        
        MDBoxLayout:
            spacing: dp(12)
            size_hint_y: None
            height: dp(56)
            
            MDRaisedButton:
                text: "Save to Device"
                icon: 'folder'
                on_release: root.select_location('local')
            
            MDRaisedButton:
                text: "Cloud"
                icon: 'cloud-upload'
                on_release: root.select_location('cloud')
        
        # Presets
        MDLabel:
            text: "Quick Presets"
            font_style: 'Subtitle'
        
        ScrollView:
            size_hint_y: 0.2
            
            MDBoxLayout:
                spacing: dp(8)
                size_hint_x: None
                width: self.minimum_width
                padding: dp(4)
                
                PresetChip:
                    text: "YouTube"
                    on_release: root.apply_preset('youtube')
                
                PresetChip:
                    text: "TikTok"
                    on_release: root.apply_preset('tiktok')
                
                PresetChip:
                    text: "Instagram"
                    on_release: root.apply_preset('instagram')
                
                PresetChip:
                    text: "Twitter"
                    on_release: root.apply_preset('twitter')
        
        # Widget
        Widget:
            size_hint_y: 0.1
        
        # Export Button
        MDRaisedButton:
            id: export_btn
            text: "Export Video"
            icon: 'export'
            on_release: root.start_export()
            size_hint_y: None
            height: dp(56)
        
        # Progress
        MDBoxLayout:
            id: progress_box
            visible: False
            spacing: dp(12)
            padding: dp(8)
            
            MDProgressBar:
                id: export_progress
                value: 0
            
            MDLabel:
                id: progress_text
                text: "0%"
                size_hint_x: 0.2


<FormatButton@MDCard>:
    elevation: 1
    padding: dp(8)
    selected: False
    
    MDLabel:
        text: root.text
        halign: 'center'
        font_style: 'Button'


<QualityButton@MDCard>:
    elevation: 1
    padding: dp(8)
    selected: False
    
    MDBoxLayout:
        orientation: 'vertical'
        halign: 'center'
        
        MDLabel:
            text: root.text
            font_style: 'Button'
        
        MDLabel:
            text: root.subtitle
            font_style: 'Caption'
            theme_text_color: 'Secondary'


<PresetChip@MDChip>:
    text: ''
""")


class ExportScreen(MDScreen):
    """Video export screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_video = None
        self.selected_format = "mp4"
        self.selected_quality = "high"
        self.selected_location = "local"
    
    def on_enter(self):
        """Called when entering screen"""
        if self.current_video:
            self._load_video_info()
    
    def set_video(self, video_path: str):
        """Set video to export"""
        self.current_video = video_path
        self._load_video_info()
    
    def _load_video_info(self):
        """Load video information"""
        from main import RecapAIApp
        
        try:
            app = RecapAIApp.get_running_instance()
            info = app.get_api_client().get_video_info(self.current_video)
            
            self.ids.video_name.text = self.current_video.split('/')[-1]
            
            video = info.get('video', {})
            self.ids.video_info.text = f"{video.get('width', 0)}x{video.get('height', 0)} • {video.get('fps', 0)}fps"
            
        except Exception as e:
            print(f"Failed to load video info: {e}")
    
    def go_back(self):
        """Navigate back"""
        self.manager.current = 'editor'
    
    def select_location(self, location: str):
        """Select export location"""
        self.selected_location = location
    
    def apply_preset(self, preset: str):
        """Apply export preset"""
        presets = {
            'youtube': {'format': 'mp4', 'quality': 'ultra', 'codec': 'h264'},
            'tiktok': {'format': 'mp4', 'quality': 'high', 'codec': 'h264'},
            'instagram': {'format': 'mp4', 'quality': 'high', 'codec': 'h264'},
            'twitter': {'format': 'mp4', 'quality': 'medium', 'codec': 'h264'},
        }
        
        if preset in presets:
            p = presets[preset]
            self.selected_format = p['format']
            self.selected_quality = p['quality']
    
    def start_export(self):
        """Start video export"""
        if not self.current_video:
            return
        
        from main import RecapAIApp
        
        self.ids.export_btn.disabled = True
        self.ids.progress_box.visible = True
        
        app = RecapAIApp.get_running_instance()
        
        def do_export():
            try:
                result = app.get_api_client().export_video(
                    video_path=self.current_video,
                    format=self.selected_format,
                    quality=self.selected_quality,
                    upload_to_cloud=(self.selected_location == 'cloud'),
                )
                
                # Simulate progress
                import time
                for i in range(100):
                    time.sleep(0.1)
                    # Would update progress from WebSocket
                
            except Exception as e:
                print(f"Export failed: {e}")
            finally:
                self.ids.export_btn.disabled = False
                self.ids.progress_box.visible = False
        
        import threading
        thread = threading.Thread(target=do_export)
        thread.start()
