from vm_auto_eq.params import vm_controller
from vm_auto_eq import paths
import numpy as np
import math

import asyncio
import json

class AutoEq:
    def __init__(self, controller:vm_controller.VMController):
        self.controller = controller

        self.previous_normalized_gain = None
        self.smoothed_gain = None
        self.MIN_DB = -60
        self.MAX_DB = -10

        self.eq_settings = self.load_eq()

    def level_to_db(self, raw: float) -> float:
        raw = max(raw, 1e-9)
        return 20 * math.log10(raw)

    def load_eq(self, preset_number:int = 0):
        filename = paths.EQ_PRO_TEMPLATE.format(i=preset_number)
        path = paths.EQ_PRESETS_DIR / filename
        with open(path, 'r') as f:
            file = json.load(f)
        return file
    
    def normalize_gain(self, raw_gain):
        t = (raw_gain - self.MIN_DB) / (self.MAX_DB - self.MIN_DB)
        t = max(0.0, min(1.0, t))
        return t
    
    def smooth_gain(self, current_gain):
        if self.smoothed_gain is None:
            self.smoothed_gain = current_gain
            return current_gain

        if current_gain > self.smoothed_gain:
            alpha = 0.1
        else:
            alpha = 0.03

        self.smoothed_gain += (current_gain - self.smoothed_gain) * alpha
        return self.smoothed_gain
        
    def calculate_smile_gain(self, low, high, normalized_gain):
        normalized_gain = normalized_gain * normalized_gain
        new_gain = low + (high - low) * normalized_gain
        return new_gain

    def apply_eq(self, bus:int, smoothed_gain:float):
        eq = self.eq_settings
        normalized = self.normalize_gain(smoothed_gain)

        if self.previous_normalized_gain is not None and abs(normalized - self.previous_normalized_gain) <  0.01:
            return
        
        for band, setting in enumerate(eq):
            calculated_gain = self.calculate_smile_gain(setting['low_gain'], setting['high_gain'], normalized)
            self.controller.set_eq_band(bus, band, freq=setting['freq'], gain=calculated_gain, q=setting['q'], filter_type=setting['type'])

        self.previous_normalized_gain = normalized

    def poll_eq(self):
        left_level, right_level = self.controller.get_stereo_out_live_level(0)
        current_gain = self.level_to_db((left_level + right_level)/2)
        smoothed_gain = self.smooth_gain(current_gain)

        self.apply_eq(0, smoothed_gain)

    async def auto_eq_loop(self):
        while(True):
            self.poll_eq()
            await asyncio.sleep(0.1)


