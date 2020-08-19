"""Main MODI module."""

import atexit
import time
from importlib import import_module as im
from typing import Optional

from modi._exe_thrd import ExeThrd
from modi.util.conn_util import is_network_module_connected, is_on_pi
from modi.util.misc import module_list
from modi.util.stranger import check_complete
from modi.util.topology_manager import TopologyManager
from modi.firmware_updater import STM32FirmwareUpdater, ESP32FirmwareUpdater


class MODI:

    def __init__(self, conn_mode: str = "", verbose: bool = False,
                 port: str = None, uuid=""):
        self._modules = list()
        self._topology_data = dict()

        self._conn = self.__init_task(conn_mode, verbose, port, uuid)

        self._exe_thrd = ExeThrd(
            self._modules, self._topology_data, self._conn
        )
        print('Start initializing connected MODI modules')
        self._exe_thrd.start()

        self._topology_manager = TopologyManager(self._topology_data,
                                                 self._modules)

        init_time = time.time()
        while not self._topology_manager.is_topology_complete():
            time.sleep(0.1)
            if time.time() - init_time > 5:
                print("MODI init timeout over. "
                      "Check your module connection.")
                break
        check_complete(self)
        print("MODI modules are initialized!")

        user_code_states = self.__wait_user_code_check()
        if sum(user_code_states):
            bad_module = self._modules[user_code_states.index(1)]
            cmd = input(f"{str(bad_module)} has user code in it.\n"
                        f"Reset the user code? [y/n] ")
            if 'y' in cmd:
                self.close()
                update_module_firmware()
                time.sleep(1)
                self.open()
        atexit.register(self.close)

    def __wait_user_code_check(self):
        def is_not_checked(module):
            return module.user_code_status < 0

        while list(filter(is_not_checked, self._modules)):
            time.sleep(0.1)
        return [module.user_code_status for module in self._modules]

    @staticmethod
    def __init_task(conn_mode, verbose, port, uuid):
        if not conn_mode:
            is_can = not is_network_module_connected() and is_on_pi()
            conn_mode = 'can' if is_can else 'ser'

        if conn_mode == 'ser':
            return im('modi.task.ser_task').SerTask(verbose, port)
        elif conn_mode == 'can':
            return im('modi.task.can_task').CanTask(verbose)
        elif conn_mode == 'ble':
            return im('modi.task.ble_task').BleTask(verbose, uuid)
        else:
            raise ValueError(f'Invalid conn mode {conn_mode}')

    def close(self):
        atexit.unregister(self.close)
        print("Closing MODI connection...")
        self._exe_thrd.close()
        self._conn.close_conn()

    def open(self):
        atexit.register(self.close)
        self._exe_thrd = ExeThrd(
            self._modules, self._topology_data, self._conn
        )
        self._conn.open_conn()
        self._exe_thrd.start()

    def send(self, message) -> None:
        """Low level method to send json pkt directly to modules

        :param message: Json packet to send
        :return: None
        """
        self._conn.send(message)

    def recv(self) -> Optional[str]:
        """Low level method to receive json pkt directly from modules

        :return: Json msg received
        :rtype: str if msg exists, else None
        """
        return self._conn.recv()

    def print_topology_map(self, print_id: bool = False) -> None:
        """Prints out the topology map

        :param print_id: if True, the result includes module id
        :return: None
        """
        self._topology_manager.print_topology_map(print_id)

    @property
    def modules(self) -> module_list:
        """Module List of connected modules except network module.
        """
        return module_list(self._modules)

    @property
    def networks(self) -> module_list:
        return module_list(self._modules, 'Network')

    @property
    def buttons(self) -> module_list:
        """Module List of connected Button modules.
        """
        return module_list(self._modules, 'button')

    @property
    def dials(self) -> module_list:
        """Module List of connected Dial modules.
        """
        return module_list(self._modules, "dial")

    @property
    def displays(self) -> module_list:
        """Module List of connected Display modules.
        """
        return module_list(self._modules, "display")

    @property
    def envs(self) -> module_list:
        """Module List of connected Env modules.
        """
        return module_list(self._modules, "env")

    @property
    def gyros(self) -> module_list:
        """Module List of connected Gyro modules.
        """
        return module_list(self._modules, "gyro")

    @property
    def irs(self) -> module_list:
        """Module List of connected Ir modules.
        """
        return module_list(self._modules, "ir")

    @property
    def leds(self) -> module_list:
        """Module List of connected Led modules.
        """
        return module_list(self._modules, "led")

    @property
    def mics(self) -> module_list:
        """Module List of connected Mic modules.
        """
        return module_list(self._modules, "mic")

    @property
    def motors(self) -> module_list:
        """Module List of connected Motor modules.
        """
        return module_list(self._modules, "motor")

    @property
    def speakers(self) -> module_list:
        """Module List of connected Speaker modules.
        """
        return module_list(self._modules, "speaker")

    @property
    def ultrasonics(self) -> module_list:
        """Module List of connected Ultrasonic modules.
        """
        return module_list(self._modules, "ultrasonic")


def update_module_firmware():
    updater = STM32FirmwareUpdater()
    updater.update_module_firmware()
    updater.close()


def update_network_firmware(stub=True, force=False):
    updater = ESP32FirmwareUpdater()
    updater.start_update(stub=stub, force=force)
