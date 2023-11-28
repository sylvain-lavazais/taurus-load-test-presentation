from functools import wraps

import structlog
from decohints import decohints


@decohints
def logit(method):
    """ log input/output of methods"""

    @wraps(method)
    def logged(*args, **kw):
        log = structlog.get_logger()
        func_name = method.__name__
        args_repr = [repr(a) for a in args]
        kwargs_repr = [f"{k}={v!r}" for k, v in kw.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        log.debug(f'{func_name} start')
        log.debug(f'with args {signature}')
        result = method(*args, **kw)
        log.debug(f'{func_name} end')
        log.debug(f'with result {result}')
        return result

    return logged
