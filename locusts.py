import locust
from locust import HttpLocust
from requests import Session

from locustscripts.Tasksets import RDTasksNFR21, STATasksNFR21


def loadInitialData():
    session = Session()
    # load initial testing stuff


locust.events.locust_start_hatching += loadInitialData


class RDLocust(HttpLocust):
    task_set = RDTasksNFR21
    min_wait = 50
    max_wait = 100


class STALocust(HttpLocust):
    task_set = STATasksNFR21
    min_wait = 1
    max_wait = 5
