import requests
import logging
from agile.extensions import celery, db
from agile.config import PREDICT_IDEA_API_URL
from agile.models import PredIdea

logger = logging.getLogger("tasks")


@celery.task
def predict_idea_task(idea_no):
    def make_text(title, content):
        return title + "\n" + content.replace('[SEP]', '\n')

    logger.info('incoming predict request:\n')
    logger.info("predict_idea_task")
    obj = PredIdea.where(idea_no=idea_no).first()
    if not obj:
        raise Exception(f"idea{idea_no} not found!")
    text = make_text(obj.title, obj.content)
    rep = requests.post(PREDICT_IDEA_API_URL, json={"text": text}, headers={'Content-Type': 'application/json'})
    if rep.status_code != 200:
        logger.error("Model serving erorr! %s" % text)
        raise Exception("Model serving erorr!")
    obj.ai_prediction = rep.json()
    obj.save()
    db.session.commit()
    return "OK"


@celery.task
def add_task(x, y):
    return x + y
