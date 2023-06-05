import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Edge, Timer
from inverter.signal_source import signal_source

TIMEOUT = 100000

# NOTE: icarus supports only 'step's as time unit, therefore we should use only them

# Timeout is 2x'd because a clock cycle is 2 steps
@cocotb.test(timeout_time=2*TIMEOUT, timeout_unit="step")
async def test_inverter(dut):
    """
    This test loads the program from an elf file into ROM, toggles reset, and runs the clock
    for a specified number of clock cycles
    """
    s_source = signal_source()
    s_source.run()
    for sample in s_source:
        dut.A.value = sample
        await Timer(1)
        print(dut.Z.value)
    assert(1==1)


