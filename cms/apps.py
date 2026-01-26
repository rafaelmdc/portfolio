from django.apps import AppConfig


class CmsConfig(AppConfig):
    name = 'cms'

    def ready(self):
        # import signal handlers
        try:
            from . import signals  # noqa: F401
        except Exception:
            # avoid breaking startup if signals fail; errors will surface in admin actions
            pass
