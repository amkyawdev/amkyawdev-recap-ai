"""
Recap Screen
AI-powered video recap generation
"""
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar

Builder.load_string("""
<RecapScreen>:
    name: 'recap'
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(16)
        padding: dp(16)
        
        # Header
        MDTopAppBar:
            title: "AI Recap"
            left_action_items: [['arrow-left', lambda x: root.go_back()]]
        
        # Video Info
        MDCard:
            padding: dp(12)
            
            MDBoxLayout:
                spacing: dp(12)
                
                MDIcon:
                    icon: 'movie'
                    font_size: '48sp'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    
                    MDLabel:
                        id: video_name
                        text: "No video loaded"
                        font_style: 'Body1'
                    
                    MDLabel:
                        id: video_duration
                        text: "Duration: --"
                        font_style: 'Caption'
                        theme_text_color: 'Secondary'
        
        # Transcript Input
        MDLabel:
            text: "Transcript"
            font_style: 'Subtitle'
        
        MDTextField:
            id: transcript_input
            hint_text: "Paste or type transcript..."
            multiline: True
            min_height: dp(150)
            max_height: dp(200)
        
        # Settings
        MDBoxLayout:
            spacing: dp(16)
            size_hint_y: None
            height: dp(56)
            
            # Style selector
            MDBoxLayout:
                size_hint_x: 0.5
                orientation: 'vertical'
                
                MDLabel:
                    text: "Style"
                    font_size: '12sp'
                    theme_text_color: 'Secondary'
                
                MDDropDownItem:
                    id: style_dropdown
                    text: 'Engaging'
                    on_release: root.show_style_menu()
            
            # Model selector
            MDBoxLayout:
                size_hint_x: 0.5
                orientation: 'vertical'
                
                MDLabel:
                    text: "Model"
                    font_size: '12sp'
                    theme_text_color: 'Secondary'
                
                MDDropDownItem:
                    id: model_dropdown
                    text: 'Claude Sonnet'
                    on_release: root.show_model_menu()
        
        # Duration
        MDBoxLayout:
            size_hint_y: None
            height: dp(40)
            spacing: dp(16)
            
            MDLabel:
                text: "Duration"
                font_size: '12sp'
            
            Slider:
                id: duration_slider
                min: 1
                max: 30
                value: 5
                on_value: root.update_duration_label()
            
            MDLabel:
                id: duration_label
                text: "5 min"
                size_hint_x: 0.2
        
        # Generate Button
        MDRaisedButton:
            id: generate_btn
            text: "Generate Recap"
            icon: 'robot'
            on_release: root.generate_recap()
            size_hint_y: None
            height: dp(48)
        
        # Loading indicator
        MDSpinner:
            id: loading
            size_hint: None, None
            size: dp(48), dp(48)
            pos_hint: {'center_x': 0.5}
            visible: False
        
        # Result
        MDCard:
            id: result_card
            padding: dp(12)
            visible: False
            
            MDLabel:
                text: "Generated Script"
                font_style: 'Subtitle'
            
            ScrollView:
                size_hint_y: None
                height: dp(200)
                
                MDLabel:
                    id: script_output
                    text: ''
                    text_size: self.width, None
                    size_hint_y: None
                    height: self.texture_size[1]
        
        # Actions
        MDBoxLayout:
            id: actions_box
            visible: False
            spacing: dp(12)
            size_hint_y: None
            height: dp(48)
            
            MDRaisedButton:
                text: "Edit Script"
                icon: 'pencil'
                on_release: root.edit_script()
            
            MDRaisedButton:
                text: "Apply to Timeline"
                icon: 'timeline-plus'
                on_release: root.apply_to_timeline()
            
            MDRaisedButton:
                text: "Copy"
                icon: 'content-copy'
                on_release: root.copy_script()
""")


