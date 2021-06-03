import logging
from datetime import datetime

import sentry_sdk
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured
from scrapy.spiders import Spider
from scrapy.utils.project import get_project_settings
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy.orm import sessionmaker
from telegram import Bot, ParseMode

from fareview.models import User, db_connect
from fareview.utils.bot import create_price_alert_summary

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
    Send price alerts via Telegram to users
    """

    def __init__(self) -> None:
        telegram_api_token = settings.get('TELEGRAM_API_TOKEN')
        if not telegram_api_token:
            raise NotConfigured('TELEGRAM_API_TOKEN is not configured.')

        engine = db_connect()

        self.session = sessionmaker(bind=engine)

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
        """
        Sends a Telegram message to users according to their `alert_settings`
        E.g. of `alert_settings`: ['asahi', 'tiger']
        """
        assert spider.name, 'Please provide a name for your spider according to the platform name that it\'s targetting.'

        logger.info(f'Spider closed: {spider.name}')
        logger.info('Sending price alerts users via Telegram.')

        session = self.session()
        try:
            users = session.query(User).filter(
                User.membership_end_date >= datetime.utcnow(),
                User.alert_settings is not None,
            ).all()

        except Exception as error:
            logger.exception(error)
            raise

        finally:
            session.close()

        summary = create_price_alert_summary(platform=spider.name)

        for user in users:
            for brand in user.alert_settings:
                text_array = [
                    f'Hey {user.first_name}! 🤩 Here are your price alerts for *{brand.title()}*.',
                    f'Below are the cheapest items I have found on *{spider.name.title()}*.👇\n'
                ]

                for info in summary[brand]:
                    volume = info['volume']
                    price = info['price']
                    url = info['url']

                    text_array.append(f'• _{volume}mL x 24_┃*${price:.2f}*┃[👉 Link]({url})')

                text = '\n'.join(text_array)
                self.bot.send_message(
                    chat_id=user.telegram_chat_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
