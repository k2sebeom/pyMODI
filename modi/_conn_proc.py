
import time

import threading as th
import multiprocessing as mp

from modi._conn_task import ConnTask
from modi._ser_task import SerTask
from modi._can_task import CanTask
from modi._ble_task import BleTask


class ConnProc(mp.Process):

    def __init__(self, recv_q, send_q, conn_mode):
        super().__init__()
        self.__delay = 0.001

        self.recv_q = recv_q
        self.send_q = send_q

    def run(self):
        with BleTask(self.recv_q, self.send_q) as ble:
            read_thread = th.Thread(
                target=ble.run_read_data, args=(self.__delay,)
            )
            read_thread.daemon = True
            read_thread.start()

            write_thread = th.Thread(
                target=ble.run_write_data, args=(self.__delay,)
            )
            write_thread.daemon = True
            write_thread.start()

            read_thread.join()
            write_thread.join()
