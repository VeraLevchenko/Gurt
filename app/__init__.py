from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import date

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')  # Загрузка конфигурации из config.py
    db.init_app(app)
    migrate.init_app(app, db)
    
    from app.routes import main, contracts
    app.register_blueprint(main.bp)
    app.register_blueprint(contracts.bp)
    
    # Добавление пользовательского фильтра для формата даты
    @app.template_filter('date_format')
    def date_format(value):
        if isinstance(value, date):
            return value.strftime('%Y-%m-%d')
        return value
    
    return app