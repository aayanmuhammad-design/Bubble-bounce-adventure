import pygame
import random
import sys

pygame.init()

# =============================
# CONFIG
# =============================
WIDTH, HEIGHT = 900, 720
GRID_SIZE = 30
COLS, ROWS = 10, 20
PLAY_X, PLAY_Y = 80, 60
FPS = 60

LEVEL_SPEEDS = {
    1: 700,
    2: 650,
    3: 600,
    4: 550,
    5: 500,
    6: 430,
    7: 380,
    8: 330,
    9: 280,
    10: 230
}

LOCK_DELAY = 40
MAX_LEVEL = 10

# =============================
# BACKGROUND
# =============================
try:
    background = pygame.image.load(
        r"C:\Users\Aayan.Muhammad\Documents\My first game\Assets\images.jpg"
    )
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))
except:
    background = None

# =============================
# COLORS
# =============================
BLACK = (0,0,0)
WHITE = (240,240,240)
GRID_COLOR = (40,40,60)
GHOST_COLOR = (100,100,100)

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
        new.insert(0, [None] * COLS)

    grid = new

    return cleared

# =============================
# DRAW GRID
# =============================
def draw_grid(screen):

    pygame.draw.rect(
        screen,
        (20,20,20),
        (PLAY_X, PLAY_Y, COLS*GRID_SIZE, ROWS*GRID_SIZE)
    )

    for y in range(ROWS):
        for x in range(COLS):

            rect = pygame.Rect(
                PLAY_X + x*GRID_SIZE,
                PLAY_Y + y*GRID_SIZE,
                GRID_SIZE,
                GRID_SIZE
            )

            color = (25,25,35) if grid[y][x] is None else COLORS[grid[y][x]]

            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

# =============================
# DRAW PIECE
# =============================
def draw_piece(screen, piece, ghost=False):

    color = GHOST_COLOR if ghost else COLORS[piece.id]

    for y,row in enumerate(piece.shape):
        for x,val in enumerate(row):

            if val:

                rect = pygame.Rect(
                    PLAY_X+(piece.x+x)*GRID_SIZE,
                    PLAY_Y+(piece.y+y)*GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE
                )

                pygame.draw.rect(screen, color, rect)
                pygame.draw.rect(screen, GRID_COLOR, rect, 1)

# =============================
# GHOST PIECE
# =============================
def get_ghost(piece):

    ghost = Piece(piece.id)

    ghost.shape = [row[:] for row in piece.shape]
    ghost.x = piece.x
    ghost.y = piece.y

    while valid(ghost,0,1):
        ghost.y += 1

    return ghost

# =============================
# SIDE PANEL
# =============================
def draw_side_panel(screen, score, level, piece):

     panel_x = 480
     panel_y = 150
     panel_width = 260
     panel_height = 360

     pygame.draw.rect(
         screen,
         (0,0,0),
         (panel_x, panel_y, panel_width, panel_height),
         border_radius=12
     )
 
     pygame.draw.rect(
         screen,
         WHITE,
         (panel_x, panel_y, panel_width, panel_height),
         2,
         border_radius=12
     )
 
     font = pygame.font.SysFont("Arial", 24, bold=True)

     screen.blit(font.render(f"Score: {score}", True, WHITE), (panel_x + 20, panel_y + 20))
     screen.blit(font.render(f"Level: {level}", True, WHITE), (panel_x + 20, panel_y + 60))

     screen.blit(font.render("Next:", True, WHITE), (panel_x + 20, panel_y + 130))

     px = panel_x + 60
     py = panel_y + 200

     for i,row in enumerate(piece.shape):
         for j,val in enumerate(row):
             if val:
                 rect = pygame.Rect(
                     px + j*GRID_SIZE,
                     py + i*GRID_SIZE,
                     GRID_SIZE,
                     GRID_SIZE
                 )
 
                 pygame.draw.rect(screen, COLORS[piece.id], rect)
                 pygame.draw.rect(screen, GRID_COLOR, rect, 1)

# =============================
# BUTTON
# =============================
def draw_button(screen, text, x, y, w, h):

    rect = pygame.Rect(x,y,w,h)

    pygame.draw.rect(screen, BLACK, rect, border_radius=10)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=10)

    font = pygame.font.SysFont("Arial", 28, bold=True)

    txt = font.render(text, True, WHITE)

    screen.blit(
        txt,
        (
            x + (w - txt.get_width())//2,
            y + (h - txt.get_height())//2
        )
    )

    return rect

