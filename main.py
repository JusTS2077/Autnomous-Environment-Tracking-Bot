"""
main.py - Mars Rover Pygame Visualizer & Live Console Logger with Hybrid AI Switch
---------------------------------------------------------------------------------
AI Express Hackathon: Hybrid Autonomous Mars Rover Agent (Units 1 - 4 AI)
Combines Propositional Logic KB (Resolution & Entailment) with A* Search Evasion (Manhattan Heuristic).
Features interactive UI buttons to trigger "Solvable", "⚡ Timed Escape", and "Quick Clear" scenarios.
"""

import sys
import time
import os
import pygame

from grid import GridEnvironment, UNKNOWN, SAFE, START, GOAL, HAZARD, RADIATION, STORM
from kb_agent import KnowledgeBase


# --- COLOR PALETTE (RGB) ---
COLOR_BG = (15, 23, 42)            # Dark Slate Space Background
COLOR_GRID_LINE = (30, 41, 59)     # Grid Line Borders
COLOR_UNKNOWN = (51, 65, 85)       # Unknown Fog-of-War (Slate)
COLOR_SAFE = (209, 250, 229)       # Proven Safe Cell (Mint Light)
COLOR_VISITED = (167, 243, 208)    # Visited Path Cell (Soft Emerald)
COLOR_HAZARD = (239, 68, 68)       # Proved Hazard Crater (Red)
COLOR_RADIATION = (168, 85, 247)   # Proved Radiation Anomaly (Purple)
COLOR_STORM = (220, 38, 38)        # Spreading Dust Storm Threat (Fiery Red)
COLOR_START = (16, 185, 129)       # Start Station S (Green)
COLOR_GOAL = (245, 158, 11)        # Target Goal G (Amber Gold)
COLOR_ROVER = (59, 130, 246)       # Mars Rover Agent (Royal Blue)
COLOR_PATH = (251, 191, 36)        # Planned Path Highlights (Yellow)
COLOR_PATH_LINE = (217, 119, 6)    # Path Line (Deep Gold)
COLOR_HUD_BG = (2, 6, 23)          # HUD Deep Dark Slate
COLOR_TEXT_MAIN = (255, 255, 255)  # Primary Text (White)
COLOR_TEXT_MUTED = (148, 163, 184)# Secondary Text (Slate Light)
COLOR_ALERT = (239, 68, 68)        # Alert Text (Red)
COLOR_SIGNAL_B = (56, 189, 248)    # Breeze Percept Signal (Sky Blue)
COLOR_SIGNAL_G = (232, 121, 249)   # Glow Percept Signal (Pink Magenta)

# Button Colors
COLOR_BTN_SOLVABLE = (16, 185, 129)
COLOR_BTN_TRAPPED = (239, 68, 68)
COLOR_BTN_CLEAR = (59, 130, 246)
COLOR_BTN_RESET = (100, 116, 139)


