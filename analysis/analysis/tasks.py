__author__ = 'akhmetov'
from analysis.celery import app

@app.task
def re_statistic():
    """
    method for static
    :return: None
    """
    print('from celery')
    #Todo