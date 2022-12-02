import re
import calendar

from datetime import datetime, date, timedelta

from flask import Flask, request, make_response
from flask_migrate import Migrate

from database import db
from models import Contestant, Type, Gender, University_Career

app = Flask(__name__)

# configuration our db
USER_DB = 'postgres'
PASS_DB = 'admin'
URL_DB = 'localhost'
NAME_DB = 'uvgdb'
FULL_URL_DB = f'postgresql://{USER_DB}:{PASS_DB}@{URL_DB}/{NAME_DB}'

# configuration our app
app.config['SQLALCHEMY_DATABASE_URI'] = FULL_URL_DB
app.config['SQLALCHEMY_TRACK_MODIFICATION'] = False

# inicialization of the object db from sqlachemy
db.init_app(app)

# configuration flask-migrate
migrate = Migrate()

# we initialize the object to be able to execute the migrations to the database
migrate.init_app(app, db)


def validate_id_card(id_card):
    is_valid = None
    card_rules = re.compile('^A[1-9]{1}5[1-9]{2}.*[1,3,9]')
    is_valid = card_rules.match(id_card)
    return is_valid


# method to calculate the constant age
def of_legal_age(birthdate):
    if type(birthdate) == str:
        birthdate = datetime.strptime(birthdate, '%Y-%m-%d')
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age


def participation_date(id_card, types_id):

    last_char = id_card[-1]
    today = date.today()
    # type id 2 is poetry epica
    if last_char == '3' and types_id == 2:
        # funcion de calendar que resive el a;o i mes y devuelve los dias
        last_day = today.replace(day=calendar.monthrange(today.year, today.month)[1])
        # week day regresa el nuemero de del dia que va de 0-6
        while today.weekday() == 5 or today.weekday() == 6:
            last_day -= timedelta(1)
        today = last_day
    # type poetry 3 dramatica
    elif last_char == '1' and types_id == 3:
        days = 0
        while days < 6:
            if today.weekday() == 4:
                today += timedelta(2)
            else:
                today += timedelta(1)
            days += 1
    # anyway
    else:
        while today.weekday() != 4:
            today += timedelta(1)

    return today


def validate_data(data):
    is_valid = True
    if not 'university_careers_id' in data:
        is_valid = False
    if not 'id_card' in data:
        is_valid = False
    if not 'name' in data:
        is_valid = False
    if not 'address' in data:
        is_valid = False
    if not 'phone' in data:
        is_valid = False
    if not 'birthdate' in data:
        is_valid = False
    if not 'genders_id' in data:
        is_valid = False
    return is_valid


def registrations():
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            valid = validate_data(data)
            if not valid:
                return make_response("sorry, you need to fill in all the fields in order to register.",
                                     400)
            card = validate_id_card(data['id_card'])
            if card is None:
                return make_response("sorry your card is invalid")
            age = of_legal_age(data['birthdate'])
            if age < 18:
                return make_response("sorry, you do not meet the required age to participate.", 400)
            else:
                participation = participation_date(data['id_card'], data['types_id'])
                new_registration = Contestant(id_card=data['id_card'], name=data['name'], address=data['address'],
                                              phone=data['phone'],
                                              birthdate=data['birthdate'], genders_id=data['genders_id'],
                                              types_id=data['types_id'],
                                              university_careers_id=data['university_careers_id'],
                                              participation_date=participation)
                db.session.add(new_registration)
                db.session.commit()
                return make_response(
                    f"Congratulations {new_registration.name} your participation date will be {participation}.")
        else:
            return {"error": "The request payload is not in Json format"}

# arguments in the url
def registration_list():
    if request.method == 'GET':
        args = request.args
        result = {}
        query = []
        career = args.get('career', default=None)
        # age = args.get('age', default=None)
        types = args.get('types', default=None)
        date = args.get('date', default=None)

        if None not in (career, types, date):
            query = Contestant.query.filter_by(university_careers_id=career, types_id=types,
                                               participation_date=date).all()
        elif None not in (career, types):
            query = Contestant.query.filter_by(university_careers_id=career, types_id=types).all()
        elif None not in (career, date):
            query = Contestant.query.filter_by(university_careers_id=career, participation_date=date).all()
        elif None not in (types, career):
            query = Contestant.query.filter_by(types_id=types, university_careers_id=career).all()
        elif None not in (types, date):
            query = Contestant.query.filter_by(types_id=types, participation_date=date).all()
        elif career is not None:
            query = Contestant.query.filter_by(university_careers_id=career).all()
        elif types is not None:
            query = Contestant.query.filter_by(types_id=types).all()
        elif date is not None:
            query = Contestant.query.filter_by(participation_date=date).all()
        else:
            query = Contestant.query.all()
        result = [
            {
                "id_card": q.id_card,
                "name": q.name,
                "address": q.address,
                "phone": q.phone,
                "birthdate": q.birthdate,
                "age": of_legal_age(q.birthdate),
                "types_id": {
                    "id": q.types_id,
                    "name": q.type.name
                },
                "gender": {
                    "id": q.genders_id,
                    "name": q.genders.name
                },
                "university_career": {
                    "id": q.university_careers_id,
                    "name": q.university_career.name
                },
                "inscription_date": q.inscription_date,
                "participation_date": q.participation_date

            }
            for q in query
        ]
        return {"Count": len(result), "results": result}


# Routes of my endpoints
app.add_url_rule('/registration', 'registration', registrations, methods=['POST'])
app.add_url_rule('/registers', 'registers', registration_list, methods=['GET'])
