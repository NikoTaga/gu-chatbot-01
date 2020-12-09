from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler

from patterns.singleton import Singleton


class SingletonAPS(metaclass=Singleton):
    _sched: BackgroundScheduler = None

    def set_aps(self, aps):
        self._sched = aps

    @property
    def get_aps(self):
        return self._sched


class BotConfig(AppConfig):
    name = 'bot'

    def ready(self):
        print('READY')
        scheduler = BackgroundScheduler()
        SingletonAPS().set_aps(scheduler)
        if not scheduler.running:
            scheduler.start()
