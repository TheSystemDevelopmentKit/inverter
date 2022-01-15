#include "Vinverter.h"
#include <iostream>             // Need std::cout
#include "verilated.h"
#include "verilated_vcd_c.h"

int main(int argc, char** argv, char** env) {
    VerilatedContext* contextp = new VerilatedContext;
    contextp->commandArgs(argc, argv);
    Vinverter* top = new Vinverter(contextp);
    Verilated::internalsDump();
    Verilated::traceEverOn(true);
    VerilatedVcdC* tfp = new VerilatedVcdC;
    top->trace(tfp, 99);  // Trace 99 levels of hierarchy
    tfp->open("foobadir/simx.vcd");
    static bool reset = 0;
    static bool clock = 0;
    static int count = 0;
    //while (!Verilated::gotFinish()) { 
    std::cout << "Starting the sucker!" << std::endl; 
    while (contextp->time() < 1000) { 
		clock = !clock;
		top->reset = 0;
		top->A = clock;
		top->eval(); 
        tfp->dump(contextp->time());
        //usleep(10000);
        VL_PRINTF("A is %d , Z is %d\n",top->A, top->Z);
            //top->clk, top->reset_l, top->in_quad, top->out_quad,
            //      top->out_wide[2], top->out_wide[1], top->out_wide[0]);
        //std::cout << contextp->time() << std::endl;
        contextp->timeInc(1);
	}
    top->final();
    delete top;
    delete contextp;
    exit(0);
}

