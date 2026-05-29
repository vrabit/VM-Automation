from vm_auto_eq.params import vm_controller
from vm_auto_eq import paths
import numpy as np
import math

import asyncio
import json
from dataclasses import dataclass, field, replace, asdict


@dataclass(frozen=True)
class EQConfig:
    bus_index: int = field(default_factory=int)
    MIN_DB: float = field(default_factory=float)
    MAX_DB: float = field(default_factory=float)
    alpha_loud: float = field(default_factory=float)
    alpha_quiet: float = field(default_factory=float)

    def __post_init__(self):

        if not (0 <= self.alpha_loud <= 1):
            raise ValueError(
                f'alpha_loud must be between 0 and 1 '
                f'(got {self.alpha_loud})'
            )

        if not (0 <= self.alpha_quiet <= 1):
            raise ValueError(
                f'alpha_quiet must be between 0 and 1 '
                f'(got {self.alpha_quiet})'
            )

        if self.MIN_DB >= self.MAX_DB:
            raise ValueError(
                'MIN_DB must be less than MAX_DB'
            )
        
    @classmethod
    def from_dict(cls, data:dict):
        return cls(**data)

    @classmethod
    def to_dict(self):
        return asdict(self)


class AutoEq:
    def __init__(self, controller:vm_controller.VMController, eq_config:EQConfig):
        self.controller = controller
        self.eq_config = eq_config

        self.previous_normalized_gain = None
        self.smoothed_gain = None
        self.preset = self.load_eq(self.eq_config.bus_index)

    def update_config(self, new_config:EQConfig):
        self.eq_config = new_config

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
        t = (raw_gain - self.eq_config.MIN_DB) / (self.eq_config.MAX_DB - self.eq_config.MIN_DB)
        t = max(0.0, min(1.0, t))
        return t
    
    def smooth_gain(self, current_gain):
        if self.smoothed_gain is None:
            self.smoothed_gain = current_gain
            return current_gain

        if current_gain > self.smoothed_gain:
            alpha = self.eq_config.alpha_loud
        else:
            alpha = self.eq_config.alpha_quiet

        self.smoothed_gain += (current_gain - self.smoothed_gain) * alpha
        return self.smoothed_gain
        
    def calculate_smile_gain(self, low, high, normalized_gain):
        normalized_gain = normalized_gain * normalized_gain
        new_gain = low + (high - low) * normalized_gain
        return new_gain

    def apply_eq(self, bus:int, smoothed_gain:float):
        eq = self.preset
        normalized = self.normalize_gain(smoothed_gain)

        if self.previous_normalized_gain is not None and abs(normalized - self.previous_normalized_gain) <  0.01:
            return
        
        for band, setting in enumerate(eq):
            calculated_gain = self.calculate_smile_gain(setting['low_gain'], setting['high_gain'], normalized)
            self.controller.set_eq_band(bus, band, freq=setting['freq'], gain=calculated_gain, q=setting['q'], filter_type=setting['type'])

        self.previous_normalized_gain = normalized

    def poll_eq(self):
        left_level, right_level = self.controller.get_stereo_out_live_level(self.eq_config.bus_index)
        current_gain = self.level_to_db((left_level + right_level)/2)
        smoothed_gain = self.smooth_gain(current_gain)

        self.apply_eq(self.eq_config.bus_index, smoothed_gain)

    async def auto_eq_loop(self):
        while(True):
            self.poll_eq()

            await asyncio.sleep(0.1)


