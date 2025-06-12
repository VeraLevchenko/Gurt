from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    jsonify,
    make_response,
)

from ..services.subject_service import SubjectService

bp = Blueprint("subjects", __name__, url_prefix="/subjects")


# ---------- Списки --------------------------------------------------------

@bp.route("/physical_persons")
def physical_persons():
    return _html("subjects/physical_persons_list.html",
                 physical_persons=SubjectService.list_physical())


@bp.route("/legal_entities")
def legal_entities():
    return _html("subjects/legal_entities_list.html",
                 legal_entities=SubjectService.list_legal())


# ---------- Поиск / Выбор -------------------------------------------------

@bp.route("/select/<string:subject_type>")
def select_subject(subject_type):
    q = request.args.get("q", "")
    if subject_type == "physical":
        subjects = SubjectService.search_physical(q)
    elif subject_type == "legal":
        subjects = SubjectService.search_legal(q)
    else:
        return jsonify({"error": "Неверный тип субъекта"}), 400
    return _html("subjects/select.html",
                 subjects=subjects,
                 subject_type=subject_type,
                 query=q)


# ---------- Детали / редактирование --------------------------------------

@bp.route("/<string:subject_type>/<int:id>")
def subject_detail(subject_type, id):
    subject = SubjectService.get(subject_type, id)
    return _html("subjects/detail.html",
                 subject=subject,
                 subject_type=subject_type,
                 edit_mode=False)


@bp.route("/<string:subject_type>/<int:id>/edit", methods=["GET", "POST"])
def edit_subject(subject_type, id):
    subject = SubjectService.get(subject_type, id)

    if request.method == "POST":
        try:
            SubjectService.update(subject, request.form)
            return redirect(url_for("subjects.subject_detail",
                                    subject_type=subject_type, id=id))
        except ValueError as err:
            return _html("subjects/detail.html",
                         subject=subject,
                         subject_type=subject_type,
                         edit_mode=True,
                         error=str(err),
                         form_data=request.form)

    # GET
    return _html("subjects/detail.html",
                 subject=subject,
                 subject_type=subject_type,
                 edit_mode=True,
                 form_data=request.form or {})


# ---------- Создание ------------------------------------------------------

@bp.route("/create/<string:subject_type>", methods=["GET", "POST"])
def create_subject(subject_type):
    if request.method == "POST":
        try:
            if subject_type == "physical":
                SubjectService.create_physical(request.form)
            elif subject_type == "legal":
                SubjectService.create_legal(request.form)
            else:
                return jsonify({"error": "Неверный тип субъекта"}), 400
            return redirect(url_for("subjects.physical_persons"
                                    if subject_type == "physical"
                                    else "subjects.legal_entities"))
        except ValueError as err:
            return _html(f"subjects/create_{subject_type}.html",
                         error=str(err),
                         form_data=request.form)

    # GET
    return _html(f"subjects/create_{subject_type}.html", form_data={})


# ---------- Удаление ------------------------------------------------------

@bp.route("/<string:subject_type>/<int:id>/delete", methods=["POST"])
def delete_subject(subject_type, id):
    try:
        SubjectService.delete(subject_type, id)
        return redirect(url_for("subjects.physical_persons"
                                if subject_type == "physical"
                                else "subjects.legal_entities"))
    except ValueError as err:
        subject = SubjectService.get(subject_type, id)
        return _html("subjects/detail.html",
                     subject=subject,
                     subject_type=subject_type,
                     edit_mode=False,
                     error=str(err))


# ---------- Вспомогательная обёртка --------------------------------------

def _html(template, **context):
    """Возвращает make_response с UTF-8, чтобы не дублировать код."""
    resp = make_response(render_template(template, **context))
    resp.headers["Content-Type"] = "text/html; charset=utf-8"
    return resp
