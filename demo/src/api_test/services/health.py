import socket
import time
from multiprocessing import Manager
from threading import Thread

import falcon
import psutil
import structlog

MEMORY = 'memory'
CPU = 'cpu'
DNS = 'dns_lookup'
POSTGRES = 'postgres'
POSTGRES_POOL = 'postgres_pool'
OK = 'OK'
KO = 'KO'
STATUS = 'status'


class HealthService(Thread):
    """ Health probe class """

    def __init__(self, dal):
        self._logger = structlog.get_logger()
        Thread.__init__(self)

        manager = Manager()

        self.dal = dal
        # TODO: to set back in dynaconf settings
        # self.cpu_limit = settings.MONITORING_CPU_LIMIT
        # self.memory_limit = settings.MONITORING_MEMORY_LIMIT
        # self.dns_host = settings.MONITORING_DNS_LOOKUP_URL
        # self.postgres_host = settings.POSTGRES_HOST
        # self.postgres_pool_limit = settings.MONITORING_DB_POOL_LIMIT
        # self.postgres_pool_max = settings.POSTGRES_POOL_MAX_SIZE
        self.cpu_limit = 90
        self.memory_limit = 90
        self.dns_host = 'dns.google'
        self.postgres_host = 'localhost'
        self.postgres_pool_limit = 10
        self.postgres_pool_max = 1

        self.readiness_probes = {DNS: self.__check_dns_probe__,
                                 POSTGRES: self.__check_postgres_probe__}

        self.liveness_probes = {
            MEMORY: self.__check_memory_probe__,
            CPU: self.__check_cpu_probe__,
            POSTGRES_POOL: self.__check_postgres_pool_probe
        }

        self.__probes__ = manager.dict()
        self.readiness_checks = manager.dict()
        self.liveness_checks = manager.dict()

    def run(self):
        while True:
            self.__update_probes__()
            time.sleep(10)

    def get_readiness_checks(self):
        """ Returns health readiness checks """
        return self.readiness_checks.copy()

    def get_liveness_checks(self):
        """ Returns health liveness checks """
        return self.liveness_checks.copy()

    def __update_probes__(self):
        self.__set_probes__()
        self.__set_readiness_checks__()
        self.__set_liveness_checks__()

    def __set_probes__(self):
        dns_lookup = None
        try:
            dns_lookup = socket.gethostbyname(self.dns_host)
        except socket.gaierror:
            pass

        self.__probes__[MEMORY] = psutil.virtual_memory().percent
        self.__probes__[CPU] = psutil.cpu_percent()
        self.__probes__[DNS] = OK if dns_lookup is not None else KO
        self.__probes__[POSTGRES] = OK if self.dal.ping_select() else KO
        self.__probes__[POSTGRES_POOL] = self.dal.get_used_connections()

    def __set_readiness_checks__(self):
        check_probes(self.readiness_probes, self.readiness_checks)

    def __set_liveness_checks__(self):
        check_probes(self.liveness_probes, self.liveness_checks)

    def __check_memory_probe__(self):
        if self.__probes__[MEMORY] > self.memory_limit:
            raise HealthProbeError("Used memory above the limit")

    def __check_cpu_probe__(self):
        if self.__probes__[CPU] > self.cpu_limit:
            raise HealthProbeError("Used CPU above the limit")

    def __check_dns_probe__(self):
        if self.__probes__[DNS] == KO:
            raise HealthProbeError("Could not resolve host")

    def __check_postgres_probe__(self):
        if self.__probes__[POSTGRES] == KO:
            raise HealthProbeError("Could not resolve postgres")

    def __check_postgres_pool_probe(self):
        pool_size = self.__probes__[POSTGRES_POOL] * 100
        if pool_size / self.postgres_pool_max > self.postgres_pool_limit:
            raise HealthProbeError("Used database connections above the limit")


class HealthProbeError(Exception):
    """ Health probe error """

    def __init__(self, message):
        Exception.__init__(self)
        self.__message__ = message

    def message(self):
        """ Returns the error message """
        return self.__message__


def check_probes(probes_map, checks_map):
    """ Creates a dict with the probes checks and the http status """

    status = falcon.HTTP_200
    for check, probe_func in probes_map.items():
        try:
            probe_func()
            checks_map[check] = OK
        except HealthProbeError as err:
            status = falcon.HTTP_503
            checks_map[check] = err.message()

    checks_map[STATUS] = status
