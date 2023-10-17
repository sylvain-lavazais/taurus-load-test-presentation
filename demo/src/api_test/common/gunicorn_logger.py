import datetime

from gunicorn import glogging

glogging.CONFIG_DEFAULTS["formatters"]["generic"]["datefmt"] = "%Y-%m-%dT%H:%M:%S.%f %Z"


class Logger(glogging.Logger):
    def __init__(self, cfg):
        self.syslog_fmt = "%(message)s"
        self.datefmt = r"%Y-%m-%dT%H:%M:%S.%f %Z"
        super().__init__(cfg)

    def now(self):
        """ return date in ISO date Format """
        return datetime.datetime.now().isoformat()
