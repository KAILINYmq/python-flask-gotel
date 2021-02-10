from datetime import datetime

from agile.extensions import db
from agile.models.concept_file import ConceptProgramme


def query_max_number_by_date_and_type(date):
    result = db.session.query(db.func.max(ConceptProgramme.number)).filter(
        db.cast(ConceptProgramme.created_at, db.DATE) == db.cast(date, db.DATE)
    ).first()
    max_length = 0 if result[0] is None else result[0]
    return max_length + 1


def generate_id_by_number_and_type(category, number):
    current_date = datetime.utcnow().strftime('%m%d')
    return category + current_date + "{0:03d}".format(number)
