import alsaaudio as audio
import wave
import numpy as np
import time
# from io import BytesIO


class AI_mic:

    def __init__(self):
        self.__mixer = None
        # Open the device object in non-blocking capture mode
        self.__device = audio.PCM(
            audio.PCM_CAPTURE,
            audio.PCM_NONBLOCK,
        )
        self.__device.setchannels(2)
        self.__device.setrate(8000)
        self.__device.setformat(audio.PCM_FORMAT_S16_LE)

        cards = audio.cards()
        for idx, card in enumerate(cards):
            if 'wm8960' in card:
                self.mixer = audio.Mixer(
                    audio.mixers(idx)[0],
                    cardindex=idx
                )
        if not self.mixer:
            raise Exception("Cannot find the MODI AI Mic")

    def record(self, destination: str, duration: float) -> np.ndarray:
        """ Record sound data catched by MODI AI shield

        :param duration: Duration for reconrding (Seconds)
        :data duration: float
        :return: ndarray
        """
        audio_file = wave.open(destination, 'wb')
        audio_file.setnchannels(2)
        audio_file.setsampwidth(2)
        audio_file.setframerate(8000)

        self.__device.setperiodsize(160)
        loops = 50000 * duration
        while loops > 0:
            loops -= 1
            # Read data from device
            l, data = self.__device.read()

            if l:
                audio_file.writeframes(data)
                time.sleep(.001)
        audio_file.close()


if __name__ == '__main__':
    mic = AI_mic()
    mic.record('./record.wav', 5)
