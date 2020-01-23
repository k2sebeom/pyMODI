# -*- coding: utf-8 -*-

import time
import queue


class ParserTask(object):
    """ This task buffering serial data and parsing serial data to json message
    param: serial_read_q: Multiprocessing Queue for serial reading data
    param: json_recv_q: Multiprocessing Queue for parsed json data
    """

    def __init__(self, serial_read_q, json_recv_q):
        super(ParserTask, self).__init__()
        self._serial_read_q = serial_read_q
        self._json_recv_q = json_recv_q

        self.__raw_data_buffer = str()
        self.__json_message = str()

    def start_thread(self):
        self.read_json()
        time.sleep(0.008)

    def read_json(self):
        """ Read serial data and put json message to json receive queue
        """

        try:
            serial_raw_data = self._serial_read_q.get_nowait()
        except queue.Empty:
            pass
        else:
            self.__raw_data_buffer += serial_raw_data

        while self.has_json():
            self._json_recv_q.put(self.__json_message)

    def has_json(self):
        """ Parsing serial data and make json message
        """

        end = self.__raw_data_buffer.find("}")
        if end >= 0:
            start = self.__raw_data_buffer.rfind("{", 0, end)
            if start >= 0:
                self.__json_message = self.__raw_data_buffer[start : end + 1]
                self.__raw_data_buffer = self.__raw_data_buffer[end + 1 :]
                return True
            else:
                self.__raw_data_buffer = self.__raw_data_buffer[end + 1 :]
                return False
        else:
            start = self.__raw_data_buffer.rfind("{")
            if start >= 0:
                self.__raw_data_buffer = self.__raw_data_buffer[start:]
            else:
                self.__raw_data_buffer = str()
            return False
