from flask import current_app

from webApp.extension import celery


@celery.task()
def trigger_celery(*params):
    current_app.logger.info("cellery get params: %s" % str(params))
    return "cellery get params: %s" % str(params)
