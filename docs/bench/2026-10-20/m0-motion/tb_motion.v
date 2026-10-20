`timescale 1ns/1ps
module tb_motion;
  reg clk=0;
  always #5 clk=~clk;
  reg advance=0;
  m0_testpattern dut(.clk(clk),.rst_i(1'b0));
  integer i;
  initial begin
    force dut.fs=advance;
    for (i=0;i<5000;i=i+1) begin
      @(negedge clk); advance=1;
      @(negedge clk); advance=0;
      $display("T %0d %0d %0d %0d %0d",i,dut.bx,dut.by,dut.dx,dut.dy);
      @(negedge clk);
      $display("H %0d %0d %0d %0d %0d",i,dut.bx,dut.by,dut.dx,dut.dy);
    end
    $display("MOTION_END 5000");
    $finish;
  end
endmodule
// Isolate the unchanged top's frame movement from video clocks and serialization.
// These stubs make no video, clock-generation or HDMI correctness claim.
module clocks_720p(input clk_27,output clk_serial,clk_pixel,locked);
  assign clk_serial=clk_27; assign clk_pixel=clk_27; assign locked=1;
endmodule
module video_timing(input clk,rst,output [11:0] x,y,output de,hsync,vsync,frame_start);
  assign x=0;assign y=0;assign de=0;assign hsync=0;assign vsync=0;assign frame_start=0;
endmodule
module dvi_tx_gowin(input clk_pixel,clk_serial,rst,de,hsync,vsync,
 input [7:0] r,g,b,input hz50,output tmds_clk_p,tmds_clk_n,output [2:0] tmds_d_p,tmds_d_n);
 assign tmds_clk_p=0;assign tmds_clk_n=0;assign tmds_d_p=0;assign tmds_d_n=0;
endmodule
