import pygame
from pygame.locals import *
import sys
import math
import random
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *

# --- PARAMETERS ---
WIDTH, HEIGHT = 1024, 768

# Colors
RED = (1, 0, 0)
BLUE = (0, 0, 1)
YELLOW = (1, 1, 0)
GRAY = (0.7, 0.7, 0.7)
BLACK = (0, 0, 0)
BROWN = (0.55, 0.27, 0.07)
METAL = (0.8, 0.8, 0.9)
BRASS = (0.85, 0.65, 0.13)
ACRYLIC = (0.7, 0.9, 1.0, 0.6)
GREEN = (0, 1, 0)
CONCRETE = (0.65, 0.65, 0.65)
WOOD_LIGHT = (0.8, 0.6, 0.4)
WOOD_DARK = (0.6, 0.4, 0.2)

# Forklift parameters
FORKLIFT_WIDTH = 1.5
FORKLIFT_LENGTH = 2.5
FORKLIFT_HEIGHT = 0.5
WHEEL_RADIUS = 0.3
WHEEL_WIDTH = 0.2
WHEEL_ROLLERS = 12
SCREW_ROD_LENGTH = 2.0
SCREW_ROD_RADIUS = 0.05
STEPPER_SIZE = 0.25
FORK_WIDTH = 1.0
FORK_LENGTH = 1.8
FORK_THICKNESS = 0.1

# Warehouse parameters
WAREHOUSE_WIDTH = 40
WAREHOUSE_LENGTH = 40
WAREHOUSE_HEIGHT = 10
SHELF_WIDTH = 5
SHELF_DEPTH = 2
SHELF_HEIGHT = 5
SHELF_LEVELS = 4
NUM_SHELVES = 5

# State
position = [0, 0, 0]
rotation = 0
fork_height = 0
max_fork_height = 95  # Set to 95% to prevent exceeding rod length
min_fork_height = 5   # Minimum height to prevent going beyond bottom
wheel_steering = [0, 0, 0, 0]
screw_rotation = [0, 0]  # Left and right screw rods

# Movement parameters
linear_speed = 0.1
angular_speed = 2
fork_speed = 1
screw_rotation_speed = 15  # Degrees per frame when raising/lowering

# Loadcell parameters
loadcell_data = []
MAX_DATA_POINTS = 100
vibration_amplitude = 0.0
load_weight = 0.0
is_vibrating = False

# Cargo/Object parameters
cargo_objects = [
    {"position": [5, 5, 0], "size": [1, 1, 0.5], "weight": 2, "color": BROWN, "carried": False, "id": 1},
    {"position": [-5, 8, 0], "size": [0.8, 1.2, 0.6], "weight": 5, "color": RED, "carried": False, "id": 2},
    {"position": [8, -6, 0], "size": [1.5, 0.8, 0.4], "weight": 3, "color": BLUE, "carried": False, "id": 3},
    {"position": [-7, -3, 0], "size": [1, 1, 1], "weight": 5, "color": GREEN, "carried": False, "id": 4},
]

# Destination zones
destination_zones = [
    {"position": [10, 10, 0], "size": [3, 3], "color": (0.2, 0.8, 0.2, 0.3)},
    {"position": [-10, 10, 0], "size": [3, 3], "color": (0.8, 0.2, 0.2, 0.3)},
    {"position": [-10, -10, 0], "size": [3, 3], "color": (0.2, 0.2, 0.8, 0.3)},
]

carried_cargo = None

# --- OPENGL PRIMITIVES ---
def create_cube(sx, sy, sz, color=RED):
    vertices = (
        (sx/2, -sy/2, -sz/2),
        (sx/2, sy/2, -sz/2),
        (-sx/2, sy/2, -sz/2),
        (-sx/2, -sy/2, -sz/2),
        (sx/2, -sy/2, sz/2),
        (sx/2, sy/2, sz/2),
        (-sx/2, -sy/2, sz/2),
        (-sx/2, sy/2, sz/2)
    )
    surfaces = (
        (0, 1, 2, 3), (4, 5, 7, 6),
        (0, 4, 6, 3), (1, 5, 7, 2),
        (0, 1, 5, 4), (3, 2, 7, 6)
    )
    normals = (
        (0, 0, -1), (0, 0, 1),
        (-1, 0, 0), (1, 0, 0),
        (0, -1, 0), (0, 1, 0)
    )
    if len(color) == 4:  # If color has alpha component
        glColor4fv(color)
    else:
        glColor3fv(color)
        
    glBegin(GL_QUADS)
    for i, surface in enumerate(surfaces):
        glNormal3fv(normals[i])
        for vertex in surface:
            glVertex3fv(vertices[vertex])
    glEnd()

