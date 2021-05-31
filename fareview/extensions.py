import logging

import sentry_sdk
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy.orm import sessionmaker
from telegram import Bot

from fareview.models import User, db_connect

logger = logging.getLogger(__name__)

settings = get_project_settings()


class SentryLogging:
    """
    Send exceptions and errors to Sentry
    """
    @classmethod
    def from_crawler(cls, crawler):
        sentry_enabled = crawler.settings.getbool('SENTRY_ENABLED')
        if not sentry_enabled:
            raise NotConfigured('Sentry extension is disabled.')

        sentry_dsn = crawler.settings.get('SENTRY_DSN', None)
        if sentry_dsn is None:
            raise NotConfigured('Sentry DSN is missing.')

        extension = cls()
        sentry_sdk.init(
            dsn=sentry_dsn,
            traces_sample_rate=1.0,
            environment=settings.get('ENVIRONMENT'),
            integrations=[SqlalchemyIntegration()],
        )

        return extension


class TelegramBot:
    """
    Send price alerts via Telegram notification to users
    WIP
    """

    def __init__(self) -> None:
        telegram_api_token = settings.get('TELEGRAM_API_TOKEN')
        if not telegram_api_token:
            raise NotConfigured('TELEGRAM_API_TOKEN is not configured.')

        engine = db_connect()

        self.session = sessionmaker(bind=engine)

        self.bot = Bot(token=telegram_api_token)

    def _create_notification_payload(self) -> str:
        return ''

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> 'TelegramBot':
        telegram_enabled = crawler.settings.getbool('TELEGRAM_ENABLED')
        if not telegram_enabled:
            raise NotConfigured('Telegram extension is disabled.')

        extension = cls()

        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(extension.spider_closed, signal=signals.spider_closed)

        return extension

    def spider_opened(self, spider: Spider) -> None:
        logger.info(f'Spider opened: {spider.name}')

    def spider_closed(self, spider: Spider) -> None:
        logger.info(f'Spider closed: {spider.name}')

        session = self.session()
        users = session.query(User).filter(User.membership_end_date.between(User.membership_start_date, User.membership_end_date)).all()

        logger.info(f'Sending Telegram notifications to {len(users)} users.')
        session.close()

        for user in users:
            # TODO: Search through the entire user list and send out notifications
            self.bot.send_message(chat_id=user.telegram_chat_id, text='Hi!')
