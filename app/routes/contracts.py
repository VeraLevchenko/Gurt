from __future__ import annotations

import os
from datetime import date

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
    send_from_directory,
)

from ..models.contracts import Contract
from ..models.work_types import WorkType
from ..services.contract_service import ContractService

bp = Blueprint("contracts", __name__, url_prefix="/contracts")

# ---------------------------------------------------------------------
#                              Л И С Т
# ---------------------------------------------------------------------
@bp.route("/")
def list_contracts():
    return render_template("contracts/list.html", contracts=ContractService.list())

# ---------------------------------------------------------------------
#                          С К А Ч И В А Н И Е
# ---------------------------------------------------------------------
@bp.route("/download_excel")
def download_excel():
    return ContractService.export_excel()


@bp.route("/files/<path:filename>")
def download_file(filename: str):
    """
    Скачивание одного вложения.
    • filename приходит из БД, поэтому может содержать 'uploads/...'.
      Берём basename, чтобы не удвоить путь и обезопаситься.
    """
    upload_dir = current_app.config.get("UPLOAD_FOLDER", "uploads")
    safe_name = os.path.basename(filename)
    return send_from_directory(upload_dir, safe_name, as_attachment=True)

# ---------------------------------------------------------------------
#                           C R U D  (договоры)
# ---------------------------------------------------------------------
@bp.route("/<int:id>")
def contract_detail(id):
    contract = Contract.query.get_or_404(id)
    return render_template("contracts/detail.html", contract=contract, edit_mode=False)


@bp.route("/create", methods=["GET", "POST"])
def create_contract():
    if request.method == "POST":
        try:
            ContractService.create_from_request(request.form, request.files)
            return redirect(url_for("contracts.list_contracts"))
        except ValueError as err:
            return render_template(
                "contracts/create.html",
                error=str(err),
                work_types=WorkType.query.all(),
                form_data=request.form,
            )

    return render_template(
        "contracts/create.html",
        work_types=WorkType.query.all(),
        form_data={"number": _suggest_number(), "contract_date": date.today()},
    )


@bp.route("/<int:id>/edit", methods=["GET", "POST"])
def edit_contract(id):
    contract = Contract.query.get_or_404(id)

    if request.method == "POST":
        try:
            ContractService.update_from_request(contract, request.form, request.files)
            return redirect(url_for("contracts.contract_detail", id=id))
        except ValueError as err:
            return render_template(
                "contracts/detail.html",
                contract=contract,
                edit_mode=True,
                error=str(err),
                work_types=WorkType.query.all(),
                form_data=request.form,
            )

    form_data = {
        "number": contract.number,
        "contract_date": contract.contract_date.strftime("%Y-%m-%d"),
        "address": contract.address,
        "object_name": contract.object_name,
        "selected_work_types": [str(w.id) for w in contract.work_types],
        "subject_type": "physical" if contract.physical_person_id else "legal",
        "subject_id": contract.physical_person_id or contract.legal_entity_id,
        "subject_name": contract.get_subject(),
    }
    return render_template(
        "contracts/detail.html",
        contract=contract,
        edit_mode=True,
        work_types=WorkType.query.all(),
        form_data=form_data,
    )


@bp.route("/<int:id>/delete", methods=["POST"])
def delete_contract(id):
    ContractService.delete(Contract.query.get_or_404(id))
    return redirect(url_for("contracts.list_contracts"))

# ---------------------------------------------------------------------
#                      В С П О М О Г А Т Е Л Ь Н О Е
# ---------------------------------------------------------------------
def _suggest_number() -> str:
    max_suffix = 29999
    for c in Contract.query.filter(Contract.number.like("08-0/%")).all():
        try:
            max_suffix = max(max_suffix, int(c.number.split("/")[-1]))
        except ValueError:
            continue
    return f"08-0/{max_suffix + 1}"
