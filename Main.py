import pygame
import sys
from pygame.locals import*
import random as rdm
import cv2
import functions
import time

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (90, 90, 90)
DARKGRAY = (30, 30, 30)
DARKBLUE = (0, 5, 92)
DARKPURPLE = (97, 0, 83)
DARKGREEN = (0, 98, 25)
RED = (255,100, 100)
window_height = 400
window_width = 600

display_surf = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Hockey")

background = pygame.image.load("./src/hockeyBG-2.png").convert()
background = pygame.transform.rotate(background, 90)
background = pygame.transform.scale(background, (window_width, window_height))

fps = 200
fps_clock = pygame.time.Clock()
cap = cv2.VideoCapture(0)
detector = functions.handDetector()

class Paddle():
    def __init__(self, x, w, h):
        self.x = x
        self.y = window_height / 2
        self.w = w
        self.h = h
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self):
        pygame.draw.rect(display_surf, GRAY, self.rect)
    
    def detectMove(self, cy):
        if cy >= window_height - (self.h / 2) - 15:
            cy = window_height - (self.h / 2) - 15
        if cy <= self.h / 2 + 15:
            cy = self.h / 2 + 15
        self.rect.centery = cy
        self.draw()

class AutoPaddle(Paddle):
    def __init__(self, x, w, h, speed, ball):
        super().__init__(x, w, h)
        self.speed = speed
        self.ball = ball
    
    def move(self):
        if self.ball.dirX == 1:
            if (self.rect.centery < self.ball.rect.centery) and (self.rect.bottom < window_height - self.ball.h + 2.5):
                self.rect.y += self.speed
            if (self.rect.centery > self.ball.rect.centery) and (self.rect.top > self.ball.h - 2.5):
                self.rect.y -= self.speed

class AutoPaddleU(Paddle):
    def __init__(self, x, w, h, speed, ball):
        super().__init__(x, w, h)
        self.speed = speed
        self.ball = ball
    
    def move(self):
        if self.ball.dirX == -1:
            # print(f'Paddle: {self.rect.centery}, ball: {self.ball.y}, dir: {self.ball.dirX}, speed: {self.speed}')
            if (self.rect.centery < self.ball.rect.centery) and (self.rect.bottom < window_height - self.ball.h + 2.5):
                # print("paddle diatas ball")
                self.rect.y += self.speed
                # print(self.rect.centery)
            if (self.rect.centery > self.ball.rect.centery) and (self.rect.top > self.ball.h - 2.5):
                # print("paddle dibawah ball")
                self.rect.y -= self.speed

class Goal():
    def __init__(self, x, w, h, color):
        self.x = x
        self.y = (window_height / 2) - (h / 2)
        self.w = w
        self.h = h
        self.rect = pygame.Rect(self.x, self.y, self.w, self.h)
        self.color = color
    
    def draw(self):
        pygame.draw.rect(display_surf, self.color, self.rect)

class ScoreBoard():
    def __init__(self, score1=0, score2=0):
        self.x = window_width / 2
        self.y = 40
        self.score1 = score1
        self.score2 = score2
        self.font = pygame.font.Font('freesansbold.ttf', 40)
    
    def display(self, score1, score2):
        scr1 = self.font.render(f'{score1}', True, BLACK)
        rect1 = scr1.get_rect()
        rect1.center = (self.x - (rect1.right - rect1.left), self.y)
        display_surf.blit(scr1, rect1)
        scr2 = self.font.render(f'{score2}', True, BLACK)
        rect2 = scr2.get_rect()
        rect2.center = (self.x + (rect2.right - rect2.left), self.y)
        display_surf.blit(scr2, rect2)

class Ball():
    def __init__(self, x, y, w, h, speed):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.speed = speed
        self.ball = pygame.image.load("./src/disc.png").convert_alpha()
        self.ball = pygame.transform.scale(self.ball, (self.w, self.h))
        self.dirX = rdm.choice([-1, 1])  # left = -1 and right = 1
        self.dirY = rdm.choice([-1, 1])   # up = -1 and down = 1
        self.rect = pygame.Rect(x, y, w, h)
    
    def draw(self):
        # pygame.draw.rect(display_surf, IDK, self.rect)
        pygame.draw.circle(display_surf, GRAY, self.rect.center, self.w / 2)
        display_surf.blit(self.ball, self.rect.topleft)
    
    def bounce(self, axis):
        if axis == 'x':
            self.dirY *= -1
        if axis == 'y':
            self.dirX *= -1
    
    def hitWallY(self):
        if (self.dirY == -1 and self.rect.top <= self.h / 2) or (self.dirY == 1 and self.rect.bottom >= window_height - (self.h / 2)):
            return True
        else:
            return False
    
    def hitWallX(self):
        if (self.dirX == -1 and self.rect.left <= self.w / 2) or (self.dirX == 1 and self.rect.right >= window_width - (self.w / 2)):
            return True
        else:
            return False
    
    def hitPaddleUser(self, paddle):
        if self.x + (self.w / 2) == paddle.rect.left and self.y + (self.h / 2) >= paddle.rect.top and self.y - (self.h / 2) <= paddle.rect.bottom:
            return True
        else:
            return False

    def move(self):
        self.rect.x += (self.dirX * self.speed)
        self.rect.y += (self.dirY * self.speed)
        # print(f'SpeedX: {(self.dirX * self.speed)}, SpeedY: {(self.dirY * self.speed)}')
        if self.hitWallY():
            self.bounce('x')
        if self.hitWallX():
            self.bounce('y')

