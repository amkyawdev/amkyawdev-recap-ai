"""
Video Editor Screen
Main editing interface with timeline and preview
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.clock import Clock
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty

Builder.load_string("""
<EditorScreen>:
    name: 'editor'
    
    on_enter:
        root.update_preview()
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: 0
        
        # Top Toolbar
        MDTopAppBar:
            title: "Editor"
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
            right_action_items:
                [['undo', lambda x: root.undo()],
                ['redo', lambda x: root.redo()],
                ['save', lambda x: root.save_project()]]
        
        # Preview Area
        BoxLayout:
            size_hint_y: 0.5
            padding: dp(8)
            
            PreviewWidget:
                id: preview
            
            # GPU Status Panel (collapsible)
            GPUStatusPanel:
                id: gpu_panel
                size_hint_x: None
                width: dp(120) if root.show_gpu_panel else 0
                opacity: 1 if root.show_gpu_panel else 0
        
        # Tools Panel
        ToolsPanel:
            id: tools_panel
            size_hint_y: None
            height: dp(80)
        
        # Timeline
        TimelineWidget:
            id: timeline
            size_hint_y: 0.25
        
        # Bottom Action Bar
        MDBoxLayout:
            size_hint_y: None
            height: dp(56)
            spacing: dp(8)
            padding: dp(8)
            
            MDRaisedButton:
                text: "AI Recap"
                icon: 'robot'
                on_release: root.go_to_recap()
            
            MDRaisedButton:
                text: "Effects"
                icon: 'auto-fix'
                on_release: root.show_effects()
            
            MDFillRoundFlatButton:
                text: "Render"
                icon: 'movie-roll'
                on_release: root.show_render_options()
            
            MDRaisedButton:
                text: "Export"
                icon: 'export'
                on_release: root.export_video()
""")


class EditorScreen(Screen):
    """Video editor main screen"""
    
    current_video = ObjectProperty(None)
    current_time = NumericProperty(0)
    duration = NumericProperty(0)
    is_playing = BooleanProperty(False)
    show_gpu_panel = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._playback_timer = None
        self.undo_stack = []
        self.redo_stack = []
    
    def load_video(self, video_path: str):
        """Load video into editor"""
        from main import RecapAIApp
        
        self.current_video = video_path
        
        # Load video info
        app = RecapAIApp.get_running_instance()
        api = app.get_api_client()
        
        try:
            info = api.get_video_info(video_path)
            self.duration = info.get('metadata', {}).get('duration', 0)
            
            # Update UI
            self.ids.preview.load_video(video_path)
            self.ids.timeline.load_video(video_path)
            
        except Exception as e:
            print(f"Failed to load video: {e}")
    
    def update_preview(self):
        """Update preview at current time"""
        if self.current_video:
            self.ids.preview.seek_to(self.current_time)
    
    def play(self):
        """Start playback"""
        self.is_playing = True
        self._playback_timer = Clock.schedule_interval(self._update_playback, 1/30)
    
    def pause(self):
        """Pause playback"""
        self.is_playing = False
        if self._playback_timer:
            self._playback_timer.cancel()
    
    def _update_playback(self, dt):
        """Update playback position"""
        if self.is_playing:
            self.current_time += dt
            if self.current_time >= self.duration:
                self.current_time = 0
            self.ids.preview.seek_to(self.current_time)
            self.ids.timeline.update_playhead(self.current_time)
    
    def seek_to(self, time: float):
        """Seek to specific time"""
        self.current_time = max(0, min(time, self.duration))
        self.ids.preview.seek_to(self.current_time)
        self.ids.timeline.update_playhead(self.current_time)
    
    def go_back(self):
        """Navigate back"""
        self.pause()
        self.manager.current = 'home'
    
    def undo(self):
        """Undo last action"""
        if self.undo_stack:
            action = self.undo_stack.pop()
            self.redo_stack.append(action)
            self._apply_undo(action)
    
    def redo(self):
        """Redo last undone action"""
        if self.redo_stack:
            action = self.redo_stack.pop()
            self.undo_stack.append(action)
            self._apply_redo(action)
    
    def _apply_undo(self, action):
        """Apply undo"""
        # TODO: Implement
        pass
    
    def _apply_redo(self, action):
        """Apply redo"""
        # TODO: Implement
        pass
    
    def save_project(self):
        """Save project"""
        from kivymd.uix.snackbar import Snackbar
        Snackbar(text="Project saved").open()
    
    def go_to_recap(self):
        """Navigate to AI recap"""
        self.manager.get_screen('recap').set_video(self.current_video)
        self.manager.current = 'recap'
    
    def show_effects(self):
        """Show effects panel"""
        self.ids.tools_panel.show_effects_browser()
    
    def show_render_options(self):
        """Show render options"""
        from kivymd.uix.dialog import MDDialog
        from kivymd.uix.button import MDFlatButton
        
        content = """
        [b]Render Settings[/b]
        
        Quality: High (1080p)
        Codec: H.264 (NVENC)
        Location: Cloud
        """
        
        dialog = MDDialog(
            title="Render Video",
            text=content,
            buttons=[
                MDFlatButton(text="Cancel", on_release=lambda x: dialog.dismiss()),
                MDFlatButton(text="Render", on_release=lambda x: self.start_render(dialog)),
            ],
        )
        dialog.open()
    
    def start_render(self, dialog):
        """Start rendering"""
        dialog.dismiss()
        from kivymd.uix.snackbar import Snackbar
        Snackbar(text="Render started").open()
        # TODO: Start render job
    
    def export_video(self):
        """Navigate to export"""
        self.manager.get_screen('export').set_video(self.current_video)
        self.manager.current = 'export'
