import logging

import sentry_sdk
from scrapy.exceptions import NotConfigured
from scrapy.utils.project import get_project_settings
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

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
