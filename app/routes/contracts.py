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
    from ..models.physical_person import PhysicalPerson
    from ..models.legal_entity import LegalEntity
    if request.method == 'POST':
        try:
            number = request.form['number']
            if not validate_contract_number(number):
                raise ValueError("Номер договора должен быть в формате 08-0/XXXXX, где XXXXX - число")
            selected_work_type_ids = request.form.getlist('work_description')
            if not selected_work_type_ids:
                raise ValueError("Не выбрано ни одного типа работ")
            work_types = WorkType.query.filter(WorkType.id.in_(selected_work_type_ids)).all()
            if not work_types:
                raise ValueError("Выбранные типы работ не найдены в базе данных")
            total_price = sum(work_type.price for work_type in work_types)
            subject_type = request.form.get('subject_type')
            subject_id = request.form.get('subject_id')
            if not subject_type or not subject_id:
                raise ValueError("Не выбран субъект договора")
            contract = Contract(
                number=number,
                contract_date=datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date(),
                price=total_price,
                address=request.form['address']
            )
            if subject_type == 'physical':
                contract.physical_person_id = subject_id
            elif subject_type == 'legal':
                contract.legal_entity_id = subject_id
            else:
                raise ValueError("Неверный тип субъекта")
            contract.work_types = work_types
            db.session.add(contract)
            db.session.commit()
            return redirect(url_for('contracts.list_contracts'))
        except ValueError as e:
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', ''),
                'contract_date': request.form.get('contract_date', date.today().strftime('%Y-%m-%d')),
                'address': request.form.get('address', ''),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', '')
            }
            return render_template('contracts/create.html', error=str(e), 
                                 work_types=work_types, form_data=form_data)
        except IntegrityError:
            db.session.rollback()
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', ''),
                'contract_date': request.form.get('contract_date', date.today().strftime('%Y-%m-%d')),
                'address': request.form.get('address', ''),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', '')
            }
            return render_template('contracts/create.html', error="Номер договора уже существует", 
                                 work_types=work_types, form_data=form_data)
    work_types = WorkType.query.all()
    contracts = Contract.query.all()
    default_number = '08-0/30000'
    max_suffix = 0
    for contract in contracts:
        if contract.number.startswith('08-0/'):
            try:
                suffix = int(contract.number.split('/')[-1])
                if suffix > max_suffix:
                    max_suffix = suffix
            except ValueError:
                continue
    if max_suffix > 0:
        default_number = f'08-0/{max_suffix + 1}'
    form_data = {
        'number': default_number,
        'contract_date': date.today().strftime('%Y-%m-%d'),
        'address': '',
        'selected_work_types': [],
        'subject_type': '',
        'subject_id': '',
        'subject_name': ''
    }
    return render_template('contracts/create.html', work_types=work_types, form_data=form_data)

@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit_contract(id):
    from ..models.contracts import Contract
    from ..models.work_types import WorkType
    from ..models.physical_person import PhysicalPerson
    from ..models.legal_entity import LegalEntity
    contract = Contract.query.get_or_404(id)
    if request.method == 'POST':
        try:
            number = request.form['number']
            if not validate_contract_number(number):
                raise ValueError("Номер договора должен быть в формате 08-0/XXXXX, где XXXXX - число")
            selected_work_type_ids = request.form.getlist('work_description')
            if not selected_work_type_ids:
                raise ValueError("Не выбрано ни одного типа работ")
            work_types = WorkType.query.filter(WorkType.id.in_(selected_work_type_ids)).all()
            if not work_types:
                raise ValueError("Выбранные типы работ не найдены в базе данных")
            subject_type = request.form.get('subject_type')
            subject_id = request.form.get('subject_id')
            if not subject_type or not subject_id:
                raise ValueError("Не выбран субъект договора")
            contract.number = number
            contract.contract_date = datetime.strptime(request.form['contract_date'], '%Y-%m-%d').date()
            contract.price = sum(work_type.price for work_type in work_types)
            contract.address = request.form['address']
            contract.physical_person_id = None
            contract.legal_entity_id = None
            if subject_type == 'physical':
                contract.physical_person_id = subject_id
            elif subject_type == 'legal':
                contract.legal_entity_id = subject_id
            else:
                raise ValueError("Неверный тип субъекта")
            contract.work_types = work_types
            db.session.commit()
            return redirect(url_for('contracts.contract_detail', id=contract.id))
        except ValueError as e:
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', contract.number),
                'contract_date': request.form.get('contract_date', contract.contract_date.strftime('%Y-%m-%d')),
                'address': request.form.get('address', contract.address),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', '')
            }
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, 
                                 error=str(e), work_types=work_types, form_data=form_data)
        except IntegrityError:
            db.session.rollback()
            work_types = WorkType.query.all()
            form_data = {
                'number': request.form.get('number', contract.number),
                'contract_date': request.form.get('contract_date', contract.contract_date.strftime('%Y-%m-%d')),
                'address': request.form.get('address', contract.address),
                'selected_work_types': selected_work_type_ids,
                'subject_type': request.form.get('subject_type', ''),
                'subject_id': request.form.get('subject_id', ''),
                'subject_name': request.form.get('subject_name', '')
            }
            return render_template('contracts/detail.html', contract=contract, edit_mode=True, 
                                 error="Номер договора уже существует", work_types=work_types, form_data=form_data)
    work_types = WorkType.query.all()
    form_data = {
        'number': contract.number,
        'contract_date': contract.contract_date.strftime('%Y-%m-%d'),
        'address': contract.address,
        'selected_work_types': [str(work_type.id) for work_type in contract.work_types],
        'subject_type': 'physical' if contract.physical_person_id else 'legal' if contract.legal_entity_id else '',
        'subject_id': contract.physical_person_id or contract.legal_entity_id or '',
        'subject_name': contract.get_subject()
    }
    return render_template('contracts/detail.html', contract=contract, edit_mode=True, work_types=work_types, form_data=form_data)

@bp.route('/<int:id>/delete', methods=['POST'])
def delete_contract(id):
    from ..models.contracts import Contract
    contract = Contract.query.get_or_404(id)
    try:
        db.session.delete(contract)
        db.session.commit()
        return redirect(url_for('contracts.list_contracts'))
    except Exception as e:
        db.session.rollback()
        return render_template('contracts/detail.html', contract=contract, edit_mode=False, 
                             error=f"Ошибка удаления договора: {str(e)}")