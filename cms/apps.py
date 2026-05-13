from django.apps import AppConfig


class CmsConfig(AppConfig):
    name = 'cms'

    def ready(self):
        # import signal handlers
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass
