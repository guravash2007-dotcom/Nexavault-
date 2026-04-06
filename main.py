import webview
import os
from tkinter import filedialog, Tk
from engine import NexaEngine

class NexaAPI:
    def __init__(self):
        self.engine = NexaEngine()

    def open_file(self):
        root = Tk()
        root.withdraw()
        path = filedialog.askopenfilename()
        root.destroy()
        return path

    def shatter_action(self, path, pw):
        return self.engine.shatter(path, pw)

    def get_history(self, pw):
        return self.engine.get_history(pw)

    def recover_action(self, fid, name, orig_dir, pw):
        # Now uses the stored original directory
        return self.engine.reconstitute(fid, name, orig_dir, pw)

if __name__ == '__main__':
    api = NexaAPI()
    webview.create_window(
        'NEXA VAULT PRO', 
        'templates/index.html', 
        js_api=api, 
        width=1100, 
        height=750,
        resizable=False
    )
    webview.start()
    