# =============================
# MAIN
# =============================
def main():

    global grid

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetraris")

    clock = pygame.time.Clock()

    title_font = pygame.font.SysFont("Arial", 60, bold=True)
    font = pygame.font.SysFont("Arial", 28)

    current = next_piece()
    next_p = next_piece()

    score = 0
    level = 1

    fall_timer = 0
    lock_timer = 0

    state = "MENU"
    level_up_timer = 0

    while True:

        dt = clock.tick(FPS)

        # =============================
        # Global BACKGROUND
        # =============================
        if background:
            screen.blit(background, (0,0))
        else:
            screen.fill(BLACK)

        # =============================
        # EVENTS
        # =============================
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:

                mx, my = pygame.mouse.get_pos()

                if state == "MENU":

                    if start_button.collidepoint(mx, my):
                        state = "PLAY"

                    if level_button.collidepoint(mx, my):
                        state = "LEVELS"

                elif state == "LEVELS":
                    state = "MENU"

            if event.type == pygame.KEYDOWN:

                if state == "GAMEOVER":

                    if event.key == pygame.K_r:

                        grid = create_grid()

                        current = next_piece()
                        next_p = next_piece()

                        score = 0
                        level = 1

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

                        if lines == 1:
                            score += 100
                        elif lines == 2:
                            score += 250
                        elif lines == 3:
                            score += 400
                        elif lines == 4:
                            score += 600
                            
                        new_level = min(MAX_LEVEL, (score // 800) + 1)

                        if new_level != level:
                            level = new_level
                            state = "LEVELUP"
                            level_up_timer = 0
                        
                        current = next_p
                        next_p = next_piece()

                        lock_timer = 0

        # =============================
        # MENU
        # =============================
        if state == "MENU":

            title = title_font.render("TETRARIS", True, WHITE)

            screen.blit(
                title,
                (WIDTH//2 - title.get_width()//2, 140)
            )

            start_button = draw_button(
                screen,
                "START",
                320,
                300,
                250,
                70
            )

            level_button = draw_button(
                screen,
                "LEVELS",
                320,
                400,
                250,
                70
            )

        # =============================
        # LEVELS
        # =============================
        elif state == "LEVELS":

            title = title_font.render("LEVELS PROGRESSION", True, WHITE)
            screen.blit(title, (WIDTH//2 - title.get_width()//2, 60))

            info_font = pygame.font.SysFont("Arial", 26)

            # table background
            pygame.draw.rect(screen, (0,0,0), (200, 130, 500, 520), border_radius=10)
            pygame.draw.rect(screen, WHITE, (200, 130, 500, 520), 2, border_radius=10)

            for i in range(1, MAX_LEVEL + 1):

                required_score = (i - 1) * 800

                text = info_font.render(
                    f"Level {i}  -  Reach {required_score} score",
                    True,
                    WHITE
                )

                screen.blit(text, (240, 150 + (i * 40)))

            back = info_font.render(
                "Click anywhere to return",
                True,
                WHITE
            )

            screen.blit(back, (300, 650))

        # =============================
        #LEVEL UP ANIMATION
        # =============================
        elif state == "LEVELUP":

            level_up_timer += dt

            screen.fill((0,0,0))

            flash = (level_up_timer // 120) % 2 == 0

            color = (255, 215, 0) if flash else WHITE

            big_text = title_font.render(
                f"LEVEL {level} COMPLETE!",
                True,
                color
            )

            sub_text = font.render(
                "Great job! Getting faster...",
                True,
                WHITE
            )

            screen.blit(big_text, (
                WIDTH//2 - big_text.get_width()//2,
                HEIGHT//2 - 60
            ))

            screen.blit(sub_text, (
                WIDTH//2 - sub_text.get_width()//2,
                HEIGHT//2
            ))

            if level_up_timer > 2000:
                state = "PLAY"        

        # =============================
        # PLAY
        # =============================
        elif state == "PLAY":

            fall_timer += dt

            speed = LEVEL_SPEEDS.get(level, 200)

            if fall_timer > speed:

                if valid(current,0,1):

                    current.y += 1

                else:

                    lock_timer += dt

                    if lock_timer > LOCK_DELAY:

                        lock(current)

                        lines = clear_lines()

                        if lines == 1:
                            score += 100
                        elif lines == 2:
                            score += 250
                        elif lines == 3:
                            score += 400
                        elif lines == 4:
                            score += 600

                        new_level = min(MAX_LEVEL, (score // 800) + 1)

                        if new_level != level:
                            level = new_level
                            state = "LEVELUP"
                            level_up_timer = 0

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

            draw_side_panel(screen, score, level, next_p)

        # =============================
        # GAME OVER
        # =============================
        elif state == "GAMEOVER":

            title = title_font.render("GAME OVER", True, WHITE)

            screen.blit(title, (240, 240))

            restart = font.render(
                "Press R to Restart",
                True,
                WHITE
            )

            screen.blit(restart, (300, 360))

        pygame.display.flip()

if __name__ == "__main__":
    main()
