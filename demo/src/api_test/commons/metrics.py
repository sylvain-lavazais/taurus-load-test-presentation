import gc
import platform

from prometheus_client import REGISTRY, Counter, Gauge, Histogram, core

from .gc_profiler import GcProfiler, set_function_on_map_gauge


class Metrics:
    def burninate_gc_collector(self):
        """ clean the Garbage Collector """
        for callback in gc.callbacks[:]:
            if callback.__qualname__.startswith('GCCollector.'):
                gc.callbacks.remove(callback)

        for name, collector in list(REGISTRY._names_to_collectors.items()):
            if name.startswith('python_gc_') or name.startswith('python_info'):
                try:
                    REGISTRY.unregister(collector)
                except KeyError:  # probably gone already
                    pass

    def __init__(self):
        self.burninate_gc_collector()
        profiler = GcProfiler()
        gc.callbacks.append(profiler.callback)

        # Setup metrics
        # Python info
        self._set_python_informations()

        # GC
        self._set_a_new_basic_gauge(
                'python_gc_enabled',
                'Whether the garbage collector is enabled.',
                'isEnabled',
                gc.isenabled,
        )
        self._set_a_new_basic_gauge(
                'python_gc_debug',
                'The debug flags currently set on the Python GC.',
                'debug',
                gc.get_debug,
        )
        self._set_a_new_multilabel_gauge(
                'python_gc_count',
                'Count of objects tracked by the Python garbage collector, by generation.',
                gc.get_count,
                (0, 1, 2),
        )
        self._set_a_new_multilabel_gauge(
                'python_gc_threshold',
                'GC thresholds by generation',
                gc.get_threshold,
                (0, 1, 2),
        )
        self._set_a_new_multilabel_gauge(
                'python_gc_uncollectables',
                'Number of uncollectable objects by generation',
                lambda: [x['python_gc_uncollectables'] for x in gc.get_stats()],
                (0, 1, 2),
        )
        self._set_a_new_multilabel_gauge(
                'python_gc_collections_total',
                'Number of GC collections that occurred by generation',
                lambda: [x['python_gc_collections_total'] for x in gc.get_stats()],
                (0, 1, 2),
        )
        self._set_a_new_multilabel_gauge(
                'python_gc_collected_total',
                'Number of garbage collected objects by generation',
                lambda: [x['python_gc_collected_total'] for x in gc.get_stats()],
                (0, 1, 2),
        )

        # Falcon
        self._set_http_total_request()
        self._set_request_latency_historygram()

    def _set_request_latency_historygram(self):
        self.request_historygram = Histogram(
                'request_latency_seconds',
                'Histogram of request latency',
                ['method', 'path', 'status'],
                registry=core.REGISTRY,
        )

    def _set_http_total_request(self):
        self.requests = Counter(
                'http_total_request',
                'Counter of total HTTP requests',
                ['method', 'path', 'status'],
                registry=core.REGISTRY,
        )

    def _set_a_new_basic_gauge(self, name: str, documentation: str, value: str, function: any):
        basic_gauge = Gauge(
                name,
                documentation,
                ['generation'],
                _labelvalues=[value],
                registry=core.REGISTRY,
                multiprocess_mode='livesum',

        )
        basic_gauge.set_function(function)

    def _set_a_new_multilabel_gauge(self, name: str, documentation: str, function: any,
                                    label_values: tuple):
        multilabel_gauge = Gauge(
                name,
                documentation,
                ['generation'],
                registry=core.REGISTRY,
                multiprocess_mode='livesum',
        )
        set_function_on_map_gauge(multilabel_gauge, label_values, function)

    def _set_python_informations(self):
        major, minor, patchlevel = platform.python_version_tuple()
        python_info = Gauge(
                "python_info",
                "Python platform information",
                ["version", "implementation", "major", "minor", "patchlevel"],
                registry=core.REGISTRY,
                multiprocess_mode='livesum',
        )
        python_info.labels(
                version=platform.python_version(),
                implementation=platform.python_implementation(),
                major=major,
                minor=minor,
                patchlevel=patchlevel,
        )