def create_cylinder(radius, length, sides=20, color=GRAY):
    glColor3fv(color)
    quadric = gluNewQuadric()
    gluCylinder(quadric, radius, radius, length, sides, 1)
    glPushMatrix()
    gluDisk(quadric, 0, radius, sides, 1)
    glTranslatef(0, 0, length)
    gluDisk(quadric, 0, radius, sides, 1)
    glPopMatrix()
    gluDeleteQuadric(quadric)

def create_mecanum_wheel(radius, width, rollers=8, angle=45, color=BLUE):
    glColor3fv(BLACK)
    quadric = gluNewQuadric()
    gluCylinder(quadric, radius, radius, width, 20, 1)
    glPushMatrix()
    gluDisk(quadric, 0, radius, 20, 1)
    glTranslatef(0, 0, width)
    gluDisk(quadric, 0, radius, 20, 1)
    glPopMatrix()
    roller_radius = radius * 0.3
    roller_length = width * 1.2
    for i in range(rollers):
        roll_angle = i * (360 / rollers)
        glPushMatrix()
        glRotatef(roll_angle, 0, 0, 1)
        glTranslatef(0, radius, width/2)
        glRotatef(angle, 0, 0, 1)
        glColor3fv(color)
        glRotatef(90, 1, 0, 0)
        create_cylinder(roller_radius, roller_length, 8, color)
        glPopMatrix()
    gluDeleteQuadric(quadric)

def create_threaded_rod(length, radius, rotation_angle=0, color=METAL):
    glColor3fv(color)
    create_cylinder(radius, length, 12, color)
    thread_spacing = length / 20
    thread_height = radius * 0.2
    glColor3fv(BLACK)
    for i in range(20):
        glPushMatrix()
        thread_angle = rotation_angle + (i * 18)
        glTranslatef(0, 0, i * thread_spacing)
        glRotatef(thread_angle, 0, 0, 1)
        glPushMatrix()
        glTranslatef(radius*0.8, 0, 0)
        create_cylinder(thread_height, thread_height*2, 8, BLACK)
        glPopMatrix()
        glPopMatrix()

def create_t_nut(radius, height, color=BRASS):
    create_cylinder(radius*2, height, 8, color)
    glPushMatrix()
    glTranslatef(0, 0, height/3)
    create_cylinder(radius*3, height/3, 8, color)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0, -0.01)
    glColor3fv(BLACK)
    create_cylinder(radius*0.8, height+0.02, 8, BLACK)
    glPopMatrix()

def create_stepper_motor(size, color=BLACK):
    create_cube(size, size, size, color)
    glPushMatrix()
    glTranslatef(0, 0, size/2)
    glColor3fv(METAL)
    create_cylinder(size/8, size/2, 12, METAL)
    glPopMatrix()

def create_coupler(radius, length, color=METAL):
    create_cylinder(radius, length, 12, color)
    glPushMatrix()
    glTranslatef(0, 0, length/4)
    glColor3fv(BLACK)
    create_cylinder(radius*1.1, length/10, 12, BLACK)
    glPopMatrix()
    glPushMatrix()
    glTranslatef(0, 0, length*3/4)
    create_cylinder(radius*1.1, length/10, 12, BLACK)
    glPopMatrix()

def create_loadcell(width, height, depth, color=METAL):
    create_cube(width, height, depth, color)
    # Add strain gauge visualization
    glPushMatrix()
    glTranslatef(0, 0, depth/2 + 0.01)
    glColor3fv(RED)
    create_cube(width*0.7, height*0.2, 0.01, RED)
    glPopMatrix()

