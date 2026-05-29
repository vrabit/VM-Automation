
from vm_auto_eq.params import vm_controller
from vm_auto_eq.auto_eq import auto_eq
from vm_auto_eq.gain_compensation import gain_compensation
import vm_auto_eq.paths as paths
import asyncio
import json


def load_json(path:str, filename:str):
    with open(path/filename, 'r') as f:
        d = json.load(f)
    return d

async def main():
    print("Hello from vm-auto-eq!")
    with vm_controller.VMController() as controller:
        kind = controller.get_kind()
        num_outs = kind.outs[0] + kind.outs[1]

        eq_configs_dicts = [
            load_json(paths.AUTO_EQ_SETTINGS_DIR, paths.AUTO_EQ_FILENAME.format(i=i))
            for i in range(num_outs)
        ]

        eq_configs = [ auto_eq.EQConfig.from_dict(config) for config in eq_configs_dicts ]
        eq_registry = [ auto_eq.AutoEq(controller, config) for config in eq_configs ]

        # load config
        config = gain_compensation.CompensationConfig(
            source_bus=0,
            target_strip=2,
            strength=1,
            threshold=0.2
        )
        gain_comp = gain_compensation.GainCompensation(controller, config)

        try:
            await asyncio.gather(
                *(element.auto_eq_loop() for element in eq_registry),
                gain_comp.auto_compensate_loop()
            )
        except asyncio.CancelledError:
            print("Loops were stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")