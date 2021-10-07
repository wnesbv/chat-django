

from django.conf import settings

CONFIG_DEFAULTS = {
    "PAGINATE_BY": 20,
    "USE_JSONFIELD": True,
    "SOFT_DELETE": False,
    "NUM_TO_FETCH": 10,
}

def get_config():
    user_config = getattr(settings, "DJANGO_NOTIFICATIONS_CONFIG", {})

    config = CONFIG_DEFAULTS.copy()
    config.update(user_config)

    return config

TIME_FORMAT = '%H:%M:%S'
DATETIME_FORMAT="%Y-%m-%d%H:%M:%S"
