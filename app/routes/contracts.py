from flask import Blueprint, render_template, request, redirect, url_for
from .. import db
from ..models.contracts import Contract
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
            contract = Contract(
                number=request.form['number'],
                contract_date=datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date(),
                subject=request.form['subject'],
                price=float(request.form['price']),
                address=request.form['address'],
                work_description=request.form['work_description']
            )
            db.session.add(contract)
            db.session.commit()
            return redirect(url_for('contracts.list_contracts'))
        except ValueError as e:
            return render_template('contracts/create.html', error="Ошибка в данных формы: " + str(e))
        except db.IntegrityError:
            db.session.rollback()
            return render_template('contracts/create.html', error="Номер договора уже существует")
    return render_template('contracts/create.html')

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_contract(id):
    contract = Contract.query.get_or_404(id)
    if request.method == 'POST':
        try:
            contract.number = request.form['number']
            contract.contract_date = datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date()
            contract.subject = request.form['subject']
            contract.price = float(request.form['price'])
            contract.address = request.form['address']
            contract.work_description = request.form['work_description']
            db.session.commit()
            return redirect(url_for('contracts.contract_detail', id=contract.id))
        except ValueError as e:
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, error="Ошибка в данных формы: " + str(e))
        except db.IntegrityError:
            db.session.rollback()
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, error="Номер договора уже существует")
    return render_template('contracts/detail.html', contract=contract, edit_mode=True)