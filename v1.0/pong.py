def run():
    print("Loading...")
    from random import randint
    from turtle import clearscreen
    from pynput.keyboard import Listener
    import threading
    from time import process_time, sleep
    from os import system, name
    from main import printOnWindow

    WIDTH, HEIGHT = 50, 30
    multiplayer = True
    rally = True

    BASE_FPS = 20
    PADDLE_LENGTH = 6

    fps = BASE_FPS


    clearScreen = lambda : system('cls' if name == 'nt' else 'clear')
    centerTo = lambda line, width : "{0:^{1}}".format(line, width)

    class Ball:
        def __init__(self, dir):
            self.collided = False
            self.x = WIDTH // 2
            self.y = HEIGHT // 2
            self.coord = (self.x, self.y)
            self.dir = dir
            # Dir 0 -> top left
            # Dir 1 -> top right
            # Dir 2 -> bottom left
            # Dir 3 -> bottom right
            
        def move(self, paddles):
            for paddle in paddles:
                if (self.x + 1, self.y) in paddle.body:
                    self.dir -= 1
                    self.collided = True
                if (self.x - 1, self.y) in paddle.body:
                    self.dir += 1
                    self.collided = True
                if (self.x, self.y + 1) in paddle.body:
                    self.dir -= 2
                    self.collided = True
                if (self.x, self.y - 1) in paddle.body:
                    self.dir += 2
                    self.collided = True
                    
            if self.y + 1 >= HEIGHT:
                self.dir -= 2
            if self.y - 1 < 0:
                self.dir += 2
            
            if not(multiplayer) and self.x >= WIDTH:
                self.dir -= 1
        
            if self.dir > 3 or self.dir < 0:
                self.dir = randint(0,3)
            
            if self.dir == 0:
                self.x -= 1
                self.y -= 1
            elif self.dir == 1:
                self.x += 1
                self.y -= 1
            elif self.dir == 2:
                self.x -= 1
                self.y += 1
            elif self.dir == 3:
                self.x += 1
                self.y += 1
            self.coord = (self.x, self.y)
            
            
    class Paddle:
        def __init__(self, x, len):
            self.body = []
            for i in range(len):
                self.body.append((x, (HEIGHT - len)//2 + i))
            self.score = 0
        
        def shift(self, up):
            for move in range(2):
                toploc = self.body[0]
                for i in range(len(self.body)):
                    if up and toploc[1] > 0:
                        self.body[i] = (self.body[i][0], self.body[i][1] - 1)
                        
                    elif (not up) and self.body[len(self.body)-1][1] <= HEIGHT - 2:
                        self.body[i] = (self.body[i][0], self.body[i][1] + 1)
                    


    ### KEYS ###

    class PressKey:
        def __init__(self, kind):
            if kind == "up":
                self.keys = ["Key.up"]
            elif kind == "down":
                self.keys = ["Key.down"]
            elif kind == "right":
                self.keys = ["Key.right"]
            elif kind == "left":
                self.keys = ["Key.left"]
                
            elif kind == "w":
                self.keys = ["\'w\'", "\'W\'"]
            elif kind == "s":
                self.keys = ["\'s\'", "\'S\'"]
            elif kind == "d":
                self.keys = ["\'d\'", "\'D\'"]
            elif kind == "a":
                self.keys = ["\'a\'", "\'A\'"]
                
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
        "w":        PressKey("w"),
        "s":        PressKey("s"),
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
        # Collect events until released
        with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
            listener.join()

    keyboardT = threading.Thread(target=keyInputs, args=(), daemon = True)
    keyboardT.start()                



    def printBoard(paddles, ball, paused = False):
        frame = []
        
        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        def makeChar(paddles, ball, x , y):
            char = ""
            isDrawn = False
            for paddle in paddles:
                if (x,y) in paddle.body:
                    char += "[]"
                    isDrawn = True
            if not isDrawn:
                if (x, y) == ball.coord:
                    char += "()"
                else:
                    char += "  "
            return char
        
        pauseMsg = "Paused"
        for y in range(HEIGHT):
            line = "|"
            if y == HEIGHT//2 and paused:
                for x in range((WIDTH*2 - (len(pauseMsg)))//4 + 1):
                    line += makeChar(paddles, ball, x , y)
                line += pauseMsg
                for x in range((WIDTH*2 - (len(pauseMsg)))//4):
                    line += makeChar(paddles, ball, x + ((WIDTH*2 + (len(pauseMsg)))//4 + 1) , y)
            else:
                for x in range(WIDTH):
                    line += makeChar(paddles, ball, x, y)
                
            line += "|"
            frame.append(line)
        
        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
            
        if multiplayer:
            frame.append(centerTo(f"Player 1 score: {paddles[0].score}", WIDTH + 1) + centerTo(f"Player 2 score: {paddles[1].score}", WIDTH + 1))
        else:
            frame.append(centerTo(f"Score: {paddles[0].score}", WIDTH*2+2))
        
        
        printOnWindow(frame, WIDTH)

    def printMenu(winner, keypos, multiplayer, baseMultiplayer, rally, scores):
        frame = []
        
        deathIcon = [
            "    ____                   ",
            "   / __ \____  ____  ____ _",
            "  / /_/ / __ \/ __ \/ __ `/",
            " / ____/ /_/ / / / / /_/ / ",
            "/_/    \____/_/ /_/\__, /  ",
            "                  /____/   "
        ]
        
        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        for y in range((HEIGHT - len(deathIcon) - 9)//2  ):
            frame.append("|" + centerTo("", WIDTH*2) + "|")
            
        if winner == 0:
            frame.append("|" + centerTo("Well played!", WIDTH*2) + "|")
            frame.append("|" + centerTo(f"You got {scores[0]} points!", WIDTH*2) + "|")
        elif winner == 3:
            frame.append("|" + centerTo("", WIDTH*2) + "|")
            if baseMultiplayer:
                frame.append("|" + centerTo(f"Player 1: {scores[0]}  Player 2: {scores[1]}", WIDTH*2) + "|")
            else:
                frame.append("|" + centerTo("", WIDTH*2) + "|")
        elif winner == 4:
            frame.append("|" + centerTo("", WIDTH*2) + "|")
            frame.append("|" + centerTo(f"Welcome to...", WIDTH*2) + "|")
        else:
            frame.append("|" + centerTo(f"Player {winner} wins!", WIDTH*2) + "|")
            frame.append("|" + centerTo("", WIDTH*2) + "|")
            
        frame.append("|" + centerTo("", WIDTH*2) + "|")
        
        for row in deathIcon:
            frame.append("|" + centerTo(row, WIDTH*2) + "|")
        
        frame.append("|" + centerTo("", WIDTH*2) + "|")
        if keypos == 0:
            frame.append("|" + centerTo("> Play  ", WIDTH*2) + "|")
        else:
            frame.append("|" + centerTo("  Play  ", WIDTH*2) + "|")
        
        
        
        frame.append("|" + centerTo("", WIDTH*2) + "|")
        
        if multiplayer:
            type="Multiplayer"
        else:
            type="Singleplayer"
            
        if keypos == 1:
            frame.append("|" + centerTo(f"> {type}  ", WIDTH*2) + "|")
        else:
            frame.append("|" + centerTo(f"  {type}  ", WIDTH*2) + "|")
        
        
        
        frame.append("|" + centerTo("", WIDTH*2) + "|")
        
        if multiplayer:
            if rally:
                type="Rally"
            else:
                type="Competitive"
            
            if keypos == 2:
                frame.append("|" + centerTo(f"> {type}  ", WIDTH*2) + "|")
            else:
                frame.append("|" + centerTo(f"  {type}  ", WIDTH*2) + "|")
        else:
            frame.append("|" + centerTo("", WIDTH*2) + "|")
        
        
            
        for y in range((HEIGHT - len(deathIcon) - 9)//2  ):
            frame.append("|" + centerTo("", WIDTH*2) + "|")
            
            
        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        printOnWindow(frame, WIDTH)



    firstgame = True

    gameloop = True
    while gameloop:
        
        paddles = [Paddle(2, PADDLE_LENGTH)]
        if multiplayer:
            paddles.append(Paddle(WIDTH - 3, PADDLE_LENGTH))
        
        
        resetBall = True
        onBallMove = False
        started = False
        winner = None

        while True:
            if firstgame:
                winner = 4
                break
            
            tick_start = process_time()
            
            if resetBall:
                ball = Ball(randint(0,3))
                fps = BASE_FPS    
                resetBall = False
                printBoard(paddles, ball)
                sleep(0.75)
                while not started:
                    for key in keys:
                        if keys[key].pressed:
                            started = True
                    sleep(0.1)
                tick_start = process_time()
            
            if keys["w"].pressed:
                paddles[0].shift(True)
            elif keys["s"].pressed:
                paddles[0].shift(False)
            
            if keys["up"].pressed:
                paddles[len(paddles)-1].shift(True)
            elif keys["down"].pressed:
                paddles[len(paddles)-1].shift(False) # If there are 2 paddles the arrows will run the second, otheriwse itll run the first
            
            if keys["space"].pressed:
                keys["space"].pressed = False
                printBoard(paddles, ball, True)
                while not keys["space"].pressed:
                    sleep(0.1)
                keys["space"].pressed = False
            
            
            if onBallMove:
                ball.move(paddles)
                onBallMove = False
            else:
                onBallMove = True
            
            if ball.x < 0 and onBallMove:
                if multiplayer:
                    paddles[1].score += 1
                else:
                    paddles[0].score -= 1
                resetBall = True
                
                    
            if ball.x >= WIDTH and onBallMove:
                paddles[0].score += 1
                if multiplayer:
                    resetBall = True
                else:
                    fps *= 1.25
                    
            if multiplayer and not rally:
                if paddles[0].score >= 10:
                    winner = 1
                    break
                elif paddles[1].score >= 10:
                    winner = 2
                    break
            elif (not multiplayer) and paddles[0].score >= 10:
                winner = 0
                break
            elif keys["esc"].pressed:
                keys["esc"].pressed = False
                winner = 3
                break
            
            if ball.collided:
                ball.collided = False
                fps *= 1.15
                    
            printBoard(paddles, ball)
                    
            sleep(max(1/fps - (process_time() - tick_start), 0))
            
        keypos = 0
        
        baseMultiplayer = multiplayer
        baseRally = rally
        
        while True:
            tick_start = process_time()
            
            firstgame = False
            
            if keys["w"].pressed or keys["up"].pressed:
                for key in keys:
                    keys[key].pressed = False
                keypos -= 1
                if keypos < 0:
                    if multiplayer:
                        keypos = 2
                    else:
                        keypos = 1
                        
            if keys["s"].pressed or keys["down"].pressed:
                for key in keys:
                    keys[key].pressed = False
                keypos += 1
                if (multiplayer and keypos > 2) or ((not multiplayer) and keypos > 1):
                    keypos = 0
                    
            
            if keys["space"].pressed:
                keys["space"].pressed = False
                if keypos == 0:
                    break
                elif keypos == 1:
                    if multiplayer:
                        multiplayer = False
                    else:
                        multiplayer = True
                elif keypos == 2:
                    if rally:
                        rally = False
                    else:
                        rally = True
            
            if keys["esc"].pressed:
                gameloop = False
                break
                        
            
            printMenu(winner, keypos, multiplayer, baseMultiplayer, rally, [paddle.score for paddle in paddles])
            
            sleep(max(1/fps - (process_time() - tick_start), 0))
        
        
    
    