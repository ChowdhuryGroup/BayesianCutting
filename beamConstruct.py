import socket
import time
import subprocess
import os

# BeamServer Config
HOST = 'localhost'
PORT = 11350

# BeamServer executable path (adjust if installed elsewhere)
BEAMSERVER_PATH = r'C:\Program Files\HALsoftware\Beamserver.exe'

# Project settings
base_project = r'C:\Users\twardowski.6a\Documents\GlassCutting\2025-04-17 messing With Beamserver\baseTemplate.beamp'
output_template = 'circle_speed{speed}_spacing{spacing}_hatch{hatch}.beamp'

# Sweep parameters
speeds = [100, 200, 300]              # Pen marking speed
spacings = [0.05]           # Hatch spacing
hatch_counts = [1]              # Hatch repetitions

# Element path to the hatch (adjust this as needed)
element_path = 'element1.hatch'  # Replace with actual element path from BeamConstruct

# Start BeamServer via CLI
print("Starting BeamServer...")
#The command parameter 1 – show drawing area (the big area in the middle where vector data are drawn) adds to 524288 – the warning-dialogue on start-up is disabled; so the parameter desired is 524289
#This is literally just addition of parameters, this is the dumbest way of flagging parameters into CLI i've ever seen
subprocess.Popen([
    r"C:\Program Files\HALsoftware\BeamServer.exe",
    "524290"
],
cwd=r"C:\Program Files\HALsoftware"
)
time.sleep(2)  # Give time to start

def send_cmd(cmd, s, expect_response = True):
    print(f"> {cmd}")
    s.sendall((cmd + '\n').encode())
    time.sleep(0.05)
    if expect_response:
        return s.recv(1024).decode()

# Main communication loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))


    print(send_cmd(f'CmdLoadPrj {base_project}', s))
    print(send_cmd("CmdAddCircle",s))

    output_name = r'C:\Users\twardowski.6a\Documents\GlassCutting\2025-04-17 messing With Beamserver\test.beamp'
    send_cmd(f'CmdSavePrj {output_name}', s)

    # Exit UI
    print("\nSending EXITUI...")
    #send_cmd('ExitUI', s,expect_response=False)


print("\n✅ All done!")