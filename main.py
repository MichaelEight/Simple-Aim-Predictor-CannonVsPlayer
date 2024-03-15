import sys
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos, radians

def startup():
    update_viewport(None, 1000, 1000)
    glClearColor(0.5, 0.5, 0.5, 1.0)

def shutdown():
    pass

def update_viewport(window, width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-100.0, 100.0, -100.0 / aspect_ratio, 100.0 / aspect_ratio,
                1.0, -1.0)
    else:
        glOrtho(-100.0 * aspect_ratio, 100.0 * aspect_ratio, -100.0, 100.0,
                1.0, -1.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

RED = (1.0, 0.0, 0.0)
GREEN = (0.0, 1.0, 0.0)
BLUE = (0.0, 0.0, 1.0)
BLACK = (0.0, 0.0, 0.0)
CYAN = (0.0, 1.0, 1.0)  # RGB for cyan color

def draw_rectangle(x, y, width, height, color):
    glBegin(GL_QUADS)
    glColor3f(*color)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_circle(x, y, radius, color):
    glBegin(GL_POLYGON)
    glColor3f(*color)
    glVertex2f(x, y)
    for i in range(360):
        x = x + radius * cos(radians(i))
        y = y + radius * sin(radians(i))
        glVertex2f(x, y)
    glEnd()

def draw_line(x1, y1, x2, y2, width, color):
    glLineWidth(width)
    glBegin(GL_LINES)
    glColor3f(*color)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glEnd()

def draw_point(x, y, radius, color):
    glPointSize(radius)
    glBegin(GL_POINTS)
    glColor3f(*color)
    glVertex2f(x, y)
    glEnd()




class Player:
    def __init__(self, x = 0.0, y = 0.0, vx = 10.0, vy = -10.0):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

player = Player(-50, 50)
prev_x = prev_y = 0
cannon_x = cannon_y = -90
cannon_size = 20

bullet_speed = 10.0
# Number of future positions to calculate
n = 15

show_all_connections = True  # Controls visibility of all connections between future points
show_infinite_lines_and_points = True  # Controls visibility of infinite lines and displaying future points

def calculate_distance(x1, y1, x2, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5

current_mode = 'A'  # Possible values: 'A', 'S', 'D'

def key_callback(window, key, scancode, action, mods):
    global bullet_speed, current_mode, player, n, show_all_connections, show_infinite_lines_and_points

    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_K:
            bullet_speed += 1.0
        elif key == GLFW_KEY_J:
            bullet_speed -= 1.0
            if bullet_speed < 1:  # Prevent bullet speed from becoming negative or zero
                bullet_speed = 1
        elif key == GLFW_KEY_N:
            n -= 1
            if n < 1:  # Prevent bullet speed from becoming negative or zero
                n = 1
        elif key == GLFW_KEY_M:
            n += 1

        elif key == GLFW_KEY_A:
            current_mode = 'A'
        elif key == GLFW_KEY_S:
            current_mode = 'S'
            xpos, ypos = glfwGetCursorPos(window)
            # Normalize and set player's position
            player.x, player.y = ((xpos / 1000) * 200) - 100, (((1000 - ypos) / 1000) * 200) - 100
        elif key == GLFW_KEY_D:
            current_mode = 'D'
            xpos, ypos = glfwGetCursorPos(window)
            normalized_xpos = ((xpos / 1000) * 200) - 100  # Scale and offset
            normalized_ypos = (((1000 - ypos) / 1000) * 200) - 100  # Invert y axis, scale and offset
            # Normalize and set player's position
            player.vx, player.vy = normalized_xpos - player.x, normalized_ypos - player.y
        elif key == GLFW_KEY_O:
            show_all_connections = not show_all_connections
        elif key == GLFW_KEY_P:
            show_infinite_lines_and_points = not show_infinite_lines_and_points


def render(time, window):
    global player, cannon_x, cannon_y, bullet_speed, n
    glClear(GL_COLOR_BUFFER_BIT)


    # Future positions arrays
    player_future_positions = []
    bullet_future_positions = []

    # Calculate future player positions
    for i in range(1, n + 1):
        future_player_x = player.x + player.vx * i
        future_player_y = player.y + player.vy * i
        player_future_positions.append((future_player_x, future_player_y))


    # Cannon center position
    cannon_center_x = cannon_x + cannon_size / 2
    cannon_center_y = cannon_y + cannon_size / 2

    # Check if mouse is inside window
    xpos, ypos = glfwGetCursorPos(window)

    # Normalize
    normalized_xpos = ((xpos / 1000) * 200) - 100  # Scale and offset
    normalized_ypos = (((1000 - ypos) / 1000) * 200) - 100  # Invert y axis, scale and offset


    # Vector from cannon to normalized point
    dx = normalized_xpos - cannon_center_x
    dy = normalized_ypos - cannon_center_y

    final_x = cannon_center_x + dx * 10
    final_y = cannon_center_y + dy * 10

    

    # Draw cannon
    draw_rectangle(cannon_x, cannon_y, cannon_size, cannon_size, BLUE)
    

    # Calculate bullet velocity vector from cannon to normalized cursor position
    bullet_magnitude = (dx ** 2 + dy ** 2) ** 0.5
    if bullet_magnitude != 0:
        dx /= bullet_magnitude
        dy /= bullet_magnitude

    # Calculate future bullet positions
    for i in range(1, n + 1):
        future_bullet_x = cannon_center_x + dx * bullet_speed * i
        future_bullet_y = cannon_center_y + dy * bullet_speed * i
        bullet_future_positions.append((future_bullet_x, future_bullet_y))

    # Optionally, draw infinite lines from cannon and player
    if show_infinite_lines_and_points:
        draw_line(cannon_center_x, cannon_center_y, final_x, final_y, 2.0, BLUE)
        draw_line(player.x, player.y, player.x + player.vx * 100, player.y + player.vy * 100, 2.0, BLUE)

        # Draw future points
        for player_pos, bullet_pos in zip(player_future_positions, bullet_future_positions):
            draw_point(*player_pos, 5.0, RED)
            draw_point(*bullet_pos, 5.0, BLUE)

    # Draw player
    draw_point(player.x, player.y, 30.0, RED)
    # Draw player's velocity vector
    draw_line(player.x, player.y, player.x + player.vx, player.y + player.vy, 10.0, BLACK)

    # Variables to track the closest positions
    min_distance = float('inf')
    closest_player_pos = None
    closest_bullet_pos = None

    # Find the closest pair
    for player_pos, bullet_pos in zip(player_future_positions, bullet_future_positions):
        distance = calculate_distance(*player_pos, *bullet_pos)
        if distance < min_distance:
            min_distance = distance
            closest_player_pos = player_pos
            closest_bullet_pos = bullet_pos

    # Always draw the closest pair in cyan
    if closest_player_pos and closest_bullet_pos:
        draw_point(*closest_player_pos, 5.0, BLACK if not show_all_connections else GREEN)
        draw_point(*closest_bullet_pos, 5.0, BLACK if not show_all_connections else GREEN)
        draw_line(*closest_player_pos, *closest_bullet_pos, 6.0 if show_all_connections else 3.0, CYAN)

    # Draw all connections if enabled
    if show_all_connections:
        for player_pos, bullet_pos in zip(player_future_positions, bullet_future_positions):
            if (player_pos, bullet_pos) != (closest_player_pos, closest_bullet_pos):
                draw_line(*player_pos, *bullet_pos, 1.0, GREEN)


    glFlush()


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(1000, 1000, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwSetKeyCallback(window, key_callback)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    glPointSize(15.0)
    glLineWidth(10.0)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime(), window)
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()