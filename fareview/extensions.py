import logging

import sentry_sdk
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from telegram import Bot

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

        self.bot = Bot(token=telegram_api_token)

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

        # TODO: Search through the entire user list and send out notifications
        self.bot.send_message(chat_id='', text='')
