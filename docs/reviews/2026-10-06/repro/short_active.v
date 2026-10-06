`timescale 1ns/1ps
// A real BT.656 -> chan_capture -> mix_chan path. Four complete rows wrap
// the ring, then a SAV is 4 bytes late but EAV spacing remains 1716 bytes.
module tb_short_active;
reg clk=0,rst=1,pop=0;
reg [7:0] d=8'h80;
always #5 clk=~clk;
wire valid;
wire [52:0] e;
wire [2:0] count;
wire bad,overflow;
wire [31:0] rd_data;
chan_capture capture(.clk(clk),.rst(rst),.d(d),.e_valid(valid),.e_data(e));
mix_chan queue(.clk(clk),.rst(rst),.ext_bad(1'b0),.in_empty(!valid),.in_data(e),
 .in_pop(),.pop_line(pop),.rd_idx(9'd359),.rd_data(rd_data),.count(count),.head_bad(bad),.overflow(overflow)
`ifdef REVIEW
 ,.peer_sick(1'b0),.peer_arrived(1'b0),.peer_last_age(13'h1fff),.sick(),.arrived(),.last_age()
`endif
);
integer words=0,markers=0,release_countdown=0,pending_n=0;
always @(posedge clk) if(!rst && valid) begin
 if(e[52]) begin
  $display("MARKER n=%0d words=%0d length=%0d xy_bad=%0d active=%0d",markers,words,e[12:1],e[20:17],capture.rec_active);
  if(e[12:1]!==1716 || e[20:17]!==0) $fatal(1,"fixture marker is not nominal");
  if(markers<4 && words!==360) $fatal(1,"positive control has wrong payload size");
  if(markers==4 && words!==359) $fatal(1,"short row not generated");
  pending_n=markers; release_countdown=3;
  words=0; markers=markers+1;
 end else words=words+1;
end
always @(negedge clk) begin
 if(pop) pop=0;
 if(release_countdown>0) begin
  release_countdown=release_countdown-1;
  if(release_countdown==0) begin
   $display("ROW n=%0d count=%0d bad=%0d overflow=%0d tail=%08x",pending_n,count,bad,overflow,rd_data);
   if(pending_n<4 && count!==1) $fatal(1,"positive full row was not accepted");
   if(count!=0) pop=1;
  end
 end
end
task put_byte(input [7:0] b); begin @(negedge clk); d=b; end endtask
task code(input [7:0] xy); begin put_byte(255); put_byte(0); put_byte(0); put_byte(xy); end endtask
task row(input integer n,input integer short);
integer k;
begin
 for(k=0;k<268+4*short;k=k+1) put_byte(128);
 code(8'h80);                         // SAV F=0, V=0
 for(k=0;k<1440-4*short;k=k+1) put_byte(k[0] ? 32+n*16 : 128);
 code(8'h9d);                         // EAV F=0, V=0, H=1
end
endtask
integer n;
initial begin
 repeat(5) @(posedge clk); @(negedge clk); rst=0;
 code(8'h9d);
 for(n=0;n<4;n=n+1) row(n,0);
 row(4,1);
 repeat(20) @(posedge clk);
 if(markers!==5) $fatal(1,"fixture marker count mismatch");
 $finish;
end
endmodule
