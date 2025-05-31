from flask import Blueprint, render_template, request, redirect, url_for
from .. import db
from datetime import datetime, date
from sqlalchemy.exc import IntegrityError
import re

bp = Blueprint('contracts', __name__, url_prefix='/contracts')

def validate_contract_number(number):
    """Validate that the contract number matches the format 08-0/XXXXX."""
    return bool(re.match(r'^08-0/\d+$', number))

@bp.route('/')
def list_contracts():
    from ..models.contracts import Contract
    contracts = Contract.query.all()
    return render_template('contracts/list.html', contracts=contracts)

@bp.route('/<int:id>')
def contract_detail(id):
    from ..models.contracts import Contract
    contract = Contract.query.get_or_404(id)
    return render_template('contracts/detail.html', contract=contract, edit_mode=False)

@bp.route('/create', methods=['GET', 'POST'])
def create_contract():
    from ..models.contracts import Contract
    from ..models.work_types import WorkType
    if request.method == 'POST':
        try:
            number = request.form['number']
            if not validate_contract_number(number):
                raise ValueError("Номер договора должен быть в формате 08-0/XXXXX, где XXXXX - число")
            selected_work_type_ids = request.form.getlist('work_description')
            print("Selected work type IDs:", selected_work_type_ids)  # Для отладки
            if not selected_work_type_ids:
                raise ValueError("Не выбрано ни одного типа работ")
            work_types = WorkType.query.filter(WorkType.id.in_(selected_work_type_ids)).all()
            if not work_types:
                raise ValueError("Выбранные типы работ не найдены в базе данных")
            total_price = sum(work_type.price for work_type in work_types)
            contract = Contract(
                number=number,
                contract_date=datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date(),
                subject=request.form['subject'],
                price=total_price,
                address=request.form['address']
            )
            contract.work_types = work_types
            db.session.add(contract)
            db.session.commit()
            return redirect(url_for('contracts.list_contracts'))
        except ValueError as e:
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', ''),
                'contract_date': request.form.get('contract_date', date.today().strftime('%Y-%m-%d')),
                'subject': request.form.get('subject', ''),
                'address': request.form.get('address', ''),
                'selected_work_types': selected_work_type_ids
            }
            print("Form data on error:", form_data)  # Для отладки
            return render_template('contracts/create.html', error=str(e), 
                                 work_types=work_types, form_data=form_data)
        except IntegrityError:
            db.session.rollback()
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', ''),
                'contract_date': request.form.get('contract_date', date.today().strftime('%Y-%m-%d')),
                'subject': request.form.get('subject', ''),
                'address': request.form.get('address', ''),
                'selected_work_types': selected_work_type_ids
            }
            print("Form data on IntegrityError:", form_data)  # Для отладки
            return render_template('contracts/create.html', error="Номер договора уже существует", 
                                 work_types=work_types, form_data=form_data)
    work_types = WorkType.query.all()
    # Get all contracts and find the highest numeric suffix
    contracts = Contract.query.all()
    default_number = '08-0/30000'  # Fallback if no valid contracts exist
    max_suffix = 0
    for contract in contracts:
        if contract.number.startswith('08-0/'):
            try:
                suffix = int(contract.number.split('/')[-1])
                if suffix > max_suffix:
                    max_suffix = suffix
            except ValueError:
                continue  # Skip invalid number formats
    if max_suffix > 0:
        default_number = f'08-0/{max_suffix + 1}'
    form_data = {
        'number': default_number,
        'contract_date': date.today().strftime('%Y-%m-%d'),
        'subject': '',
        'address': '',
        'selected_work_types': []
    }
    return render_template('contracts/create.html', work_types=work_types, form_data=form_data)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_contract(id):
    from ..models.contracts import Contract
    from ..models.work_types import WorkType
    contract = Contract.query.get_or_404(id)
    if request.method == 'POST':
        try:
            number = request.form['number']
            if not validate_contract_number(number):
                raise ValueError("Номер договора должен быть в формате 08-0/XXXXX, где XXXXX - число")
            selected_work_type_ids = request.form.getlist('work_description')
            print("Selected work type IDs (edit):", selected_work_type_ids)  # Для отладки
            if not selected_work_type_ids:
                raise ValueError("Не выбрано ни одного типа работ")
            work_types = WorkType.query.filter(WorkType.id.in_(selected_work_type_ids)).all()
            if not work_types:
                raise ValueError("Выбранные типы работ не найдены в базе данных")
            contract.number = number
            contract.contract_date = datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date()
            contract.subject = request.form['subject']
            contract.price = sum(work_type.price for work_type in work_types)
            contract.address = request.form['address']
            contract.work_types = work_types
            db.session.commit()
            return redirect(url_for('contracts.contract_detail', id=contract.id))
        except ValueError as e:
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', contract.number),
                'contract_date': request.form.get('contract_date', contract.contract_date.strftime('%Y-%m-%d')),
                'subject': request.form.get('subject', contract.subject),
                'address': request.form.get('address', contract.address),
                'selected_work_types': selected_work_type_ids
            }
            print("Form data on error (edit):", form_data)  # Для отладки
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, 
                                 error=str(e), work_types=work_types, form_data=form_data)
        except IntegrityError:
            db.session.rollback()
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', contract.number),
                'contract_date': request.form.get('contract_date', contract.contract_date.strftime('%Y-%m-%d')),
                'subject': request.form.get('subject', contract.subject),
                'address': request.form.get('address', contract.address),
                'selected_work_types': selected_work_type_ids
            }
            print("Form data on IntegrityError (edit):", form_data)  # Для отладки
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, 
                                 error="Номер договора уже существует", work_types=work_types, form_data=form_data)
    work_types = WorkType.query.all()
    form_data = {
        'number': contract.number,
        'contract_date': contract.contract_date.strftime('%Y-%m-%d'),
        'subject': contract.subject,
        'address': contract.address,
        'selected_work_types': [str(work_type.id) for work_type in contract.work_types]
    }
    return render_template('contracts/detail.html', contract=contract, edit_mode=True, work_types=work_types, form_data=form_data)