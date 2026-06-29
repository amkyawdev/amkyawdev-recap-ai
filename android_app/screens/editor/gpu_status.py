"""
GPU Status Panel
Display GPU rendering status
"""
from kivy.lang import Builder
from kivymd.uix.card import MDCard
from kivy.properties import ObjectProperty

Builder.load_string("""
<GPUStatusPanel>:
    orientation: 'vertical'
    spacing: dp(8)
    padding: dp(8)
    
    MDLabel:
        text: "GPU Status"
        font_style: 'Caption'
        halign: 'center'
    
    # GPU Name
    MDLabel:
        id: gpu_name
        text: "Loading..."
        font_style: 'Body2'
        halign: 'center'
    
    # GPU Memory
    MDBoxLayout:
        size_hint_y: None
        height: dp(30)
        spacing: dp(4)
        halign: 'center'
        
        MDProgressBar:
            id: memory_bar
            value: 0
            size_hint_x: 0.8
        
        MDLabel:
            id: memory_text
            text: "0%"
            font_size: '10sp'
            size_hint_x: 0.2
    
    # GPU Utilization
    MDBoxLayout:
        size_hint_y: None
        height: dp(30)
        spacing: dp(4)
        halign: 'center'
        
        MDProgressBar:
            id: util_bar
            value: 0
            size_hint_x: 0.8
        
        MDLabel:
            id: util_text
            text: "0%"
            font_size: '10sp'
            size_hint_x: 0.2
    
    # Temperature
    MDLabel:
        id: temperature
        text: "0°C"
        font_style: 'Caption'
        halign: 'center'
        theme_text_color: 'Secondary'
    
    # Render Queue
    MDLabel:
        text: "Queue: 0"
        font_style: 'Caption'
        halign: 'center'
""")


class GPUStatusPanel(MDCard):
    """GPU status display panel"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._update_timer = None
        self._poll_status()
    
    def _poll_status(self):
        """Poll GPU status periodically"""
        import threading
        import time
        
        def poll():
            while True:
                self._update_status()
                time.sleep(5)  # Update every 5 seconds
        
        thread = threading.Thread(target=poll, daemon=True)
        thread.start()
    
    def _update_status(self):
        """Update GPU status display"""
        try:
            from main import RecapAIApp
            app = RecapAIApp.get_running_instance()
            
            if app and app.gpu_available:
                status = app.get_api_client().get_gpu_status()
                
                if status.get('available') and status.get('devices'):
                    device = status['devices'][0]
                    
                    # Update UI
                    self.ids.gpu_name.text = device.get('name', 'GPU')[:20]
                    
                    # Memory
                    mem_used = device.get('memory_used_gb', 0)
                    mem_total = device.get('memory_total_gb', 1)
                    mem_percent = (mem_used / mem_total * 100) if mem_total > 0 else 0
                    self.ids.memory_bar.value = mem_percent
                    self.ids.memory_text.text = f"{mem_percent:.0f}%"
                    
                    # Utilization
                    util = device.get('utilization_percent', 0)
                    self.ids.util_bar.value = util
                    self.ids.util_text.text = f"{util:.0f}%"
                    
                    # Temperature
                    temp = device.get('temperature_celsius', 0)
                    self.ids.temperature.text = f"{temp}°C"
        except:
            self.ids.gpu_name.text = "CPU Mode"
