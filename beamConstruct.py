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
base_project = 'circle_base.beamp'
output_template = 'circle_speed{speed}_spacing{spacing}_hatch{hatch}.beamp'

# Sweep parameters
speeds = [100, 200, 300]              # Pen marking speed
spacings = [0.05, 0.1, 0.2]           # Hatch spacing
hatch_counts = [1, 3, 5]              # Hatch repetitions

# Element path to the hatch (adjust this as needed)
element_path = 'element1.hatch'  # Replace with actual element path from BeamConstruct

# Start BeamServer via CLI
print("Starting BeamServer...")
subprocess.call([BEAMSERVER_PATH, "1"])
time.sleep(2)  # Give time to start

def send_cmd(cmd, s):
    print(f"> {cmd}")
    s.sendall((cmd + '\n').encode())
    time.sleep(0.05)
    return s.recv(1024).decode()

# Main communication loop
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))

    for speed in speeds:
        for spacing in spacings:
            for hatch in hatch_counts:
                print(f"\nCreating config: Speed={speed}, Spacing={spacing}, HatchCount={hatch}")
                send_cmd(f'LOAD_PROJECT {base_project}', s)
                send_cmd(f'SET_PEN_PARAM pen1.mark_speed {speed}', s)
                send_cmd(f'SET_ELEMENT_PARAM {element_path}.spacing {spacing}', s)
                send_cmd(f'SET_ELEMENT_PARAM {element_path}.repetitions {hatch}', s)

                output_name = output_template.format(speed=speed, spacing=spacing, hatch=hatch)
                send_cmd(f'SAVE_PROJECT {output_name}', s)

    # Exit UI
    print("\nSending EXITUI...")
    send_cmd('EXITUI', s)


print("\n✅ All done!")