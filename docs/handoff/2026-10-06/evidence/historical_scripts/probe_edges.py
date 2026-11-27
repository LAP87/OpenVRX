from pathlib import Path
import json,subprocess
ROOT=Path('/home/owner/Projekt/DIY_Drone_Lab/projects/OpenVRX-repos')
CORE=ROOT/'OpenVRX-Core';WORK=Path(__file__).resolve().parent
BIN=CORE/'.tools/iverilog/bin'
GENLOCK=r"""
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
"""
I2C=r"""
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
"""

def run(top,text,rtl,params=()):
 (WORK/f'{top}.v').write_text(text)
 subprocess.run([str(BIN/'iverilog'),'-g2012','-s',top,'-o',str(WORK/f'{top}.vvp'),*params,str(CORE/'gateware/rtl'/rtl),str(WORK/f'{top}.v')],check=True,capture_output=True,text=True)
 return subprocess.run([str(BIN/'vvp'),'-n',str(WORK/f'{top}.vvp')],capture_output=True,text=True,check=True,timeout=10).stdout

g=run('genlock_tb',GENLOCK,'genlock_timing.v')
frames=[int(l.split()[1]) for l in g.splitlines() if l.startswith('FRAME')]
# Discard the frame-start value held through reset, before measuring complete frames.
steady_frames=frames[1:]
periods=[b-a for a,b in zip(steady_frames,steady_frames[1:])]
assert periods[:2]==[168,168] and min(periods)<154,(frames,periods)
i0=run('i2c_tb',I2C,'i2c_master.v')
i1=run('i2c_tb',I2C,'i2c_master.v',['-Pi2c_tb.STUCK=1'])
assert 'busy=0 completions=1' in i0,i0
assert 'busy=1 completions=0' in i1,i1
result={'genlock':{'frame_cycles':frames,'period_cycles':periods,'natural_locked_min_cycles':154},'i2c_normal_nack':i0.strip(),'i2c_clock_held_low':i1.strip()}
print(json.dumps(result,indent=2))
(WORK/'edge_probe_results.json').write_text(json.dumps(result,indent=2))
