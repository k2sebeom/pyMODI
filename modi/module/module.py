"""Module module."""

import time

from enum import IntEnum

from modi.util.msgutil import parse_message

BROADCAST_ID = 0xFFF


class Module:
    """
    :param int id_: The id of the module.
    :param int uuid: The uuid of the module.
    :param msg_send_q: multiprocessing.queue of the serial writing
    """
    class Property:
        def __init__(self):
            self.value = 0
            self.last_update_time = 0
            self.last_request_time = 0

    class State(IntEnum):
        RUN = 0
        WARNING = 1
        FORCED_PAUSE = 2
        ERROR_STOP = 3
        UPDATE_FIRMWARE = 4
        UPDATE_FIRMWARE_READY = 5
        REBOOT = 6
        PNP_ON = 1
        PNP_OFF = 2

    def __init__(self, id_, uuid, msg_send_q):
        self._id = id_
        self._uuid = uuid
        self._msg_send_q = msg_send_q

        self.module_type = str()
        self._properties = dict()

        self.is_connected = True
        self.last_updated = time.time()
        self.battery = 100
        self.position = (0, 0)
        self.__version = None
        self.is_up_to_date = True
        self.has_user_code = False

    def __gt__(self, other):
        if self.order == other.order:
            if self.position[0] == other.position[0]:
                return self.position[1] < other.position[1]
            else:
                return self.position[0] > other.position[0]
        else:
            return self.order > other.order

    @property
    def version(self):
        version_string = ""
        version_string += str(self.__version >> 13) + '.'
        version_string += str(self.__version % (2 ** 13) >> 8) + '.'
        version_string += str(self.__version % (2 ** 8))
        return version_string

    @version.setter
    def version(self, version_info):
        self.__version = version_info

    @property
    def order(self):
        return self.position[0] ** 2 + self.position[1] ** 2

    @property
    def id(self) -> int:
        return self._id

    @property
    def uuid(self) -> int:
        return self._uuid

    def _get_property(self, property_type: IntEnum) -> float:
        """ Get module property value and request

        :param property_type: Type of the requested property
        :type property_type: IntEnum
        """

        # Register property if not exists
        if property_type not in self._properties.keys():
            self._properties[property_type] = self.Property()
            request_property_msg = self.request_property(
                self._id, property_type
            )
            self._msg_send_q.put(request_property_msg)
            self._properties[property_type].last_request_time = time.time()

        # Request property value if not updated for 0.5 sec
        duration = time.time() - \
            self._properties[property_type].last_update_time
        if duration > 1:
            modi_serialtemp = self.request_property(
                self._id, property_type
            )
            self._msg_send_q.put(modi_serialtemp)
            self._properties[property_type].last_request_time = time.time()
        time.sleep(0.001)
        return self._properties[property_type].value

    def update_property(self, property_type: IntEnum,
                        property_value: float) -> None:
        """ Update property value and time

        :param property_type: Type of the updated property
        :type property_type: IntEnum
        :param property_value: Value to update the property
        :type property_value: float
        """
        if property_type in self._properties.keys():
            self._properties[property_type].value = property_value
            self._properties[property_type].last_update_time = time.time()

    @staticmethod
    def request_property(destination_id: int,
                         property_type: IntEnum) -> str:
        """ Generate message for request property

        :param destination_id: Id of the destination module
        :type destination_id: int
        :param property_type: Type of the requested property
        :type property_type: int
        :return: json serialized message for request property
        :rtype: str
        """
        return parse_message(0x03, 0, destination_id,
                             (property_type, None, 95, None))
