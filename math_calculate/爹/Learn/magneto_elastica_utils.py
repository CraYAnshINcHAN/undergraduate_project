from elastica_utils import Tolerance

def compute_ramp_factor(time, ramp_interval, start_time, end_time):
    factor = (time > start_time) * (time <= end_time) * min(
        1.0, (time - start_time) / (ramp_interval + Tolerance.atol())
    ) + (time > end_time) * max(
        0.0, -1/ (ramp_interval + Tolerance.atol()) * (time - end_time) + 1.0
    )