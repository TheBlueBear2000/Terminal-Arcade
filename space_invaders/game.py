print("Loading...")
from random import randint
from turtle import clearscreen
from pynput.keyboard import Listener
import threading
from time import process_time, sleep
from os import system, name

WIDTH, HEIGHT = 50, 30

class Rocket:
    def __init__(self, cornerX, cornerY):
        image = [
        "  /\  ",
        "±-||-±"
        ]
        self.body_image = []
        self.body_pos   = []
        for y, row in enumerate(image):
            self.body_image.append([])
            self.body_pos.append([])
            for x in range(len(row)//2):
                self.body_pos[y].append((cornerX + x, cornerY + y))
                self.body_image[y].append(image[y][x*2:x*2+1])
        
    def shift(self, left):
        for y, row in enumerate(self.body_pos):
            for x, point in enumerate(row):
                if left:
                    self.body_pos[y][x] = (point[0] - 1, point[1])
                else:
                    self.body_pos[y][x] = (point[0] + 1, point[1])
                    

class Bullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.im = ["/\\",
                   "||"]
                    
    
class Alien:
    def __init__(self, x, y, level):
        self.x, self.y = (x, x+1), y
        images = [
            " <> ",
            "-<>-",
            "~[]~",
            "/()\\",
            "±[]±",
            "[OO]",
            "{**}"
        ]
        self.im = images[level]
        
class AlienBullet:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.im = ["||",
                   "\/"]


class Wave:
    def __init__(self, lvl):
        self.left = False
        self.leftX = WIDTH // 4
        self.rightX = WIDTH // 4 * 3
        self.wave = []
        for y in range(HEIGHT//6):
            self.wave.append([])
            for x in range(WIDTH//4):
                self.wave[y].append(Alien(x*2 + (WIDTH//4),  y,  lvl))
            
    def move(self):
        if self.left:
            if self.leftX - 1 > 0:
                self.left -= 2
                for row in self.wave:
                    for alien in row:
                        if alien != None:
                            alien.x -= 2
            else:
                self.left = False
                for row in self.wave:
                    for alien in row:
                        if alien != None:
                            alien.y += 1
                            
        else:
            if self.rightX + 1 < WIDTH - 1:
                self.left += 2
                for row in self.wave:
                    for alien in row:
                        if alien != None:
                            alien.x += 2
            else:
                self.left = True
                for row in self.wave:
                    for alien in row:
                        if alien != None:
                            alien.y += 1
                            
    def isAlive(self):
        alive = False
        for row in self.wave:
            for alien in row:
                if alien != None:
                    alive = True
                    break
            if alive:
                break
        return alive
                            
                    

### KEYS ###
class PressKey:
    def __init__(self, kind):
        if kind == "up":
            self.keys = ["\'w\'", "\'W\'","Key.up"]
        elif kind == "down":
            self.keys = ["\'s\'", "\'S\'","Key.down"]
        elif kind == "right":
            self.keys = ["\'d\'", "\'D\'","Key.right"]
        elif kind == "left":
            self.keys = ["\'a\'", "\'A\'","Key.left"]
            
            
        elif kind == "space":
            self.keys = ["Key.space"]
        elif kind == "esc":
            self.keys = ["Key.esc"]
        else:
            raise Exception("Tried to create a key with an invalid type")
        
        self.pressed = False
        

keys = {
    "up":       PressKey("up"),
    "down":     PressKey("down"),
    "left":     PressKey("left"),
    "right":    PressKey("right"),
    "space":    PressKey("space"),
    "esc":      PressKey("esc")
}


def on_key_press(key):
    for keytype in keys:
        if str(key) in keys[keytype].keys:
            keys[keytype].pressed = True
    
        
def on_key_release(key):
    for keytype in keys:
        if str(key) in keys[keytype].keys and not (keytype == "space" or keytype == "esc"):
            keys[keytype].pressed = False


def keyInputs():
    with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

keyboardT = threading.Thread(target=keyInputs, args=(), daemon = True)
keyboardT.start()



rocket = Rocket(WIDTH//2 - 1,  HEIGHT - 3)
lvl = 0
wave = Wave(lvl)
bullets = []
alienBullets = []

while True:
    tick_start = process_time()
    
    if keys["left"].pressed:
        rocket.shift(True)
    if keys["right"].pressed:
        rocket.shift(False)
    if keys["up"].pressed:
        bullets.append(Bullet(rocket.body_pos[0][len(rocket.body_pos[0])//2][0]  ,  rocket.body_pos[0][0][1]))
        
    newBullets = []
    for i, bullet in enumerate(bullets):
        bullet.y -= 1
        for y, row in enumerate(wave.wave):
            for x, alien in enumerate(row):
                if alien != None:
                    if bullet.x in alien.x and bullet.y == alien.y:
                        wave[y][x] = None
                    else:
                        newBullets.append(bullet)
    bullets = newBullets
                        
                        
    for row in enumerate(wave.wave):
        for alien in enumerate(row):
            if alien != None:
                if randint(0,50) == 0:
                    alienBullets.append(AlienBullet(alien.x, alien.y+1))
    
    wave.move()
    
    
    
    
