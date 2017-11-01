import os
basedir=os.path.abspath(os.path.dirname(__file__))
class Config:
	SECRET_KEY=os.environ.get('SECRET_KEY') or 'hard to guess string'
	SQLALCHEMY_COMMIT_ON_TEARDOWN=True
	FLASKY_MAIL_SUBJECT_PREFIX='[Flasky]'
	FLASKY_MAIL_SENDER='632131247@qq.com'
	FLASKY_ADMIN=os.environ.get('FLASKY_ADMIN')
	FLASK_POSTS_PER_PAGE=10
	FLASK_COMMETS_PER_PAGE=10
	SQLALCHEMY_RECORD_QUERIES=True
	FLASKY_SLOW_DB_QUERY_TIME=0.5
	FLASKY_FOLLOWERS_PER_PAGE=20
	@staticmethod
	def init_app(app):
		pass
class DevelopmentConfig(Config):
	DEBUG=True
	MAIL_SERVER='smtp.qq.com'
	MAIL_PORT=25
	MAIL_USE_TLS=True
	MAIL_USERNAME='632131247@qq.com'
	MAIL_PASSWORD='118899Shi'
	SQLALCHEMY_DATABASE_URI=os.environ.get('DEV_DATABASE_URI') or \
		'sqlite:///'+os.path.join(basedir,'data-dev.sqlite')
class TestingConfig(Config):
	TESTING=True
	WTF_CSRF_ENABLED=False
	SQLALCHEMY_DATABASE_URI=os.environ.get('TEST_DATABASE_URL')or \
		'sqlite:///'+os.path.join(basedir,'data-test.sqlite')
class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or \
		'sqlite:///'+os.path.join(basedir,'data.sqlite')
	@classmethod
	def init_app(cls,app):
		Config.init_app(app)
		import logging
		from logging.handlers import SMTPHandler
		credentials=None
		secure=None
		if getattr(cls,'MAIL_USENAME',None) is not None :
			credentials=(cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
			if getattr(cls,'MAIL_USE_TLS',None):
				secure=()
		mail_handler=SMTPHandler(
			mailhost=(cls.MAIL_SERVER,cls.MAIL_PORT),
			fromaddr=cls.FLASKY_MAIL_SENDER,
			toaddrs=[cls.FLASKY_ADMIN],
			subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + 'Application Error',
			credentials=credentials,
			secure=secure)
		mail_handler.setLevel(logging.ERROR)
		app.logger.addHandler(mail_handler)
class HerokuConfig(ProductionConfig):
	@classmethod
	def init_app():
		ProductionConfig.init_app(app)
		import logging
		from logging import StreamHandler
		file_handler=StreamHandler()
		file_handler.setLevel(logging.WARNING)
		app.logger.addHandler(file_handler)

config={'development':DevelopmentConfig,'testing':TestingConfig,'production':ProductionConfig,
'default':DevelopmentConfig,'heroku': HerokuConfig}

