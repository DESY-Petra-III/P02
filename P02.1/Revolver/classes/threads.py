'''
Created on Oct 11, 2013

@author: Martin Domaracky
'''

import logging
import threading
from time import sleep
def frange(start, end=None, inc=None):
    "A range function, that does accept float increments..."

    if end == None:
        end = start + 0.0
        start = 0.0
    else: start += 0.0 # force it to be a float

    if inc == None:
        inc = 1.0

    count = int((end - start) / inc)
    if start + count * inc != end:
        # need to adjust the count.
        # AFAIKT, it always comes up one short.
        count += 1

    L = [None,] * count
    for i in xrange(count):
        L[i] = start + i * inc

    return L

THREAD_KEEP_ALIVE = True
THREAD_TIMEOUT = 0
runningThreads = set()
widgetThreads = {}

def thread_sleep(time, sleepFlags=[True]):
    """
    Threaded sleep loop, which could be terminated be setting sleepFlags[0] flag to zero
    @type sleepFlags: Dictionary
    """
    if time <= 1: sleep(time)
    else:
        time_range = frange(1, time, 1)
        for i in time_range:
            if THREAD_KEEP_ALIVE and sleepFlags[0]:
                sleep(1)
            else:
                break

def stop_all_threads():
    """
    Stop all running threads
    """
    logging.warn("Stoping all running registered threads")
    global THREAD_KEEP_ALIVE
    global runningThreads
    global widgetThreads
    THREAD_KEEP_ALIVE = False
    actualRunningThreads = threading.enumerate()
    
    if actualRunningThreads:
        for thread in runningThreads:
            if thread.isAlive() and not thread.isDaemon():
                try:
                    thread.join()
                except RuntimeError:
                    pass
    runningThreads = set()
    THREAD_KEEP_ALIVE = True
 
def stop_widget_threads(widgetId):
    """
    Force threads from specified widget to be stopped
    @type widgetId: int
    """
    global runningThreads
    if not widgetThreads.has_key(widgetId): return
    threadsToStop = widgetThreads[widgetId]
    
    for thread in threadsToStop:
            if thread.isAlive() and not thread.isDaemon():
                try:
                    thread._Thread__stop()
                except:
                    pass
        
def add_thread(thread, widgetId=None):
    """
    Add thread into spool.
    Link thread to widget if widgetId was specified.
    @type widgetId: int
    """
    runningThreads.add(thread)
    if widgetId:
        try:
            widgetThreads[widgetId]
        except KeyError:
            widgetThreads[widgetId] = set()
        finally:
            widgetThreads[widgetId].add(thread)
        
def join_thread(thread):
    """
    Join selected thread
    @type thread: thread
    """
    if thread and isinstance(thread, threading.thread):
        print thread.isAlive()
        if thread.isAlive():
            thread.join()
            runningThreads.remove(thread)