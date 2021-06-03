from .dfplayer import Player
from utime import sleep_ms
from machine import Pin

class ScanPlayer(Player):
    def __init__(self, folders=10, scan=True, *a, **k ):
        if 'busy_pin' not in k: 
            k['busy_pin'] = Pin(4) # configure D3/GPIO0 as default busy pin
        super().__init__(*a, **k)
        if folders > 99:
            raise AssertionError("Max 99 folders (00-99)")
        self.folders = folders
        self.tracks = None
        self.recent = {}
        if scan:
            self.scan()
        # TODO handle resetting volume after scan
    
    def scan(self):
        self.awaitconfig()
        self.volume(0.1)
        self.awaitvolume()
        self.tracks = {}
        for folder_num in range(0,self.folders): 
            for file_num in range(0,256):                # max tracks-per-folder supported by dfplayer
                self.play(folder_num,file_num)
                if self.playing():
                    if not(folder_num in self.tracks):
                        self.tracks[folder_num] = []
                    self.tracks[folder_num].append(file_num)
                    continue
                else:
                    break
        self.volume(1.0) # TODO find principled way to set this, or remove volume control from scan
    
    def play_next(self, folder_num, wrap=True):
        if self.tracks is not None:
            if folder_num in self.tracks:
                files = self.tracks[folder_num]
                if folder_num in self.recent:
                    file_num = self.recent[folder_num]
                    file_num = (file_num + 1)
                    if file_num == len(files):
                        if wrap:
                            file_num = file_num % len(files) # increment with wraparound
                        else:
                            return False
                else:
                    file_num = 0
                self.recent[folder_num] = file_num
                self.play(folder_num, file_num)
                return True
            else:
                raise AssertionError("Scan found no '{}' folder".format(folder_num))
        else:
            raise AssertionError("No scan available, run player.scan() first.")

    def finish_all(self, folder_num):
        if self.tracks is not None:
            if folder_num in self.tracks:
                folder_tracks = self.tracks[folder_num]
                for track_num in folder_tracks:
                    self.finish(folder_num, track_num)
            else:
                raise AssertionError("Scan found no '{}' folder".format(folder_num))
        else:
            raise AssertionError("No scan available, run player.scan() first.")