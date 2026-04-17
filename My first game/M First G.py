import pygame
import random
import sys

pygame.init()

# =============================
# CONFIG
# =============================
WIDTH, HEIGHT = 800, 720
GRID_SIZE = 30
COLS, ROWS = 10, 20
PLAY_X, PLAY_Y = 80, 60
FPS = 60
LOCK_DELAY = 40

# =============================
# LOAD BACKGROUND
# =============================
try:
    background = pygame.image.load(
        r"C:\Users\Aayan.Muhammad\Documents\My first game\Assets\images.jpg"
    )
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = None  # prevents crash if file missing

# =============================
# COLORS
# =============================
BLACK = (15, 15, 25)
GRID_COLOR = (40, 40, 60)
WHITE = (240, 240, 240)
GHOST_COLOR = (90, 90, 90)

COLORS = {
    0:(0,255,255),
    1:(0,100,255),
    2:(255,140,0),
    3:(255,255,0),
    4:(0,255,100),
    5:(180,0,255),
    6:(255,0,80)
}

SHAPES = {
0:[[1,1,1,1]],
1:[[1,0,0],[1,1,1]],
2:[[0,0,1],[1,1,1]],
3:[[1,1],[1,1]],
4:[[0,1,1],[1,1,0]],
5:[[0,1,0],[1,1,1]],
6:[[1,1,0],[0,1,1]]
}

# =============================
# GRID
# =============================
def create_grid():
    return [[None for _ in range(COLS)] for _ in range(ROWS)]

grid = create_grid()

# =============================
# PIECE
# =============================
class Piece:
    def __init__(self, id):
        self.id = id
        self.shape = [row[:] for row in SHAPES[id]]
        self.x = 3
        self.y = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

# =============================
# BAG SYSTEM
# =============================
def generate_bag():
    bag = list(range(7))
    random.shuffle(bag)
    return bag

bag = generate_bag()

def next_piece():
    global bag
    if not bag:
        bag = generate_bag()
    return Piece(bag.pop())

# =============================
# LOGIC
# =============================
def valid(piece, dx=0, dy=0):
    for y,row in enumerate(piece.shape):
        for x,val in enumerate(row):
            if val:
                nx = piece.x + x + dx
                ny = piece.y + y + dy
                if nx < 0 or nx >= COLS or ny >= ROWS:
                    return False
                if ny >= 0 and grid[ny][nx] is not None:
                    return False
    return True

def lock(piece):
    for y,row in enumerate(piece.shape):
        for x,val in enumerate(row):
            if val:
                grid[piece.y+y][piece.x+x] = piece.id

def clear_lines():
    global grid
    new = [row for row in grid if any(cell is None for cell in row)]
    cleared = ROWS - len(new)
    for _ in range(cleared):
        new.insert(0,[None]*COLS)
    grid = new
    return cleared

# =============================
# DRAWING
# =============================
def draw_grid(screen):
    for y in range(ROWS):
        for x in range(COLS):
            rect = pygame.Rect(PLAY_X+x*GRID_SIZE, PLAY_Y+y*GRID_SIZE, GRID_SIZE, GRID_SIZE)
            color = (20,20,30) if grid[y][x] is None else COLORS[grid[y][x]]
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

def draw_piece(screen, piece, ghost=False):
    color = GHOST_COLOR if ghost else COLORS[piece.id]
    for y,row in enumerate(piece.shape):
        for x,val in enumerate(row):
            if val:
                rect = pygame.Rect(
                    PLAY_X+(piece.x+x)*GRID_SIZE,
                    PLAY_Y+(piece.y+y)*GRID_SIZE,
                    GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

def get_ghost(piece):
    ghost = Piece(piece.id)
    ghost.shape = [row[:] for row in piece.shape]
    ghost.x = piece.x
    ghost.y = piece.y
    while valid(ghost,0,1):
        ghost.y += 1
    return ghost

def draw_preview(screen, piece, x, y):
    font = pygame.font.SysFont("Arial", 22)
    screen.blit(font.render("Next:", True, WHITE), (x, y-30))

    for i,row in enumerate(piece.shape):
        for j,val in enumerate(row):
            if val:
                rect = pygame.Rect(x + j*GRID_SIZE, y + i*GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, COLORS[piece.id], rect)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

# =============================
# MAIN
# =============================
def main():
    global grid

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetraris")
    clock = pygame.time.Clock()

    font = pygame.font.SysFont("Arial", 22)
    big = pygame.font.SysFont("Arial", 48)

    current = next_piece()
    next_p = next_piece()

    score = 0
    level = 1
    fall_timer = 0
    lock_timer = 0
    state = "START"

    while True:
        dt = clock.tick(FPS)

        # ===== BACKGROUND HANDLING =====
        if state == "PLAY" and background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:

                if state == "START":
                    state = "PLAY"

                elif state == "GAMEOVER":
                    if event.key == pygame.K_r:
                        grid = create_grid()
                        current = next_piece()
                        next_p = next_piece()
                        score = 0
                        state = "PLAY"

                elif state == "PLAY":

                    if event.key == pygame.K_LEFT and valid(current,-1,0):
                        current.x -= 1
                        lock_timer = 0

                    if event.key == pygame.K_RIGHT and valid(current,1,0):
                        current.x += 1
                        lock_timer = 0

                    if event.key == pygame.K_DOWN and valid(current,0,1):
                        current.y += 1
                        score += 1
                        lock_timer = 0

                    if event.key == pygame.K_UP:
                        old = [row[:] for row in current.shape]
                        current.rotate()
                        if not valid(current):
                            current.shape = old
                        else:
                            lock_timer = 0

                    if event.key == pygame.K_SPACE:
                        while valid(current,0,1):
                            current.y += 1
                            score += 2
                        lock(current)
                        lines = clear_lines()
                        score += lines * 100
                        current = next_p
                        next_p = next_piece()
                        lock_timer = 0

        if state == "PLAY":

            fall_timer += dt
            speed = max(100, 600 - level*40)

            if fall_timer > speed:
                if valid(current,0,1):
                    current.y += 1
                else:
                    lock_timer += dt
                    if lock_timer > LOCK_DELAY:
                        lock(current)
                        lines = clear_lines()
                        score += lines * 100
                        level = score // 1000 + 1
                        current = next_p
                        next_p = next_piece()
                        lock_timer = 0
                        if not valid(current):
                            state = "GAMEOVER"
                fall_timer = 0

            draw_grid(screen)
            ghost = get_ghost(current)
            draw_piece(screen, ghost, True)
            draw_piece(screen, current)

            draw_preview(screen, next_p, 500, 350)

            screen.blit(font.render(f"Score: {score}", True, WHITE), (500, 200))
            screen.blit(font.render(f"Level: {level}", True, WHITE), (500, 240))

        elif state == "START":
            screen.blit(big.render("TETRARIS", True, WHITE), (300, 300))
            screen.blit(font.render("Press Any Key", True, WHITE), (330, 360))

        elif state == "GAMEOVER":
            screen.blit(big.render("GAME OVER", True, WHITE), (280, 300))
            screen.blit(font.render("Press R to Restart", True, WHITE), (300, 360))

        pygame.display.flip()

if __name__ == "__main__":
    main()
