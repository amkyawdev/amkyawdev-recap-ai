"""
Preview Widget
Video preview with playback controls
"""
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.button import MDIconButton
from kivy.properties import ObjectProperty, NumericProperty, BooleanProperty

Builder.load_string("""
<PreviewWidget>:
    orientation: 'vertical'
    spacing: dp(4)
    padding: dp(4)
    
    # Video display area
    BoxLayout:
        id: video_container
        size_hint_y: 1
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
    
    # Playback controls
    MDBoxLayout:
        size_hint_y: None
        height: dp(40)
        spacing: dp(8)
        padding: dp(8, 0)
        
        # Time display
        MDLabel:
            id: time_label
            text: "00:00 / 00:00"
            font_size: '12sp'
            size_hint_x: 0.3
        
        # Progress slider
        Slider:
            id: progress_slider
            min: 0
            max: 100
            value: 0
            size_hint_x: 1
            on_value: root.on_slider_change(self.value)
        
        # Play/Pause
        MDIconButton:
            id: play_button
            icon: 'play'
            on_release: root.toggle_play()
        
        # Volume
        MDIconButton:
            icon: 'volume-high'
            on_release: root.toggle_mute()
""")


class PreviewWidget(BoxLayout):
    """Video preview with controls"""
    
    video_path = ObjectProperty(None)
    is_playing = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_time = 0
        self.duration = 0
    
    def load_video(self, path: str):
        """Load video file"""
        self.video_path = path
        # TODO: Initialize video player
        
    def seek_to(self, time: float):
        """Seek to specific time"""
        self.current_time = time
        self.update_time_label()
        self.update_slider()
        # TODO: Seek video player
    
    def toggle_play(self):
        """Toggle play/pause"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start playback"""
        self.is_playing = True
        self.ids.play_button.icon = 'pause'
        # TODO: Start video playback
    
    def pause(self):
        """Pause playback"""
        self.is_playing = False
        self.ids.play_button.icon = 'play'
        # TODO: Pause video playback
    
    def toggle_mute(self):
        """Toggle mute"""
        # TODO: Toggle audio
        pass
    
    def on_slider_change(self, value: float):
        """Handle slider change"""
        if self.duration > 0:
            time = (value / 100) * self.duration
            self.seek_to(time)
    
    def update_time_label(self):
        """Update time display"""
        current = self._format_time(self.current_time)
        total = self._format_time(self.duration)
        self.ids.time_label.text = f"{current} / {total}"
    
    def update_slider(self):
        """Update progress slider"""
        if self.duration > 0:
            self.ids.progress_slider.value = (self.current_time / self.duration) * 100
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
