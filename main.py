"""
main.py - Full-Screen Mars Rover Telemetry Dashboard & Asset Image Renderer
---------------------------------------------------------------------------------
AI Express Hackathon: Hybrid Autonomous Mars Rover Agent (Units 1 - 4 AI)
Features:
- Automatic PNG Asset Loading from assets/ folder (rover.png, hazard.png, radiation.png, etc.)
- Full-Screen Desktop Dashboard with live telemetry (Speedometer m/s, Battery Indicator %, Heading)
- Perfectly centered cell positioning for Rover chassis and station lander icons
- Silky-Smooth 60 FPS Sub-Frame Pixel Interpolation for driving animation
- Interactive Scenario Buttons: [Normal Run], [Martian Storm], [Quick Clear], [Reset]
"""

import sys
import time
import math
import random
import os
import pygame

from grid import GridEnvironment, UNKNOWN, SAFE, START, GOAL, HAZARD, RADIATION, STORM
from kb_agent import KnowledgeBase


# --- COLOR PALETTE (RGB) ---
COLOR_BG = (10, 15, 29)            # Deep Space Background
COLOR_GRID_LINE = (30, 41, 59)     # Grid Line Borders
COLOR_UNKNOWN = (30, 41, 59)       # Fog-of-War (Dark Slate)
COLOR_SAFE = (209, 250, 229)       # Proven Safe Cell (Mint Light)
COLOR_VISITED = (167, 243, 208)    # Visited Path Cell (Soft Emerald)
COLOR_HAZARD = (239, 68, 68)       # Proved Hazard Crater (Red)
COLOR_RADIATION = (168, 85, 247)   # Proved Radiation Anomaly (Purple)
COLOR_STORM = (220, 38, 38)        # Spreading Dust Storm Threat (Fiery Red)
COLOR_START = (16, 185, 129)       # Start Station S (Green)
COLOR_GOAL = (245, 158, 11)        # Target Goal G (Amber Gold)
COLOR_ROVER = (59, 130, 246)       # Mars Rover Agent Chassis (Royal Blue)
COLOR_SHIELD = (56, 189, 248)      # Overdrive Shield Aura (Sky Blue / Cyan)
COLOR_PATH = (251, 191, 36)        # Planned Path Highlights (Yellow)
COLOR_PATH_LINE = (217, 119, 6)    # Path Line (Deep Gold)
COLOR_PANEL_BG = (15, 23, 42)      # Dashboard Panel BG
COLOR_PANEL_BORDER = (51, 65, 85)  # Panel Border
COLOR_TEXT_MAIN = (248, 250, 252)  # Primary Text (Slate Light)
COLOR_TEXT_MUTED = (148, 163, 184)# Secondary Text
COLOR_ALERT = (239, 68, 68)        # Alert Text
COLOR_GAUGE_BAR = (16, 185, 129)   # Speedometer Gauge Bar

# Button Colors
COLOR_BTN_SOLVABLE = (16, 185, 129)
COLOR_BTN_TRAPPED = (239, 68, 68)
COLOR_BTN_CLEAR = (59, 130, 246)
COLOR_BTN_RESET = (100, 116, 139)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)


