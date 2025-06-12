"""
Создаёт и настраивает Flask-приложение.

• Загружает конфигурацию из app.config.Config + instance/config.py (если есть).  
• Инициализирует SQLAlchemy и Alembic-Migrate.  
• Регистрирует блюпринты.  
• Создаёт каталог instance/uploads и прописывает его в UPLOAD_FOLDER.
"""
from __future__ import annotations

import os
import logging
from datetime import date

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# -----------------------------------------------------------------------------
db = SQLAlchemy()
migrate = Migrate()
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

# -----------------------------------------------------------------------------
def create_app() -> Flask:
    # instance_relative_config=True ― Flask ищет instance/ рядом с app/
    app = Flask(__name__, instance_relative_config=True)

    # базовая конфигурация из класса Config
    app.config.from_object("app.config.Config")
    # при наличии instance/config.py он перезапишет нужные значения
    app.config.from_pyfile("config.py", silent=True)

    # глобальные мелкие настройки
    app.config.setdefault("JSON_AS_ASCII", False)
    app.config.setdefault("DEFAULT_CHARSET", "utf-8")

    # -----------------------------------------------------------------
    # Папка для загрузок: instance/uploads
    # -----------------------------------------------------------------
    uploads_dir = os.path.join(app.instance_path, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    app.config.setdefault("UPLOAD_FOLDER", uploads_dir)

    # -----------------------------------------------------------------
    # Инициализация расширений
    # -----------------------------------------------------------------
    db.init_app(app)
    migrate.init_app(app, db)

    # -----------------------------------------------------------------
    # Регистрация блюпринтов
    # -----------------------------------------------------------------
    from app.routes import main, contracts, subjects

    app.register_blueprint(main.bp)
    app.register_blueprint(contracts.bp)
    app.register_blueprint(subjects.bp)

    # -----------------------------------------------------------------
    # Пользовательские фильтры и контекст
    # -----------------------------------------------------------------
    @app.template_filter("date_format")
    def date_format(value):
        if isinstance(value, date):
            return value.strftime("%Y-%m-%d")
        return value

    @app.context_processor
    def utility_processor():
        return {"today": date.today}

    return app
