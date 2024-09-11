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
    BASE_FPS = 20
    PADDLE_WIDTH = 7


    clearScreen = lambda : system('cls' if name == 'nt' else 'clear')
    centerTo = lambda line, width : "{0:^{1}}".format(line, width)

    class Ball:
        def __init__(self, dir, y, x):
            self.collided = False
            self.score = 0
            self.x = x
            self.y = y
            self.coord = (self.x, self.y)
            self.dir = dir
            # Dir 0 -> top left
            # Dir 1 -> top right
            # Dir 2 -> bottom left
            # Dir 3 -> bottom right
            
        def move(self, paddle, bricks, fps):
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
                    
            if self.y - 1 < 0:
                self.dir += 2
            if self.x <= 0:
                self.dir += 1
            if self.x >= WIDTH-1:
                self.dir -= 1
                
            for y, row in enumerate(bricks):
                for x, brick in enumerate(row):
                    if brick != None:
                        if (self.x + 1, self.y) in brick.parts:
                            bricks[y][x] = None
                            self.score += 1
                            self.dir -= 1
                            fps += 0.1
                        if (self.x - 1, self.y) in brick.parts:
                            bricks[y][x] = None
                            self.score += 1
                            self.dir += 1
                            fps += 0.1
                        if (self.x, self.y + 1) in brick.parts:
                            bricks[y][x] = None
                            self.score += 1
                            self.dir -= 2
                            fps += 0.1
                        if (self.x, self.y - 1) in brick.parts:
                            bricks[y][x] = None
                            self.score += 1
                            self.dir += 2
                            fps += 0.1
        
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
            return bricks, fps
                    
            
            
    class Paddle:
        def __init__(self, y):
            self.y = y
            self.x = WIDTH//2
            self.coord = (self.x, y)
            self.body = []
            for x in range(PADDLE_WIDTH):
                self.body.append(((WIDTH-PADDLE_WIDTH)//2 + x, self.y))

        def shift(self, left):
            for move in range(2):
                firstblock = self.body[0]
                lastblock = self.body[len(self.body)-1]
                for i in range(len(self.body)):
                    if left and firstblock[0] > 0:
                        self.body[i] = (self.body[i][0] - 1, self.body[i][1])
                        
                    elif (not left) and lastblock[0] < WIDTH - 1:
                        self.body[i] = (self.body[i][0] + 1, self.body[i][1])
                        

    class Block:
        def __init__(self, leftCoord):
            self.parts = []
            for x in range(2):
                self.parts.append((leftCoord[0] + x, leftCoord[1]))
            


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



    def printBoard(paddle, ball, bricks, score, paused = False):
        frame = []
        
        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        
        def makeChar(paddle, ball, bricks, x , y):
            char = ""
            if (x,y) == ball.coord:
                char += f"\033[1;39m(){colour}"
            elif y > 3 and y <= 11:
                if bricks[y-4][x//2] != None:
                    if x%2 == 0:
                        char += "[_"
                    else:
                        char += "_]"
                else:
                    char += "  "
            elif (x,y) in paddle.body:
                char += "[]"
            else:
                char += "  "
            return char
        
        for y in range(HEIGHT):
            line = "|"
            if y > 11:
                colour = "\033[1;39m"
            elif y > 9:
                colour = "\033[1;33m"
            elif y > 7:
                colour = "\033[1;32m"
            elif y > 5:
                colour = "\033[1;33m"
            elif y > 3:
                colour = "\033[1;31m"
            else:
                colour = "\033[1;39m"
            line += colour
            if paused and y == HEIGHT//2:
                pauseMsg = "Paused"
                for x in range((WIDTH-len(pauseMsg))//2+2):
                    line += makeChar(paddle, ball, bricks, x , y)
                line += pauseMsg
                for x in range((WIDTH-len(pauseMsg))//2+1):
                    line += makeChar(paddle, ball, bricks, x + ((WIDTH*2 + (len(pauseMsg)))//4 + 1) , y)
            else:
                for x in range(WIDTH):
                    line += makeChar(paddle, ball, bricks, x , y)
                
                
            line += "\033[1;39m|"
            frame.append(line)

        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        frame.append(centerTo(f"Score: {score}", WIDTH*2+2))
        
        printOnWindow(frame, WIDTH)



    def printMenu(score, win, isFlash):
        frame = []
        
        deathIcon = [
            "\033[1;31m______   ______ _______ _______ _     _  _____  _     _ _______",
            "\033[1;32m|_____] |_____/ |______ |_____| |____/  |     | |     |    |   ",
            "\033[1;33m|_____] |    \_ |______ |     | |    \_ |_____| |_____|    |   "
        ]
        
        
        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        for y in range((HEIGHT-len(deathIcon))//2-2):
            frame.append("|" + centerTo("",WIDTH*2) + "|")
            
        if win:
            frame.append("|" + centerTo("YOU WIN!",WIDTH*2) + "|")
        else:
            frame.append("|" + centerTo("Thank you for playing...",WIDTH*2) + "|")
        frame.append("|" + centerTo("",WIDTH*2) + "|")
        for y in range(len(deathIcon)):
            if isFlash:
                frame.append("|" + centerTo(deathIcon[y],WIDTH*2+7) + "\033[1;39m|")
            else:
                frame.append("|" + centerTo("",WIDTH*2) + "|")
        frame.append("|" + centerTo("",WIDTH*2) + "|")
        frame.append("|" + centerTo(f"Score: {score}",WIDTH*2) + "|")
        frame.append("|" + centerTo("",WIDTH*2) + "|")
        frame.append("|" + centerTo("Press SPACE to play again",WIDTH*2) + "|")
            
        for y in range((HEIGHT-len(deathIcon))//2-4):
            frame.append("|" + centerTo("",WIDTH*2) + "|")
            
        line = "+"
        for x in range(WIDTH):
            line += "--"
        line += "+"
        frame.append(line)
        
        printOnWindow(frame, WIDTH)


    gameloop = True
    while gameloop:
        
        bricks = []
        for y in range(8):
            bricks.append([])
            for x in range(WIDTH//2):
                bricks[y].append(Block((x*2, y + 3)))
                
        fps = BASE_FPS
        paddle = Paddle(HEIGHT - 3)
        moveBall = True
        newBall = False
        ball = Ball(randint(0,1), paddle.y - 2, paddle.body[len(paddle.body)//2][0])
        ballPauseTimer = 0
        started = False
        
        while True:
            tick_start = process_time()
            
            if newBall:
                ball.x = paddle.body[len(paddle.body)//2][0]
                ball.y = paddle.y - 2
                ball.coord = (ball.x, ball.y)
                ball.dir = randint(0,1)
                ballPauseTimer = 10
                ball.score -= 5
                fps = BASE_FPS
                newBall = False
            
            if keys["left"].pressed:
                paddle.shift(True)
                started = True
            if keys["right"].pressed:
                paddle.shift(False)
                started = True

            if started:
                if moveBall:
                    if ballPauseTimer <= 0:
                        bricks, fps = ball.move(paddle, bricks, fps)
                        moveBall = False
                    else:
                        ballPauseTimer -= 1
                        ball.x = paddle.body[len(paddle.body)//2][0]
                        ball.coord = (ball.x, ball.y)
                else:
                    moveBall = True
                
            if ball.y >= HEIGHT:
                newBall = True
                
            win = True
            for row in bricks:
                for brick in row:
                    if brick != None:
                        win = False
                        break
                if win == False:
                    break
            if win:
                break
            
            if keys["esc"].pressed:
                keys["esc"].pressed = False
                win = False
                break
                
            # Pause
            if keys["space"].pressed:
                keys["space"].pressed = False
                printBoard(paddle, ball, bricks, ball.score, True)
                while not keys["space"].pressed:
                    sleep(0.1)
                keys["space"].pressed = False
                
            printBoard(paddle, ball, bricks, ball.score)
            
            
            sleep(max(1/fps  -  (process_time() - tick_start), 0.05))

        isFlash = True
        while True:
            tick_start = process_time()
            
            if keys["space"].pressed:
                keys["space"].pressed = False
                break
            if keys["esc"].pressed:
                gameloop = False
                break
            
            printMenu(ball.score, win, isFlash)
            
            if isFlash:
                isFlash = False
            else:
                isFlash = True
            
            sleep(max(0.5  -  (process_time() - tick_start), 0.05))
            