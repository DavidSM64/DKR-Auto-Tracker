from flask import Flask, jsonify
from flask_cors import CORS
import logging
import threading
import time

DEFAULT_SERVER_PORT = 4675

class DkrAutoTrackerServer:
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app) # Allow this server to work with local files.
        
        log = logging.getLogger('werkzeug')
        log.setLevel(logging.ERROR) # Only log errors.

        self.savedata = {}
        self.goldballoons = {}
        self.map = {}
        self.error = {}
        
        self.add_endpoint('/', '', self.get_heartbeat, methods=['GET'])
        self.add_endpoint('/savedata', 'savedata', self.get_savedata, methods=['GET'])
        self.add_endpoint('/goldballoons', 'goldballoons', self.get_goldballoons, methods=['GET'])
        self.add_endpoint('/map', 'map', self.get_map, methods=['GET'])
        self.add_endpoint('/servererror', 'servererror', self.get_servererror, methods=['GET'])
        
    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, methods=['GET'], *args, **kwargs):
        self.app.add_url_rule(endpoint, endpoint_name, handler, methods=methods, *args, **kwargs)

    def run(self):
        self.data_thread = threading.Thread(target=self._run)
        self.data_thread.daemon = True
        self.data_thread.start()
        
    def _run(self):
        self.app.run(port=DEFAULT_SERVER_PORT)

    def get_servererror(self):
        return jsonify(self.error)
        
    def get_map(self):
        return jsonify(self.map)
        
    def get_goldballoons(self):
        return jsonify(self.goldballoons)
        
    def get_savedata(self):
        return jsonify(self.savedata)
        
    def get_heartbeat(self):
        return {}

if __name__ == '__main__':
    server = DkrAutoTrackerServer()
    server.run()
    while input().lower() != 'quit':
        pass
