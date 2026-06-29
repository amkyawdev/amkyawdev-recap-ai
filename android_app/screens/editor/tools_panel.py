"""
Tools Panel
Video editing tools toolbar
"""
from kivy.lang import Builder
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.button import MDIconButton

Builder.load_string("""
<ToolsPanel>:
    size_hint_y: None
    height: dp(80)
    
    canvas.before:
        Color:
            rgba: 0.15, 0.15, 0.15, 1
        Rectangle:
            pos: self.pos
            size: self.size
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(8)
        padding: dp(8)
        halign: 'center'
        valign: 'middle'
        
        ToolButton:
            icon: 'content-cut'
            tooltip: 'Trim'
            on_release: root.trim_selected()
        
        ToolButton:
            icon: 'content-copy'
            tooltip: 'Split'
            on_release: root.split_clip()
        
        ToolButton:
            icon: 'content-paste'
            tooltip: 'Paste'
            on_release: root.paste()
        
        ToolButton:
            icon: 'delete'
            tooltip: 'Delete'
            on_release: root.delete_selected()
        
        ToolButton:
            icon: 'undo'
            tooltip: 'Undo'
            on_release: root.undo()
        
        ToolButton:
            icon: 'redo'
            tooltip: 'Redo'
            on_release: root.redo()
        
        Widget:
            size_hint_x: 0.2
        
        ToolButton:
            icon: 'crop-rotate'
            tooltip: 'Transform'
            on_release: root.show_transform()
        
        ToolButton:
            icon: 'palette'
            tooltip: 'Color'
            on_release: root.show_color_adjust()
        
        ToolButton:
            icon: 'auto-fix'
            tooltip: 'Effects'
            on_release: root.show_effects_browser()
        
        ToolButton:
            icon: 'format-letter-case'
            tooltip: 'Text'
            on_release: root.show_text_overlay()


<ToolButton@MDIconButton>:
    icon: ''
    user_font_size: '24sp'
    theme_icon_color: 'Custom'
    icon_color: 1, 1, 1, 0.8
""")


class ToolsPanel:
    """Tools panel widget"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def trim_selected(self):
        """Trim selected clip"""
        pass
    
    def split_clip(self):
        """Split clip at playhead"""
        pass
    
    def paste(self):
        """Paste from clipboard"""
        pass
    
    def delete_selected(self):
        """Delete selected clip"""
        pass
    
    def undo(self):
        """Undo last action"""
        pass
    
    def redo(self):
        """Redo last undone action"""
        pass
    
    def show_transform(self):
        """Show transform options"""
        pass
    
    def show_color_adjust(self):
        """Show color adjustment"""
        pass
    
    def show_effects_browser(self):
        """Show effects browser"""
        pass
    
    def show_text_overlay(self):
        """Show text overlay options"""
        pass