# --- WAREHOUSE ELEMENTS ---
def create_floor():
    # Main floor
    glColor3fv(CONCRETE)
    create_cube(WAREHOUSE_WIDTH, WAREHOUSE_LENGTH, 0.1, CONCRETE)
    
    # Floor markings
    glColor3f(1.0, 1.0, 0.0)  # Yellow
    line_width = 0.1
    
    # Draw perimeter lines
    for x in [-WAREHOUSE_WIDTH/2 + 1, WAREHOUSE_WIDTH/2 - 1]:
        for y in range(-int(WAREHOUSE_LENGTH/2) + 1, int(WAREHOUSE_LENGTH/2), 2):
            glPushMatrix()
            glTranslatef(x, y, 0.06)
            create_cube(line_width, 1, 0.01, YELLOW)
            glPopMatrix()
    
    for y in [-WAREHOUSE_LENGTH/2 + 1, WAREHOUSE_LENGTH/2 - 1]:
        for x in range(-int(WAREHOUSE_WIDTH/2) + 1, int(WAREHOUSE_WIDTH/2), 2):
            glPushMatrix()
            glTranslatef(x, y, 0.06)
            create_cube(1, line_width, 0.01, YELLOW)
            glPopMatrix()
    
    # Draw traffic lanes
    for x in range(-int(WAREHOUSE_WIDTH/4), int(WAREHOUSE_WIDTH/4) + 1, int(WAREHOUSE_WIDTH/4)):
        for y in range(-int(WAREHOUSE_LENGTH/2) + 3, int(WAREHOUSE_LENGTH/2) - 3, 4):
            glPushMatrix()
            glTranslatef(x, y, 0.06)
            create_cube(WAREHOUSE_WIDTH/2 - 2, line_width, 0.01, YELLOW)
            glPopMatrix()

def create_walls():
    wall_height = WAREHOUSE_HEIGHT
    wall_thickness = 0.3
    
    # North wall
    glPushMatrix()
    glTranslatef(0, WAREHOUSE_LENGTH/2, wall_height/2)
    create_cube(WAREHOUSE_WIDTH, wall_thickness, wall_height, GRAY)
    glPopMatrix()
    
    # South wall
    glPushMatrix()
    glTranslatef(0, -WAREHOUSE_LENGTH/2, wall_height/2)
    create_cube(WAREHOUSE_WIDTH, wall_thickness, wall_height, GRAY)
    glPopMatrix()
    
    # West wall
    glPushMatrix()
    glTranslatef(-WAREHOUSE_WIDTH/2, 0, wall_height/2)
    create_cube(wall_thickness, WAREHOUSE_LENGTH, wall_height, GRAY)
    glPopMatrix()
    
    # East wall
    glPushMatrix()
    glTranslatef(WAREHOUSE_WIDTH/2, 0, wall_height/2)
    create_cube(wall_thickness, WAREHOUSE_LENGTH, wall_height, GRAY)
    glPopMatrix()
    
    # Add windows to north wall
    window_size = 1.5
    window_spacing = 5
    for x in range(-int(WAREHOUSE_WIDTH/2) + window_spacing, int(WAREHOUSE_WIDTH/2), window_spacing):
        glPushMatrix()
        glTranslatef(x, WAREHOUSE_LENGTH/2 - 0.1, wall_height/2 + 1)
        glColor4f(0.5, 0.7, 1.0, 0.5)
        create_cube(window_size, 0.1, window_size, (0.5, 0.7, 1.0))
        glPopMatrix()

