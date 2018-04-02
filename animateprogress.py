#-*- coding:utf-8 -*-
import time
import threading
import logger

class AnimateProgress(object):
    def __init__(self):
        self._running = False
        self._count = 0
        self._logger = logger.register(__name__)

    def _rotated_progress(self, interval):
        flags = ['-', '\\', '|', '/']
        while self._running:
            print('\b'+flags[self._count%4], end='', flush=True)
            time.sleep(interval)
            self._count += 1

    def _bar_progress(self, interval, flag):
        while self._running:
            print(flag, end='', flush=True)
            time.sleep(interval)
            self._count += 1

    def _start_progress(self, args, target):
        self._running = True
        self._count = 0
        trd = threading.Thread(target=target, args=args, name='Rotated Progress Animation')
        trd.start()
        return trd
    
    def start_rotated_progress(self, text='', interval=0.5):
        if not self._running:
            print(text, end=' ')
            return self._start_progress((interval,), self._rotated_progress)

    def start_bar_progress(self, text='', interval=0.5, flag='.'):
        print(text, end='')
        return self._start_progress((interval, flag,), self._bar_progress)

    def stop_progress(self):
        if self._running:
            self._running = False
            print('\n', end='')
            self._logger.debug('Process Time: %d tick(s).' % self._count)
