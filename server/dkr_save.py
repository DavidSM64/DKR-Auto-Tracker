import json

NUM_WORLDS = 6 # 
MAX_NUM_LEVELS = 34
NUM_TROPHIES = 5

_levelStatus = [
    "Not Visited",
    "Visited",
    "Done",
    "Done (Silver Coins)"
]

_levelsSaveOrder = [
    "Walrus Boss",
    "Fossil Canyon",
    "Pirate Lagoon",
    "Ancient Lake",
    "Walrus Cove",
    "Hot Top Volcano",
    "Whale Bay",
    "Snowball Valley",
    "Crescent Island",
    "Fire Mountain",
    "EverFrost Peak",
    "Spaceport Alpha",
    "Spacedust Alley",
    "Greenwood Village",
    "Boulder Canyon",
    "Windmill Plains",
    "Smokey Castle",
    "Darkwater Beach",
    "Icicle Pyramid",
    "Frosty Village",
    "Jungle Falls",
    "Treasure Caves",
    "Haunted Woods",
    "DarkMoon Caverns",
    "Star City",
    "WizPig 1",
    "TrickyTops 1",
    "Sherbet Boss",
    "Dragon Boss",
    "TrickyTops 2",
    "Walrus 2",
    "Sherbet 2",
    "Dragon 2",
    "WizPig 2"
]

LevelsShortNames = {
    "Central Area" : "OW",
    "Walrus Boss" : "BL1",
    "Fossil Canyon" : "FC",
    "Pirate Lagoon" : "PL",
    "Ancient Lake" : "AL",
    "Walrus Cove" : "WC",
    "Hot Top Volcano" : "HTV",
    "Whale Bay" : "WB",
    "Snowball Valley" : "SV",
    "Crescent Island" : "CI",
    "Fire Mountain" : "FM",
    "EverFrost Peak" : "EP",
    "Spaceport Alpha" : "SPA",
    "Spacedust Alley" : "SDA",
    "Greenwood Village" : "GV",
    "Boulder Canyon" : "BC",
    "Windmill Plains" : "WP",
    "Smokey Castle" : "SMC",
    "Darkwater Beach" : "DWB",
    "Icicle Pyramid" : "IP",
    "Frosty Village" : "FV",
    "Jungle Falls" : "JF",
    "Treasure Caves" : "TC",
    "Haunted Woods" : "HW",
    "DarkMoon Caverns" : "DC",
    "Star City" : "SC",
    "WizPig 1" : "WIZ1",
    "TrickyTops 1" : "TR1",
    "Sherbet Boss" : "BU1",
    "Dragon Boss" : "SM1",
    "TrickyTops 2" : "TR2",
    "Walrus 2" : "BL2",
    "Sherbet 2" : "BU2",
    "Dragon 2" : "SM2",
    "WizPig 2" : "WIZ2"
}

TrophyStatus = [
    "None",
    "Bronze",
    "Silver",
    "Gold"
]

FILENAME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ.?    "

class DkrSave:
    def __init__(self, saveBytes):
        self.bits = ''.join([bin(b)[2:].zfill(8) for b in saveBytes]) # Turn the list of bytes into a bit string.
        self.readOffset = 0
        checksum = self._read_bits(16)
        self.levelStatus = {}
        for i in range(0, MAX_NUM_LEVELS):
            self.levelStatus[LevelsShortNames[_levelsSaveOrder[i]]] = self._parse_status(self._read_bits(2))
        tajFlags = self._read_bits(6) >> 3
        self.tajDone = {
            "Car":   self._is_bit_set(tajFlags, 0), 
            "Hover": self._is_bit_set(tajFlags, 1), 
            "Plane": self._is_bit_set(tajFlags, 2), 
        }
        self.trophies = [0] * NUM_TROPHIES
        for i in range(0, NUM_TROPHIES):
            self.trophies[(NUM_TROPHIES-1) - i] = TrophyStatus[self._read_bits(2)]
        bosses = self._read_bits(12) #self.bosses = self._read_bits(12)
        #self.worldBalloonCount = [0] * NUM_WORLDS
        for i in range(0, NUM_WORLDS):
            #self.worldBalloonCount[i] = self._read_bits(7)
            worldBalloonCount = self._read_bits(7)
            if i == 0:
                self.totalBalloonCount = worldBalloonCount
        self.ttAmuletCount = self._read_bits(3)
        self.wizpigAmuletCount = self._read_bits(3)
        #self.worldFlags = [0] * NUM_WORLDS
        for i in range(0, NUM_WORLDS):
            #worldFlags[i] = self._read_bits(16)
            worldFlags = self._read_bits(16)
            if i == 0: # Overworld
                self.overworldBalloonCount = (worldFlags & 0x4444).bit_count()
                
        keyFlags = (self._read_bits(8) >> 1) & 0xF
        self.keys = {
            "AL": self._is_bit_set(keyFlags, 0),
            "CI": self._is_bit_set(keyFlags, 1),
            "SV": self._is_bit_set(keyFlags, 2),
            "BC": self._is_bit_set(keyFlags, 3)
        }
        self.cutsceneFlags = self._read_bits(32)
        
        self._read_bits(1)
        
        self.filename = ""
        for i in range(0, 3): # Read filename (3 characters)
            self.filename += FILENAME_CHARS[self._read_bits(5)]
            
        del self.readOffset
        del self.bits
        
    def get_data_as_dict(self):
        return self.__dict__

    def _is_bit_set(self, val, index):
        mask = (1 << index)
        return (val & mask) == mask
    
    def _read_bits(self, numBits):
        val = int(self.bits[self.readOffset:self.readOffset+numBits], 2)
        self.readOffset += numBits
        return val
        
    def _parse_status(self, statusVal):
        return 0 if (statusVal < 2) else statusVal - 1
        
            

if __name__ == '__main__':
    with open('save.bin', 'rb') as f:
        saveData = DkrSave(f.read())
        print(saveData.get_data_as_dict())
