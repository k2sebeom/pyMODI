import numpy as np
import wave

from io import BytesIO
from modi.util.audiolib import write
from modi.util.conn_util import is_modi_pi, AIModuleNotFoundException
from typing import Union

# Import alsaaudio if the module is on raspberry pi
if is_modi_pi():
    import alsaaudio as audio


class AISpeaker:
    def __init__(self):
        if not self.is_ai_speaker_connected():
            raise AIModuleNotFoundException("Cannot find the MODI Speaker")

        self.__device = audio.PCM()
        self.__mixer = None
        cards = audio.cards()
        for idx, card in enumerate(cards):
            if 'wm8960' in card:
                self.__mixer = audio.Mixer(
                    audio.mixers(idx)[0],
                    cardindex=idx)
        # If MODI sound card is not found
        if not self.__mixer:
            raise AIModuleNotFoundException("Cannot find the MODI Speaker")

    @staticmethod
    def is_ai_speaker_connected():
        connected_devices = audio.pcms(audio.PCM_PLAYBACK)
        for device in connected_devices:
            if 'wm8960' in device:
                return True
        return False

    def play(self, data: Union[str, np.ndarray], rate: int = 44100) -> None:
        """ Play wave file by a given filename or numpy array

        :param data: File path of numpy array
        :type data: Union[str, np.ndarray]
        :param rate: Sampling rate if the data is numpy array
        :type rate: int
        :return: None
        """
        if isinstance(data, str):
            audio_file = wave.open(data, 'rb')
        else:
            audio_file = self.__numpy_to_wave(data, rate)

        _, _, _, period_size = self.__set_attribute(audio_file)

        stream = audio_file.readframes(period_size)
        while stream:
            # Read data from stdin
            self.__device.write(stream)
            stream = audio_file.readframes(period_size)

    def __set_attribute(self, audio_file):
        # Set attributes
        self.__device.setchannels(audio_file.getnchannels())
        self.__device.setrate(audio_file.getframerate())

        # 8bit is unsigned in wav files
        if audio_file.getsampwidth() == 1:
            self.__device.setformat(audio.PCM_FORMAT_U8)
        # Otherwise we assume signed data, little endian
        elif audio_file.getsampwidth() == 2:
            self.__device.setformat(audio.PCM_FORMAT_S16_LE)
        elif audio_file.getsampwidth() == 3:
            self.__device.setformat(audio.PCM_FORMAT_S24_LE)
        elif audio_file.getsampwidth() == 4:
            self.__device.setformat(audio.PCM_FORMAT_S32_LE)
        else:
            raise ValueError('Unsupported format')

        period_size = audio_file.getframerate() // 8
        self.__device.setperiodsize(period_size)
        return (audio_file.getnchannels(), audio_file.getframerate(),
                audio_file.getsampwidth(), period_size)

    def play_tune(self, frequency: float, duration: float,
                  volume: float = 1) -> None:
        """ Play a tune of given frequency and volume for a given duration

        :param frequency: Frequency of the tune
        :type frequency: float
        :param duration: Duration of the tune in seconds
        :type duration: float
        :param volume: Volume of the sine wave
        :type volume: float
        :return: None
        """
        rate = 44100
        sine_wave = volume * (np.sin(2 * np.pi * np.arange(rate * duration) *
                                     frequency / rate))
        self.play(sine_wave, rate)

    @property
    def volume(self) -> int:
        """ Getter method of volume

        :return: Current volume
        :type: int
        """
        return self.__mixer.getvolume()

    def set_volume(self, vol: int) -> None:
        """ Set the volume by given number

        :param vol: Volume to set between 0 and 100
        :type vol: int
        :return: None
        """
        self.__mixer.setvolume(vol)

    def mute(self) -> None:
        """ Mute the speaker

        :return: None
        """
        self.__mixer.setmute(1)

    def unmute(self) -> None:
        """ Unmute the speaker

        :return: None
        """
        self.__mixer.setmute(0)

    def __numpy_to_wave(self, data: np.ndarray, rate: int) -> wave.Wave_read:
        """ Parse a given array to a wave file

        :param data: Numpy array to parse
        :type data: np.ndarray
        :param rate: Sampling rate
        :type rate: int
        :return: Wave_read object of the parsed wave file
        :rtype: Wave_read
        """
        buffer = BytesIO()
        write(buffer, rate, self.__float_to_pcm(data))
        return wave.open(buffer, "rb")

    @staticmethod
    def __float_to_pcm(signal: np.ndarray, dtype: str = 'int16') -> np.ndarray:
        """ Convert a given np array to a wave-convertible format

        :param signal: Numpy array signal to convert
        :type signal: np.ndarray
        :param dtype: Datatype to change (Almost always int16)
        :type dtype: str
        :return: Converted signal in numpy array
        :rtype: np.ndarray
        """
        i = np.iinfo(dtype)
        abs_max = 2 ** (i.bits - 1)
        offset = i.min + abs_max
        return (signal * abs_max + offset).clip(i.min, i.max).astype(dtype)
