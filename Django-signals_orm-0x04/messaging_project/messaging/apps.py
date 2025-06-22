from django.apps import AppConfig


class ModelsConfig(AppConfig):
    name = 'Django-Chat.Models'

    def ready(self):
        import Django-Chat.Models.signals
