
`timescale 1ns/1ps
module genlock_tb;
reg clk=0,rst=1,lock=0,trig=0;
always #5 clk=~clk;
wire fs;wire [11:0] x,y;
genlock_timing #(.H_ACTIVE(8),.H_FP(2),.H_SYNC(2),.H_BP(2),.V_ACTIVE(8),.V_FP(1),.V_SYNC(1),.V_BP(2)) dut
 (.clk(clk),.rst(rst),.lock(lock),.trig(trig),.h_alt(1'b0),.x(x),.y(y),.de(),.hsync(),.vsync(),.frame_start(fs));
integer cyc=0;
always @(negedge clk) if(!rst) begin cyc=cyc+1;if(fs) $display("FRAME %0d",cyc);end
initial begin
 #30 rst=0;
 repeat(3) @(posedge fs);
 @(negedge clk) lock=1;
 wait(dut.vc==2 && dut.hc==1);
 @(negedge clk) trig=1;
 @(negedge clk) trig=0;
 repeat(300) @(posedge clk);
 $finish;
end
endmodule