class RoverVisualizer:
    def __init__(self, grid_size=10, cell_size=55):
        self.grid_size = grid_size
        self.cell_size = cell_size
        self.grid_width = grid_size * cell_size
        self.grid_height = grid_size * cell_size
        self.hud_height = 145

        self.screen_width = self.grid_width
        self.screen_height = self.grid_height + self.hud_height

        pygame.init()
        pygame.display.set_caption("Autonomous Mars Rover - Hybrid AI Agent (Logic KB + A* Search)")

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        self.clock = pygame.time.Clock()

        self.font_title = pygame.font.SysFont("Segoe UI", 15, bold=True)
        self.font_hud = pygame.font.SysFont("Consolas", 13, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 11)
        self.font_btn = pygame.font.SysFont("Segoe UI", 12, bold=True)
        self.font_icon = pygame.font.SysFont("Consolas", 13, bold=True)

        # Interactive Button Rectangles
        self.btn_solvable = pygame.Rect(15, self.grid_height + 98, 125, 32)
        self.btn_trapped = pygame.Rect(150, self.grid_height + 98, 135, 32)
        self.btn_clear = pygame.Rect(295, self.grid_height + 98, 105, 32)
        self.btn_reset = pygame.Rect(410, self.grid_height + 98, 90, 32)

    def draw(self, grid_env, kb, rover_pos, planned_path, step_count, breeze, glow, status_msg="NAVIGATING", active_preset="solvable"):
        """Renders Mars terrain, fog-of-war, KB inferred states, Rover, HUD, and Buttons."""
        self.screen.fill(COLOR_BG)
        mouse_pos = pygame.mouse.get_pos()

        # 1. Draw Grid Cells based on Knowledge Base State
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                pos = (x, y)
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)

                if pos in grid_env.storm_cells:
                    color = COLOR_STORM
                elif pos == grid_env.start:
                    color = COLOR_START
                elif pos == grid_env.goal:
                    color = COLOR_GOAL
                elif pos in kb.known_hazards:
                    color = COLOR_HAZARD
                elif pos in kb.known_radiation:
                    color = COLOR_RADIATION
                elif pos in kb.visited:
                    color = COLOR_VISITED
                elif pos in kb.known_safe:
                    color = COLOR_SAFE
                else:
                    color = COLOR_UNKNOWN

                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, rect, 1)

                if pos in grid_env.storm_cells:
                    lbl = self.font_icon.render("⚡", True, (255, 255, 255))
                    self.screen.blit(lbl, (x * self.cell_size + 20, y * self.cell_size + 15))
                elif pos in kb.known_hazards:
                    lbl = self.font_icon.render("H", True, (255, 255, 255))
                    self.screen.blit(lbl, (x * self.cell_size + 20, y * self.cell_size + 15))
                elif pos in kb.known_radiation:
                    lbl = self.font_icon.render("R", True, (255, 255, 255))
                    self.screen.blit(lbl, (x * self.cell_size + 20, y * self.cell_size + 15))

        # Station Labels
        sx, sy = grid_env.start
        gx, gy = grid_env.goal
        s_lbl = self.font_hud.render("S", True, (255, 255, 255))
        g_lbl = self.font_hud.render("G", True, (255, 255, 255))
        self.screen.blit(s_lbl, (sx * self.cell_size + 20, sy * self.cell_size + 15))
        self.screen.blit(g_lbl, (gx * self.cell_size + 20, gy * self.cell_size + 15))

        # 2. Draw Planned Path (Gold Line)
        if planned_path and len(planned_path) > 1:
            points = [(px * self.cell_size + self.cell_size // 2, py * self.cell_size + self.cell_size // 2) for px, py in planned_path]
            pygame.draw.lines(self.screen, COLOR_PATH_LINE, False, points, 3)
            for px, py in planned_path:
                if (px, py) not in (grid_env.start, grid_env.goal, rover_pos):
                    p_rect = pygame.Rect(px * self.cell_size + 18, py * self.cell_size + 18, 
                                         self.cell_size - 36, self.cell_size - 36)
                    pygame.draw.rect(self.screen, COLOR_PATH, p_rect, border_radius=3)

        # 3. Draw Mars Rover Agent
        rx, ry = rover_pos
        center_x = rx * self.cell_size + self.cell_size // 2
        center_y = ry * self.cell_size + self.cell_size // 2
        pygame.draw.circle(self.screen, COLOR_ROVER, (center_x, center_y), self.cell_size // 3)
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), self.cell_size // 3, 2)

        if breeze:
            b_surf = self.font_small.render("B", True, COLOR_SIGNAL_B)
            self.screen.blit(b_surf, (rx * self.cell_size + 5, ry * self.cell_size + 5))
        if glow:
            g_surf = self.font_small.render("G", True, COLOR_SIGNAL_G)
            self.screen.blit(g_surf, (rx * self.cell_size + self.cell_size - 12, ry * self.cell_size + 5))

        # 4. Draw HUD Bar
        hud_rect = pygame.Rect(0, self.grid_height, self.screen_width, self.hud_height)
        pygame.draw.rect(self.screen, COLOR_HUD_BG, hud_rect)

        mode_badge = f"ALGO: [{kb.current_algo_mode}]"
        title_surf = self.font_title.render(f"Mars Rover Agent | {mode_badge}", True, COLOR_TEXT_MAIN)
        self.screen.blit(title_surf, (15, self.grid_height + 8))

        status_color = COLOR_ALERT if "TRAPPED" in status_msg else COLOR_START
        status_surf = self.font_hud.render(f"STATUS: {status_msg}", True, status_color)
        self.screen.blit(status_surf, (self.screen_width - status_surf.get_width() - 15, self.grid_height + 8))

        # HUD Metrics Row 1
        percept_str = f"Breeze={'TRUE' if breeze else 'False'}, Glow={'TRUE' if glow else 'False'}"
        m1_text = f"Step: {step_count:<2} | Pos: ({rx},{ry}) | Percepts: [{percept_str}]"
        m1_surf = self.font_hud.render(m1_text, True, COLOR_TEXT_MAIN)
        self.screen.blit(m1_surf, (15, self.grid_height + 36))

        # HUD Metrics Row 2
        m2_text = f"KB Updates: {kb.total_kb_updates:<2} | Inferences: {kb.total_inferences:<2} | Proven Safe: {len(kb.known_safe):<2} | A* Switches: {kb.a_star_switches_count}"
        m2_surf = self.font_hud.render(m2_text, True, COLOR_TEXT_MUTED)
        self.screen.blit(m2_surf, (15, self.grid_height + 62))

        # 5. Render Interactive Scenario Buttons
        buttons = [
            (self.btn_solvable, "Normal Run", COLOR_BTN_SOLVABLE, active_preset == "solvable"),
            (self.btn_trapped, "Martian Storm", COLOR_BTN_TRAPPED, active_preset == "trapped"),
            (self.btn_clear, "Quick Clear", COLOR_BTN_CLEAR, active_preset == "clear"),
            (self.btn_reset, "Reset", COLOR_BTN_RESET, False)
        ]

        for btn_rect, text, base_color, is_active in buttons:
            is_hovered = btn_rect.collidepoint(mouse_pos)
            bg_color = base_color if not is_hovered else (min(255, base_color[0]+30), min(255, base_color[1]+30), min(255, base_color[2]+30))
            border_color = (255, 255, 255) if is_active or is_hovered else (71, 85, 105)
            border_width = 3 if is_active else 1

            pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=5)
            pygame.draw.rect(self.screen, border_color, btn_rect, border_width, border_radius=5)

            btn_txt = self.font_btn.render(text, True, (255, 255, 255))
            txt_x = btn_rect.x + (btn_rect.width - btn_txt.get_width()) // 2
            txt_y = btn_rect.y + (btn_rect.height - btn_txt.get_height()) // 2
            self.screen.blit(btn_txt, (txt_x, txt_y))

        pygame.display.flip()

    def handle_click(self, mouse_pos):
        """Returns the clicked scenario preset string if a button was clicked, or None."""
        if self.btn_solvable.collidepoint(mouse_pos):
            return "solvable"
        elif self.btn_trapped.collidepoint(mouse_pos):
            return "trapped"
        elif self.btn_clear.collidepoint(mouse_pos):
            return "clear"
        elif self.btn_reset.collidepoint(mouse_pos):
            return "reset"
        return None


def run_mars_rover_simulation(grid_size=10, step_delay=0.35, initial_preset="solvable"):
    """Main execution loop for Hybrid Mars Rover AI Agent (Logic KB + A* Search)."""
    
    print("=" * 75)
    print("       COLLEGE AI HACKATHON: HYBRID AUTONOMOUS MARS ROVER AGENT")
    print("         Track: Hybrid AI Agent (Logic KB + A* Search Evasion)")
    print("=" * 75)
    print(f"Grid Dimensions   : {grid_size} x {grid_size} (Hidden Hazard & Multi-Cell Storm)")
    print(f"Primary Algorithm : Propositional Logic KB (Resolution & Entailment)")
    print(f"Evasion Algorithm : A* Search Engine (Manhattan Heuristic h(n)=|dx|+|dy|)")
    print(f"Interactive UI    : Use UI Buttons to trigger A* Evasion & Logic scenarios!")
    print("=" * 75)

    visualizer = RoverVisualizer(grid_size=grid_size, cell_size=55)

    def init_scenario(preset_name):
        env = GridEnvironment(size=grid_size, start=(0, 0), goal=(grid_size-1, grid_size-1), preset=preset_name)
        agent_kb = KnowledgeBase(grid_size=grid_size)
        return env, agent_kb

    active_preset = initial_preset
    grid_env, kb = init_scenario(active_preset)

    start_time = time.time()
    current_pos = grid_env.start
    step_count = 0
    running = True
    paused = False
    status_msg = "NAVIGATING"
    mission_finished = False

    print("\n" + "-" * 75)
    print(f"INITIALIZING SCENARIO PRESET: [{active_preset.upper()}]")
    if active_preset == "trapped":
        print("[HYBRID ALGORITHM SWITCH] Multi-Cell Storm Barrier Detected!")
        print("   Switching from [PROPOSITIONAL LOGIC KB] --> [A* SEARCH WITH MANHATTAN HEURISTIC]!")
    print("LIVE LOGICAL & SEARCH INFERENCE LOG (Split-Screen Capture Ready):")
    print("-" * 75)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicked_action = visualizer.handle_click(event.pos)
                if clicked_action:
                    if clicked_action == "reset":
                        preset_to_load = active_preset
                    else:
                        preset_to_load = clicked_action

                    active_preset = preset_to_load
                    grid_env, kb = init_scenario(active_preset)
                    current_pos = grid_env.start
                    step_count = 0
                    start_time = time.time()
                    mission_finished = False
                    status_msg = "NAVIGATING"
                    print("\n" + "★" * 75)
                    print(f"[SCENARIO TRIGGERED] Loaded Scenario Preset: [{active_preset.upper()}]")
                    if active_preset == "trapped":
                        print("[HYBRID SWITCH] Activated A* Search Evasion Mode!")
                    print("★" * 75 + "\n")

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_p):
                    paused = not paused
                    print(f"[USER] {'PAUSED' if paused else 'RESUMED'} simulation.")

        if paused:
            visualizer.draw(grid_env, kb, current_pos, [], step_count, False, False, status_msg="PAUSED", active_preset=active_preset)
            visualizer.clock.tick(10)
            continue

        elapsed_time = time.time() - start_time

        # Check Goal Condition FIRST
        if current_pos == grid_env.goal:
            if not mission_finished:
                mission_finished = True
                status_msg = "GOAL REACHED!"
                print("\n" + "=" * 75)
                print("                  MISSION SUCCESS SUMMARY")
                print("=" * 75)
                print(f" Goal Reached Pos          : {current_pos}")
                print(f" Active Algorithm Engine   : {kb.current_algo_mode}")
                print(f" Total Time Elapsed        : {elapsed_time:.2f} seconds")
                print(f" Total Path Cost (Steps)   : {step_count} steps")
                print(f" Total KB Updates          : {kb.total_kb_updates}")
                print(f" A* Search Engine Switches : {kb.a_star_switches_count}")
                print("=" * 75 + "\n")

            breeze, glow = grid_env.perceive(current_pos[0], current_pos[1])
            visualizer.draw(grid_env, kb, current_pos, [], step_count, breeze, glow, status_msg=status_msg, active_preset=active_preset)
            visualizer.clock.tick(10)
            continue

        # 1. PERCEIVE
        breeze, glow = grid_env.perceive(current_pos[0], current_pos[1])

        # 2. TELL
        asserted_facts = kb.tell_percept(current_pos, breeze, glow)

        # 3. INFER
        new_safe, new_hazards, new_radiation = kb.run_inference()

        # Console Log
        print(f"\n[STEP {step_count:02d}] Rover at {current_pos} | Percepts: Breeze={breeze}, Glow={glow} | Mode: {kb.current_algo_mode}")
        print(f" -> [KB TELL] Asserted Facts ({len(asserted_facts)}): {', '.join(asserted_facts[:3])}{'...' if len(asserted_facts)>3 else ''}")
        
        infer_summary = []
        if new_safe:
            infer_summary.append(f"Proven Safe: {new_safe}")
        if new_hazards:
            infer_summary.append(f"Proven HAZARDS: {new_hazards}")
        if new_radiation:
            infer_summary.append(f"Proven RADIATION: {new_radiation}")
        
        if infer_summary:
            print(f" -> [KB RESOLUTION INFER] { ' | '.join(infer_summary) }")

        # 4. DECIDE
        next_step, target_node, reason = kb.plan_next_action(current_pos, grid_env.goal, grid_env)

        print(f" -> [DECISION ENGINE] Next Step: {next_step} | Target: {target_node} | {reason}")

        if not next_step:
            status_msg = "ROVER TRAPPED!"
            print("\n[MISSION FAILED] Rover is completely trapped by surrounding hazards/radiation!")
            visualizer.draw(grid_env, kb, current_pos, [], step_count, breeze, glow, status_msg=status_msg, active_preset=active_preset)
            visualizer.clock.tick(10)
            continue

        planned_path = kb.find_safe_path(current_pos, target_node) or [current_pos, next_step]

        # Update Pygame Visualization
        visualizer.draw(grid_env, kb, current_pos, planned_path, step_count, breeze, glow, status_msg=status_msg, active_preset=active_preset)
        time.sleep(step_delay)

        # Move Rover
        current_pos = next_step
        step_count += 1

    pygame.quit()


if __name__ == "__main__":
    run_mars_rover_simulation()