class Game():
    def __init__(self, line_thickness=20, speed=8):
        self.line_thickness = line_thickness
        self.speed = speed
        ballX = window_width / 2
        ballY = window_height / 2
        ballW = self.line_thickness
        ballH = self.line_thickness
        self.ball = Ball(ballX, ballY, ballW, ballH, self.speed)
        self.paddles = {}
        paddleX = 15
        paddleW = 10
        paddleH = 60
        self.paddles['user'] = Paddle(paddleX, paddleW, paddleH)
        # self.paddles['user'] = AutoPaddleU(paddleX, paddleW, paddleH, max((self.speed / 2), 1), self.ball)
        self.paddles['computer'] = AutoPaddle(window_width - paddleX - paddleW, paddleW, paddleH, self.speed, self.ball)
        self.goals = {}
        goalX = 0
        goalW = 13
        goalH = 100
        self.goals['user'] = Goal(goalX, goalW, goalH, DARKGREEN)
        self.goals['computer'] = Goal(window_width - goalW, goalW, goalH, DARKPURPLE)
        self.scores = ScoreBoard()

    def drawArena(self):
        display_surf.blit(background, [0, 0])
    
    def resetBall(self):
        self.ball.rect.center = (window_width / 2, window_height / 2)
        self.ball.dirX, self.ball.dirY = rdm.choice([-1, 1]), rdm.choice([-1, 1])

    def playAgain(self):
        # print("R Pressed")
        replay = True
        self.scores.score1, self.scores.score2 = 0, 0
        self.ball.rect.center = (window_width / 2, window_height / 2)
        self.ball.dirX, self.ball.dirY = rdm.choice([-1, 1]), rdm.choice([-1, 1])
        self.paddles['user'].rect.centery, self.paddles['computer'].rect.centery = window_height / 2, window_height / 2
        
        font1 = pygame.font.Font('freesansbold.ttf', 24)
        font2 = pygame.font.Font('freesansbold.ttf', 16)
        Header = font1.render("Replay", True, DARKGRAY)
        HeaderR = Header.get_rect()
        HeaderR.center = (window_width / 2, (window_height / 2) - 12)
        mini = font2.render("Click 'p' to continue", True, DARKGRAY)
        miniR = mini.get_rect()
        miniR.center = (window_width / 2, (window_height / 2) + 8)
        self.update()
        
        display_surf.blit(Header, HeaderR)
        display_surf.blit(mini, miniR)
        pygame.display.update()
        
        while replay:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == K_p:
                        replay = False
                    if event.key == K_q:
                        cap.release()
                        cv2.destroyAllWindows()
                        pygame.quit()
                        sys.exit()
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

    def paused(self):
        paused = True
        font1 = pygame.font.Font('freesansbold.ttf', 24)
        font2 = pygame.font.Font('freesansbold.ttf', 16)
        Header = font1.render("Paused", True, DARKGRAY)
        HeaderR = Header.get_rect()
        HeaderR.center = (window_width / 2, (window_height / 2) - 12)
        mini = font2.render("Click 'p' to continue", True, DARKGRAY)
        miniR = mini.get_rect()
        miniR.center = (window_width / 2, (window_height / 2) + 8)
        display_surf.blit(Header, HeaderR)
        display_surf.blit(mini, miniR)
        pygame.display.update()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == K_p:
                        paused = False
                    if event.key == K_q:
                        cap.release()
                        cv2.destroyAllWindows()
                        pygame.quit()
                        sys.exit()
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

    def update(self):
        self.drawArena()
        self.ball.draw()
        self.paddles['user'].draw()
        self.paddles['computer'].draw()
        self.ball.move()
        # self.paddles['user'].move()
        self.paddles['computer'].move()
        self.goals['user'].draw()
        self.goals['computer'].draw()
        
        if self.ball.rect.colliderect(self.goals['user']) or self.ball.rect.colliderect(self.goals['computer']):
            if self.ball.rect.colliderect(self.goals['user']):
                self.scores.score2 += 1
            else:
                self.scores.score1 += 1
            self.resetBall()

        if self.ball.rect.colliderect(self.paddles['user']) or self.ball.rect.colliderect(self.paddles['computer']):
            self.ball.bounce('y')

        self.scores.display(self.scores.score1, self.scores.score2)


def main():
    pygame.init()
    game = Game()
    loop = True

    while loop :
        _, frame = cap.read()
        pos, frame = detector.findIndex(frame)

        if pos:        
            # print(f'X: {pos[0].x * window_width}, Y: {pos[0].y * window_height}')
            game.paddles['user'].detectMove(pos[0].y * window_height)

        cv2.imshow("camera", frame)
        
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == K_q:
                    loop = False
                elif event.key == K_p:
                    game.paused()
                elif event.key == K_r:
                    game.playAgain()
            if event.type == QUIT:
                loop = False
   
        game.update()
        pygame.display.update()
        fps_clock.tick(fps)
    
    print("FINISHED")
    cap.release()
    cv2.destroyAllWindows()
    pygame.quit()
    sys.exit()

if __name__ == '__main__' :
    main()