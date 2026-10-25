"""Factoría de aplicación y configuración de DataConnect."""
import hmac
import os
import secrets
from datetime import timedelta
from pathlib import Path

from flask import Flask, render_template, request, session
from werkzeug.security import generate_password_hash

from .storage import CATEGORIES, ContactStore, StorageError


def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DEMO_MODE=os.getenv("DATACONNECT_DEMO", "1") == "1",
        SECRET_KEY=os.getenv("DATACONNECT_SECRET_KEY"),
        ADMIN_USERNAME=os.getenv("DATACONNECT_USERNAME"),
        ADMIN_PASSWORD=os.getenv("DATACONNECT_PASSWORD"),
        DATA_FILE=os.getenv("DATACONNECT_DATA_FILE"),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("DATACONNECT_HTTPS", "0") == "1",
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        MAX_CONTENT_LENGTH=64 * 1024,
    )
    if config:
        app.config.update(config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    if app.config["DEMO_MODE"]:
        app.config["ADMIN_USERNAME"] = "demo"
        app.config["ADMIN_PASSWORD"] = "dataconnect-demo"
        if not app.config["SECRET_KEY"]:
            secret_file = Path(app.instance_path) / ".secret-key"
            if not secret_file.exists():
                secret_file.write_text(secrets.token_hex(32), encoding="utf-8")
            app.config["SECRET_KEY"] = secret_file.read_text(encoding="utf-8")
    else:
        if len(app.config["SECRET_KEY"] or "") < 24:
            raise ValueError("Configurá DATACONNECT_SECRET_KEY con al menos 24 caracteres.")
        if not app.config["ADMIN_USERNAME"] or len(app.config["ADMIN_PASSWORD"] or "") < 12:
            raise ValueError("Configurá un usuario y una contraseña privada de al menos 12 caracteres.")
    app.config["PASSWORD_HASH"] = generate_password_hash(app.config.pop("ADMIN_PASSWORD"))
    filename = app.config["DATA_FILE"] or Path(app.instance_path) / "contactos.xlsx"
    store = ContactStore(filename)
    if app.config["DEMO_MODE"]:
        store.seed_demo()
    app.extensions["contacts"] = store

    @app.before_request
    def csrf_protection():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_urlsafe(32)
        if request.method == "POST":
            submitted = request.form.get("csrf_token", "")
            if not submitted.isascii() or not hmac.compare_digest(submitted, session["csrf_token"]):
                return render_template("error.html", code=400, title="El formulario venció",
                                       message="Volvé a abrir la página e intentá de nuevo."), 400

    @app.after_request
    def response_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; font-src 'self'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'; object-src 'none'"
        )
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        return response

    @app.context_processor
    def template_context():
        return {"csrf_token": session.get("csrf_token", ""), "categories": CATEGORIES,
                "demo_mode": app.config["DEMO_MODE"], "signed_in": session.get("authenticated", False)}

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("error.html", code=404, title="No encontramos este contacto",
                               message="Puede haber sido eliminado. Volvé al directorio para continuar."), 404

    @app.errorhandler(StorageError)
    def storage_error(error):
        app.logger.error("El almacenamiento de contactos no está disponible: %s", type(error).__name__)
        return render_template("error.html", code=503, title="No pudimos abrir el directorio",
                               message="Cerrá el archivo Excel si está abierto e intentá de nuevo. Tus datos no se han reemplazado."), 503

    @app.errorhandler(413)
    def too_large(_error):
        return render_template("error.html", code=413, title="El formulario es demasiado grande",
                               message="Revisá la extensión de los campos e intentá de nuevo."), 413

    from .routes import bp
    app.register_blueprint(bp)
    return app
