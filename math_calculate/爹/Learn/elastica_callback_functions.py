import os
import numpy as np
import sys
import logging

from collections import defaultdict

class CallBackBaseClass:
    def __init__(self):
        pass

    def make_callback(self, system, time, current_step:int):
        pass