from flask import Blueprint, render_template, request, redirect, url_for
from .. import db
from ..models.contracts import Contract
from ..models.work_types import WorkType
from datetime import datetime

bp = Blueprint('contracts', __name__, url_prefix='/contracts')

@bp.route('/')
def list_contracts():
    contracts = Contract.query.all()
    return render_template('contracts/list.html', contracts=contracts)

@bp.route('/<int:id>')
def contract_detail(id):
    contract = Contract.query.get_or_404(id)
    return render_template('contracts/detail.html', contract=contract, edit_mode=False)

@bp.route('/create', methods=['GET', 'POST'])
def create_contract():
    if request.method == 'POST':
        try:
            # Получаем список выбранных чекбоксов
            selected_work_types = request.form.getlist('work_description')
            if not selected_work_types:
                raise ValueError("Не выбрано ни одного типа работ")
            # Получаем объекты WorkType для выбранных названий
            work_types = WorkType.query.filter(WorkType.name.in_(selected_work_types)).all()
            # Вычисляем сумму цен
            total_price = sum(work_type.price for work_type in work_types)
            contract = Contract(
                number=request.form['number'],
                contract_date=datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date(),
                subject=request.form['subject'],
                price=total_price,
                address=request.form['address']
            )
            contract.work_types = work_types  # Связываем выбранные виды работ
            db.session.add(contract)
            db.session.commit()
            return redirect(url_for('contracts.list_contracts'))
        except ValueError as e:
            work_types = WorkType.query.all()
            return render_template('contracts/create.html', error="Ошибка в данных формы: " + str(e), work_types=work_types)
        except db.IntegrityError:
            db.session.rollback()
            work_types = WorkType.query.all()
            return render_template('contracts/create.html', error="Номер договора уже существует", work_types=work_types)
    work_types = WorkType.query.all()
    return render_template('contracts/create.html', work_types=work_types)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_contract(id):
    contract = Contract.query.get_or_404(id)
    if request.method == 'POST':
        try:
            selected_work_types = request.form.getlist('work_description')
            if not selected_work_types:
                raise ValueError("Не выбрано ни одного типа работ")
            work_types = WorkType.query.filter(WorkType.name.in_(selected_work_types)).all()
            contract.number = request.form['number']
            contract.contract_date = datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date()
            contract.subject = request.form['subject']
            contract.price = sum(work_type.price for work_type in work_types)
            contract.address = request.form['address']
            contract.work_types = work_types  # Обновляем виды работ
            db.session.commit()
            return redirect(url_for('contracts.contract_detail', id=contract.id))
        except ValueError as e:
            work_types = WorkType.query.all()
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, error="Ошибка в данных формы: " + str(e), work_types=work_types)
        except db.IntegrityError:
            db.session.rollback()
            work_types = WorkType.query.all()
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, error="Номер договора уже существует", work_types=work_types)
    work_types = WorkType.query.all()
    return render_template('contracts/detail.html', contract=contract, edit_mode=True, work_types=work_types)