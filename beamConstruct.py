import socket
import time
import subprocess
import os

# BeamServer Config
HOST = "localhost"
PORT = 11350

# BeamServer executable path (adjust if installed elsewhere)
BEAMSERVER_PATH = r"C:\Program Files\HALsoftware\Beamserver.exe"

# Project settings
base_project = r"C:\Users\twardowski.6a\Documents\GlassCutting\2025-04-17 messing With Beamserver\BayesianTemplate.beamp"

#Trial Settings
trial_number = "011"
laser_speed = 35.5 #mm/s
repeats = 66
hatch_distance = .012

# Names in the beamproject of the elements
elements = [
    "Circle 1",
    "Circle 2",
    "Circle 3",
    "Circle 4",
    "Rectangle 1",
    "Rectangle 2",
    "Rectangle 3",
    "Rectangle 4",
]



def send_cmd(cmd, s, expect_response = True):
    #print(f"> {cmd}") #Uncomment line to see commands being sent
    s.sendall((cmd + '\n').encode())
    time.sleep(0.05)
    if expect_response:
        return s.recv(1024).decode()


def generateBeampFile(trial_number,laser_speed,repeats,hatch_distance,outputFileDirectory):
    '''
    trial_number will be written as label on beam path and as saved file name
    laser_speed in mm/s
    repeats 0 marks the sample only one time, 4 will scan over the sample 5 times
    hatch_distance distance between interior hatches  
    '''
    # Start BeamServer via CLI
    print("Starting BeamServer...")
    # The command parameter 1 – show drawing area (the big area in the middle where vector data are drawn) adds to 524288 – the warning-dialogue on start-up is disabled; so the parameter desired is 524289
    # This is literally just addition of parameters, this is the dumbest way of flagging parameters into CLI i've ever seen
    subprocess.Popen(
        [r"C:\Program Files\HALsoftware\BeamServer.exe", f"{524288+1+2+4+8}"],
        cwd=r"C:\Program Files\HALsoftware",
    )
    time.sleep(2)  # Give time to start
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))


        print(send_cmd(f'CmdLoadPrj {base_project}', s))
        time.sleep(1)

        #Lets map out the ID of each Hatch
        name_uid_map = {}
        index = 0

        while True:
            # Retrieve the element name at the current index
            name_response = send_cmd(f"CmdListName {index}",s)
            if name_response.startswith("ERROR"):
                break  # No more elements
            name = name_response.split("\n")[1].strip()

            # Retrieve the UID at the same index
            uid_response = send_cmd(f"CmdListUID {index}",s)
            if uid_response.startswith("ERROR"):
                break  # No more UIDs
            uid = uid_response.split("\n")[1].strip()

            # Map the name to the UID
            name_uid_map[name] = uid
            index += 1


        #Configure Hatch for only the hatches
        for elementName,id in name_uid_map.items():
            #Set Repeats
            if "Label" not in elementName:
                send_cmd(f"CmdSelEntName {elementName}",s )
                time.sleep(.05)
                send_cmd(f"CmdSetLoopRepeat {repeats}",s)  
            #Set Hatch spacing
            if "Hatch" in elementName:
                send_cmd(f"CmdSetHatchDist {hatch_distance*1000}",s)
                send_cmd("CmdSetHatchStyle inner",s)
                send_cmd(f"CmdSetHatch {id}",s) 
     

        #Set Pen speed
        send_cmd(f"CmdSetPenMSpeed 0 {laser_speed*1000}",s) #This command takes speed in units of microns per second

        # Set Label Mark Name
        send_cmd("CmdSelEntName Label", s)
        send_cmd(f"CmdSetElemText {trial_number}", s)

        #Save new Trial
        output_name = os.path.join(outputFileDirectory,f"{trial_number}.beamp")
        send_cmd(f'CmdSavePrj {output_name}', s)

        #Uncomment to test commands
        # while True:
        #     i = input("Enter command:")
        #     print(send_cmd(f"{i}", s))

        # Exit UI
        print("\nSending EXITUI...")
        send_cmd('ExitUI', s,expect_response=False)

#ouputDirectory = "C:\\Users\\twardowski.6a\\Documents\\GlassCutting\\2025-04-17 messing With Beamserver\\"

#path = r"C:\Users\twardowski.6a\Documents\GlassCutting\2025-04-27\Templates"
#generateBeampFile(56,20,333,.012,path)

