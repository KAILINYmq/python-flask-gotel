import factory
import logging
import sqlalchemy
from pytest_factoryboy import register

from agile.models import PredIdea

logger = logging.getLogger("test_models")


def test_init_predideas(db, admin_user):
    try:
        PredIdea.init_predideas()
    except sqlalchemy.exc.IntegrityError:
        pass
    assert PredIdea.query.count() > 100
