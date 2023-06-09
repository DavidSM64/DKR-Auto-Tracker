# DKR Auto Tracker (Server and Client)

Supported Flashcarts:
* Everdrive X7
* Everdrive 3.0
* 64Drive HW2
* SC64

Note: So far, only the X7 has been tested.

----

## Client

The main piece of code is `autotracker.js`, which you should be able to include into any html page.

See `client.html` for an example of how to use `autotracker.js`, and `map.js`

----

## Server

Note: Only Windows is supported at this time.

Run `python dkr_auto_tracker.py`. It *should* just work if you have the USB connected from your everdrive.

## Python Packages

#### Windows

`pip install pywinpty appjar pyinstaller`

* pywinpty - For simulating a terminal, required for reading output of UNFLoader in real time.
* appjar - For the GUI interface.
* pyinstaller - For distributing the final output to an exe.


## Distributing

`pyinstaller --clean dkr_auto_tracker.spec`

This should create a `/dist/` directory with the files to be distributed. Make sure UNFLoader.exe is in there, otherwise the program won't start.

----