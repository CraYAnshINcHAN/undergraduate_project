import numpy as np
from magneto_elastica_utils import compute_ramp_factor
class BaseMagneticField:
    def __init__(self):
        """
        """
    def value(self, time: np.float64 = 0.0):
        """
        """
#这里的磁场是一个常数磁场，不随时间变化，但实际上并不完全是这样
#我们给出的ram_interval，start_time，end_time是指磁场开始时间，结束时间以及磁场在ramp_interval时间内会逐渐增加到达end_time后又
#会在ramp_interval时间内逐渐减小
        
class ConstantMagneticField(BaseMagneticField):
    def __init__(self, magnetic_field_amplitude, ramp_interval, start_time, end_time):
        super(ConstantMagneticField, self).__init__()
        self.magnetic_field_amplitude = magnetic_field_amplitude
        self.ramp_interval = ramp_interval
        self.start_time = start_time
        self.end_time = end_time

    def value(self, time: np.float64 = 0.0):
        factor = compute_ramp_factor(time = time, ramp_interval = self.ramp_interval,
                                     start_time = self.start_time, end_time = self.end_time)
        return factor * self.magnetic_field_amplitude
        

