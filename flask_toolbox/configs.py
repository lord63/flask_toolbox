import os


class Config:
    SECRET_KEY = '123456790'  # Create dummy secrey key so we can use sessions
    SENTRY_DSN = os.environ.get('FLASK_TOOLBOX_SENTRY_DSN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ROOT = os.path.dirname(os.path.realpath(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(
        os.path.join(ROOT, 'flask_toolbox_dev.db'))


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('FLASK_TOOLBOX_SECRET_KEY')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(
        os.path.join(Config.ROOT, 'flask_toolbox_prod.db'))


class TestConfig(Config):
    DEBUG = True
    TESTING = True
