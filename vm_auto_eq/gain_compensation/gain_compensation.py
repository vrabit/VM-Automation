from vm_auto_eq.params import vm_controller
import asyncio

class GainCompensation:
    def __init__(self, controller:vm_controller.VMController):
        self.controller = controller

        self.leader = 0
        self.follower = 2

        self.previous_gain = None
        self.compensation_amount = 0


    async def get_gain(self, strip:int, strip_type:str = 'strip'):
        gain = await self.controller.get_strip_gain(strip, strip_type)
        return gain

    async def compensation_required(self):
        leader_gain = await self.get_gain(0, 'bus')

        if self.previous_gain is None:
            self.previous_gain = leader_gain
            return False
        
        diff = leader_gain - self.previous_gain 
        if abs(diff) > 0.2:
            self.compensation_amount = diff
            self.previous_gain = leader_gain
            return True
        return False
        
    async def apply_compensation(self):
        follower_gain = await self.get_gain(self.follower, 'strip')
        new_gain = follower_gain - self.compensation_amount
        self.controller.set_volume(self.follower, new_gain)
        self.compensation_amount = 0

    async def auto_compensate_loop(self):
        while(True):
            required = await self.compensation_required()
            if required:
                await self.apply_compensation()
            await asyncio.sleep(0.5)