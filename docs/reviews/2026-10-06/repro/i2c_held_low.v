
`timescale 1ns/1ps
module i2c_tb;
parameter STUCK=0;
reg clk=0,rst=1,start=0;
always #5 clk=~clk;
wire busy,done,nack,scl_low,sda_low;
wire scl_in=STUCK ? 1'b0 : ~scl_low;
i2c_master #(.DIV(2)) dut(.clk(clk),.rst(rst),.start(start),.rw(1'b0),.dev(7'h5C),.addr(8'h00),.wdata(8'h00),
 .busy(busy),.done(done),.nack(nack),.rdata(),.scl_low(scl_low),.sda_low(sda_low),.scl_in(scl_in),.sda_in(1'b1));
integer completions=0;
always @(negedge clk) if(done) completions=completions+1;
initial begin
 #30 rst=0;
 @(negedge clk) start=1;
 @(negedge clk) start=0;
 repeat(2000) @(posedge clk);
 @(negedge clk);
 $display("I2C stuck=%0d busy=%0d completions=%0d",STUCK,busy,completions);
 $finish;
end
endmodule
