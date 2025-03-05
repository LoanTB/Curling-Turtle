import pygame, math, random

pygame.init()
resolution = (450, 900)
window = pygame.display.set_mode(resolution)
timer = pygame.time.Clock()

MOUSEDOWN = False
BALL_SIZE = 25
TURTLE_ANIMATION_FRAMES = 5

class Ball:
    def __init__(self, x, y, vx, vy, r, a):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.r = r
        self.a = a
        self.va = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.a += self.va
        self.a %= 2 * math.pi

    def draw(self, window):
        pygame.draw.circle(window, (255, 255, 255), (self.x, self.y), self.r)

class Manager:
    def __init__(self):
        self.balls = []

    def __repr__(self):
        return f"Ball(x={self.x}, y={self.y})"

    def run(self):
        self.update()
        self.draw(window)

    def add_ball(self, ball):
        if ball != None:
            self.balls.append(ball)

    def update(self):
        for ball in self.balls:
            ball.vx *= 0.99
            ball.vy *= 0.99
            ball.va *= 0.99
            if ball.vy > 10:
                ball.vy = 10
            if ball.vx > 10:
                ball.vx = 10
            ball.update()
        self.resolve_balls_collisions()
        self.resolve_walls_collision()

    def draw(self, window):
        for ball in self.balls:
            ball.draw(window)
        if len(self.balls) > 0:
            target = (resolution[0]*0.5,resolution[1]*0.2)
            closest_turtle = sorted(self.balls, key=lambda ball: math.sqrt((ball.x - target[0]) ** 2 + (ball.y - target[1]) ** 2))[0]
            closest_turtle.closest()

    def resolve_walls_collision(self):
        for ball in self.balls:
            intersect = ball.x + ball.r - resolution[0]
            if intersect > 0:
                ball.vx = -ball.vx
                ball.x -= intersect
            intersect = ball.r - ball.x
            if intersect > 0:
                ball.vx = -ball.vx
                ball.x += intersect
            intersect = ball.y + ball.r - resolution[1]
            if intersect > 0:
                ball.vy = -ball.vy
                ball.y -= intersect
            intersect = ball.r - ball.y
            if intersect > 0:
                ball.vy = -ball.vy
                ball.y += intersect

    def resolve_balls_collisions(self):
        for i in range(len(self.balls)):
            for j in range(i + 1, len(self.balls)):
                ball = self.balls[i]
                other = self.balls[j]
                dx = other.x - ball.x
                dy = other.y - ball.y
                d = math.sqrt(dx ** 2 + dy ** 2)
                intersect = (ball.r + other.r) - d
                if intersect > 0:
                    collision_angle = math.atan2(dy, dx)
                    normal_x = dx / d
                    normal_y = dy / d

                    # Calculate relative velocity
                    relative_velocity_x = ball.vx - other.vx
                    relative_velocity_y = ball.vy - other.vy

                    # Calculate normal and tangential components of the relative velocity
                    vn = relative_velocity_x * normal_x + relative_velocity_y * normal_y
                    vt = relative_velocity_x * -normal_y + relative_velocity_y * normal_x

                    # Calculate impulse
                    m1 = ball.r ** 3
                    m2 = other.r ** 3
                    M = m1 + m2
                    impulse = 2 * m1 * m2 / M * vn / (m1 + m2)

                    # Apply impulse to linear velocities
                    ball.vx -= impulse * normal_x * m2 / M
                    ball.vy -= impulse * normal_y * m2 / M
                    other.vx += impulse * normal_x * m1 / M
                    other.vy += impulse * normal_y * m1 / M

                    # Apply friction to angular velocities
                    friction = 0.1  # Friction coefficient
                    angular_impulse = friction * vt * ball.r
                    ball.va += angular_impulse / (ball.r ** 2)
                    other.va -= angular_impulse / (other.r ** 2)

                    # Resolve overlap
                    overlap = 0.5 * (intersect + 1)
                    ball.x -= overlap * normal_x
                    ball.y -= overlap * normal_y
                    other.x += overlap * normal_x
                    other.y += overlap * normal_y

class Playground:
    def __init__(self):
        self.manager = Manager()
        self.shooter = Shooter()
    def draw(self):
        pygame.draw.circle(window, (0,0,255), (resolution[0]*0.5,resolution[1]*0.2), resolution[0]*0.3)
        pygame.draw.circle(window, (255,255,255), (resolution[0]*0.5,resolution[1]*0.2), resolution[0]*0.2)
        pygame.draw.circle(window, (255,0,0), (resolution[0]*0.5,resolution[1]*0.2), resolution[0]*0.1)
        pygame.draw.circle(window, (255,255,255), (resolution[0]*0.5,resolution[1]*0.2), resolution[0]*0.01)
        pygame.draw.rect(window, (0,0,0), (resolution[0]*0.5-1,0,2,resolution[1]))
        pygame.draw.rect(window, (0,0,0), (0,resolution[1]*0.2-1,resolution[0],2))
        pygame.draw.rect(window, (0,0,0), (0,resolution[1]*0.8-1,resolution[0],2))
    def run(self):
        self.draw()
        self.manager.run()
        self.manager.add_ball(self.shooter.run())

