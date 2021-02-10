import pytest
from agile.app import init_celery
from agile.tasks import predict_idea_task, add_task
from agile.extensions import celery
from agile.models import PredIdea


@pytest.fixture
def celery_app(celery_app, app):
    celery = init_celery(app)
    celery_app.conf = celery.conf
    yield celery_app


@pytest.fixture(scope="session")
def celery_worker_pool():
    return "prefork"


@pytest.fixture
def celery_worker_parameters():
    # type: () -> Mapping[str, Any]
    """Redefine this fixture to change the init parameters of Celery workers.

    This can be used e. g. to define queues the worker will consume tasks from.

    The dict returned by your fixture will then be used
    as parameters when instantiating :class:`~celery.worker.WorkController`.
    """
    return {
        # For some reason this `celery.ping` is not registed IF our own worker is still
        # running. To avoid failing tests in that case, we disable the ping check.
        # see: https://github.com/celery/celery/issues/3642#issuecomment-369057682
        # here is the ping task: `from celery.contrib.testing.tasks import ping`
        "perform_ping_check": False
    }


@pytest.mark.celery(result_backend="redis://")
def test_predidea(celery_app, celery_worker, db):
    """Simply test our dummy task using celery"""

    expected = {
        "HCL00065": {
            "Indicated Action": "Abandon",
            "Advantage": "Abandon",
            "Attention Catching": "Abandon",
            "Distinct Proposition": "Abandon",
            "Need/Desire": "Abandon",
        }
    }
    for idea_no, result in expected.items():
        res = predict_idea_task("HCL00065")  # 奇强亮白去渍洗衣粉
        assert res == "OK"
        obj = PredIdea.where(idea_no=idea_no).first()
        assert obj.ai_prediction is not None
        assert obj.ai_prediction["Indicated Action"] == result["Indicated Action"], 'Indicated Action error'
        assert obj.ai_prediction["Advantage"] == result["Advantage"], 'Advantage error'
        assert obj.ai_prediction["Attention Catching"] == result["Attention Catching"], 'Attention Catching error'
        assert obj.ai_prediction["Distinct Proposition"] == result["Distinct Proposition"], 'Distinct Proposition error'
        assert obj.ai_prediction["Need/Desire"] == result["Need/Desire"], 'Need/Desire error'

    # Reload worker to add test_task to its registry.
    # res=add_task.delay(2,2)
