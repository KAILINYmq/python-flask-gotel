from flask import Flask
from flask_cors import CORS
from agile import auth, api, commands
from agile.extensions import db, ma, jwt, migrate, celery, cache, apispec
from agile.models import User
from agile.database import BaseModel
from flasgger import Swagger
from agile.commons.audit import AuditTrail

audit = AuditTrail()


def create_app(testing=False, cli=False):
    """Application factory, used to create application
    """
    app = Flask('agile')
    app.config.from_object('agile.config')
    app.config['debug'] = True
    # if testing is True:
    #     app.config['TESTING'] = True
    #     app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
    # app.config['SQLALCHEMY_DATABASE_URI']='postgres://testman:testman@10.86.86.218:54321/postgres'

    if testing or app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        del app.config['SQLALCHEMY_POOL_SIZE']
        del app.config['SQLALCHEMY_POOL_RECYCLE']

    configure_extensions(app, cli)
    register_blueprints(app)
    configure_apispec(app)
    init_celery(app, testing)
    register_shellcontext(app)
    register_commands(app)
    # register for model mixin function
    BaseModel.set_session(db.session)
    if not testing and not cli:
        register_apidoc(app)

    audit.init_app(app)
    return app


def register_apidoc(app):
    app.config['SWAGGER'] = {
        'title': 'Agile Product Innovatin - API',
        'uiversion': 3
    }
    swagger_config = Swagger.DEFAULT_CONFIG
    swagger_config['swagger_ui_bundle_js'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui-bundle.js'
    swagger_config['swagger_ui_standalone_preset_js'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui-standalone-preset.js'
    swagger_config['jquery_js'] = '//unpkg.com/jquery@2.2.4/dist/jquery.min.js'
    swagger_config['swagger_ui_css'] = '//unpkg.com/swagger-ui-dist@3/swagger-ui.css'
    Swagger(app, config=swagger_config)


def configure_extensions(app, cli):
    """configure flask extensions
    """
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    cache.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, origins="*")
    # if cli is True:
    migrate.init_app(app, db)


def register_blueprints(app):
    """register all blueprints for application
    """
    app.register_blueprint(auth.views.blueprint)

    app.register_blueprint(api.views.blueprint)


def init_celery(app=None, testing=False):
    app = app or create_app()
    if testing:
        celery.conf.broker_url = 'sqla+sqlite:///celerydb.sqlite'
        celery.conf.result_backend = 'db+sqlite:///results.sqlite'
    else:
        celery.conf.broker_url = app.config['CELERY_BROKER_URL']
        celery.conf.result_backend = app.config['CELERY_RESULT_BACKEND']
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def register_shellcontext(app):
    """Register shell context objects."""

    def shell_context():
        """Shell context objects."""
        return {
            'db': db,
            'User': User}

    app.shell_context_processor(shell_context)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.test)
    app.cli.add_command(commands.lint)
    app.cli.add_command(commands.clean)
    app.cli.add_command(commands.urls)
    app.cli.add_command(commands.init)
    app.cli.add_command(commands.generate_token)
    app.cli.add_command(commands.add_user_to_role)
    app.cli.add_command(commands.test_permission)


def configure_apispec(app):
    """Configure APISpec for swagger support
    """
    apispec.init_app(app, security=[{"jwt": []}])
    apispec.spec.components.security_scheme(
        "jwt", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    )
    apispec.spec.components.schema(
        "PaginatedResult",
        {
            "properties": {
                "total": {"type": "integer"},
                "pages": {"type": "integer"},
                "next": {"type": "string"},
                "prev": {"type": "string"},
            }
        },
    )