def draw_custom_rover_icon(surface, center_x, center_y, size, shield_active=False, heading_angle=45, custom_img=None):
    """Draws Mars Rover chassis centered at (center_x, center_y) using PNG image or procedural vector."""
    if custom_img:
        img_rect = custom_img.get_rect(center=(center_x, center_y))
        surface.blit(custom_img, img_rect)
        if shield_active:
            pygame.draw.circle(surface, (56, 189, 248), (center_x, center_y), size // 2 + 4, 3)
        return

    body_half = int(size * 0.22)
    wheel_w = int(size * 0.12)
    wheel_h = int(size * 0.18)

    if shield_active:
        pygame.draw.circle(surface, (56, 189, 248), (center_x, center_y), body_half + 8, 3)
        pygame.draw.circle(surface, (186, 230, 253), (center_x, center_y), body_half + 12, 1)

    wheel_positions = [
        (center_x - body_half - wheel_w + 2, center_y - body_half),
        (center_x - body_half - wheel_w + 2, center_y - wheel_h // 2),
        (center_x - body_half - wheel_w + 2, center_y + body_half - wheel_h),
        (center_x + body_half - 2, center_y - body_half),
        (center_x + body_half - 2, center_y - wheel_h // 2),
        (center_x + body_half - 2, center_y + body_half - wheel_h)
    ]
    for wx, wy in wheel_positions:
        w_rect = pygame.Rect(wx, wy, wheel_w, wheel_h)
        pygame.draw.rect(surface, (30, 41, 59), w_rect, border_radius=2)
        pygame.draw.rect(surface, (148, 163, 184), w_rect, 1, border_radius=2)

    body_rect = pygame.Rect(center_x - body_half, center_y - body_half, body_half * 2, body_half * 2)
    pygame.draw.rect(surface, (37, 99, 235), body_rect, border_radius=4)
    pygame.draw.rect(surface, (255, 255, 255), body_rect, 2, border_radius=4)

    solar_half = int(body_half * 0.65)
    solar_rect = pygame.Rect(center_x - solar_half, center_y - solar_half, solar_half * 2, solar_half * 2)
    pygame.draw.rect(surface, (245, 158, 11), solar_rect, border_radius=2)
    pygame.draw.line(surface, (180, 83, 9), (solar_rect.left, center_y), (solar_rect.right, center_y), 1)
    pygame.draw.line(surface, (180, 83, 9), (center_x, solar_rect.top), (center_x, solar_rect.bottom), 1)

    mast_dist = body_half - 2
    mast_x = center_x + int(math.cos(math.radians(heading_angle)) * mast_dist)
    mast_y = center_y - int(math.sin(math.radians(heading_angle)) * mast_dist)
    pygame.draw.circle(surface, (226, 232, 240), (mast_x, mast_y), 4)
    pygame.draw.circle(surface, (239, 68, 68), (mast_x, mast_y), 2)


def draw_station_lander_icon(surface, x, y, size, is_start=True, custom_img=None):
    """Draws station lander icon for Start (S) or Goal (G)."""
    if custom_img:
        surface.blit(custom_img, (x, y))
        return

    cx = x + size // 2
    cy = y + size // 2
    r = size // 3.2

    bg_color = (16, 185, 129) if is_start else (245, 158, 11)
    pygame.draw.circle(surface, bg_color, (cx, cy), int(r))
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), int(r), 2)

    for dx, dy in [(-r, -r), (r, -r), (-r, r), (r, r)]:
        pygame.draw.line(surface, (255, 255, 255), (cx, cy), (cx + int(dx), cy + int(dy)), 2)

    font = pygame.font.SysFont("Consolas", 14, bold=True)
    lbl = font.render("S" if is_start else "G", True, (255, 255, 255))
    surface.blit(lbl, (cx - lbl.get_width() // 2, cy - lbl.get_height() // 2))


class RoverVisualizer:
    def __init__(self, grid_size=10):
        pygame.init()
        pygame.display.set_caption("NASA / JPL Autonomous Mars Rover Telemetry Dashboard")

        display_info = pygame.display.Info()
        self.screen_width = display_info.current_w
        self.screen_height = display_info.current_h

        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN | pygame.RESIZABLE)
        self.clock = pygame.time.Clock()

        self.grid_size = grid_size
        
        self.margin = 30
        self.panel_width = 420
        self.grid_area_width = self.screen_width - self.panel_width - (self.margin * 3)
        self.grid_area_height = self.screen_height - (self.margin * 2)

        self.cell_size = min(self.grid_area_width // grid_size, self.grid_area_height // grid_size)
        self.grid_width = self.cell_size * grid_size
        self.grid_height = self.cell_size * grid_size

        self.grid_x = self.margin + (self.grid_area_width - self.grid_width) // 2
        self.grid_y = self.margin + (self.grid_area_height - self.grid_height) // 2

        self.panel_x = self.screen_width - self.panel_width - self.margin
        self.panel_y = self.margin

        # Fonts
        self.font_header = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_title = pygame.font.SysFont("Segoe UI", 16, bold=True)
        self.font_hud = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_small = pygame.font.SysFont("Consolas", 12)
        self.font_btn = pygame.font.SysFont("Segoe UI", 13, bold=True)

        # Telemetry State Variables
        self.simulated_speed = 0.0
        self.target_speed = 2.8
        self.battery_level = 98.0
        self.heading_angle = 45

        # UI Buttons in Panel
        btn_y_start = self.panel_y + 480
        btn_w, btn_h = 180, 36
        self.btn_solvable = pygame.Rect(self.panel_x + 20, btn_y_start, btn_w, btn_h)
        self.btn_trapped = pygame.Rect(self.panel_x + 215, btn_y_start, btn_w, btn_h)
        self.btn_clear = pygame.Rect(self.panel_x + 20, btn_y_start + 48, btn_w, btn_h)
        self.btn_reset = pygame.Rect(self.panel_x + 215, btn_y_start + 48, btn_w, btn_h)
        self.btn_fullscreen = pygame.Rect(self.panel_x + 20, btn_y_start + 96, 375, 36)

        # Load Custom PNG Assets if present in assets/ directory
        self.assets = {}
        self._load_custom_assets()

    def _load_custom_assets(self):
        """Loads custom PNG images from assets/ directory if available."""
        asset_names = ["rover", "hazard", "radiation", "storm", "start", "goal", "safe"]
        for name in asset_names:
            filename = f"{name}.png"
            path = os.path.join(ASSETS_DIR, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    scaled_img = pygame.transform.smoothscale(img, (self.cell_size, self.cell_size))
                    self.assets[name] = scaled_img
                    print(f" -> [ASSET LOADED] Loaded custom asset: assets/{filename}")
                except Exception as e:
                    print(f" -> [ASSET WARNING] Could not load assets/{filename}: {e}")

    def update_telemetry(self, is_moving, new_heading=None):
        """Simulates live speed gauge fluctuations, battery drain indicator, and heading angle."""
        if is_moving:
            self.target_speed = random.uniform(2.5, 3.8)
            self.simulated_speed += (self.target_speed - self.simulated_speed) * 0.25
            self.battery_level = max(10.0, self.battery_level - 0.03)
            if new_heading is not None:
                self.heading_angle = new_heading
        else:
            self.simulated_speed += (0.0 - self.simulated_speed) * 0.25

    def draw_frame(self, grid_env, kb, rover_center_x, rover_center_y, planned_path, step_count, breeze, glow, status_msg="NAVIGATING", active_preset="solvable"):
        """Renders Mars terrain, fog-of-war, KB inferred states, Rover at exact center, HUD Telemetry Panel, and Buttons."""
        self.screen.fill(COLOR_BG)
        mouse_pos = pygame.mouse.get_pos()

        # 1. Render Main Grid Canvas Container
        grid_container = pygame.Rect(self.grid_x - 10, self.grid_y - 10, self.grid_width + 20, self.grid_height + 20)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, grid_container, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, grid_container, 2, border_radius=10)

        # Render Grid Cells
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                pos = (x, y)
                cell_rect = pygame.Rect(self.grid_x + x * self.cell_size, self.grid_y + y * self.cell_size, self.cell_size, self.cell_size)

                if pos in grid_env.storm_cells:
                    color = COLOR_STORM
                    asset_key = "storm"
                elif pos == grid_env.start:
                    color = COLOR_SAFE
                    asset_key = "start"
                elif pos == grid_env.goal:
                    color = COLOR_SAFE
                    asset_key = "goal"
                elif pos in kb.known_hazards:
                    color = COLOR_HAZARD
                    asset_key = "hazard"
                elif pos in kb.known_radiation:
                    color = COLOR_RADIATION
                    asset_key = "radiation"
                elif pos in kb.visited:
                    color = COLOR_VISITED
                    asset_key = "safe"
                elif pos in kb.known_safe:
                    color = COLOR_SAFE
                    asset_key = "safe"
                else:
                    color = COLOR_UNKNOWN
                    asset_key = None

                pygame.draw.rect(self.screen, color, cell_rect)
                pygame.draw.rect(self.screen, COLOR_GRID_LINE, cell_rect, 1)

                if asset_key and asset_key in self.assets and asset_key not in ("start", "goal"):
                    self.screen.blit(self.assets[asset_key], cell_rect.topleft)
                else:
                    if pos in grid_env.storm_cells:
                        lbl = self.font_hud.render("⚡", True, (255, 255, 255))
                        self.screen.blit(lbl, (cell_rect.x + self.cell_size // 2 - 6, cell_rect.y + self.cell_size // 2 - 8))
                    elif pos in kb.known_hazards:
                        lbl = self.font_hud.render("H", True, (255, 255, 255))
                        self.screen.blit(lbl, (cell_rect.x + self.cell_size // 2 - 5, cell_rect.y + self.cell_size // 2 - 8))
                    elif pos in kb.known_radiation:
                        lbl = self.font_hud.render("R", True, (255, 255, 255))
                        self.screen.blit(lbl, (cell_rect.x + self.cell_size // 2 - 5, cell_rect.y + self.cell_size // 2 - 8))

        sx, sy = grid_env.start
        gx, gy = grid_env.goal
        draw_station_lander_icon(self.screen, self.grid_x + sx * self.cell_size, self.grid_y + sy * self.cell_size, self.cell_size, is_start=True, custom_img=self.assets.get("start"))
        draw_station_lander_icon(self.screen, self.grid_x + gx * self.cell_size, self.grid_y + gy * self.cell_size, self.cell_size, is_start=False, custom_img=self.assets.get("goal"))

        # 2. Draw Planned Path (Gold Line)
        if planned_path and len(planned_path) > 1:
            points = [(self.grid_x + px * self.cell_size + self.cell_size // 2, self.grid_y + py * self.cell_size + self.cell_size // 2) for px, py in planned_path]
            pygame.draw.lines(self.screen, COLOR_PATH_LINE, False, points, 4)

        # 3. Render Custom Mars Rover Agent Chassis at Sub-Pixel Center (rover_center_x, rover_center_y)
        draw_custom_rover_icon(
            self.screen, 
            int(rover_center_x), 
            int(rover_center_y), 
            self.cell_size, 
            shield_active=kb.overdrive_shield_active,
            heading_angle=self.heading_angle,
            custom_img=self.assets.get("rover")
        )

        # 4. Render Telemetry Dashboard Panel
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.grid_height + 20)
        pygame.draw.rect(self.screen, COLOR_PANEL_BG, panel_rect, border_radius=10)
        pygame.draw.rect(self.screen, COLOR_PANEL_BORDER, panel_rect, 2, border_radius=10)

        title_surf = self.font_header.render("MARS ROVER TELEMETRY", True, COLOR_TEXT_MAIN)
        self.screen.blit(title_surf, (self.panel_x + 20, self.panel_y + 20))
        sub_title = self.font_small.render("NASA / JPL Autonomous Mission Control", True, COLOR_TEXT_MUTED)
        self.screen.blit(sub_title, (self.panel_x + 20, self.panel_y + 48))

        # Speedometer Gauge & Battery Indicator
        speed_box = pygame.Rect(self.panel_x + 20, self.panel_y + 75, 375, 80)
        pygame.draw.rect(self.screen, (30, 41, 59), speed_box, border_radius=8)
        
        speed_label = self.font_title.render(f"SPEED: {self.simulated_speed:.1f} m/s", True, (56, 189, 248))
        self.screen.blit(speed_label, (speed_box.x + 15, speed_box.y + 12))

        batt_label = self.font_hud.render(f"BATTERY: {self.battery_level:.0f}%", True, (16, 185, 129))
        self.screen.blit(batt_label, (speed_box.x + 220, speed_box.y + 14))

        gauge_bg = pygame.Rect(speed_box.x + 15, speed_box.y + 45, 345, 16)
        pygame.draw.rect(self.screen, (15, 23, 42), gauge_bg, border_radius=4)
        gauge_fill_w = int((self.simulated_speed / 5.0) * 345)
        gauge_fill = pygame.Rect(speed_box.x + 15, speed_box.y + 45, min(345, max(0, gauge_fill_w)), 16)
        pygame.draw.rect(self.screen, COLOR_GAUGE_BAR, gauge_fill, border_radius=4)

        # AI Engine Telemetry
        ai_box = pygame.Rect(self.panel_x + 20, self.panel_y + 170, 375, 150)
        pygame.draw.rect(self.screen, (30, 41, 59), ai_box, border_radius=8)

        mode_badge = f"ALGORITHM: {kb.current_algo_mode}"
        mode_surf = self.font_hud.render(mode_badge, True, (251, 191, 36) if "A_STAR" in kb.current_algo_mode else (16, 185, 129))
        self.screen.blit(mode_surf, (ai_box.x + 15, ai_box.y + 12))

        status_color = COLOR_ALERT if "TRAPPED" in status_msg or "FAILED" in status_msg else COLOR_START
        status_surf = self.font_hud.render(f"MISSION STATUS: {status_msg}", True, status_color)
        self.screen.blit(status_surf, (ai_box.x + 15, ai_box.y + 38))

        rx_grid = int((rover_center_x - self.grid_x) // self.cell_size)
        ry_grid = int((rover_center_y - self.grid_y) // self.cell_size)

        m_lines = [
            f"Step Count          : {step_count:<3} | Pos: ({rx_grid},{ry_grid})",
            f"KB Updates / Infer  : {kb.total_kb_updates:<3} / {kb.total_inferences}",
            f"Proven Safe Cells   : {len(kb.known_safe):<3} / {self.grid_size*self.grid_size}",
            f"Hazards / Radiation : {len(kb.known_hazards):<2} / {len(kb.known_radiation)}",
            f"A* Search Switches  : {kb.a_star_switches_count:<2} switches"
        ]
        for idx, line in enumerate(m_lines):
            l_surf = self.font_small.render(line, True, COLOR_TEXT_MAIN)
            self.screen.blit(l_surf, (ai_box.x + 15, ai_box.y + 65 + (idx * 16)))

        # Sensor Percepts Panel
        sensor_box = pygame.Rect(self.panel_x + 20, self.panel_y + 335, 375, 130)
        pygame.draw.rect(self.screen, (30, 41, 59), sensor_box, border_radius=8)

        s_title = self.font_title.render("LOCAL SENSOR PERCEPTS", True, COLOR_TEXT_MAIN)
        self.screen.blit(s_title, (sensor_box.x + 15, sensor_box.y + 10))

        b_txt = f"Hazard Breeze  : {'ACTIVE (BREEZE DETECTED)' if breeze else 'Clear'}"
        g_txt = f"Radiation Glow : {'ACTIVE (GLOW DETECTED)' if glow else 'Clear'}"
        heading_txt = f"Rover Heading  : {int(self.heading_angle):03d}° NE | Signal: 98%"

        self.screen.blit(self.font_small.render(b_txt, True, (56, 189, 248) if breeze else COLOR_TEXT_MUTED), (sensor_box.x + 15, sensor_box.y + 40))
        self.screen.blit(self.font_small.render(g_txt, True, (232, 121, 249) if glow else COLOR_TEXT_MUTED), (sensor_box.x + 15, sensor_box.y + 65))
        self.screen.blit(self.font_small.render(heading_txt, True, COLOR_TEXT_MUTED), (sensor_box.x + 15, sensor_box.y + 95))

        # 5. Render Interactive Buttons
        buttons = [
            (self.btn_solvable, "Normal Run", COLOR_BTN_SOLVABLE, active_preset == "solvable"),
            (self.btn_trapped, "Martian Storm", COLOR_BTN_TRAPPED, active_preset == "trapped"),
            (self.btn_clear, "Quick Clear", COLOR_BTN_CLEAR, active_preset == "clear"),
            (self.btn_reset, "Reset Scenario", COLOR_BTN_RESET, False),
            (self.btn_fullscreen, "Toggle Fullscreen / Window", (71, 85, 105), False)
        ]

        for btn_rect, text, base_color, is_active in buttons:
            is_hovered = btn_rect.collidepoint(mouse_pos)
            bg_color = base_color if not is_hovered else (min(255, base_color[0]+30), min(255, base_color[1]+30), min(255, base_color[2]+30))
            border_color = (255, 255, 255) if is_active or is_hovered else (71, 85, 105)
            border_width = 3 if is_active else 1

            pygame.draw.rect(self.screen, bg_color, btn_rect, border_radius=6)
            pygame.draw.rect(self.screen, border_color, btn_rect, border_width, border_radius=6)

            btn_txt = self.font_btn.render(text, True, (255, 255, 255))
            txt_x = btn_rect.x + (btn_rect.width - btn_txt.get_width()) // 2
            txt_y = btn_rect.y + (btn_rect.height - btn_txt.get_height()) // 2
            self.screen.blit(btn_txt, (txt_x, txt_y))

        pygame.display.flip()

    def handle_click(self, mouse_pos):
        """Returns the clicked action string."""
        if self.btn_solvable.collidepoint(mouse_pos):
            return "solvable"
        elif self.btn_trapped.collidepoint(mouse_pos):
            return "trapped"
        elif self.btn_clear.collidepoint(mouse_pos):
            return "clear"
        elif self.btn_reset.collidepoint(mouse_pos):
            return "reset"
        elif self.btn_fullscreen.collidepoint(mouse_pos):
            return "fullscreen"
        return None

    def animate_smooth_movement(self, from_pos, to_pos, grid_env, kb, planned_path, step_count, breeze, glow, status_msg="NAVIGATING", active_preset="solvable", num_subframes=12):
        """Animates sub-frame linear pixel interpolation centered inside cell boundaries at 60 FPS."""
        fx, fy = from_pos
        tx, ty = to_pos

        start_center_x = self.grid_x + fx * self.cell_size + self.cell_size // 2
        start_center_y = self.grid_y + fy * self.cell_size + self.cell_size // 2

        target_center_x = self.grid_x + tx * self.cell_size + self.cell_size // 2
        target_center_y = self.grid_y + ty * self.cell_size + self.cell_size // 2

        dx = target_center_x - start_center_x
        dy = target_center_y - start_center_y
        if dx != 0 or dy != 0:
            target_heading = (math.degrees(math.atan2(-dy, dx))) % 360
        else:
            target_heading = self.heading_angle

        for frame in range(1, num_subframes + 1):
            t = frame / float(num_subframes)
            curr_cx = (1.0 - t) * start_center_x + t * target_center_x
            curr_cy = (1.0 - t) * start_center_y + t * target_center_y

            self.update_telemetry(is_moving=True, new_heading=target_heading)

            self.draw_frame(grid_env, kb, curr_cx, curr_cy, planned_path, step_count, breeze, glow, status_msg=status_msg, active_preset=active_preset)
            self.clock.tick(60)


def run_mars_rover_simulation(grid_size=10, step_delay=0.1, initial_preset="solvable"):
    """Main execution loop for Full-Screen Mars Rover Dashboard with Centered 60 FPS Interpolation."""
    
    print("=" * 75)
    print("  NASA / JPL AUTONOMOUS MARS ROVER TELEMETRY DASHBOARD (CENTERED 60 FPS)")
    print("         Track: Hybrid AI Agent (Logic KB + A* Search Evasion)")
    print("=" * 75)
    print(f"Grid Dimensions   : {grid_size} x {grid_size} (Hidden Hazards & Storm Zones)")
    print(f"Assets Directory  : assets/ (Place custom rover.png, hazard.png, radiation.png, etc.)")
    print(f"Telemetry Panel   : Live Speedometer (m/s), Battery Indicator %, Heading")
    print("=" * 75)

    visualizer = RoverVisualizer(grid_size=grid_size)

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
    print("LIVE TELEMETRY & INFERENCE LOG:")
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
                    if clicked_action == "fullscreen":
                        pygame.display.toggle_fullscreen()
                    else:
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
                        print("★" * 75 + "\n")

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_SPACE, pygame.K_p):
                    paused = not paused
                    print(f"[USER] {'PAUSED' if paused else 'RESUMED'} simulation.")
                elif event.key == pygame.K_ESCAPE:
                    running = False

        if paused:
            visualizer.update_telemetry(is_moving=False)
            curr_cx = visualizer.grid_x + current_pos[0] * visualizer.cell_size + visualizer.cell_size // 2
            curr_cy = visualizer.grid_y + current_pos[1] * visualizer.cell_size + visualizer.cell_size // 2
            visualizer.draw_frame(grid_env, kb, curr_cx, curr_cy, [], step_count, False, False, status_msg="PAUSED", active_preset=active_preset)
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
                print(f" Battery Level Remaining   : {visualizer.battery_level:.0f}%")
                print("=" * 75 + "\n")

            visualizer.update_telemetry(is_moving=False)
            breeze, glow = grid_env.perceive(current_pos[0], current_pos[1])
            curr_cx = visualizer.grid_x + current_pos[0] * visualizer.cell_size + visualizer.cell_size // 2
            curr_cy = visualizer.grid_y + current_pos[1] * visualizer.cell_size + visualizer.cell_size // 2
            visualizer.draw_frame(grid_env, kb, curr_cx, curr_cy, [], step_count, breeze, glow, status_msg=status_msg, active_preset=active_preset)
            visualizer.clock.tick(10)
            continue

        # 1. PERCEIVE
        breeze, glow = grid_env.perceive(current_pos[0], current_pos[1])

        # 2. TELL
        asserted_facts = kb.tell_percept(current_pos, breeze, glow)

        # 3. INFER
        new_safe, new_hazards, new_radiation = kb.run_inference()

        # Console Log
        print(f"\n[STEP {step_count:02d}] Rover at {current_pos} | Speed: {visualizer.simulated_speed:.1f} m/s | Batt: {visualizer.battery_level:.0f}% | Percepts: Breeze={breeze}, Glow={glow}")
        print(f" -> [KB TELL] Asserted Facts ({len(asserted_facts)}): {', '.join(asserted_facts[:3])}{'...' if len(asserted_facts)>3 else ''}")

        # 4. DECIDE
        next_step, target_node, reason = kb.plan_next_action(current_pos, grid_env.goal, grid_env)

        print(f" -> [DECISION ENGINE] Next Step: {next_step} | Target: {target_node} | {reason}")

        if not next_step:
            status_msg = "ROVER TRAPPED!"
            print("\n[MISSION FAILED] Rover is completely trapped by surrounding hazards/radiation!")
            visualizer.update_telemetry(is_moving=False)
            curr_cx = visualizer.grid_x + current_pos[0] * visualizer.cell_size + visualizer.cell_size // 2
            curr_cy = visualizer.grid_y + current_pos[1] * visualizer.cell_size + visualizer.cell_size // 2
            visualizer.draw_frame(grid_env, kb, curr_cx, curr_cy, [], step_count, breeze, glow, status_msg=status_msg, active_preset=active_preset)
            visualizer.clock.tick(10)
            continue

        planned_path = kb.find_safe_path(current_pos, target_node) or [current_pos, next_step]

        # 5. PERFECTLY CENTERED SUB-FRAME SMOOTH ANIMATION
        visualizer.animate_smooth_movement(
            current_pos, 
            next_step, 
            grid_env, 
            kb, 
            planned_path, 
            step_count, 
            breeze, 
            glow, 
            status_msg=status_msg, 
            active_preset=active_preset,
            num_subframes=12
        )

        # Move Rover
        current_pos = next_step
        step_count += 1

    pygame.quit()


if __name__ == "__main__":
    run_mars_rover_simulation()
