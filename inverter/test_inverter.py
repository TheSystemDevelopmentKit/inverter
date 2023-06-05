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
    Inverter test
    """
    s_source = signal_source()
    s_source.run()
    for sample in s_source.IOS.Members['data'].Data:
        dut.A.value = int(sample[0])
        await Timer(1)
        assert(dut.Z.value == abs(int(sample[0]) - 1))


