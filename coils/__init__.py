import time

from nidaqmx import Task
import numpy as np
import threading

import config

class Waveform(threading.Thread):
    def __init__(self, amp, freq):
        threading.Thread.__init__(self)
        self.daemon = True
        self.amp = amp
        self.freq = freq
        self.phase = np.pi / 2

        self._stopper = threading.Event()

    def stopit(self):
        self._stopper.set()

    def stopped(self):
        return self._stopper.is_set()

    # Sine wave generator (freq in rad / s)
    def f(self, t, amp, freq, phase):
        return amp * np.sin(freq * t + phase)

    def run(self):
        with nidaqmx.Task() as task:
            # Define voltage output channels for coil control ([X, Y])
            task.ao_channels.add_ao_voltage_chan(config.COILS_NAME_OX)
            task.ao_channels.add_ao_voltage_chan(config.COILS_NAME_OY)

            # Set maximum permittable voltage for output channels
            task.ao_channels.all.ao_max = config.COILS_MAX_CURRENT
            task.ao_channels.all.ao_min = -config.COILS_MAX_CURRENT

            # Waveform generation loop
            time_start = time.time_ns() * 1e-9
            while not self.stopped():
                time_now = time.time_ns() * 1e-9
                t = time_now - time_start

                # Set coil voltages
                task.write([
                    self.f(t, self.amp, self.freq, 0) * config.COILS_MT_TO_V_X,
                    self.f(t, self.amp, self.freq, self.phase) * config.COILS_MT_TO_V_Y,
                ])

                # Limit frame rate
                time.sleep(max(1./config.COILS_FPS - (time.time_ns() * 1e-9 - time_now), 0))

            # Set current through coils to zero upon exit
            task.write([0, 0])