def create_shelves():
    shelf_positions = [
        (WAREHOUSE_WIDTH/2 - SHELF_DEPTH/2 - 1, 0, 0),  # East wall
        (-(WAREHOUSE_WIDTH/2 - SHELF_DEPTH/2 - 1), 0, 0),  # West wall
        (0, WAREHOUSE_LENGTH/2 - SHELF_DEPTH/2 - 1, 0),  # North wall
        (0, -(WAREHOUSE_LENGTH/2 - SHELF_DEPTH/2 - 1), 0),  # South wall
        (WAREHOUSE_WIDTH/4, WAREHOUSE_LENGTH/4, 0),  # Middle
    ]
    
    for pos in shelf_positions:
        glPushMatrix()
        glTranslatef(pos[0], pos[1], 0)
        
        # Vertical supports
        for x in [-SHELF_WIDTH/2, SHELF_WIDTH/2]:
            for y in [-SHELF_DEPTH/2, SHELF_DEPTH/2]:
                glPushMatrix()
                glTranslatef(x, y, SHELF_HEIGHT/2)
                glColor3fv(METAL)
                create_cylinder(0.1, SHELF_HEIGHT, 8, METAL)
                glPopMatrix()
        
        # Horizontal shelves
        level_height = SHELF_HEIGHT / SHELF_LEVELS
        for level in range(SHELF_LEVELS):
            glPushMatrix()
            glTranslatef(0, 0, level * level_height)
            glColor3fv(WOOD_DARK)
            create_cube(SHELF_WIDTH + 0.1, SHELF_DEPTH + 0.1, 0.05, WOOD_DARK)
            glPopMatrix()
            
            # Add some random boxes on shelves (except bottom shelf)
            if level > 0 and random.random() > 0.3:
                num_boxes = random.randint(1, 3)
                for _ in range(num_boxes):
                    box_x = random.uniform(-SHELF_WIDTH/2 + 0.3, SHELF_WIDTH/2 - 0.3)
                    box_y = random.uniform(-SHELF_DEPTH/2 + 0.3, SHELF_DEPTH/2 - 0.3)
                    box_width = random.uniform(0.3, 0.8)
                    box_depth = random.uniform(0.3, 0.8)
                    box_height = random.uniform(0.2, 0.5)
                    box_color = random.choice([BROWN, BLUE, RED, GREEN, YELLOW])
                    
                    glPushMatrix()
                    glTranslatef(box_x, box_y, level * level_height + box_height/2 + 0.05)
                    create_cube(box_width, box_depth, box_height, box_color)
                    glPopMatrix()
                
        glPopMatrix()

def create_destination_zones():
    for zone in destination_zones:
        glPushMatrix()
        glTranslatef(zone["position"][0], zone["position"][1], zone["position"][2] + 0.05)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        create_cube(zone["size"][0], zone["size"][1], 0.02, zone["color"])
        glDisable(GL_BLEND)
        glPopMatrix()

def create_cargo():
    for cargo in cargo_objects:
        if not cargo["carried"]:
            glPushMatrix()
            glTranslatef(cargo["position"][0], cargo["position"][1], cargo["position"][2] + cargo["size"][2]/2)
            create_cube(cargo["size"][0], cargo["size"][1], cargo["size"][2], cargo["color"])
            glPopMatrix()

