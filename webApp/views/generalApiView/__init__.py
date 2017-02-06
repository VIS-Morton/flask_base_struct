from webApp import app
from webApp.celeryBackgound import trigger_celery


@app.route("/cellery_test")
def test():
    trigger_celery.apply_async(("test", 1), countdown=5)
    return "hello world, celery trigger success"