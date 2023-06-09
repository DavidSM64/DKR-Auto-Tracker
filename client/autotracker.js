/*
    ----- DKR Rando Automatic Tracker API -----
    
    class:
        DkrRandoAutoTracker(callbacks: Dictionary, port: int = 4675)
            Automatically tries to connect to the auto-tracker server. 
            Uses callbacks for when new information arrives. If a callback is not
                provided for a function, then it will do nothing.
            The port number can be anything really, as I chose 4675 to be the default arbitrarily.
    
    class methods:
        void setCallback(callback: string, callbackFunction: function?)
            Sets the callback key to the specified function. 
            Set `callbackFunction` to `null` if you want the callback to do nothing.
        void setInternalLoopDelay(delayInSeconds: number);
            Sets how many seconds (decimals included) to wait before getting new data 
            from the server. Also calls restartInternalLoop()
        void setPort(newPortNumber: int)
            Sets the port number to another integer.
        void setReconnectAttemptsCount(newCount: int)
            By default set to 5, but can be changed to set when the `reconnectFailed` 
            callback gets triggered.
        void stopInternalLoop()
            Stops the internal loop from getting new data.
        void restartInternalLoop()
            Restarts the internal loop that gets the data. Useful if an error occured.

    callbacks:
    {
              "connected" : void connected(firstConnection: boolean)
                                Gets triggered when the user connects to the auto-tracker server.
                                The first argument tells you if this is the first connection,
                                    or if this is a reconnect.
           "disconnected" : void disconnected()
                                Gets triggered when the user disconnected from the auto-tracker server.
        "reconnectFailed" : bool reconnectFailed()
                                Gets triggered after N (default 5) failed attempts at reconnecting. 
                                Useful if you want to stop the internal loop after so many attempts.
            "serverError" : bool serverError(errorData: Dictionary)
                                TODO: Implement this on the server! Supposed to tell the client about 
                                          server errors, but currently does nothing.
        "saveDataUpdated" : void saveDataUpdated(newSaveData: Dictionary)
                                Gets triggered when the save data has changed.
    "goldBalloonsUpdated" : void goldBalloonsUpdated(newGoldBalloonsData: Dictionary)
                                Gets triggered when the player has picked up a new gold balloon.
                                This is needed to detect if the player picked up Smokey's balloons.
             "mapUpdated" : void mapUpdated(newMapData: Dictionary)
                                Gets triggered when the map data has changed. Usually happens when the 
                                    player enters a new door/warp.
    }
*/

class DkrRandoAutoTracker {
    constructor(callbacks, port=4675) {
        // Map localhost pages to callbacks.
        this.pageCallbacks = {
            "savedata": callbacks["saveDataUpdated"],
            "goldballoons": callbacks["goldBalloonsUpdated"],
            "map": callbacks["mapUpdated"],
            "servererror": callbacks["serverError"]
        }
        this.pages = Object.keys(this.pageCallbacks);
        this.previousPageContents = {}
        for (var page of this.pages) {
            this.previousPageContents[page] = '{}'
        }
        this._connectedCallback = callbacks["connected"] ?? this._doNothing;
        this._disconnectedCallback = callbacks["disconnected"] ?? this._doNothing;
        this._reconnectFailedCallback = callbacks["reconnectFailed"] ?? this._doNothing;
        this.setReconnectAttemptsCount(5); // Do 5 attempts before calling the reconnectFailed callback.
        this.setPort(port);
        this._firstConnection = true;
        this._isCurrentlyConnected = false;
        this._loopTimeoutId = null;
        this.setInternalLoopDelay(1); // Wait a second before calling the loop again.
    }

    /*** Public methods ***/
    
    setCallback(callback, callbackFunction) {
        this.pageCallbacks[callback] = callbackFunction ?? this._doNothing
    }
    
    setInternalLoopDelay(delayInSeconds) {
        this._loopDelay = delayInSeconds * 1000;
        this.restartInternalLoop()
    }
    
    setReconnectAttemptsCount(newCount) {
        this._connectAttempts = 0
        this._reconnectAttempts = newCount
    }

    setPort(newPortNumber) {
      this.port = newPortNumber;
    }
    
    stopInternalLoop() {
        if(this._loopTimeoutId != null) {
            clearTimeout(this._loopTimeoutId);
            this._loopTimeoutId = null;
        }
    }

    restartInternalLoop() {
        this.stopInternalLoop();
        this._callLoop();
    }

    /*** Private methods ***/

    async _callCallbackIfDataHasChanged(pageName) {
        if(!this.pageCallbacks[pageName]) {
            // Don't even attempt to connect to the page if no callback has been set.
            return;
        }
        const response = await fetch(`http://localhost:${this.port}/${pageName}`);
        const responseJson = await response.json();
        const responseText = JSON.stringify(responseJson);
        if(this.previousPageContents[pageName] == responseText) {
            // Page has not updated, so just exit.
            return;
        }
        this.previousPageContents[pageName] = responseText; // Save this as the previous result.
        const callbackResult = this.pageCallbacks[pageName](responseJson);
        if(pageName == 'servererror' && callbackResult == true) {
            // Callback returned true, so stop the loop!
            throw "Stop Loop";
        }
    }
    
    // Default function for non-server callbacks
    _doNothing(){ 
        return false;
    }
    
    _callLoop() {
        this._loopTimeoutId = setTimeout(() => { this._loop(); }, this._loopDelay);
    }
    
    // Internal loop for updating pages.
    _loop() {
        if(this._loopTimeoutId == null) {
            return;
        }
        this._checkOnlineStatus().then(() => {
            if(this._loopTimeoutId == null) {
                return;
            }
            if (this._isOnline && !this._isCurrentlyConnected) {
                // Connected!
                this._connectedCallback(this._firstConnection);
                this._firstConnection = false;
                this._isCurrentlyConnected = true;
            } else if (!this._isOnline && this._isCurrentlyConnected) {
                // Disconnected!
                this._disconnectedCallback();
                this._isCurrentlyConnected = false;
                this._callLoop();
                return;
            }
            if(!this._isCurrentlyConnected) {
                // Try again later.
                this._callLoop();
                return;
            }
            var promises = []
            // Add promise for each page.
            for(var page of this.pages) {
                promises.push(this._callCallbackIfDataHasChanged(page));
            }
            Promise.all(promises).then((values) => {
                // All pages returned with no errors. So go for another loop.
                this._callLoop();
            }).catch((error) => {
                // Stop the loop and don't set another timeout!
                this._loopTimeoutId = null;
            });
        })
    }

    async _checkOnlineStatus() {
        await fetch(`http://localhost:${this.port}`).then((response) => {
            this._isOnline = true;
            this._connectAttempts = 0;
        }).catch(error => {
            this._isOnline = false;
            this._connectAttempts++;
            if(this._connectAttempts >= this._reconnectAttempts) {
                this._reconnectFailedCallback();
                this._connectAttempts = 0; // Back to zero.
            }
        });
    }
}
