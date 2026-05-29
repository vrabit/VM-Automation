import vm_auto_eq.params.vm_params as VM_P

import voicemeeterlib
from voicemeeterlib.remote import Remote
from voicemeeterlib.kinds import request_kind_map, KindId
import math
import asyncio


class VMController:

    def __init__(self):
        self.vm: Remote | None = None

    def login(self):
        self.vm.login()

    def logout(self):
        self.vm.logout()

    def __enter__(self):
        self.vm = voicemeeterlib.api("potato")
        self.vm.login()
        return self 
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.vm is not None:
            self.vm.logout()
            self.vm = None
        
    async def wait_for_update(self):
        if self.vm.pdirty:
            while self.vm.pdirty:
                await asyncio.sleep(0.01)

    async def get_strip_gain(self, strip: int, strip_type:str = 'strip'):
        await self.wait_for_update()
        if strip_type == 'strip':
            return self.vm.strip[strip].gain
        elif strip_type == 'bus':
            return self.vm.bus[strip].gain


    def get_kind(self):
        '''
         {
             'name': 'name',
             'ins': (physical_inputs, virtual_inputs)
             'outs': (hardware output buses, virtual output buses),
             'vban': (VBAN receive streams, VBAN transmit streams, VBAN input client, VBAN output client),
             'asio': (ASIO input channels exposed, ASIO output channels exposed),
             'insert': Number of insert patch points available,
             'composite': Number of composite routing channels,
             'strip_channels': stereo channels,
             'bus_channels': up to # channels,
             'cells': #-bands/cells parametric EQ
         }
        
         Bus Channel layout:
             0 -> Left
             1 -> Right
             2 -> Center
             3 -> LFE
             4 -> Rear Left
             5 -> Rear Right
             6 -> Side Left
             7 -> Side Right
        '''
        return self.vm.kind
    
    def get_num_ins(self):
        physical = self.vm.kind.ins[0]
        virtual = self.vm.kind.ins[1]
        return physical, virtual

    def get_num_outs(self):
        physical = self.vm.kind.outs[0]
        virtual = self.vm.kind.outs[1]
        return physical, virtual
    
    def get_num_channels(self):
        strip = self.vm.kind.strip_channels
        bus = self.vm.kind.bus_channels
        return strip, bus

    # INPUT STRIPS
    def set_volume(self, strip: int, gain: float, strip_type:str = 'strip'):
        if strip_type == 'strip':
            self.vm.set(VM_P.param("strip", "gain", strip), gain)
        elif strip_type == 'bus':
            self.vm.set(VM_P.param("bus", "gain", strip), gain)
        

    def get_cached_volume(self, strip: int, strip_type:str = 'strip'):     
        if strip_type == 'strip':
            return self.vm.get(VM_P.param('strip', 'gain', strip))
        elif strip_type == 'bus':
            return self.vm.get(VM_P.param('bus', 'gain', strip))
        return 0
    
    def get_stereo_out_live_level(self, out_strip:int):
        physical, virtual = self.get_num_outs()
        if out_strip >= (physical + virtual):
            print('invalid strip number')
            return 0
        
        _, bus_channels = self.get_num_channels()
        left = out_strip * bus_channels 
        right = left + 1

        left_level = self.vm.get_level(3,left)
        right_level = self.vm.get_level(3, right)
        return left_level, right_level

    def get_device_desc(self, index:int, direction:str='out'):
        return self.vm.get_device_description(0,'out')

    # EQ
    def get_raw(self, param:str):
        return self.vm.get(param)

    def set_preset(self, bus:int, preset:int):
        if preset <= 1 and preset >= 0:
            self.vm.set(VM_P.eq_param("bus_eq", "preset", bus), preset)  

        
    def set_eq_band(self, bus, band, *,
        freq=None,
        gain=None,
        q=None,
        filter_type=None,
    ):
        for channel in (0, 1):
            base = VM_P.eq_param("bus_eq", "base", bus, band, channel)
            if base is None:
                return

            if freq is not None:
                self.vm.set(f"{base}.freq", freq)

            if gain is not None:
                self.vm.set(f"{base}.gain", gain)

            if q is not None:
                self.vm.set(f"{base}.q", q)

            if filter_type is not None:
                filter_type_val = VM_P.eq_param("eq_type", filter_type)
                self.vm.set(f"{base}.type", int(filter_type_val))

