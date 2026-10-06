`timescale 1ns/1ps
module tb;
reg clk=0,rst=1;always #5 clk=~clk;
wire [15:0]status0,status1;wire[1:0] dev_err,status_valid;wire init_done;
tvp_ctrl #(.CLK_HZ(1000),.N_DEV(1),.POWER_MS(1),.RESET_MS(1),.BOOT_MS(1),.POLL_MS(1)) dut(
 .clk(clk),.rst(rst),.scl_in(1'b1),.sda_in(2'b11),.hold(1'b0),.active(),.tvp_resetb(),.scl_low(),.sda_low(),
 .init_done(init_done),.dev_err(dev_err),.status0(status0),.status1(status1),.status_valid(status_valid),.reinit0(),.reinit1());
initial begin
 repeat(4)@(posedge clk);@(negedge clk);rst=0;
 wait(dut.st==6&&dut.i2c.reads88==1);@(negedge clk);
 $display("POSITIVE status_valid=%0d dev_err=%0d status=%04x",status_valid[0],dev_err[0],status0);
 if(status_valid[0]!==1||dev_err[0]!==0||status0!==16'h000e)$fatal(1,"clean poll failed");
 wait(dut.st==6&&dut.i2c.failed88);@(negedge clk);
 $display("AFTER_NACK88 status_valid=%0d dev_err=%0d status=%04x",status_valid[0],dev_err[0],status0);
 $finish;
end
initial begin #100000;$fatal(1,"timeout");end
endmodule
