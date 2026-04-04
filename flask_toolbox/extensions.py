from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


admin = Admin()
db = SQLAlchemy()


class Sentry:
    def init_app(self, app):
        dsn = app.config.get('SENTRY_DSN')
        if dsn:
            sentry_sdk.init(dsn=dsn, integrations=[FlaskIntegration()])


sentry = Sentry()
