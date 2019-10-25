# -*- coding: utf-8 -*-

"""Stoppable Thread module."""

from __future__ import absolute_import

from abc import *
from multiprocessing import Process
from multiprocessing import Event

class StoppableProcess(Process):
    def __init__(self):
        super(StoppableProcess, self).__init__(target=self.run)
        self._stop = Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.is_set()
    
    @abstractmethod
    def run(self):
        pass