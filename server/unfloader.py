# TODO:
# * Support Linux! (Only Windows is supported at the moment)
# * Download UNFLoader automatically, instead of including the binary in the repo?

# Windows specific stuff:
from winpty import PtyProcess
NEWLINE = '\r\n'

import os
import threading
import re

# Debug Options
_PRINT_OUTPUT_BYTES = False

_UNFLOADER_EXE = 'UNFLoader.exe'

class NoProgramException(Exception):
    pass
class RunOnMainThreadException(Exception):
    pass
class NotStartedException(Exception):
    pass
    

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

class UNFLoader:
    def __init__(self, callbacks={}):
        if not os.path.exists(_UNFLOADER_EXE):
            raise NoProgramException("UNFLoader could not be found in the working directory. Aborting!")
        self._proc = None
        self._uploadRomMode = False
        self._callbacks = callbacks
        
    def add_callback(self, callbackName, callbackFunc):
        self._callbacks[callbackName] = callbackFunc
        
    def start(self, romPath=None):
        if self._proc != None:
            return
        self._proc = PtyProcess.spawn(self._get_cmd(romPath))
        
    def restart(self, romPath=None):
        try:
            self._proc.close()
        except Exception:
            pass
        self._proc = PtyProcess.spawn(self._get_cmd(romPath))
        self.loop()
        
    def _get_cmd(self, romPath):
        if romPath != None and self._uploadRomMode:
            return [_UNFLOADER_EXE, "-b", "-r", romPath, "-d"]
        else:
            return [_UNFLOADER_EXE, "-b", "-d"]
    
    def _preprocess_line_into_lines(self, line):
        while line.endswith('\n') or line.endswith('\r'):
            line = line[:-1] # Remove ending newline
        line = line.replace('\r\n', '\n') # Convert Windows newline to Unix newline 
        line = ansi_escape.sub('\n', line) # Replaces all ansi commands with newlines.
        if '\x07' in line:
            line = line[line.rindex('\x07')+1:] # Removes some prefix stuff that I don't use.
        lines = line.split('\n') # Split string into list based on unix newlines.
        lines = [x for x in lines if x] # Remove all empty entries 
        return lines
            
    def _handle_line(self, line):
        lines = self._preprocess_line_into_lines(line)
        for line in lines:
            if line.startswith('Wrote ') and 'bytes to ' in line:
                binaryFilePath = line[line.index("'")+1:line.rindex("'")]
                if 'binary' in self._callbacks:
                    with open(binaryFilePath, 'rb') as f:
                        data = f.read()
                        self._callbacks['binary'](data)
                os.remove(binaryFilePath)
            else:
                if 'text' in self._callbacks:
                    self._callbacks['text'](line)
                    
    # Note: This needs to be run in another thread!
    def loop(self):
        if threading.current_thread() is threading.main_thread():
            raise RunOnMainThreadException("You must not run UNFLoader.loop() on the main thread!")
        if self._proc == None:
            raise NotStartedException("You must call UNFLoader.start() before running the loop!")
        while self._proc.isalive():
            try:
                line = self._proc.readline()
                if _PRINT_OUTPUT_BYTES:
                    print(line.encode('utf-8'))
                self._handle_line(line)
            except (EOFError, ConnectionAbortedError):
                break
