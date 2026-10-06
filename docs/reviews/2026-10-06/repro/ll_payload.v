`timescale 1ns/1ps
// Audit fixture: real fb_backend, tagged FWFT words in LOW mode. No SDRAM
// transfers occur. The source sends whole lines, then a short field ends
// immediately after its line-1 trigger. Compare the payload at the toggle
// with the payload actually latched by the pixel-domain receiver.
module tb_ll_payload;
parameter GUARD = 0;
reg sd_clk=0, pix_clk=0, rst=1, empty=1;
reg [51:0] data=0;
always #7.7 sd_clk=~sd_clk;
always #6.7 pix_clk=~pix_clk;
wire pop;
wire [31:0] dq;
fb_backend #(.LL_EQ(0)) dut(
 .sd_clk(sd_clk), .sd_clk_shift(sd_clk), .pix_clk(pix_clk),
 .rst_async(rst), .ll_mode(1'b1), .f_empty(empty), .f_data(data), .f_pop(pop),
 .SDRAM_DQ(dq));
integer sent=0,received=0,k;
reg last_toggle=0;
reg [9:0] payload [0:15];
always @(posedge sd_clk) begin
 #1;
 if(!rst && dut.s_ll_trig !== last_toggle) begin
  payload[sent]=dut.s_ll_lines;
  $display("SEND n=%0d payload=%0d time=%0t",sent,dut.s_ll_lines,$time);
  sent=sent+1;
 end
 last_toggle=dut.s_ll_trig;
end
always @(posedge pix_clk) begin
 #1;
 if(!rst && dut.ll_trig) begin
  $display("RECEIVE n=%0d expected=%0d actual=%0d time=%0t",received,payload[received],dut.ll_lines,$time);
  if(received==1) begin
   if(payload[received]!==3) $fatal(1,"fixture: expected second field to carry 3 lines");
   if(GUARD!=0 && dut.ll_lines!==3) $fatal(1,"guarded positive control failed");
   if(GUARD==0 && dut.ll_lines!==2) $fatal(1,"short-field counterexample was not reproduced");
  end
  received=received+1;
 end
end
task word(input f,input [9:0] line,input [8:0] idx);
begin @(negedge sd_clk); empty=0; data={f,line,idx,32'h10203040}; end
endtask
task line(input f,input [9:0] n);
integer w;
begin for(w=0;w<360;w=w+1) word(f,n,w[8:0]); end
endtask
initial begin
 #100; rst=0;
 repeat(10) @(posedge sd_clk);
 line(0,0); line(0,1); line(0,2);
 line(1,0); line(1,1);
 if(GUARD!=0) begin
  @(negedge sd_clk); empty=1;
  repeat(20) @(posedge sd_clk);
 end
 word(0,0,0);
 @(negedge sd_clk); empty=1;
 repeat(30) @(posedge sd_clk);
 if(sent!==2 || received!==2) $fatal(1,"fixture event count mismatch");
 $display("DONE guard=%0d sent=%0d received=%0d",GUARD,sent,received);
 $finish;
end
endmodule