# --- MAIN DRAW FUNCTION ---
def draw_forklift():
    global vibration_amplitude, is_vibrating, carried_cargo
    
    glPushMatrix()
    glTranslatef(position[0], position[1], position[2])
    glRotatef(rotation, 0, 0, 1)
    create_cube(FORKLIFT_WIDTH, FORKLIFT_LENGTH, FORKLIFT_HEIGHT, BLUE)
    wheel_positions = [
        (-FORKLIFT_WIDTH/2, -FORKLIFT_LENGTH/2 + WHEEL_RADIUS, -FORKLIFT_HEIGHT/2),
        (FORKLIFT_WIDTH/2, -FORKLIFT_LENGTH/2 + WHEEL_RADIUS, -FORKLIFT_HEIGHT/2),
        (FORKLIFT_WIDTH/2, FORKLIFT_LENGTH/2 - WHEEL_RADIUS, -FORKLIFT_HEIGHT/2),
        (-FORKLIFT_WIDTH/2, FORKLIFT_LENGTH/2 - WHEEL_RADIUS, -FORKLIFT_HEIGHT/2)
    ]
    wheel_angles = [45, -45, 45, -45]
    for i, (wx, wy, wz) in enumerate(wheel_positions):
        glPushMatrix()
        glTranslatef(wx, wy, wz)
        glRotatef(wheel_steering[i], 0, 0, 1)
        if i == 0 or i == 3:
            glRotatef(90, 0, 1, 0)
        else:
            glRotatef(-90, 0, 1, 0)
        create_mecanum_wheel(WHEEL_RADIUS, WHEEL_WIDTH, WHEEL_ROLLERS, wheel_angles[i])
        glPopMatrix()
    # --- Vertical support and rods ---
    glPushMatrix()
    glTranslatef(0, -FORKLIFT_LENGTH/2 + 0.1, FORKLIFT_HEIGHT/2)
    rod_distance = FORKLIFT_WIDTH * 0.3
    rod_height = SCREW_ROD_LENGTH
    
    # Draw vertical poles to visualize limits
    for x_offset in [-rod_distance, rod_distance]:
        glPushMatrix()
        glTranslatef(x_offset, 0, 0)
        glColor3fv(GRAY)
        create_cylinder(SCREW_ROD_RADIUS*0.5, rod_height, 8, GRAY)
        glPopMatrix()
    
    for i, x_offset in enumerate([-rod_distance, rod_distance]):
        glPushMatrix()
        glTranslatef(x_offset, 0, -FORKLIFT_HEIGHT/2)
        create_stepper_motor(STEPPER_SIZE)
        glPushMatrix()
        glTranslatef(0, 0, STEPPER_SIZE * 0.75)
        create_coupler(STEPPER_SIZE/6, STEPPER_SIZE/2)
        glPopMatrix()
        glPushMatrix()
        glTranslatef(0, 0, STEPPER_SIZE * 1.25)
        create_threaded_rod(rod_height - STEPPER_SIZE * 1.25, SCREW_ROD_RADIUS, screw_rotation[i])
        glPopMatrix()
        glPopMatrix()
    
    # Calculate normalized height percentage (0.0 to 1.0)
    normalized_height = (fork_height - min_fork_height) / (max_fork_height - min_fork_height)
    # Scale to actual rod height (accounting for limits)
    usable_rod_height = rod_height - STEPPER_SIZE * 1.25 - SCREW_ROD_RADIUS * 8
    current_height = STEPPER_SIZE * 1.25 + normalized_height * usable_rod_height
    
    # --- Acrylic fork attached to T-nuts with vibration ---
    fork_vibration_offset = 0
    if is_vibrating:
        fork_vibration_offset = math.sin(pygame.time.get_ticks() * 0.01) * vibration_amplitude
    
    glPushMatrix()
    glTranslatef(0, 0.1, current_height + fork_vibration_offset)
    
    # T-nuts
    for x_offset in [-rod_distance, rod_distance]:
        glPushMatrix()
        glTranslatef(x_offset, 0, 0)
        create_t_nut(SCREW_ROD_RADIUS * 2, SCREW_ROD_RADIUS * 8)
        glPopMatrix()
    
    # Acrylic sheet (fork)
    glPushMatrix()
    glTranslatef(0, 0, SCREW_ROD_RADIUS * 4)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(*ACRYLIC)
    create_cube(rod_distance*2+0.2, FORK_LENGTH, 0.08, ACRYLIC)
    glDisable(GL_BLEND)
    glPopMatrix()
    
    # Load cell on the fork
    glPushMatrix()
    glTranslatef(0, FORK_LENGTH*0.3, SCREW_ROD_RADIUS * 4 + 0.08)
    create_loadcell(rod_distance*0.8, 0.3, 0.1, METAL)
    glPopMatrix()
    
    # Draw carried cargo if any
    if carried_cargo:
        glPushMatrix()
        glTranslatef(0, FORK_LENGTH*0.3, SCREW_ROD_RADIUS * 4 + 0.18)
        create_cube(
            carried_cargo["size"][0], 
            carried_cargo["size"][1], 
            carried_cargo["size"][2], 
            carried_cargo["color"]
        )
        glPopMatrix()
    
    glPopMatrix()  # End fork assembly
    glPopMatrix()  # End vertical support
    glPopMatrix()  # End forklift

