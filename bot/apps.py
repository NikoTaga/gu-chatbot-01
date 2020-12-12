import logging
from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
from pathlib import Path
from dotenv import load_dotenv

from patterns.singleton import Singleton


logger = logging.getLogger('root')


class SingletonAPS(metaclass=Singleton):
    """Класс для хранения и передачи единственного инстанса планировщика.

     Оборачивает инициализированный инстанс BackgroungScheduler в форму Singleton."""

    _sched: BackgroundScheduler = None

    def set_aps(self, aps: BackgroundScheduler) -> None:
        self._sched = aps

    @property
    def get_aps(self) -> BackgroundScheduler:
        return self._sched


class BotConfig(AppConfig):
    name = 'bot'

    def ready(self) -> None:
        logger.info('Executing botconfig ready()')
        project_folder = Path(__file__).parent.parent.absolute()
        load_dotenv(project_folder.parent.joinpath('.env'))
        logger.info('Environment ready')
        scheduler = BackgroundScheduler()
        SingletonAPS().set_aps(scheduler)
        if not scheduler.running:
            scheduler.start()
            logger.info('Scheduler started')
