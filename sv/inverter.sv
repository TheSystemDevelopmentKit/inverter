//verilator lint_off UNUSED
module inverter( input reset,
                 input A, 
                 output Z );
//reset does nothing
assign Z= !A;

endmodule
//verilator lint_on UNUSED
