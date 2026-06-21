from vm_auto_eq.params import vm_controller
from dataclasses import dataclass, field, asdict, replace
import asyncio


@dataclass(frozen=True)
class CompensationRuntimeState:
    previous_master_gain: float | None = field(default_factory=float)
    compensation_amount: float = field(default_factory=float)
    enabled: bool = field(default_factory=bool)
    source_bus: int = field(default_factory=int)
    target_strips:list[int] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data:dict):
        return cls(**data)

    @classmethod
    def to_dict(self):
        return asdict(self)


@dataclass(frozen=True)
class CompensationConfig:
    enabled_engaged: bool = field(default_factory=bool)
    source_bus: int = field(default_factory=int)
    target_strips:list[int] = field(default_factory=list)
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
        self.runtime_state: CompensationRuntimeState = None
        self._set_default_state()

    def _set_default_state(self):
        self.runtime_state: CompensationRuntimeState = CompensationRuntimeState.from_dict({
            "previous_master_gain" : None,
            "compensation_amount" : 0,
            "enabled" : self.config.enabled_engaged,
            "source_bus" : self.config.source_bus,
            "target_strips" : self.config.target_strips
        })
    
    def get_runtime_state(self):
        return self.runtime_state.copy()

    async def _get_gain(self, strip:int, strip_type:str = 'strip'):
        gain = await self.controller.get_strip_gain(strip, strip_type)
        return gain

    async def _compensation_required(self):
        if self.runtime_state.source_bus is None:
            return False

        leader_gain = await self._get_gain(self.runtime_state.source_bus, 'bus')

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
        
    async def _apply_compensation(self):
        for target_strips in self.config.target_strips:
            target_gain = await self._get_gain(target_strips, 'strip')
            new_gain = target_gain - self.runtime_state.compensation_amount
            self.controller.set_volume(target_strips, new_gain)
        self.runtime_state = replace(self.runtime_state, compensation_amount = 0)

    async def auto_compensate_loop(self):
        while(True):
            required = await self._compensation_required()
            if required and self.runtime_state.enabled:
                await self._apply_compensation()
            await asyncio.sleep(0.5)


    # Interface
    async def enable(self):
        self.runtime_state = replace(self.runtime_state, enabled=True)

    async def disable(self):
        self.runtime_state = replace(self.runtime_state, enabled=False)

    async def get_enabled(self):
        return self.runtime_state.enabled
    
    async def get_source_strip_enable(self, bus:int):
        return True if self.runtime_state.source_bus == bus else False
    
    async def change_source_bus(self, bus:int):
        self.runtime_state = replace(self.runtime_state, source_bus=bus, previous_master_gain=None, compensation_amount=0)

    async def remove_source_bus(self, bus:int):
        if self.runtime_state.source_bus == bus:
            self.runtime_state = replace(self.runtime_state, source_bus=None)

    async def get_target_strip_enable(self, strip:int):
        return True if strip in self.runtime_state.target_strips else False
    
    async def remove_target_strip(self, strip:int):
        if strip in self.runtime_state.target_strips:
            temp_list = self.runtime_state.target_strips
            temp_list.remove(strip)
            self.runtime_state = replace(self.runtime_state, target_strips=temp_list)

    async def add_target_strip(self, strip:int):
        if strip not in self.runtime_state.target_strips:
            temp_list = self.runtime_state.target_strips
            temp_list.append(strip)
            self.runtime_state = replace(self.runtime_state, target_strips=temp_list)
