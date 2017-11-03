import os
import datetime
import logging
import logging.config


# BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_logger(path, logger_name='root', ):
    """"""
    LOG_DIR = os.path.join(path, "logs")
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # 创建路径

    LOG_FILE = datetime.datetime.now().strftime("%Y-%m-%d") + ".log"

    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "simple": {
                'format': '%(asctime)s [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s',
                'datefmt': '%H:%M:%S'
            },
            'standard': {
                'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
            },
        },
        
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "simple",
                "stream": "ext://sys.stdout"
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "standard",
                "filename": os.path.join(LOG_DIR, LOG_FILE),
                'mode': 'w+',
                "maxBytes": 1024*1024*5,  # 5 MB
                "backupCount": 20,
                "encoding": "utf8"
            },
        },

        "loggers": {
            "console": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False
            }
        },

        "root": {
            'handlers': ['file', 'console'],
            'level': "DEBUG",
        }
    }

    logging.config.dictConfig(LOGGING)
    
    if logger_name == 'console':
        logger = logging.getLogger('console')
    else:
        logger = logging.getLogger(__name__)
        
    return logger


if __name__ == '__main__':
    a = os.path.dirname(os.path.abspath(__file__))
    print(a)