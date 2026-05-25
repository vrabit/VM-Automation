
from vm_auto_eq.params import vm_controller
from vm_auto_eq.auto_eq import auto_eq
from vm_auto_eq.gain_compensation import gain_compensation
import asyncio


async def main():
    print("Hello from vm-auto-eq!")
    with vm_controller.VMController() as controller:
        smile_eq = auto_eq.AutoEq(controller)
        gain_comp = gain_compensation.GainCompensation(controller)

        try:
            await asyncio.gather(
                smile_eq.auto_eq_loop(),
                gain_comp.auto_compensate_loop()
            )
        except asyncio.CancelledError:
            print("Loops were stopped cleanly.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")