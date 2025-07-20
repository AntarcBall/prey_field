import pygame
import numpy as np
import sys
import os
import csv
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
from config import sim_cfg, Config
from utils.logger import setup_signal_handlers, log_shutdown
from control_window import ControlWindow

# --- Global State ---
simulation_paused = False

def toggle_pause_simulation():
    """Toggles the simulation's paused state."""
    global simulation_paused
    simulation_paused = not simulation_paused

# --- Constants ---
AGENT_TYPE_RABBIT = 0
AGENT_TYPE_FOX = 1

# --- Simulation Logging ---
LOG_FILE = "simulation_log.csv"

def log_simulation_data(duration: float, config: Config, prevailing_specie: str = None, prevailing_specie_count: int = None):
    """Logs simulation duration and configuration parameters to a CSV file."""
    fieldnames = []
    row_data = {}

    # Manually get all parameters from the nested classes
    # Field parameters
    fieldnames.extend(['field.width', 'field.height', 'field.color'])
    row_data['field.width'] = config.field.width
    row_data['field.height'] = config.field.height
    row_data['field.color'] = str(config.field.color)

    # Simulation parameters
    fieldnames.extend(['simulation.fps', 'simulation.max_agents'])
    row_data['simulation.fps'] = config.simulation.fps
    row_data['simulation.max_agents'] = config.simulation.max_agents

    # Agent parameters
    fieldnames.extend(['agent.initial_foxes', 'agent.initial_rabbits', 'agent.speed_pixels_per_sec', 'agent.speed_per_frame'])
    row_data['agent.initial_foxes'] = config.agent.initial_foxes
    row_data['agent.initial_rabbits'] = config.agent.initial_rabbits
    row_data['agent.speed_pixels_per_sec'] = config.agent.speed_pixels_per_sec
    row_data['agent.speed_per_frame'] = round(config.agent.speed_per_frame, 5)

    # Fox parameters
    fieldnames.extend(['fox.replication_mean', 'fox.replication_sigma', 'fox.replication_range', 'fox.death_prob_per_frame', 'fox.satiation_duration_frames'])
    row_data['fox.replication_mean'] = config.fox.replication_mean
    row_data['fox.replication_sigma'] = config.fox.replication_sigma
    row_data['fox.replication_range'] = str(config.fox.replication_range.tolist())
    row_data['fox.death_prob_per_frame'] = config.fox.death_prob_per_frame
    row_data['fox.satiation_duration_frames'] = config.fox.satiation_duration_frames

    # Rabbit parameters
    fieldnames.extend(['rabbit.replication_rate_per_min', 'rabbit.replication_prob_per_frame'])
    row_data['rabbit.replication_rate_per_min'] = config.rabbit.replication_rate_per_min
    row_data['rabbit.replication_prob_per_frame'] = round(config.rabbit.replication_prob_per_frame, 5)

    # Collision parameters
    fieldnames.extend(['collision.distance'])
    row_data['collision.distance'] = config.collision.distance

    # Simulation results
    fieldnames.extend(["duration_seconds", "prevailing_specie", "prevailing_specie_count"])
    row_data["duration_seconds"] = duration
    row_data["prevailing_specie"] = prevailing_specie
    row_data["prevailing_specie_count"] = prevailing_specie_count


    file_exists = os.path.isfile(LOG_FILE)

    with open(LOG_FILE, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()  # Write header only if file is new
        writer.writerow(row_data)



# --- Constants ---
AGENT_TYPE_RABBIT = 0
AGENT_TYPE_FOX = 1

# --- Pygame Setup ---
os.environ['SDL_VIDEO_WINDOW_POS'] = f"0,0"
pygame.init()
screen = pygame.display.set_mode((sim_cfg.field.width, sim_cfg.field.height))
pygame.display.set_caption("Optimized Killing Field Simulation")
clock = pygame.time.Clock()

# --- PyQtGraph Setup ---
app = QApplication.instance() or QApplication(sys.argv)
win = pg.GraphicsLayoutWidget(show=True, title="Population over Time")
win.resize(800, 400)
win.setWindowTitle('Population Dynamics')
win.move(sim_cfg.field.width, 0) # Position next to Pygame window
pg.setConfigOptions(antialias=True)

plot = win.addPlot(title="Population")
plot.setLabel('left', 'Count')
plot.setLabel('bottom', 'Time (s)')
plot.addLegend()
fox_curve = plot.plot(pen='r', name='Foxes')
rabbit_curve = plot.plot(pen='g', name='Rabbits')

time_points = []
fox_counts = []
rabbit_counts = []

# --- Agent Data (NumPy Array) ---
# [pos_x, pos_y, vel_x, vel_y, type, active, satiation]
agents = np.zeros((sim_cfg.simulation.max_agents, 7), dtype=np.float32)
num_agents = 0

# --- Simulation Functions ---
def add_agent(agent_type, x, y, satiation_level=0):
    """Adds a new agent to the simulation."""
    global num_agents
    if num_agents >= sim_cfg.simulation.max_agents:
        return

    agents[num_agents, 0] = x
    agents[num_agents, 1] = y
    angle = np.random.uniform(0, 2 * np.pi)
    agents[num_agents, 2] = np.cos(angle) * sim_cfg.agent.speed_per_frame
    agents[num_agents, 3] = np.sin(angle) * sim_cfg.agent.speed_per_frame
    agents[num_agents, 4] = agent_type
    agents[num_agents, 5] = 1  # Active
    agents[num_agents, 6] = satiation_level  # Satiation
    num_agents += 1

def remove_agent(index):
    """Removes an agent by swapping with the last active one."""
    global num_agents
    num_agents -= 1
    agents[index] = agents[num_agents]
    agents[num_agents, 5] = 0 # Mark as inactive


def get_replication_count():
    """
    Determines the number of new foxes to create based on a discretized
    normal distribution.
    """
    if sim_cfg.fox.replication_sigma < 0.01:
        return int(round(sim_cfg.fox.replication_mean))
    
    weights = np.exp(-0.5 * ((sim_cfg.fox.replication_range - sim_cfg.fox.replication_mean) / sim_cfg.fox.replication_sigma)**2)
    probabilities = weights / np.sum(weights)
    return np.random.choice(sim_cfg.fox.replication_range, p=probabilities)

def create_initial_agents():
    """Creates the initial set of agents."""
    for _ in range(sim_cfg.agent.initial_rabbits):
        add_agent(AGENT_TYPE_RABBIT, np.random.randint(20, sim_cfg.field.width - 20), np.random.randint(20, sim_cfg.field.height - 20))
    for _ in range(sim_cfg.agent.initial_foxes):
        add_agent(AGENT_TYPE_FOX, np.random.randint(20, sim_cfg.field.width - 20), np.random.randint(20, sim_cfg.field.height - 20))


def draw_agents(surface):
    """Draws all active agents."""
    active_agents = agents[:num_agents]
    is_rabbit = active_agents[:, 4] == AGENT_TYPE_RABBIT
    is_fox = ~is_rabbit

    # Draw Rabbits
    for pos in active_agents[is_rabbit, :2]:
        pygame.draw.circle(surface, (100, 255, 100), pos.astype(int), 5)

    # Draw Foxes
    for agent in active_agents[is_fox]:
        pos = agent[:2]
        vel = agent[2:4]
        satiation = agent[6]
        
        color = (255, 100, 100)  # Default red
        if satiation > 0:
            color = (255, 165, 0) # Orange for satiated

        angle = np.arctan2(vel[1], vel[0])
        size = 8
        p1 = pos + np.array([np.cos(angle), np.sin(angle)]) * size
        p2 = pos + np.array([np.cos(angle + 2.5), np.sin(angle + 2.5)]) * size * 0.8
        p3 = pos + np.array([np.cos(angle - 2.5), np.sin(angle - 2.5)]) * size * 0.8
        pygame.draw.polygon(surface, color, [p1.tolist(), p2.tolist(), p3.tolist()])


# --- Main Simulation ---
def main():
    """Main function to run the simulation loop."""
    setup_signal_handlers()
    global num_agents
    create_initial_agents()

    # --- Control Window Setup ---
    control_win = ControlWindow()
    control_win.show()
    control_win.pause_toggled.connect(toggle_pause_simulation)
    control_win.fps_changed.connect(lambda fps: setattr(sim_cfg.simulation, 'fps', fps))

    running = True
    simulation_active = True
    simulation_ended_naturally = False
    start_time = pygame.time.get_ticks()
    last_plot_update = start_time

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Check if PyQtGraph window is closed
        if not win.isVisible() and not control_win.isVisible():
            running = False

        app.processEvents()

        if simulation_paused:
            # When paused, still draw and tick, but don't update the simulation
            screen.fill(sim_cfg.field.color)
            draw_agents(screen)
            pygame.display.flip()
            clock.tick(sim_cfg.simulation.fps)
            continue

        if simulation_active:
            active_agents = agents[:num_agents]

            # --- Agent Movement ---
            active_agents[:, :2] += active_agents[:, 2:4]
            
            # Wall collisions
            hit_left_wall = active_agents[:, 0] < 0
            hit_right_wall = active_agents[:, 0] > sim_cfg.field.width
            hit_top_wall = active_agents[:, 1] < 0
            hit_bottom_wall = active_agents[:, 1] > sim_cfg.field.height

            active_agents[hit_left_wall | hit_right_wall, 2] *= -1
            active_agents[hit_top_wall | hit_bottom_wall, 3] *= -1
            
            np.clip(active_agents[:, 0], 0, sim_cfg.field.width, out=active_agents[:, 0])
            np.clip(active_agents[:, 1], 0, sim_cfg.field.height, out=active_agents[:, 1])


            # --- Fox Satiation Decay ---
            is_fox_mask = active_agents[:, 4] == AGENT_TYPE_FOX
            satiated_foxes_mask = is_fox_mask & (active_agents[:, 6] > 0)
            active_agents[satiated_foxes_mask, 6] -= 1


            # --- Agent Masks ---
            is_rabbit = active_agents[:, 4] == AGENT_TYPE_RABBIT
            is_fox = ~is_rabbit
            
            # --- Natural Rabbit Replication ---
            if sim_cfg.rabbit.replication_prob_per_frame > 0:
                num_rabbits = np.sum(is_rabbit)
                replication_chance = np.random.rand(num_rabbits) < sim_cfg.rabbit.replication_prob_per_frame
                rabbits_that_replicated = active_agents[is_rabbit][replication_chance]
                for r in rabbits_that_replicated:
                    add_agent(AGENT_TYPE_RABBIT, r[0], r[1])

            # --- Natural Fox Death ---
            if sim_cfg.fox.death_prob_per_frame > 0:
                num_foxes = np.sum(is_fox)
                death_chance = np.random.rand(num_foxes) < sim_cfg.fox.death_prob_per_frame
                fox_indices_to_remove = np.where(is_fox)[0][death_chance]
                # Iterate backwards to not mess up indices while removing
                for i in sorted(fox_indices_to_remove, reverse=True):
                    remove_agent(i)
                    
            # --- Collision Detection ---
            # Re-calculate masks after potential removals
            active_agents = agents[:num_agents]
            is_rabbit = active_agents[:, 4] == AGENT_TYPE_RABBIT
            is_fox = ~is_rabbit
            
            fox_pos = active_agents[is_fox, :2]
            rabbit_pos = active_agents[is_rabbit, :2]
            
            if fox_pos.size > 0 and rabbit_pos.size > 0:
                dist_matrix = np.sqrt(((fox_pos[:, np.newaxis, :] - rabbit_pos[np.newaxis, :, :])**2).sum(axis=2))
                collisions = dist_matrix < sim_cfg.collision.distance
                
                collided_fox_indices, collided_rabbit_indices = np.where(collisions)
                
                unique_collided_rabbits, unique_indices = np.unique(collided_rabbit_indices, return_index=True)
                
                if unique_collided_rabbits.size > 0:
                    rabbits_to_remove_indices = np.where(is_rabbit)[0][unique_collided_rabbits]
                    
                    # Use the first fox that collided with each unique rabbit
                    colliding_fox_indices = np.where(is_fox)[0][collided_fox_indices[unique_indices]]

                    # Filter for foxes that are not satiated
                    hungry_fox_mask = agents[colliding_fox_indices, 6] == 0
                    
                    hungry_foxes_that_ate = colliding_fox_indices[hungry_fox_mask]
                    rabbits_eaten_by_hungry_foxes = rabbits_to_remove_indices[hungry_fox_mask]

                    # Add new foxes and update satiation
                    for i in hungry_foxes_that_ate:
                        agents[i, 6] = sim_cfg.fox.satiation_duration_frames
                        num_new_foxes = get_replication_count()
                        for _ in range(num_new_foxes):
                            add_agent(AGENT_TYPE_FOX, agents[i, 0], agents[i, 1], satiation_level=sim_cfg.fox.satiation_duration_frames)
                    
                    # Remove eaten rabbits (iterate backwards)
                    for i in sorted(rabbits_eaten_by_hungry_foxes, reverse=True):
                        remove_agent(i)

            # Check for simulation end conditions
            if np.sum(agents[:num_agents, 4] == AGENT_TYPE_RABBIT) == 0 or \
               np.sum(agents[:num_agents, 4] == AGENT_TYPE_FOX) == 0:
                simulation_active = False
                simulation_ended_naturally = True
                log_shutdown("extinction")
                print("Simulation over. Populations died out.")
                if sim_cfg.simulation.close_on_extinction:
                    running = False

        # --- Drawing ---
        screen.fill(sim_cfg.field.color)
        draw_agents(screen)
        pygame.display.flip()

        # --- Data Update for Plot ---
        if simulation_active:
            current_time = pygame.time.get_ticks()
            if current_time - last_plot_update > 250:
                elapsed_time_sec = (current_time - start_time) / 1000.0
                time_points.append(elapsed_time_sec)
                
                active_agents = agents[:num_agents]
                num_foxes = np.sum(active_agents[:, 4] == AGENT_TYPE_FOX)
                num_rabbits = num_agents - num_foxes
                
                fox_counts.append(num_foxes)
                rabbit_counts.append(num_rabbits)
                
                fox_curve.setData(time_points, fox_counts)
                rabbit_curve.setData(time_points, rabbit_counts)
                last_plot_update = current_time

        # --- Tick ---
        clock.tick(sim_cfg.simulation.fps)

    # Log simulation data before quitting
    if simulation_ended_naturally:
        final_elapsed_time_sec = (pygame.time.get_ticks() - start_time) / 1000.0
        
        # Determine prevailing species
        num_rabbits = np.sum(agents[:num_agents, 4] == AGENT_TYPE_RABBIT)
        num_foxes = np.sum(agents[:num_agents, 4] == AGENT_TYPE_FOX)
        
        prevailing_specie = "None"
        prevailing_specie_count = 0
        if num_rabbits > 0:
            prevailing_specie = "Rabbit"
            prevailing_specie_count = num_rabbits
        elif num_foxes > 0:
            prevailing_specie = "Fox"
            prevailing_specie_count = num_foxes
            
        log_simulation_data(final_elapsed_time_sec, sim_cfg, prevailing_specie, prevailing_specie_count)
    else:
        log_shutdown("normal_exit")

    pygame.quit()
    win.close()
    app.quit()


if __name__ == '__main__':
    main()