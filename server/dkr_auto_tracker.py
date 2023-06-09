from server import DkrAutoTrackerServer
from dkr_save import DkrSave
from unfloader import UNFLoader

from appJar import gui
import os
import re

levelShortNames = [
    "OW",
    "BL1",
    "DF",
    "FC",
    "PL",
    "AL",
    "WC",
    "HTV",
    "WB",
    "SV",
    "CI",
    "FM",
    "DD",
    "EP",
    "SI",
    "SPA",
    "HSG",
    "SDA",
    "GV",
    "BC",
    "WP",
    "FE",
    "CS",
    "TSS",
    "SM",
    "SMC",
    "DWB",
    "IP",
    "FV",
    "JF",
    "TC",
    "HW",
    "DC",
    "SC",
    "TR",
    "FFL",
    "OS",
    "WIZ1",
    "TR1",
    "OBG",
    "BU1",
    "SM1",
    "WIZM",
    "AMW",
    "WMTT",
    "RS",
    "TR2",
    "DDT",
    "SMT",
    "SIT",
    "DFT",
    "FFLT",
    "BL2",
    "BU2",
    "SM2",
    "WIZ2",
    "PS",
    "TRA",
    "SMA",
    "BLA",
    "WIZ1A",
    "BUA",
    "WIZ2A",
    "LB",
    "LBB"
]

unfloader = UNFLoader()
server = DkrAutoTrackerServer()
app = None
lastFileIndex = -1
PROGRAM_TITLE = "DKR Auto Tracker Server"
COLOR_BG = '#222222'
reconnectAttempts = 0

###################################################################

# Status colors
COLOR_NORMAL = '#E0E0E0'
COLOR_GOOD = '#44C044'
COLOR_BAD = '#F08888'
COLOR_ACTION = '#F0F888'
status = "Not Connected"

def set_status_text_and_color(newStatus, color):
    app.setLabel("status", currentStatus)
    app.setLabelFg("status", color)

def set_status(newStatus, color=COLOR_NORMAL):
    global currentStatus
    currentStatus = newStatus
    app.queueFunction(set_status_text_and_color, currentStatus, color)
    
###################################################################

def unfloader_thread():
    unfloader.loop()
    
def unfloader_disconnected(arg):
    set_status("Disconnected", COLOR_BAD)
    try_reconnect()
    
def restart_unfloader():
    app.threadCallback(unfloader.restart, unfloader_disconnected)
    
def try_reconnect():
    global reconnectAttempts
    reconnectAttempts += 1
    set_status("Reconnecting... (" + str(reconnectAttempts) + " attempt" + ("s" if reconnectAttempts != 1 else "") + " so far)")
    app.after(1000, restart_unfloader)

def status_ready():
    global reconnectAttempts
    reconnectAttempts = 0
    set_status("Ready", COLOR_GOOD)

###################################################################

def binary_handler(binData):
    global lastFileIndex
    dataTag = binData[0:4].decode('utf-8')
    if dataTag == 'SAVE':
        saveData = DkrSave(binData[4:44])
        if saveData.cutsceneFlags == 0xFFFFFFFF and saveData.totalBalloonCount == 127:
            # This is an erased file. Don't send it!
            return
        server.savedata = saveData.get_data_as_dict()
        fileIndex = binData[44]
        server.savedata["fileIndex"] = fileIndex
        if fileIndex != lastFileIndex:
            server.goldballoons = {}
            server.map = {}
            lastFileIndex = fileIndex
    elif dataTag == 'GOLD': # Gold balloon data
        flag = int.from_bytes(binData[4:6], byteorder='big')
        worldId = binData[6]
        levelId = binData[7]
        levelName = levelShortNames[levelId]
        
        if not levelName in server.goldballoons:
            server.goldballoons[levelName] = []
        
        server.goldballoons[levelName].append({
            "flag": flag
        })
    elif dataTag == 'MAPW': # Map warp data
        level = levelShortNames[binData[4]]
        levelToWarpTo = levelShortNames[binData[5]]
        
        if not level in server.map:
            server.map[level] = []
        
        if not levelToWarpTo in server.map[level]:
            server.map[level].append(levelToWarpTo)

def text_handler(text):
    print(text)
    if text.startswith('Debug mode started'):
        status_ready()

def gui_init():
    unfloader.start()
    unfloader.add_callback('binary', binary_handler)
    unfloader.add_callback('text', text_handler)
    app.addLabel("status", 'Not Started')
    app.threadCallback(unfloader_thread, unfloader_disconnected)
    server.run()
    
###################################################################
    
def main():
    global app
    app = gui(handleArgs=False)
    app.setTitle(PROGRAM_TITLE)
    app.setBg(COLOR_BG)
    app.setSize(300, 100)
    app.setStartFunction(gui_init)
    app.go()

if __name__ == '__main__':
    main()