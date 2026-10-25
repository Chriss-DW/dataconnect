"""Rutas de acceso, directorio, contactos y estadísticas."""
from collections import Counter
from datetime import datetime
from functools import wraps
import re
import secrets
import unicodedata
from urllib.parse import urlsplit

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .storage import CATEGORIES

bp = Blueprint("main", __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            return redirect(url_for("main.login", next=request.full_path.rstrip("?")))
        return view(*args, **kwargs)
    return wrapped


def safe_next(value, fallback):
    if value and value.startswith("/") and not value.startswith("//") and "\\" not in value and not any(ord(char) < 32 for char in value):
        parsed = urlsplit(value)
        if not parsed.netloc and not parsed.scheme:
            return value
    return fallback


def contacts_store():
    return current_app.extensions["contacts"]


def get_contact(contact_id):
    contact = contacts_store().get(contact_id)
    if contact is None:
        abort(404)
    return contact


def searchable(value):
    return "".join(char for char in unicodedata.normalize("NFKD", value.casefold()) if not unicodedata.combining(char))


def validate_contact(form):
    values = {field: form.get(field, "").strip() for field in ("full_name", "phone", "email", "address", "category")}
    errors = {}
    if not values["full_name"] or len(values["full_name"]) > 120:
        errors["full_name"] = "Escribí un nombre de entre 1 y 120 caracteres."
    if not re.fullmatch(r"[0-9]{8}", values["phone"]):
        errors["phone"] = "El teléfono debe contener exactamente 8 dígitos."
    if len(values["email"]) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@.]{2,}", values["email"]):
        errors["email"] = "Escribí un correo válido, por ejemplo nombre@empresa.com."
    if len(values["address"]) > 240:
        errors["address"] = "La dirección puede tener hasta 240 caracteres."
    if values["category"] not in CATEGORIES:
        errors["category"] = "Elegí una de las categorías disponibles."
    for field, value in values.items():
        if any(ord(char) < 32 and char not in "\t\n\r" for char in value):
            errors[field] = "El campo contiene caracteres no admitidos. Volvé a escribirlo."
    parts = values["full_name"].split(maxsplit=1)
    record = {"first_name": parts[0] if parts else "", "last_name": parts[1] if len(parts) > 1 else "",
              "phone": values["phone"], "email": values["email"], "address": values["address"], "category": values["category"]}
    return values, record, errors


@bp.app_template_filter("date_label")
def date_label(value):
    return datetime.fromisoformat(value).strftime("%d/%m/%Y") if value else "—"


@bp.route("/")
def home():
    return redirect(url_for("main.contacts" if session.get("authenticated") else "main.login"))


@bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("main.contacts"))
    error = None
    username = request.form.get("username", "").strip()
    if request.method == "POST":
        valid_password = check_password_hash(current_app.config["PASSWORD_HASH"], request.form.get("password", ""))
        if username == current_app.config["ADMIN_USERNAME"] and valid_password:
            session.clear()
            session["authenticated"] = True
            session["csrf_token"] = secrets.token_urlsafe(32)
            session.permanent = True
            return redirect(safe_next(request.args.get("next"), url_for("main.contacts")))
        error = "El usuario o la contraseña no son correctos. Intentá de nuevo."
    return render_template("login.html", error=error, username=username), (422 if error else 200)


@bp.post("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@bp.get("/contactos")
@login_required
def contacts():
    all_contacts = contacts_store().all()
    query = request.args.get("q", "").strip()[:120]
    category = request.args.get("categoria", "")
    favorites_only = request.args.get("favoritos") == "1"
    order = request.args.get("orden", "nombre")
    filtered = all_contacts
    if query:
        needle = searchable(query)
        filtered = [contact for contact in filtered if needle in searchable(" ".join(str(contact[field]) for field in ("full_name", "phone", "email", "address", "category")))]
    if category in CATEGORIES:
        filtered = [contact for contact in filtered if contact["category"] == category]
    else:
        category = ""
    if favorites_only:
        filtered = [contact for contact in filtered if contact["favorite"]]
    filtered = sorted(filtered, key=(lambda c: c["created_at"]) if order == "recientes" else (lambda c: searchable(c["full_name"])), reverse=order == "recientes")
    return render_template("contacts.html", contacts=filtered, total=len(all_contacts), query=query,
                           selected_category=category, order=order, favorites_only=favorites_only)


@bp.route("/contactos/nuevo", methods=["GET", "POST"])
@login_required
def create_contact():
    values, errors = {"category": "Trabajo"}, {}
    if request.method == "POST":
        values, record, errors = validate_contact(request.form)
        if not errors:
            contact_id = contacts_store().create(record)
            flash("Contacto creado. Ya forma parte de tu directorio.", "success")
            return redirect(url_for("main.contact_detail", contact_id=contact_id))
    return render_template("contact_form.html", values=values, errors=errors, editing=False), (422 if errors else 200)


@bp.get("/contactos/<contact_id>")
@login_required
def contact_detail(contact_id):
    return render_template("contact_detail.html", contact=get_contact(contact_id))


@bp.route("/contactos/<contact_id>/editar", methods=["GET", "POST"])
@login_required
def edit_contact(contact_id):
    contact = get_contact(contact_id)
    values, errors = dict(contact), {}
    if request.method == "POST":
        values, record, errors = validate_contact(request.form)
        if not errors:
            if not contacts_store().update(contact_id, record):
                abort(404)
            flash("Los cambios del contacto se guardaron correctamente.", "success")
            return redirect(url_for("main.contact_detail", contact_id=contact_id))
    return render_template("contact_form.html", values=values, errors=errors, editing=True, contact=contact), (422 if errors else 200)


@bp.post("/contactos/<contact_id>/favorito")
@login_required
def favorite(contact_id):
    if not contacts_store().update(contact_id, toggle=True):
        abort(404)
    flash("Favoritos actualizados.", "success")
    return redirect(safe_next(request.form.get("return_to"), url_for("main.contacts")))


@bp.route("/contactos/<contact_id>/eliminar", methods=["GET", "POST"])
@login_required
def delete_contact(contact_id):
    contact = get_contact(contact_id)
    if request.method == "POST":
        if not contacts_store().delete(contact_id):
            abort(404)
        flash("El contacto se eliminó del directorio.", "success")
        return redirect(url_for("main.contacts"))
    return render_template("confirm_delete.html", contact=contact)


@bp.get("/estadisticas")
@login_required
def stats():
    contacts = contacts_store().all()
    counts = Counter(contact["category"] for contact in contacts)
    return render_template("stats.html", total=len(contacts), favorites=sum(contact["favorite"] for contact in contacts),
                           counts=counts, recent=sorted(contacts, key=lambda c: c["created_at"], reverse=True)[:5])
