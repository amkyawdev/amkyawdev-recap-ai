"""
Timeline Widget
Video timeline with clips and playhead
"""
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty
from kivy.graphics import Color, Rectangle, Line
from kivy.graphics.texture import Texture

Builder.load_string("""
<TimelineWidget>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size
""")


class TimelineWidget(Widget):
    """Video timeline widget"""
    
    duration = NumericProperty(0)
    current_time = NumericProperty(0)
    zoom = NumericProperty(1.0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.clips = []
        self.selected_clip = None
        self._bind_properties()
    
    def _bind_properties(self):
        """Bind property listeners"""
        self.bind(
            duration=self._draw_timeline,
            current_time=self._draw_playhead,
            zoom=self._draw_timeline,
            size=self._draw_timeline
        )
    
    def load_video(self, video_path: str):
        """Load video and display on timeline"""
        # Get video duration
        from main import RecapAIApp
        app = RecapAIApp.get_running_instance()
        
        try:
            info = app.get_api_client().get_video_info(video_path)
            self.duration = info.get('metadata', {}).get('duration', 60)
            
            # Add clip
            self.add_clip(0, self.duration, video_path)
        except Exception as e:
            print(f"Failed to load video: {e}")
            self.duration = 60
            self.add_clip(0, 60, video_path)
    
    def add_clip(self, start: float, end: float, source: str):
        """Add clip to timeline"""
        self.clips.append({
            'start': start,
            'end': end,
            'source': source,
            'thumbnail': None
        })
        self._draw_timeline()
    
    def remove_clip(self, index: int):
        """Remove clip from timeline"""
        if 0 <= index < len(self.clips):
            del self.clips[index]
            self._draw_timeline()
    
    def update_playhead(self, time: float):
        """Update playhead position"""
        self.current_time = time
        self._draw_playhead()
    
    def seek_to(self, x: float):
        """Seek to position based on x coordinate"""
        if self.width > 0 and self.duration > 0:
            ratio = x / self.width
            return ratio * self.duration
        return 0
    
    def _draw_timeline(self, *args):
        """Draw timeline background and clips"""
        self.canvas.clear()
        
        with self.canvas:
            # Background
            Color(0.15, 0.15, 0.15, 1)
            Rectangle(pos=self.pos, size=self.size)
            
            # Time ruler
            Color(0.3, 0.3, 0.3, 1)
            self._draw_ruler()
            
            # Clips
            for clip in self.clips:
                self._draw_clip(clip)
            
            # Playhead
            self._draw_playhead()
    
    def _draw_ruler(self):
        """Draw time ruler"""
        # Draw ruler background
        Color(0.2, 0.2, 0.2, 1)
        Rectangle(
            pos=(self.x, self.y + self.height - 20),
            size=(self.width, 20)
        )
        
        # Calculate tick marks
        if self.duration <= 0:
            return
        
        pixels_per_second = self.width / self.duration
        
        # Major ticks every 10 seconds
        for t in range(0, int(self.duration) + 1, 10):
            x = self.x + (t * pixels_per_second)
            
            # Tick mark
            Color(0.5, 0.5, 0.5, 1)
            Line(points=[x, self.y + self.height - 20, x, self.y + self.height], width=1)
            
            # Time label
            # (would need Label widget for actual text)
    
    def _draw_clip(self, clip: dict):
        """Draw individual clip"""
        if self.duration <= 0:
            return
        
        pixels_per_second = self.width / self.duration
        
        start_x = self.x + (clip['start'] * pixels_per_second)
        end_x = self.x + (clip['end'] * pixels_per_second)
        
        # Clip background
        Color(0.3, 0.5, 0.8, 1)
        Rectangle(
            pos=(start_x, self.y + 30),
            size=(end_x - start_x, self.height - 60)
        )
        
        # Clip border
        Color(0.5, 0.7, 1, 1)
        Line(
            rectangle=(start_x, self.y + 30, end_x - start_x, self.height - 60),
            width=1
        )
    
    def _draw_playhead(self, *args):
        """Draw playhead line"""
        if self.duration <= 0:
            return
        
        pixels_per_second = self.width / self.duration
        x = self.x + (self.current_time * pixels_per_second)
        
        # Playhead line
        Color(1, 0.3, 0.3, 1)
        Line(points=[x, self.y, x, self.y + self.height], width=2)
        
        # Playhead handle
        Color(1, 0.3, 0.3, 1)
        Rectangle(
            pos=(x - 6, self.y + self.height - 10),
            size=(12, 10)
        )
    
    def on_touch_down(self, touch):
        """Handle touch down"""
        if self.collide_point(*touch.pos):
            time = self.seek_to(touch.pos[0] - self.x)
            self.update_playhead(time)
            return True
        return super().on_touch_down(touch)
    
    def on_touch_move(self, touch):
        """Handle touch move"""
        if self.collide_point(*touch.pos):
            time = self.seek_to(touch.pos[0] - self.x)
            self.update_playhead(time)
            return True
        return super().on_touch_move(touch)
