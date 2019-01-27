import sys
import logging.config

# time compression factor
# if you want to make the simulation
# eg 2 times faster, set TIME_FACTOR=2
# with speed=1.00  it takes ~ 2 minutes to reach 100 robots
# with speed=18.0 it takes ~ 10 sec to reach 100 robots
TIME_FACTOR = 5.

# The simulation will stop when this number
# is blown up
MAX_ROBOTS = 100

# selling price in euros for a foobar item
FOOBAR_PRICE = 1

# buy price for a robot
ROBOT_PRICE_EUROS = 3
ROBOT_PRICE_FOOS = 6

# Max Batch Size for selling Foobars
FOOBAR_BATCH_SIZE = 5

# initial FOOBAR quantity to produce.
# On each session, we are going to make twice
# as much FOOs as BARs
FOOBAR_QUANTITY_FOR_PRODUCTION = 50
FOO_FACTORS = 3  # how many foo per bar we must produce

logging.config.dictConfig(
    {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'stream': sys.stdout,
            },
        },
        'loggers': {
            '': {
                'handlers': ['console'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
)