# --- SUPPORT ---
def display_text(text, x, y, size=18):
    font = pygame.font.SysFont('Arial', size)
    text_surface = font.render(text, True, (255, 255, 255))
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, HEIGHT, 0)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    screen = pygame.display.get_surface()
    screen.blit(text_surface, text_rect)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_grid():
    glDisable(GL_LIGHTING)
    glColor3f(0.5, 0.5, 0.5)
    glLineWidth(1.0)
    grid_size = 20
    grid_step = 1
    glBegin(GL_LINES)
    for i in range(-grid_size, grid_size + 1, grid_step):
        glVertex3f(i, -grid_size, -FORKLIFT_HEIGHT/2 - 0.01)
        glVertex3f(i, grid_size, -FORKLIFT_HEIGHT/2 - 0.01)
        glVertex3f(-grid_size, i, -FORKLIFT_HEIGHT/2 - 0.01)
        glVertex3f(grid_size, i, -FORKLIFT_HEIGHT/2 - 0.01)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_loadcell_graph():
    if not loadcell_data:
        return
        
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, WIDTH, 0, HEIGHT)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    # Draw background
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(WIDTH - 310, HEIGHT - 210)
    glVertex2f(WIDTH - 10, HEIGHT - 210)
    glVertex2f(WIDTH - 10, HEIGHT - 10)
    glVertex2f(WIDTH - 310, HEIGHT - 10)
    glEnd()
    
    # Draw graph border
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(WIDTH - 300, HEIGHT - 200)
    glVertex2f(WIDTH - 20, HEIGHT - 200)
    glVertex2f(WIDTH - 20, HEIGHT - 20)
    glVertex2f(WIDTH - 300, HEIGHT - 20)
    glEnd()
    
    # Draw data points
    glColor3f(0.0, 1.0, 0.0)
    glBegin(GL_LINE_STRIP)
    data_len = len(loadcell_data)
    for i, value in enumerate(loadcell_data):
        x = WIDTH - 300 + (280 * i / MAX_DATA_POINTS)
        y = HEIGHT - 110 + value * 80  # Scale for display
        glVertex2f(x, y)
    glEnd()

    # Draw label
    display_text("Load Cell Data", WIDTH - 300, HEIGHT - 220)
    
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def update_physics():
    global screw_rotation, loadcell_data, vibration_amplitude, is_vibrating, carried_cargo, load_weight
    
    keys = pygame.key.get_pressed()
    if keys[K_r] and fork_height < max_fork_height:
        screw_rotation[0] = (screw_rotation[0] + screw_rotation_speed) % 360
        screw_rotation[1] = (screw_rotation[1] + screw_rotation_speed) % 360
    elif keys[K_f] and fork_height > min_fork_height:
        screw_rotation[0] = (screw_rotation[0] - screw_rotation_speed) % 360
        screw_rotation[1] = (screw_rotation[1] - screw_rotation_speed) % 360
    
    # Update loadcell data
    current_weight = 0
    if carried_cargo:
        current_weight = carried_cargo["weight"]
    load_weight = current_weight
    
    base_value = load_weight / 10.0  # Base value depends on weight
    
    # Add some noise
    noise = random.uniform(-0.05, 0.05)
    
    # Add vibration if fork is moving or if there's active vibration
    movement_vibration = 0
    if (keys[K_r] or keys[K_f]) and (fork_height > min_fork_height and fork_height < max_fork_height):
        movement_vibration = math.sin(pygame.time.get_ticks() * 0.01) * 0.2
        is_vibrating = True
        vibration_amplitude = 0.03 + (load_weight * 0.01)
    elif is_vibrating:
        # Gradually reduce vibration when movement stops
        vibration_amplitude *= 0.98
        if vibration_amplitude < 0.001:
            is_vibrating = False
            vibration_amplitude = 0
    
    # Calculate current value and add to data
    current_value = base_value + noise + movement_vibration
    loadcell_data.append(current_value)
    
    # Keep only the last MAX_DATA_POINTS values
    if len(loadcell_data) > MAX_DATA_POINTS:
        loadcell_data.pop(0)

def check_pickup():
    global carried_cargo
    
    if carried_cargo:
        return  # Already carrying something
    
    # Calculate normalized height percentage (0.0 to 1.0)
    normalized_height = (fork_height - min_fork_height) / (max_fork_height - min_fork_height)
    usable_rod_height = SCREW_ROD_LENGTH - STEPPER_SIZE * 1.25 - SCREW_ROD_RADIUS * 8
    current_height = STEPPER_SIZE * 1.25 + normalized_height * usable_rod_height
    
    # Calculate the global position of the fork
    fork_x = position[0] + math.sin(math.radians(rotation)) * (-FORKLIFT_LENGTH/2 + 0.1 + FORK_LENGTH*0.3)
    fork_y = position[1] - math.cos(math.radians(rotation)) * (-FORKLIFT_LENGTH/2 + 0.1 + FORK_LENGTH*0.3)
    fork_z = position[2] + current_height + SCREW_ROD_RADIUS * 4 + 0.08
    
    pickup_distance = 0.8  # Maximum distance for pickup
    
    for cargo in cargo_objects:
        if not cargo["carried"]:
            cargo_x = cargo["position"][0]
            cargo_y = cargo["position"][1]
            cargo_z = cargo["position"][2] + cargo["size"][2]/2
            
            # Calculate distance between fork and cargo
            distance = math.sqrt((fork_x - cargo_x)**2 + (fork_y - cargo_y)**2 + (fork_z - cargo_z)**2)
            
            # Check if fork is at the right height (with some tolerance)
            height_diff = abs(fork_z - (cargo_z + cargo["size"][2]/2))
            
            if distance < pickup_distance and height_diff < 0.3:
                cargo["carried"] = True
                carried_cargo = cargo
                print(f"Picked up cargo {cargo['id']} with weight {cargo['weight']}kg")
                break

