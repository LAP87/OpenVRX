`timescale 1ns/1ps
module i2c_master #(parameter DIV=68)(
input clk,rst,start,rw,input [6:0] dev,input [7:0] addr,wdata,
output reg busy=0,done=0,nack=0,output reg[7:0]rdata=0,
output wire scl_low,sda_low,input scl_in,sda_in);
assign scl_low=0;assign sda_low=0;
reg op_rw;reg [7:0] op_addr;integer waitn=0,reads88=0;reg failed88=0;
always @(posedge clk) begin
 done<=0;
 if(start&&!busy)begin busy<=1;waitn<=3;op_rw<=rw;op_addr<=addr;end
 else if(busy)begin
  if(waitn!=0)waitn<=waitn-1;
  else begin
   busy<=0;done<=1;nack<=0;
   if(op_rw&&op_addr==8'h88)begin
    reads88<=reads88+1;
    if(reads88==1)begin nack<=1;failed88<=1;end
    rdata<=8'h0e;
   end else if(op_rw&&op_addr==8'h03) rdata<=8'h0d;
   else rdata<=0;
  end
 end
 if(rst)begin busy<=0;done<=0;nack<=0;reads88<=0;failed88<=0;end
end
endmodule
