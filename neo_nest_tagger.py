#!/usr/bin/env python3
# neo_nest_tagged.py — shareware
# drag-drop folder, watch iron rain charge to 0 0 8 0 0
import os, struct, hashlib, time, threading, tkinter as tk
from tkinter import filedialog
import random

CHARS = list('))))))))1((((((((')

def make_nest(original):
    h = hashlib.sha256(original).digest()
    parent = struct.unpack('>I', h[:4])[0]
    header = struct.pack('>4sBBH', b'((1)', 1, 1, 0)
    vec = [0,0,8,0,0]  # charge vector
    shell = struct.pack('>5b', *vec) + struct.pack('>I', parent) + struct.pack('>H', int(time.time())%65536)
    shells = shell + b'\x00'*77
    return header + shells + struct.pack('>I', 100) + b'\x00'*28

class RainApp:
    def __init__(self, root):
        self.root = root
        root.title("NEST // iron rain")
        root.configure(bg='black')
        self.canvas = tk.Canvas(root, width=800, height=600, bg='black', highlightthickness=0)
        self.canvas.pack()
        self.btn = tk.Button(root, text="SELECT FOLDER", command=self.pick, bg='#003300', fg='#00ff00')
        self.btn.pack(pady=10)
        self.drops = []
        self.running = True
        self.animate()
    
    def animate(self):
        self.canvas.delete('all')
        # spawn new drops
        if random.random() < 0.3:
            x = random.randint(0, 780)
            self.drops.append({'x':x, 'y':0, 'char': random.choice(CHARS), 'speed': random.randint(4,8)})
        for d in self.drops[:]:
            d['y'] += d['speed']
            self.canvas.create_text(d['x'], d['y'], text=d['char'], fill='#00ff41', font=('Courier',14))
            if d['y'] > 600:
                self.drops.remove(d)
        if self.running:
            self.root.after(30, self.animate)
    
    def pick(self):
        folder = filedialog.askdirectory()
        if not folder: return
        threading.Thread(target=self.tag_folder, args=(folder,), daemon=True).start()
    
    def tag_folder(self, folder):
        count = 0
        for root, _, files in os.walk(folder):
            for f in files:
                if not f.lower().endswith(('.png','.jpg','.jpeg','.mp4','.wav','.pdf','.webp')):
                    continue
                path = os.path.join(root,f)
                with open(path,'rb') as r: data = r.read()
                if b'NEST' in data[-200:]: continue
                nest = make_nest(data)
                with open(path,'ab') as w: w.write(b'NEST'+nest)
                count += 1
                # flash charge vector
                self.canvas.create_text(400, 300, text='0 0 8 0 0', fill='#ff0040', font=('Courier',32))
        self.canvas.create_text(400, 550, text=f'WAKE UP — {count} files tagged', fill='#00ff41', font=('Courier',16))

if __name__ == '__main__':
    root = tk.Tk()
    app = RainApp(root)
    root.mainloop()
