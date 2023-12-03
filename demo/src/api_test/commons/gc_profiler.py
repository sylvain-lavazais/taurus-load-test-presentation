import time

from prometheus_client import Gauge, core


class GcProfiler:
    def __init__(self):
        self.collection_total = Gauge('python_gc_collection_process_time_total_s',
                                      'Total process time spent in garbage collection',
                                      ['generation'],
                                      registry=core.REGISTRY)
        self.last_collection_start = None

    def now(self) -> float:
        """ :return Process time for profiling: sum of the kernel and user-space CPU time. """
        return time.process_time()

    def update_metrics(self, interval: float):
        """ update a metrics by interval"""
        self.collection_total.labels(generation=interval).inc()

    def callback(self, phase: str, _):
        if phase == 'start':
            self.last_collection_start = self.now()
        elif phase == 'stop':
            now = self.now()
            self.update_metrics(now - self.last_collection_start)


def set_function_on_map_gauge(gauge: Gauge, label_values: tuple, fn: any):
    for val in label_values:
        def get_item(fnc=fn, v=val):
            return fnc()[v]

        gauge.labels(generation=val).set_function(get_item)
