"""
Recap AI - Android MainActivity
"""
from jnius import autoclass
from kivy.app import App
from kivy.utils import platform

# Android-specific imports
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

    # Request permissions
    def request_android_permissions():
        request_permissions([
            Permission.INTERNET,
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.CAMERA,
            Permission.RECORD_AUDIO,
        ])

    request_android_permissions()

    # Get external storage path
    ExStorage = primary_external_storage_path()


class RecapAIActivity(App):
    """Main Android Activity"""

    def on_start(self):
        """App started"""
        super().on_start()
        if platform == 'android':
            self.setup_android()

    def setup_android(self):
        """Android-specific setup"""
        # Keep screen on during editing
        activity = autoclass('org.kivy.android.PythonActivity').mActivity
        activity.getWindow().addFlags(autoclass('android.view.WindowManager').LayoutParams.FLAG_KEEP_SCREEN_ON)

    def get_external_storage(self):
        """Get external storage path"""
        if platform == 'android':
            return primary_external_storage_path()
        return '/storage/emulated/0'


if __name__ == '__main__':
    RecapAIActivity().run()
