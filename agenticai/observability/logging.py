import logging
import os
import sys
def configure():
    handler = logging.StreamHandler(sys.stdout)
    fmt = '{"time":"%(asctime)s","level":"%(levelname)s","module":"%(module)s","message":"%(message)s"}'
    handler.setFormatter(logging.Formatter(fmt))
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(os.getenv("LOG_LEVEL", "INFO"))