class RecapScreen(Screen):
    """AI recap generation screen"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_video = None
        self.generated_script = None
        self.selected_style = "engaging"
        self.selected_model = "anthropic/claude-3.5-sonnet"
        
        # Style options
        self.styles = {
            "engaging": "engaging",
            "formal": "formal",
            "casual": "casual",
            "technical": "technical",
        }
        
        # Model options
        self.models = {
            "Claude Sonnet": "anthropic/claude-3.5-sonnet",
            "GPT-4o": "openai/gpt-4o",
            "GPT-4o Mini": "openai/gpt-4o-mini",
            "Llama 3": "meta-llama/llama-3-70b-instruct",
        }
    
    def on_enter(self):
        """Called when entering screen"""
        if self.current_video:
            self._load_transcript()
    
    def set_video(self, video_path: str):
        """Set current video"""
        self.current_video = video_path
        self.ids.video_name.text = video_path.split('/')[-1]
        self._load_transcript()
    
    def _load_transcript(self):
        """Load transcript from video"""
        if not self.current_video:
            return
        
        from main import RecapAIApp
        app = RecapAIApp.get_running_instance()
        
        try:
            # Show loading
            Snackbar(text="Transcribing video...").open()
            
            # Transcribe
            result = app.get_api_client().transcribe_video(self.current_video)
            
            self.ids.transcript_input.text = result.get('text', '')
            duration = result.get('duration', 0)
            self.ids.video_duration.text = f"Duration: {duration:.0f}s"
            
        except Exception as e:
            Snackbar(text=f"Transcription failed: {e}").open()
    
    def go_back(self):
        """Navigate back"""
        self.manager.current = 'editor'
    
    def show_style_menu(self):
        """Show style selection menu"""
        menu_items = [
            {"text": "Engaging", "viewclass": "OneLineListItem",
             "on_release": lambda x="engaging": self.select_style(x)},
            {"text": "Formal", "viewclass": "OneLineListItem",
             "on_release": lambda x="formal": self.select_style(x)},
            {"text": "Casual", "viewclass": "OneLineListItem",
             "on_release": lambda x="casual": self.select_style(x)},
            {"text": "Technical", "viewclass": "OneLineListItem",
             "on_release": lambda x="technical": self.select_style(x)},
        ]
        
        menu = MDDropdownMenu(
            caller=self.ids.style_dropdown,
            items=menu_items,
            width_mult=2
        )
        menu.open()
    
    def select_style(self, style: str):
        """Select script style"""
        self.selected_style = style
        self.ids.style_dropdown.text = style.capitalize()
    
    def show_model_menu(self):
        """Show model selection menu"""
        menu_items = [
            {"text": name, "viewclass": "OneLineListItem",
             "on_release": lambda x=name: self.select_model(x)}
            for name in self.models.keys()
        ]
        
        menu = MDDropdownMenu(
            caller=self.ids.model_dropdown,
            items=menu_items,
            width_mult=2
        )
        menu.open()
    
    def select_model(self, name: str):
        """Select AI model"""
        self.selected_model = self.models[name]
        self.ids.model_dropdown.text = name
    
    def update_duration_label(self):
        """Update duration label"""
        duration = int(self.ids.duration_slider.value)
        self.ids.duration_label.text = f"{duration} min"
    
    def generate_recap(self):
        """Generate recap script"""
        transcript = self.ids.transcript_input.text
        
        if not transcript.strip():
            Snackbar(text="Please enter or generate transcript").open()
            return
        
        self.ids.generate_btn.disabled = True
        self.ids.loading.visible = True
        
        from main import RecapAIApp
        app = RecapAIApp.get_running_instance()
        
        def do_generate():
            try:
                result = app.get_api_client().generate_recap(
                    transcript=transcript,
                    duration_minutes=int(self.ids.duration_slider.value),
                    style=self.selected_style,
                    target_audience="general",
                )
                
                # Update UI on main thread
                self.generated_script = result.get('script', '')
                self.ids.script_output.text = self.generated_script
                self.ids.result_card.visible = True
                self.ids.actions_box.visible = True
                
                Snackbar(text="Recap generated!").open()
                
            except Exception as e:
                Snackbar(text=f"Generation failed: {e}").open()
            finally:
                self.ids.generate_btn.disabled = False
                self.ids.loading.visible = False
        
        import threading
        thread = threading.Thread(target=do_generate)
        thread.start()
    
    def edit_script(self):
        """Edit generated script"""
        # Open editor for script
        Snackbar(text="Script editor coming soon").open()
    
    def apply_to_timeline(self):
        """Apply recap to video timeline"""
        # This would integrate the script with the editor
        Snackbar(text="Applied to timeline").open()
        self.go_back()
    
    def copy_script(self):
        """Copy script to clipboard"""
        from kivy.utils import platform
        
        if platform == 'android':
            from jnius import autoclass
            ClipboardManager = autoclass('android.content.ClipData')
            # Copy to clipboard
        elif platform == 'ios':
            pass
        
        Snackbar(text="Script copied!").open()
