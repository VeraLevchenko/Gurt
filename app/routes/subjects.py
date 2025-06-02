from flask import Blueprint, render_template, request, jsonify, redirect, url_for, make_response
from .. import db
from ..models.physical_person import PhysicalPerson
from ..models.legal_entity import LegalEntity
from sqlalchemy.exc import IntegrityError

bp = Blueprint('subjects', __name__, url_prefix='/subjects')

@bp.route('/physical_persons')
def physical_persons():
    physical_persons = PhysicalPerson.query.all()
    response = make_response(render_template('subjects/physical_persons_list.html', physical_persons=physical_persons))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@bp.route('/legal_entities')
def legal_entities():
    legal_entities = LegalEntity.query.all()
    response = make_response(render_template('subjects/legal_entities_list.html', legal_entities=legal_entities))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@bp.route('/select/<string:subject_type>', methods=['GET'])
def select_subject(subject_type):
    query = request.args.get('q', '')
    new_subject_id = request.args.get('new_subject_id')
    if subject_type == 'physical':
        subjects = PhysicalPerson.query.filter(
            PhysicalPerson.full_name.ilike(f'%{query}%') |
            PhysicalPerson.passport.ilike(f'%{query}%')
        ).all()
        response = make_response(render_template('subjects/select.html', subjects=subjects, subject_type='physical', query=query, new_subject_id=new_subject_id))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    elif subject_type == 'legal':
        subjects = LegalEntity.query.filter(
            LegalEntity.name.ilike(f'%{query}%') |
            LegalEntity.inn.ilike(f'%{query}%')
        ).all()
        response = make_response(render_template('subjects/select.html', subjects=subjects, subject_type='legal', query=query, new_subject_id=new_subject_id))
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        return response
    return jsonify({'error': 'Неверный тип субъекта'}), 400

@bp.route('/create/<string:subject_type>', methods=['GET', 'POST'])
def create_subject(subject_type):
    redirect_param = request.args.get('redirect')
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
            if redirect_param == 'list' and not request.headers.get('X-Requested-With'):
                return redirect(url_for('subjects.physical_persons' if subject_type == 'physical' else 'subjects.legal_entities'))
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
            response = make_response(render_template('subjects/select.html', subjects=subjects, subject_type=subject_type, query=query, new_subject_id=subject.id))
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response
        except IntegrityError as e:
            db.session.rollback()
            error = "Такое лицо уже существует (проверьте паспорт или ИНН)"
            if request.headers.get('X-Requested-With'):
                return jsonify({'error': error}), 400
            response = make_response(render_template(f'subjects/create_{subject_type}.html', error=error, form_data=request.form.to_dict()))
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With'):
                return jsonify({'error': str(e)}), 400
            response = make_response(render_template(f'subjects/create_{subject_type}.html', error=str(e), form_data=request.form.to_dict()))
            response.headers['Content-Type'] = 'text/html; charset=utf-8'
            return response
    response = make_response(render_template(f'subjects/create_{subject_type}.html', form_data={}))
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response