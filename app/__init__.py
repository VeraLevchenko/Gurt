from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Импорты маршрутов после инициализации db
    from app.routes import main, contracts, subjects
    app.register_blueprint(main.bp)
    app.register_blueprint(contracts.bp)
    app.register_blueprint(subjects.bp)
    
    # Фильтр для формата даты
    @app.template_filter('date_format')
    def date_format(value):
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        return value
    
    # Контекстный процессор для текущей даты
    @app.context_processor
    def utility_processor():
        def today():
            return date.today()
        return dict(today=today)
    
    return app