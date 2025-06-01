from flask import Blueprint, render_template, request, jsonify
from .. import db
from ..models.physical_person import PhysicalPerson
from ..models.legal_entity import LegalEntity
from sqlalchemy.exc import IntegrityError

bp = Blueprint('subjects', __name__, url_prefix='/subjects')

@bp.route('/select/<string:subject_type>', methods=['GET'])
def select_subject(subject_type):
    query = request.args.get('q', '')
    new_subject_id = request.args.get('new_subject_id')
    if subject_type == 'physical':
        subjects = PhysicalPerson.query.filter(
            PhysicalPerson.full_name.ilike(f'%{query}%') |
            PhysicalPerson.passport.ilike(f'%{query}%')
        ).all()
        return render_template('subjects/select.html', subjects=subjects, subject_type='physical', query=query, new_subject_id=new_subject_id)
    elif subject_type == 'legal':
        subjects = LegalEntity.query.filter(
            LegalEntity.name.ilike(f'%{query}%') |
            LegalEntity.inn.ilike(f'%{query}%')
        ).all()
        return render_template('subjects/select.html', subjects=subjects, subject_type='legal', query=query, new_subject_id=new_subject_id)
    return jsonify({'error': 'Неверный тип субъекта'}), 400

@bp.route('/create/<string:subject_type>', methods=['GET', 'POST'])
def create_subject(subject_type):
    if request.method == 'POST':
        try:
            if subject_type == 'physical':
                subject = PhysicalPerson(
                    full_name=request.form['full_name'],
                    passport=request.form['passport'],
                    address=request.form['address'],
                    phone=request.form['phone'],
                    email=request.form.get('email', None)
                )
            elif subject_type == 'legal':
                subject = LegalEntity(
                    name=request.form['name'],
                    inn=request.form['inn'],
                    legal_address=request.form['legal_address'],
                    director_full_name=request.form['director_full_name'],
                    payment_details=request.form['payment_details'],
                    phone=request.form['phone'],
                    email=request.form.get('email', None)
                )
            else:
                return jsonify({'error': 'Неверный тип субъекта'}), 400
            db.session.add(subject)
            db.session.commit()
            query = request.form.get('q', '')
            if subject_type == 'physical':
                subjects = PhysicalPerson.query.filter(
                    PhysicalPerson.full_name.ilike(f'%{query}%') |
                    PhysicalPerson.passport.ilike(f'%{query}%')
                ).all()
            else:
                subjects = LegalEntity.query.filter(
                    LegalEntity.name.ilike(f'%{query}%') |
                    LegalEntity.inn.ilike(f'%{query}%')
                ).all()
            # Возвращаем HTML для модального окна с новым субъектом
            return render_template('subjects/select.html', subjects=subjects, subject_type=subject_type, query=query, new_subject_id=subject.id)
        except IntegrityError as e:
            db.session.rollback()
            error = "Такое лицо уже существует (проверьте паспорт или ИНН)"
            return jsonify({'error': error}), 400 if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render_template(f'subjects/create_{subject_type}.html', error=error, form_data=request.form.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400 if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else render_template(f'subjects/create_{subject_type}.html', error=str(e), form_data=request.form.to_dict())
    return render_template(f'subjects/create_{subject_type}.html', form_data={})