class Shooter:
    def __init__(self):
        self.active = False
        self.start = ()
        self.team_switch = -1
    def run(self):
        if MOUSEDOWN:
            mouse = pygame.mouse.get_pos()
            if not self.active:
                self.active = True
                self.start = (mouse[0],resolution[1]*0.8)
            dx = self.start[0]-mouse[0]
            dy = self.start[1]-mouse[1]
            d = math.sqrt(dx**2+dy**2)
            if d > 200:
                color = (255,0,0)
            elif d > 100:
                color = (255*((d-100)/100),0,255*(1-(d-100)/100))
            else:
                color = (0,0,255*(d/100))
            pygame.draw.line(window,color,mouse,self.start,20)
            Turtle(self.start[0], self.start[1], 0, 0, BALL_SIZE, math.atan2(dx,dy), self.team_switch*-1).draw(window)
        elif self.active:
            self.active = False
            mouse = pygame.mouse.get_pos()
            dx = self.start[0]-mouse[0]
            dy = self.start[1]-mouse[1]
            d = math.sqrt(dx**2+dy**2)
            self.team_switch *= -1
            return Turtle(self.start[0], self.start[1], dx*0.05, dy*0.05, BALL_SIZE, math.atan2(dx,dy), self.team_switch)

class Turtle(Ball):
    def __init__(self, x, y, vx, vy, r, a, team):
        super().__init__(x, y, vx, vy, r, a)
        self.animation_frame = 0
        self.animation_status = 1
        self.animate = False
        self.random_move = [random.randint(350,600),random.randint(10,60),random.randint(0,1)]
        self.team = team

    def forward(self):
        self.animate = True
        self.vx += math.sin(self.a)*0.05
        self.vy += math.cos(self.a)*0.05

    def turn(self):
        self.animate = True
        self.a += 0.05

    def stop(self):
        self.animate = False

    def update(self):
        super().update()
        mouse = pygame.mouse.get_pos()
        dx = mouse[0]-self.x
        dy = mouse[1]-self.y
        d = math.sqrt(dx**2+dy**2)
        if d < self.r:
            if abs(self.vx)+abs(self.vy) > 1:
                self.forward()
            else:
                self.turn()
        else:
            self.stop()
        if self.random_move[0] <= 0:
            if self.random_move[1] <= 0:
                self.random_move = [random.randint(350,600),random.randint(10,60),random.randint(0,1)]
                self.stop()
            else:
                self.random_move[1] -= 1
                if self.random_move[2] == 0:
                    self.forward()
                else:
                    self.turn()
        else:
            self.random_move[0] -= 1

    def draw(self, window):
        if self.animate:
            if self.animation_status == 1:
                self.animation_frame += 1
            else:
                self.animation_frame -= 1
            if self.animation_frame >= TURTLE_ANIMATION_FRAMES or self.animation_frame <= 0:
                self.animation_status *= -1
        else:
            self.animation_frame = 0
            self.animation_status = 1

        for i in range(4):
            if i%2 == 0:
                x = self.x + math.sin(self.a + math.pi * 0.5 * (i + 0.5 + self.animation_frame/TURTLE_ANIMATION_FRAMES*0.25)) * self.r
                y = self.y + math.cos(self.a + math.pi * 0.5 * (i + 0.5 + self.animation_frame/TURTLE_ANIMATION_FRAMES*0.25)) * self.r
            else:
                x = self.x + math.sin(self.a + math.pi * 0.5 * (i + 0.5 - self.animation_frame/TURTLE_ANIMATION_FRAMES*0.25)) * self.r
                y = self.y + math.cos(self.a + math.pi * 0.5 * (i + 0.5 - self.animation_frame/TURTLE_ANIMATION_FRAMES*0.25)) * self.r

            pygame.draw.circle(window, (30, 132, 73), (x, y), self.r * 0.4)
        pygame.draw.circle(window, (30, 132, 73), (self.x + math.sin(self.a) * self.r * 1.2, self.y + math.cos(self.a) * self.r * 1.2), self.r * 0.5)
        if self.team == 1:
            pygame.draw.circle(window, (146,43,33), (self.x, self.y), self.r)
        else:
            pygame.draw.circle(window, (31,97,141), (self.x, self.y), self.r)

    def closest(self):
        pygame.draw.circle(window, ( 241, 196, 15 ), (self.x + math.sin(self.a) * self.r * 1.2, self.y + math.cos(self.a) * self.r * 1.2), self.r * 0.25)

playground = Playground()

while True:
    timer.tick(60)
    window.fill((255, 255, 255))
    playground.run()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            MOUSEDOWN = True
        elif event.type == pygame.MOUSEBUTTONUP:
            MOUSEDOWN = False
