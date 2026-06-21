from vm_auto_eq.params import vm_controller
from vm_auto_eq.auto_eq import auto_eq
from vm_auto_eq.gain_compensation import gain_compensation
import vm_auto_eq.paths as paths

import threading
import asyncio
import json

from time import sleep 

class AsyncManager:
    def __init__(self):
        self.loop = None
        self.thread = None
        self.controller = None
        self.service_task = None 
        self.eq_configs = None
        self.eq_registry = None
        self.gain_comp = None

        self.startup_done = threading.Event()
        self.connected = False

    def load_json(self, path:str, filename:str):
        with open(path/filename, 'r') as f:
            d = json.load(f)
        return d
    
    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.loop.create_task(
            self._startup()
        )
        
        self.loop.run_forever()

    async def _startup(self):
        await self.initialize_services()

        self.service_task = asyncio.create_task(
            self._run_services()
        )
        self.startup_done.set()

    async def _run_services(self):
        try:
            await asyncio.gather(
                *(element.auto_eq_loop() for element in self.eq_registry),
                self.gain_comp.auto_compensate_loop()
            )
        except asyncio.CancelledError:
            self.connected = False
            print("Loops were stopped cleanly.")

    async def initialize_services(self):

        self.controller = vm_controller.VMController()
        self.controller.connect()
        
        self.kind = self.controller.get_kind()
        num_outs = self.kind.outs[0] + self.kind.outs[1]

        eq_configs_dicts = [
            self.load_json(paths.AUTO_EQ_SETTINGS_DIR, paths.AUTO_EQ_FILENAME.format(i=i))
            for i in range(num_outs)
        ]

        self.eq_configs = [ auto_eq.EQConfig.from_dict(config) for config in eq_configs_dicts ]
        self.eq_registry = [ auto_eq.AutoEq(self.controller, config) for config in self.eq_configs ]

        # load config
        config = gain_compensation.CompensationConfig(
            enabled_engaged=True,
            source_bus=0,
            target_strips=[2,3],
            strength=1,
            threshold=0.2
        )
        self.gain_comp = gain_compensation.GainCompensation(self.controller, config)

    def start(self):
        self.thread = threading.Thread(
            target=self._run_loop,
            daemon=True
        )
        self.thread.start()

        print("Main Thread: Waiting for background thread to spin up...")
        is_ready = self.startup_done.wait(timeout=10.0) 
        
        if not is_ready:
            raise RuntimeError("Background thread failed to start up in time!")
        
        self.connected = True

    async def shutdown(self):
        if self.service_task is not None:
            self.service_task.cancel()
        
            try:
                await self.service_task
            except asyncio.CancelledError:
                pass
            self.controller.disconnect()
            self.connected = False

    # gain comp
    async def _get_enabled_state(self):
        return await self.gain_comp.get_enabled()

    async def _enable_compensation(self):
        await self.gain_comp.enable()
    
    async def _disable_compensation(self):
        await self.gain_comp.disable()

    async def _get_bus_enabled_state(self, bus:int):
        return await self.gain_comp.get_source_strip_enable(bus)
    
    async def _change_source_bus(self, bus:int):
        return await self.gain_comp.change_source_bus(bus)
    
    async def _remove_source_bus(self, bus:int):
        return await self.gain_comp.remove_source_bus(bus)

    async def _get_strip_enabled_state(self, strip:int):
        return await self.gain_comp.get_target_strip_enable(strip)
    
    async def _remove_target_strip(self, strip:int):
        await self.gain_comp.remove_target_strip(strip)

    async def _add_target_strip(self, strip:int):
        await self.gain_comp.add_target_strip(strip)

    # auto eq
    async def _get_enabled_state_autoeq(self,strip):
        return await self.eq_registry[strip].get_enabled()

    async def _enable_autoeq_bus(self, strip:int):
        await self.eq_registry[strip].enable_bus()

    async def _disable_autoeq_bus(self, strip:int):
        print(f"_disable : {strip}")
        await self.eq_registry[strip].disable_bus()

    # useful info
    def get_info(self):
        return self.controller.get_kind()

    # interface
    def is_connected(self):
        return self.connected

    # interface - gain comp
    def get_enabled_state(self):
        state = asyncio.run_coroutine_threadsafe(
            self._get_enabled_state(),
            self.loop
        )

        try:
            return state.result(timeout=2.0)
        except AttributeError:
            print(f"Error: self.gain_comp enable is still None init.")
            return False

    def enable_compensation(self):
        asyncio.run_coroutine_threadsafe(
            self._enable_compensation(),
            self.loop
        )

    def disable_compensation(self):
        asyncio.run_coroutine_threadsafe(
            self._disable_compensation(),
            self.loop
        )

    def get_bus_enabled_state(self, bus:int):
        state = asyncio.run_coroutine_threadsafe(
            self._get_bus_enabled_state(bus),
            self.loop
        )

        try:
            return state.result(timeout=2.0)
        except AttributeError:
            print(f"Error: self.gain_comp is still None when source bus {bus} init.")
            return False
        
    def change_source_bus(self, bus:int):
        asyncio.run_coroutine_threadsafe(
            self._change_source_bus(bus),
            self.loop
        )

    def remove_source_bus(self, bus:int):
        asyncio.run_coroutine_threadsafe(
            self._remove_source_bus(bus),
            self.loop
        )

    def get_strip_enabled_state(self, strip:int):
        state = asyncio.run_coroutine_threadsafe(
            self._get_strip_enabled_state(strip),
            self.loop
        )

        try:
            return state.result(timeout=2.0)
        except AttributeError:
            print(f"Error: self.gain_comp is still None when target strip {strip} init.")
            return False
    
    def remove_target_strip(self, strip:int):
        asyncio.run_coroutine_threadsafe(
            self._remove_target_strip(strip),
            self.loop
        )

    def add_target_strip(self, strip:int):
        asyncio.run_coroutine_threadsafe(
            self._add_target_strip(strip),
            self.loop
        )

    # interface - auto_eq
    def get_enabled_state_autoeq(self, bus:int):
        state = asyncio.run_coroutine_threadsafe(
            self._get_enabled_state_autoeq(bus),
            self.loop
        )

        try:
            return state.result(timeout=2.0)
        except AttributeError:
            print(f"Error: autoeq bus channel {bus} is still None when init.")
            return False

    def enable_autoeq_bus(self, bus:int):
        asyncio.run_coroutine_threadsafe(
            self._enable_autoeq_bus(bus),
            self.loop
        )

    def disable_autoeq_bus(self, bus:int):
        asyncio.run_coroutine_threadsafe(
            self._disable_autoeq_bus(bus),
            self.loop
        )
