from vm_auto_eq.params import vm_controller
from dataclasses import dataclass, field, asdict, replace
import asyncio


@dataclass(frozen=True)
class CompensationRuntimeState:
    previous_master_gain: float = field(default_factory=float)
    compensation_amount: float = field(default_factory=float)

    @classmethod
    def from_dict(cls, data:dict):
        return cls(**data)

    @classmethod
    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class CompensationConfig:
    enabled: bool = field(default_factory=bool)
    source_bus: int = field(default_factory=int)
    target_strip: int = field(default_factory=int)
    strength: float = field(default_factory=float)
    threshold:float = field(default_factory=float)

    @classmethod
    def from_dict(cls, data:dict):
        return cls(**data)

    @classmethod
    def to_dict(self):
        return asdict(self)


class GainCompensation:

    def __init__(self, controller:vm_controller.VMController, config:CompensationConfig):
        self.controller:vm_controller.VMController = controller
        self.config: CompensationConfig = config
        self.runtime_state: CompensationRuntimeState = CompensationRuntimeState.from_dict({
            "previous_master_gain" : None,
            "compensation_amount" : 0
        })

    async def get_gain(self, strip:int, strip_type:str = 'strip'):
        gain = await self.controller.get_strip_gain(strip, strip_type)
        return gain

    async def compensation_required(self):
        leader_gain = await self.get_gain(self.config.source_bus, 'bus')

        if self.runtime_state.previous_master_gain is None:
            self.runtime_state = replace(self.runtime_state, previous_master_gain=leader_gain)
            return False
        
        diff = leader_gain - self.runtime_state.previous_master_gain 
        if abs(diff) > self.config.threshold:
            self.runtime_state = replace(
                self.runtime_state, 
                compensation_amount = (diff * self.config.strength),
                previous_master_gain = leader_gain
            )
            return True
        return False
        
    async def apply_compensation(self):
        target_gain = await self.get_gain(self.config.target_strip, 'strip')
        new_gain = target_gain - self.runtime_state.compensation_amount
        self.controller.set_volume(self.config.target_strip, new_gain)
        self.runtime_state = replace(self.runtime_state, compensation_amount = 0)

    async def auto_compensate_loop(self):
        while(True):
            required = await self.compensation_required()
            if required:
                await self.apply_compensation()
            await asyncio.sleep(0.5)