def check_drop():
    global carried_cargo
    
    if not carried_cargo:
        return
    
    # Check if we're over a destination zone
    for zone in destination_zones:
        zone_x = zone["position"][0]
        zone_y = zone["position"][1]
        zone_width = zone["size"][0]
        zone_depth = zone["size"][1]
        
        # Calculate forklift position relative to zone
        rel_x = position[0] - zone_x
        rel_y = position[1] - zone_y
        
        if (abs(rel_x) < zone_width/2 and abs(rel_y) < zone_depth/2):
            # Drop the cargo here
            carried_cargo["carried"] = False
            carried_cargo["position"] = [position[0], position[1], 0]
            print(f"Dropped cargo {carried_cargo['id']} in destination zone")
            carried_cargo = None
            break

def handle_input():
    global position, rotation, fork_height
    
    keys = pygame.key.get_pressed()
    
    # Movement controls
    if keys[K_UP]:
        position[0] += math.sin(math.radians(rotation)) * linear_speed
        position[1] -= math.cos(math.radians(rotation)) * linear_speed
    if keys[K_DOWN]:
        position[0] -= math.sin(math.radians(rotation)) * linear_speed
        position[1] += math.cos(math.radians(rotation)) * linear_speed
    if keys[K_LEFT]:
        rotation += angular_speed
    if keys[K_RIGHT]:
        rotation -= angular_speed
    
    # Fork controls
    if keys[K_r] and fork_height < max_fork_height:
        fork_height += fork_speed
    if keys[K_f] and fork_height > min_fork_height:
        fork_height -= fork_speed
    
    # Cargo controls
    if keys[K_SPACE]:
        check_pickup()
    if keys[K_d]:
        check_drop()

def setup_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 5.0, 10.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.2, 0.2, 0.2, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glMaterialfv(GL_FRONT_AND_BACK, GL_SPECULAR, (1.0, 1.0, 1.0, 1.0))
    glMaterialf(GL_FRONT_AND_BACK, GL_SHININESS, 50.0)
    glEnable(GL_NORMALIZE)

def main():
    global position, rotation, wheel_steering, fork_height
    
    pygame.init()
    pygame.display.set_mode((WIDTH, HEIGHT), DOUBLEBUF|OPENGL)
    pygame.display.set_caption('Industrial Forklift Simulator with Vibration Analysis')
    
    gluPerspective(45, (WIDTH/HEIGHT), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -20)
    glRotatef(-30, 1, 0, 0)  # Tilt view down slightly
    
    setup_lighting()
    
    clock = pygame.time.Clock()
    
    # Initialize fork height
    fork_height = min_fork_height
    
    # Camera follow variables
    camera_distance = 15
    camera_height = 5
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        handle_input()
        update_physics()
        
        # Camera follow
        glLoadIdentity()
        camera_x = position[0] - math.sin(math.radians(rotation)) * camera_distance
        camera_y = position[1] + math.cos(math.radians(rotation)) * camera_distance
        camera_z = position[2] + camera_height
        gluLookAt(
            camera_x, camera_y, camera_z,  # Camera position
            position[0], position[1], position[2],  # Look at point
            0, 0, 1  # Up vector
        )
        
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        
        # Draw scene
        draw_grid()
        create_floor()
        create_walls()
        create_shelves()
        create_destination_zones()
        create_cargo()
        draw_forklift()
        
        # UI elements
        draw_loadcell_graph()
        display_text(f"Position: X={position[0]:.1f}, Y={position[1]:.1f}", 10, 10)
        display_text(f"Rotation: {rotation:.1f}°", 10, 30)
        display_text(f"Fork Height: {fork_height}%", 10, 50)
        display_text(f"Current Load: {load_weight} kg", 10, 70)
        display_text(f"Vibration: {'ON' if is_vibrating else 'OFF'} (Amp: {vibration_amplitude:.3f})", 10, 90)
        display_text("Controls: Arrows=Move, R/F=Raise/Lower Fork, Space=Pickup, D=Drop", 10, HEIGHT-30)
