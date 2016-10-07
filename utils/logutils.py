import config
import pprint
import threading
import traceback
import sys
import os
import psutil

def logToFile(src, exitAfter=True):
    with open('log', 'w', encoding='UTF-8') as f:
        f.write(src)
    if exitAfter:
        exit()

def log(*args):
    if config.log:
        print(threading.current_thread().name)
        for arg in args:
            pprint.pprint(arg)

def format_exception(e):
	exception_list = traceback.format_stack()
	exception_list = exception_list[:-2]
	exception_list.extend(traceback.format_tb(sys.exc_info()[2]))
	exception_list.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

	exception_str = "Traceback (most recent call last):\n"
	exception_str += "".join(exception_list)
	# Removing the last \n
	exception_str = exception_str[:-1]
	return exception_str

def getMemory():
    process = psutil.Process(os.getpid())
    return process.memory_percent()