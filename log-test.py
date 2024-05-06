"""
program.py
This script will keep adding logs to our logger file.
"""

import logging
import time
import os
# create logger with log app
real_path = os.path.realpath(__file__)
dir_path = os.path.dirname(real_path)
LOGFILE = f"{dir_path}/test.log"
logger = logging.getLogger('log_app')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOGFILE)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

#infinite while loop printing to our log file.
i = 0
crq = 'CRQ-1111111'
while True:
    print(crq)
    if(crq == 'CRQ-2222222'):
        crq = 'CRQ-1111111'
    else:
        crq = 'CRQ-2222222'
    logger.info(crq+"  : log message num: " + str(i))
    i += 1
    time.sleep(1)
