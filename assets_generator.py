import pygame
import math
import random

# Color Palette Constants
COLOR_ASPHALT = (45, 48, 55)
COLOR_ASPHALT_DARK = (38, 40, 46)
COLOR_ROAD_MARKING = (245, 245, 235)
COLOR_ROAD_YELLOW = (255, 204, 0)
COLOR_CURB_YELLOW = (255, 215, 0)
COLOR_CURB_BLACK = (25, 25, 25)
COLOR_PAVEMENT = (180, 168, 150)
COLOR_PAVEMENT_DARK = (150, 138, 122)

COLOR_SKY_DAY = (135, 206, 235)
COLOR_SUNSET_ORANGE = (255, 120, 50)
COLOR_NIGHT_SKY = (15, 18, 35)

COLOR_GOLD = (255, 215, 0)
COLOR_CHAI = (210, 130, 60)
COLOR_CHAI_MILK = (240, 200, 150)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (10, 10, 10)
COLOR_SHADOW = (0, 0, 0, 90)

class AssetGenerator:
    """Procedurally renders high-quality 2D illustrated arcade assets for Indian Streets."""

    def __init__(self):
        # Cache of generated surfaces
        self.vehicles = {}
        self.buildings = []
        self.props = {}
        self.pickups = {}
        self.road_tiles = {}
        self.ui_elements = {}

        # Fonts for decals and shop boards
        self.font_tiny = pygame.font.SysFont("arial", 9, bold=True)
        self.font_small = pygame.font.SysFont("arial", 12, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 16, bold=True)
        self.font_large = pygame.font.SysFont("arial", 22, bold=True)
        self.font_title = pygame.font.SysFont("impact", 32)

    def generate_all(self):
        """Generates all sprite assets into memory."""
        self._generate_vehicles()
        self._generate_buildings()
        self._generate_props()
        self._generate_pickups()
        self._generate_ui_elements()
        return self

    # -------------------------------------------------------------
    # 1. VEHICLE GENERATION
    # -------------------------------------------------------------
    def _create_vehicle_canvas(self, w, h):
        surf = pygame.Surface((w + 12, h + 16), pygame.SRCALPHA)
        # Soft drop shadow
        shadow_rect = pygame.Rect(4, 8, w + 4, h + 4)
        pygame.draw.rect(surf, (0, 0, 0, 70), shadow_rect, border_radius=8)
        return surf, 6, 4  # surface, offset_x, offset_y

    def _draw_wheels(self, surf, ox, oy, w, h, wheel_w=6, wheel_h=14):
        # 4 wheels visible from top-down
        wheel_color = (25, 25, 25)
        rim_color = (180, 180, 180)
        # Front Left
        pygame.draw.rect(surf, wheel_color, (ox - 2, oy + 12, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surf, rim_color, (ox - 1, oy + 15, wheel_w - 2, wheel_h - 6))
        # Front Right
        pygame.draw.rect(surf, wheel_color, (ox + w - wheel_w + 2, oy + 12, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surf, rim_color, (ox + w - wheel_w + 3, oy + 15, wheel_w - 2, wheel_h - 6))
        # Rear Left
        pygame.draw.rect(surf, wheel_color, (ox - 2, oy + h - wheel_h - 8, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surf, rim_color, (ox - 1, oy + h - wheel_h - 5, wheel_w - 2, wheel_h - 6))
        # Rear Right
        pygame.draw.rect(surf, wheel_color, (ox + w - wheel_w + 2, oy + h - wheel_h - 8, wheel_w, wheel_h), border_radius=2)
        pygame.draw.rect(surf, rim_color, (ox + w - wheel_w + 3, oy + h - wheel_h - 5, wheel_w - 2, wheel_h - 6))

    def _generate_vehicles(self):
        # A. Auto-Rickshaw (Yellow & Green / Yellow & Black)
        self.vehicles['auto_green'] = self._draw_auto_rickshaw(body_color=(20, 140, 60), hood_color=(255, 204, 0))
        self.vehicles['auto_black'] = self._draw_auto_rickshaw(body_color=(30, 30, 30), hood_color=(255, 204, 0))
        self.vehicles['auto_super'] = self._draw_auto_rickshaw(body_color=(220, 40, 30), hood_color=(255, 220, 50), is_player=True)

        # B. Highway Overloaded Tata Truck
        self.vehicles['truck_blue'] = self._draw_tata_truck(cabin_color=(0, 110, 190), cargo_color=(200, 140, 50))
        self.vehicles['truck_red'] = self._draw_tata_truck(cabin_color=(200, 30, 30), cargo_color=(50, 150, 80))

        # C. Premier Padmini / Ambassador Taxi (Kaali Peeli & Kolkata Yellow)
        self.vehicles['taxi_mumbai'] = self._draw_taxi(body_color=(35, 35, 35), roof_color=(255, 210, 0))
        self.vehicles['taxi_kolkata'] = self._draw_taxi(body_color=(245, 190, 10), roof_color=(245, 190, 10))

        # D. Bajaj Chetak Scooter with Milk Cans / Delivery Rider
        self.vehicles['scooter_mint'] = self._draw_scooter(scooter_color=(70, 180, 160))
        self.vehicles['scooter_red'] = self._draw_scooter(scooter_color=(220, 50, 40))

        # E. Street Handcart (Thela with fruit)
        self.vehicles['thela'] = self._draw_thela()

        # F. Modern Indian Cars & Player Cars
        self.vehicles['car_maruti_red'] = self._draw_hatchback(color=(220, 35, 45), stripes=True)
        self.vehicles['car_maruti_blue'] = self._draw_hatchback(color=(25, 110, 220), stripes=False)
        self.vehicles['car_sedan_white'] = self._draw_sedan(color=(240, 240, 245))
        self.vehicles['car_suv_orange'] = self._draw_suv(color=(235, 95, 25))

        # Player Options
        self.vehicles['player_800'] = self._draw_hatchback(color=(235, 30, 40), stripes=True, is_player=True)
        self.vehicles['player_ambassador'] = self._draw_taxi(body_color=(240, 235, 225), roof_color=(240, 235, 225), is_ambassador=True, is_player=True)

    def _draw_auto_rickshaw(self, body_color, hood_color, is_player=False):
        w, h = 50, 78
        surf, ox, oy = self._create_vehicle_canvas(w, h)

        # 3 wheels (1 front in center, 2 rear)
        wheel_c = (25, 25, 25)
        # Front wheel
        pygame.draw.rect(surf, wheel_c, (ox + w // 2 - 3, oy + 4, 6, 12), border_radius=2)
        # Rear wheels
        pygame.draw.rect(surf, wheel_c, (ox - 2, oy + h - 22, 6, 14), border_radius=2)
        pygame.draw.rect(surf, wheel_c, (ox + w - 4, oy + h - 22, 6, 14), border_radius=2)

        # Main Chassis / Lower Body (Tapered front)
        points = [
            (ox + w // 2 - 8, oy + 10),
            (ox + w // 2 + 8, oy + 10),
            (ox + w - 4, oy + 28),
            (ox + w - 2, oy + h - 6),
            (ox + 2, oy + h - 6),
            (ox + 4, oy + 28)
        ]
        pygame.draw.polygon(surf, body_color, points)
        pygame.draw.polygon(surf, (15, 15, 15), points, 2)

        # Windshield
        ws_points = [
            (ox + w // 2 - 10, oy + 16),
            (ox + w // 2 + 10, oy + 16),
            (ox + w - 8, oy + 30),
            (ox + 8, oy + 30)
        ]
        pygame.draw.polygon(surf, (160, 220, 245), ws_points)
        pygame.draw.polygon(surf, (50, 70, 90), ws_points, 1)

        # Canvas Hood / Canopy (Iconic Auto Yellow Top)
        hood_rect = pygame.Rect(ox + 5, oy + 30, w - 10, h - 40)
        pygame.draw.rect(surf, hood_color, hood_rect, border_radius=6)
        # Hood texture lines / seams
        pygame.draw.line(surf, (180, 140, 10), (ox + 10, oy + 45), (ox + w - 10, oy + 45), 2)
        pygame.draw.line(surf, (180, 140, 10), (ox + 10, oy + 58), (ox + w - 10, oy + 58), 2)

        # Rear luggage bar & bumper decal
        bumper_rect = pygame.Rect(ox + 3, oy + h - 10, w - 6, 8)
        pygame.draw.rect(surf, (40, 40, 40), bumper_rect, border_radius=2)
        # Red tail lights
        pygame.draw.circle(surf, (240, 30, 30), (ox + 8, oy + h - 6), 3)
        pygame.draw.circle(surf, (240, 30, 30), (ox + w - 8, oy + h - 6), 3)

        # Decal Text: "HORN OK" or "BOSS"
        decal_text = "TURBO" if is_player else "HORN OK"
        txt_surf = self.font_tiny.render(decal_text, True, (255, 255, 255))
        surf.blit(txt_surf, (ox + w // 2 - txt_surf.get_width() // 2, oy + h - 18))

        # Side mirrors
        pygame.draw.rect(surf, (200, 200, 200), (ox + 2, oy + 24, 4, 3))
        pygame.draw.rect(surf, (200, 200, 200), (ox + w - 6, oy + 24, 4, 3))

        # Headlight
        pygame.draw.circle(surf, (255, 255, 200), (ox + w // 2, oy + 9), 4)

        return surf

    def _draw_tata_truck(self, cabin_color, cargo_color):
        w, h = 64, 130
        surf, ox, oy = self._create_vehicle_canvas(w, h)

        # 6 Heavy Wheels
        wheel_c = (20, 20, 20)
        rim_c = (220, 180, 50)
        # Front pair
        pygame.draw.rect(surf, wheel_c, (ox - 3, oy + 20, 7, 18), border_radius=2)
        pygame.draw.rect(surf, wheel_c, (ox + w - 4, oy + 20, 7, 18), border_radius=2)
        # Rear Dual Axles
        pygame.draw.rect(surf, wheel_c, (ox - 3, oy + h - 45, 7, 18), border_radius=2)
        pygame.draw.rect(surf, wheel_c, (ox + w - 4, oy + h - 45, 7, 18), border_radius=2)
        pygame.draw.rect(surf, wheel_c, (ox - 3, oy + h - 22, 7, 18), border_radius=2)
        pygame.draw.rect(surf, wheel_c, (ox + w - 4, oy + h - 22, 7, 18), border_radius=2)

        # Front Cabin (Rounded chrome crown)
        cabin_rect = pygame.Rect(ox + 4, oy + 6, w - 8, 38)
        pygame.draw.rect(surf, cabin_color, cabin_rect, border_radius=6)
        pygame.draw.rect(surf, (20, 20, 20), cabin_rect, 2, border_radius=6)

        # Chrome Front Grill & Big Headlights
        pygame.draw.rect(surf, (230, 230, 240), (ox + 10, oy + 7, w - 20, 6), border_radius=2)
        pygame.draw.circle(surf, (255, 255, 220), (ox + 9, oy + 10), 4)
        pygame.draw.circle(surf, (255, 255, 220), (ox + w - 9, oy + 10), 4)

        # Windshield
        ws_rect = pygame.Rect(ox + 8, oy + 18, w - 16, 12)
        pygame.draw.rect(surf, (150, 210, 240), ws_rect, border_radius=2)
        pygame.draw.line(surf, (40, 60, 80), (ox + w // 2, oy + 18), (ox + w // 2, oy + 30), 2)

        # Tasseled Big Rearview Mirrors
        pygame.draw.rect(surf, (255, 100, 0), (ox - 2, oy + 16, 5, 8))
        pygame.draw.rect(surf, (255, 100, 0), (ox + w - 3, oy + 16, 5, 8))

        # Wooden Cargo Bed / Truck Body (Overloaded with colorful art)
        cargo_rect = pygame.Rect(ox + 2, oy + 42, w - 4, h - 48)
        pygame.draw.rect(surf, cargo_color, cargo_rect, border_radius=3)
        pygame.draw.rect(surf, (30, 20, 10), cargo_rect, 2)

        # Colorful Slatted Wooden Planks
        colors_slats = [(230, 190, 40), (220, 60, 40), (40, 170, 70), (0, 140, 210)]
        for i, y_pos in enumerate(range(oy + 48, oy + h - 22, 14)):
            c = colors_slats[i % len(colors_slats)]
            pygame.draw.rect(surf, c, (ox + 6, y_pos, w - 12, 10), border_radius=1)
            pygame.draw.line(surf, (255, 255, 255), (ox + 8, y_pos + 5), (ox + w - 8, y_pos + 5), 1)

        # Iconic Truck Art Decals: "BLOW HORN" / "OK"
        text_blow = self.font_tiny.render("BLOW", True, (255, 255, 255))
        text_horn = self.font_tiny.render("HORN", True, (255, 255, 255))
        surf.blit(text_blow, (ox + 8, oy + h - 18))
        surf.blit(text_horn, (ox + w - 24, oy + h - 18))

        # Tarp rope criss-cross pattern
        pygame.draw.line(surf, (255, 220, 120), (ox + 6, oy + 50), (ox + w - 6, oy + 85), 1)
        pygame.draw.line(surf, (255, 220, 120), (ox + w - 6, oy + 50), (ox + 6, oy + 85), 1)

        # Rear bumper & hazard stripes
        pygame.draw.rect(surf, (255, 204, 0), (ox + 4, oy + h - 8, w - 8, 6))
        for x_s in range(ox + 6, ox + w - 6, 8):
            pygame.draw.line(surf, (20, 20, 20), (x_s, oy + h - 8), (x_s + 4, oy + h - 2), 2)

        return surf

    def _draw_taxi(self, body_color, roof_color, is_ambassador=False, is_player=False):
        w, h = 54, 94 if is_ambassador else 88
        surf, ox, oy = self._create_vehicle_canvas(w, h)

        self._draw_wheels(surf, ox, oy, w, h)

        # Car Chassis
        car_rect = pygame.Rect(ox + 3, oy + 6, w - 6, h - 12)
        pygame.draw.rect(surf, body_color, car_rect, border_radius=10 if is_ambassador else 7)
        pygame.draw.rect(surf, (30, 30, 30), car_rect, 2, border_radius=10 if is_ambassador else 7)

        # Hood & Chrome Grille
        grille_rect = pygame.Rect(ox + 10, oy + 7, w - 20, 5)
        pygame.draw.rect(surf, (220, 220, 230), grille_rect, border_radius=2)
        # Round Classic Headlights
        pygame.draw.circle(surf, (255, 255, 230), (ox + 9, oy + 10), 4)
        pygame.draw.circle(surf, (255, 255, 230), (ox + w - 9, oy + 10), 4)

        # Front Windshield
        ws_rect = pygame.Rect(ox + 8, oy + 22, w - 16, 12)
        pygame.draw.rect(surf, (160, 215, 240), ws_rect, border_radius=3)

        # Roof / Taxi Top
        roof_rect = pygame.Rect(ox + 7, oy + 34, w - 14, h - 54)
        pygame.draw.rect(surf, roof_color, roof_rect, border_radius=4)
        pygame.draw.rect(surf, (20, 20, 20), roof_rect, 1, border_radius=4)

        # Rear Windshield
        rear_ws = pygame.Rect(ox + 8, oy + h - 28, w - 16, 10)
        pygame.draw.rect(surf, (150, 205, 230), rear_ws, border_radius=2)

        # Taxi Sign or Luggage Rack on roof
        if not is_ambassador or not is_player:
            taxi_box = pygame.Rect(ox + w // 2 - 12, oy + 42, 24, 8)
            pygame.draw.rect(surf, (255, 240, 50), taxi_box, border_radius=2)
            pygame.draw.rect(surf, (20, 20, 20), taxi_box, 1)
            txt = self.font_tiny.render("TAXI", True, (0, 0, 0))
            surf.blit(txt, (ox + w // 2 - txt.get_width() // 2, oy + 41))
        else:
            # VIP Red Beacon for Ambassador
            pygame.draw.circle(surf, (240, 20, 20), (ox + w // 2, oy + 44), 4)

        # Rear Taillights & Chrome Bumper
        pygame.draw.rect(surf, (210, 210, 220), (ox + 8, oy + h - 9, w - 16, 4), border_radius=2)
        pygame.draw.circle(surf, (230, 20, 20), (ox + 8, oy + h - 7), 3)
        pygame.draw.circle(surf, (230, 20, 20), (ox + w - 8, oy + h - 7), 3)

        return surf

    def _draw_scooter(self, scooter_color):
        w, h = 32, 60
        surf, ox, oy = self._create_vehicle_canvas(w, h)

        # Front & Rear Wheels
        pygame.draw.rect(surf, (20, 20, 20), (ox + w // 2 - 2, oy + 4, 5, 10), border_radius=2)
        pygame.draw.rect(surf, (20, 20, 20), (ox + w // 2 - 2, oy + h - 14, 5, 10), border_radius=2)

        # Handlebar & Mirror
        pygame.draw.line(surf, (50, 50, 50), (ox + 4, oy + 14), (ox + w - 4, oy + 14), 3)
        pygame.draw.circle(surf, (255, 255, 200), (ox + w // 2, oy + 10), 4)  # Round Headlight
        pygame.draw.circle(surf, (200, 200, 200), (ox + 4, oy + 12), 2)
        pygame.draw.circle(surf, (200, 200, 200), (ox + w - 4, oy + 12), 2)

        # Scooter Footboard & Bulgy Side Cowls (Chetak style)
        body_rect = pygame.Rect(ox + 7, oy + 18, w - 14, h - 26)
        pygame.draw.rect(surf, scooter_color, body_rect, border_radius=6)

        # Rider (Top-down view of Helmet & Shoulders)
        # Shoulders
        pygame.draw.ellipse(surf, (40, 80, 160), (ox + 6, oy + 22, w - 12, 14))
        # Helmet
        pygame.draw.circle(surf, (240, 240, 240), (ox + w // 2, oy + 26), 7)
        pygame.draw.line(surf, (20, 20, 20), (ox + w // 2 - 4, oy + 24), (ox + w // 2 + 4, oy + 24), 2)

        # Milk Cans / Delivery boxes hanging on sides
        pygame.draw.circle(surf, (220, 220, 220), (ox + 3, oy + 38), 4)
        pygame.draw.circle(surf, (220, 220, 220), (ox + w - 3, oy + 38), 4)

        # Spare wheel on rear
        pygame.draw.ellipse(surf, (30, 30, 30), (ox + w // 2 - 5, oy + h - 12, 10, 6))

        return surf

    def _draw_thela(self):
        w, h = 48, 70
        surf, ox, oy = self._create_vehicle_canvas(w, h)

        # 4 Spoked Handcart Wheels
        wheel_c = (60, 40, 20)
        pygame.draw.rect(surf, wheel_c, (ox - 2, oy + 10, 4, 12))
        pygame.draw.rect(surf, wheel_c, (ox + w - 2, oy + 10, 4, 12))
        pygame.draw.rect(surf, wheel_c, (ox - 2, oy + h - 22, 4, 12))
        pygame.draw.rect(surf, wheel_c, (ox + w - 2, oy + h - 22, 4, 12))

        # Wooden Platform
        bed_rect = pygame.Rect(ox + 2, oy + 6, w - 4, h - 12)
        pygame.draw.rect(surf, (180, 130, 80), bed_rect, border_radius=2)
        pygame.draw.rect(surf, (100, 70, 40), bed_rect, 2)

        # Green Tender Coconuts & Yellow Bananas
        # Coconuts (Left half)
        for cx in range(ox + 8, ox + w // 2 - 2, 7):
            for cy in range(oy + 12, oy + h - 16, 8):
                pygame.draw.circle(surf, (60, 160, 50), (cx, cy), 4)
                pygame.draw.circle(surf, (100, 200, 80), (cx - 1, cy - 1), 2)

        # Bananas & Mangoes (Right half)
        for bx in range(ox + w // 2 + 4, ox + w - 8, 7):
            for by in range(oy + 12, oy + h - 16, 8):
                pygame.draw.ellipse(surf, (255, 210, 30), (bx, by, 7, 5))

        # Push Handlebar
        pygame.draw.line(surf, (90, 60, 30), (ox + 4, oy + h - 2), (ox + w - 4, oy + h - 2), 3)

        return surf

    def _draw_hatchback(self, color, stripes=False, is_player=False):
        w, h = 50, 82
        surf, ox, oy = self._create_vehicle_canvas(w, h)
        self._draw_wheels(surf, ox, oy, w, h)

        # Body
        body_rect = pygame.Rect(ox + 4, oy + 6, w - 8, h - 12)
        pygame.draw.rect(surf, color, body_rect, border_radius=8)
        pygame.draw.rect(surf, (25, 25, 25), body_rect, 2, border_radius=8)

        # Sporty Dual Racing Stripes
        if stripes:
            pygame.draw.line(surf, (255, 255, 255), (ox + w // 2 - 4, oy + 6), (ox + w // 2 - 4, oy + h - 6), 2)
            pygame.draw.line(surf, (255, 255, 255), (ox + w // 2 + 4, oy + 6), (ox + w // 2 + 4, oy + h - 6), 2)

        # Windshields
        pygame.draw.rect(surf, (160, 220, 245), (ox + 8, oy + 20, w - 16, 12), border_radius=2)
        pygame.draw.rect(surf, (150, 210, 240), (ox + 8, oy + h - 24, w - 16, 8), border_radius=2)

        # Roof / Sunroof
        roof_rect = pygame.Rect(ox + 8, oy + 32, w - 16, h - 54)
        if is_player:
            pygame.draw.rect(surf, (30, 30, 30), roof_rect, border_radius=3)  # Glossy black panoramic roof
        else:
            pygame.draw.rect(surf, color, roof_rect)

        # Headlights & Taillights
        pygame.draw.circle(surf, (255, 255, 230), (ox + 9, oy + 9), 3)
        pygame.draw.circle(surf, (255, 255, 230), (ox + w - 9, oy + 9), 3)
        pygame.draw.circle(surf, (240, 20, 20), (ox + 8, oy + h - 8), 3)
        pygame.draw.circle(surf, (240, 20, 20), (ox + w - 8, oy + h - 8), 3)

        return surf

    def _draw_sedan(self, color):
        w, h = 52, 92
        surf, ox, oy = self._create_vehicle_canvas(w, h)
        self._draw_wheels(surf, ox, oy, w, h)

        body_rect = pygame.Rect(ox + 4, oy + 5, w - 8, h - 10)
        pygame.draw.rect(surf, color, body_rect, border_radius=9)
        pygame.draw.rect(surf, (30, 30, 30), body_rect, 2, border_radius=9)

        # Windshields
        pygame.draw.rect(surf, (160, 220, 245), (ox + 8, oy + 24, w - 16, 14), border_radius=3)
        pygame.draw.rect(surf, (150, 210, 240), (ox + 8, oy + h - 28, w - 16, 12), border_radius=2)

        # Headlights & Grille
        pygame.draw.rect(surf, (200, 200, 210), (ox + 12, oy + 6, w - 24, 4), border_radius=1)
        pygame.draw.circle(surf, (255, 255, 230), (ox + 9, oy + 8), 3)
        pygame.draw.circle(surf, (255, 255, 230), (ox + w - 9, oy + 8), 3)

        return surf

    def _draw_suv(self, color):
        w, h = 56, 96
        surf, ox, oy = self._create_vehicle_canvas(w, h)
        self._draw_wheels(surf, ox, oy, w, h, wheel_w=7, wheel_h=16)

        body_rect = pygame.Rect(ox + 4, oy + 5, w - 8, h - 10)
        pygame.draw.rect(surf, color, body_rect, border_radius=6)
        pygame.draw.rect(surf, (20, 20, 20), body_rect, 2, border_radius=6)

        # Roof Rails
        pygame.draw.line(surf, (40, 40, 40), (ox + 8, oy + 26), (ox + 8, oy + h - 20), 3)
        pygame.draw.line(surf, (40, 40, 40), (ox + w - 8, oy + 26), (ox + w - 8, oy + h - 20), 3)

        # Windshields
        pygame.draw.rect(surf, (140, 200, 235), (ox + 8, oy + 22, w - 16, 13), border_radius=2)
        pygame.draw.rect(surf, (130, 190, 225), (ox + 8, oy + h - 24, w - 16, 10), border_radius=2)

        # Rear Mounted Spare Wheel
        pygame.draw.circle(surf, (30, 30, 30), (ox + w // 2, oy + h - 6), 6)
        pygame.draw.circle(surf, (180, 180, 180), (ox + w // 2, oy + h - 6), 3)

        return surf

    # -------------------------------------------------------------
    # 2. ROADSIDE SHOPFRONTS & INDIAN BUILDINGS
    # -------------------------------------------------------------
    def _generate_buildings(self):
        # We generate a rich assortment of illustrated shopfronts with authentic Indian motifs
        self.buildings.append(self._create_chai_shop())
        self.buildings.append(self._create_sweets_shop())
        self.buildings.append(self._create_xerox_shop())
        self.buildings.append(self._create_tyre_shop())
        self.buildings.append(self._create_kirana_shop())
        self.buildings.append(self._create_paan_shop())
        self.buildings.append(self._create_poster_wall())
        self.buildings.append(self._create_heritage_building())

    def _create_chai_shop(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Plastered Wall (Mint / Chai Green)
        pygame.draw.rect(surf, (70, 150, 120), (0, 0, w, h))
        pygame.draw.rect(surf, (40, 100, 80), (0, 0, w, h), 3)

        # Top Signboard ("RAJU CHAIWALA")
        board_rect = pygame.Rect(10, 12, w - 20, 48)
        pygame.draw.rect(surf, (245, 190, 30), board_rect, border_radius=4)
        pygame.draw.rect(surf, (180, 50, 20), board_rect, 3, border_radius=4)
        t1 = self.font_medium.render("RAJU CHAIWALA", True, (180, 20, 10))
        t2 = self.font_tiny.render("Special Cutting Chai & Maska Bun", True, (20, 20, 20))
        surf.blit(t1, (w // 2 - t1.get_width() // 2, 16))
        surf.blit(t2, (w // 2 - t2.get_width() // 2, 38))

        # Striped Awning / Chhappar (Red & White)
        for i, x in enumerate(range(8, w - 8, 16)):
            c = (220, 40, 40) if (i % 2 == 0) else (255, 255, 255)
            pygame.draw.rect(surf, c, (x, 62, 16, 20), border_radius=2)
        pygame.draw.line(surf, (150, 30, 30), (8, 82), (w - 8, 82), 2)

        # Hanging Marigold Flowers garland
        for gx in range(12, w - 12, 10):
            pygame.draw.circle(surf, (255, 140, 0), (gx, 88 + (gx % 4)), 4)
            pygame.draw.circle(surf, (255, 215, 0), (gx, 88 + (gx % 4)), 2)

        # Wooden Counter & Tea Kettle & Glass Stand
        counter_rect = pygame.Rect(14, 110, w - 28, 85)
        pygame.draw.rect(surf, (140, 90, 50), counter_rect, border_radius=4)
        pygame.draw.rect(surf, (90, 50, 25), counter_rect, 2)

        # Brass Kettle / Samovar
        pygame.draw.rect(surf, (220, 170, 40), (26, 120, 24, 28), border_radius=3)
        pygame.draw.circle(surf, (240, 190, 50), (38, 116), 8)

        # Cutting Chai Glass Rack
        for rx in range(65, w - 30, 12):
            pygame.draw.rect(surf, (200, 230, 245), (rx, 125, 8, 18), border_radius=1)
            pygame.draw.rect(surf, (210, 130, 50), (rx + 1, 132, 6, 10))  # Chai inside

        # Wooden Benches / Stools
        pygame.draw.rect(surf, (100, 65, 35), (20, 185, 35, 14), border_radius=2)
        pygame.draw.rect(surf, (100, 65, 35), (w - 55, 185, 35, 14), border_radius=2)

        return surf

    def _create_sweets_shop(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Saffron/Orange Building Wall
        pygame.draw.rect(surf, (240, 140, 60), (0, 0, w, h))
        pygame.draw.rect(surf, (190, 80, 20), (0, 0, w, h), 3)

        # Signboard ("SHARMA SWEETS")
        board_rect = pygame.Rect(10, 12, w - 20, 46)
        pygame.draw.rect(surf, (180, 20, 20), board_rect, border_radius=4)
        pygame.draw.rect(surf, (255, 215, 0), board_rect, 2, border_radius=4)
        t1 = self.font_medium.render("SHARMA SWEETS", True, (255, 220, 40))
        t2 = self.font_tiny.render("Pure Ghee Jalebi • Samosa • Ladoo", True, (255, 255, 255))
        surf.blit(t1, (w // 2 - t1.get_width() // 2, 16))
        surf.blit(t2, (w // 2 - t2.get_width() // 2, 38))

        # Sweet Display Counter (Glass Showcase with tiers)
        showcase = pygame.Rect(12, 75, w - 24, 120)
        pygame.draw.rect(surf, (225, 240, 250), showcase, border_radius=4)
        pygame.draw.rect(surf, (180, 120, 50), showcase, 3)

        # Shelves with sweets
        # Top tier: Yellow Motichoor Ladoos
        for lx in range(22, w - 22, 10):
            pygame.draw.circle(surf, (255, 190, 20), (lx, 95), 4)

        # Middle tier: Swirly Orange Jalebis
        for jx in range(24, w - 24, 14):
            pygame.draw.circle(surf, (255, 110, 10), (jx, 125), 6, 2)

        # Bottom tier: Golden Brown Samosas (Triangles)
        for sx in range(25, w - 25, 16):
            tri = [(sx, 160), (sx + 10, 160), (sx + 5, 150)]
            pygame.draw.polygon(surf, (210, 140, 40), tri)

        return surf

    def _create_xerox_shop(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Bright Blue Facade
        pygame.draw.rect(surf, (40, 120, 200), (0, 0, w, h))
        pygame.draw.rect(surf, (20, 70, 140), (0, 0, w, h), 3)

        # Board ("SUPERFAST XEROX")
        board_rect = pygame.Rect(8, 12, w - 16, 52)
        pygame.draw.rect(surf, (255, 230, 20), board_rect, border_radius=4)
        pygame.draw.rect(surf, (20, 20, 20), board_rect, 2)
        t1 = self.font_medium.render("SUPERFAST XEROX", True, (0, 0, 0))
        t2 = self.font_tiny.render("Print • Lamination • Aadhaar Card", True, (180, 20, 20))
        surf.blit(t1, (w // 2 - t1.get_width() // 2, 16))
        surf.blit(t2, (w // 2 - t2.get_width() // 2, 40))

        # Counter & Huge Xerox Machine
        counter = pygame.Rect(14, 80, w - 28, 110)
        pygame.draw.rect(surf, (230, 230, 235), counter, border_radius=3)
        pygame.draw.rect(surf, (80, 80, 90), counter, 2)

        # Xerox Machine Glass Top & Display
        pygame.draw.rect(surf, (40, 40, 45), (25, 95, 55, 45), border_radius=2)
        pygame.draw.rect(surf, (100, 220, 120), (32, 102, 15, 8))  # Green LED display
        pygame.draw.rect(surf, (255, 255, 255), (92, 95, 45, 55))  # Paper stack
        for py in range(100, 145, 6):
            pygame.draw.line(surf, (200, 200, 200), (94, py), (134, py), 1)

        return surf

    def _create_tyre_shop(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Weathered Workshop Wall
        pygame.draw.rect(surf, (160, 150, 140), (0, 0, w, h))
        pygame.draw.rect(surf, (90, 80, 70), (0, 0, w, h), 3)

        # Board ("SPEEDY TYRE PUNCHER")
        board_rect = pygame.Rect(10, 10, w - 20, 48)
        pygame.draw.rect(surf, (220, 30, 30), board_rect, border_radius=4)
        t1 = self.font_medium.render("SPEEDY PUNCTURE", True, (255, 255, 255))
        t2 = self.font_tiny.render("Tubeless Tyre Repair & Nitrogen Air", True, (255, 220, 50))
        surf.blit(t1, (w // 2 - t1.get_width() // 2, 14))
        surf.blit(t2, (w // 2 - t2.get_width() // 2, 38))

        # Stacks of Tyres
        for i, ty in enumerate(range(75, 170, 32)):
            pygame.draw.ellipse(surf, (30, 30, 30), (20, ty, 50, 26))
            pygame.draw.ellipse(surf, (150, 150, 150), (30, ty + 4, 30, 18), 3)

        # Red Air Pressure Tank
        pygame.draw.rect(surf, (200, 40, 30), (105, 85, 36, 75), border_radius=8)
        pygame.draw.circle(surf, (240, 240, 240), (123, 85), 8)  # Pressure Gauge
        pygame.draw.line(surf, (20, 20, 20), (123, 85), (127, 82), 2)  # Needle

        return surf

    def _create_kirana_shop(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Sunny Yellow Wall
        pygame.draw.rect(surf, (245, 210, 70), (0, 0, w, h))
        pygame.draw.rect(surf, (180, 140, 30), (0, 0, w, h), 3)

        # Board ("BABU BHAI GENERAL STORE")
        board_rect = pygame.Rect(8, 10, w - 16, 50)
        pygame.draw.rect(surf, (20, 130, 60), board_rect, border_radius=4)
        t1 = self.font_medium.render("BABU BHAI STORE", True, (255, 255, 255))
        t2 = self.font_tiny.render("Daily Kirana • Snacks • Cold Drinks", True, (255, 220, 50))
        surf.blit(t1, (w // 2 - t1.get_width() // 2, 14))
        surf.blit(t2, (w // 2 - t2.get_width() // 2, 38))

        # Packed Shelves with Colorful Hanging Sachet Packets
        shelf_rect = pygame.Rect(12, 70, w - 24, 125)
        pygame.draw.rect(surf, (130, 90, 50), shelf_rect, border_radius=3)

        # Hanging Kurkure/Lays Chips packets
        chips_colors = [(230, 40, 40), (40, 160, 220), (240, 180, 20), (40, 180, 60)]
        for col, cx in enumerate(range(20, w - 20, 16)):
            for row, cy in enumerate(range(80, 170, 22)):
                c = chips_colors[(col + row) % len(chips_colors)]
                pygame.draw.rect(surf, c, (cx, cy, 12, 16), border_radius=2)

        return surf

    def _create_paan_shop(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Royal Maroon Facade
        pygame.draw.rect(surf, (160, 25, 45), (0, 0, w, h))
        pygame.draw.rect(surf, (100, 10, 25), (0, 0, w, h), 3)

        # Board ("BANARAS PAAN SHOP")
        board_rect = pygame.Rect(10, 12, w - 20, 48)
        pygame.draw.rect(surf, (255, 215, 0), board_rect, border_radius=4)
        t1 = self.font_medium.render("BANARAS PAAN", True, (160, 20, 30))
        t2 = self.font_tiny.render("Meetha Paan • Cold Drinks • Mukhwas", True, (10, 10, 10))
        surf.blit(t1, (w // 2 - t1.get_width() // 2, 16))
        surf.blit(t2, (w // 2 - t2.get_width() // 2, 38))

        # Brass Box & Heart-shaped Betel Leaves Display
        counter = pygame.Rect(15, 75, w - 30, 115)
        pygame.draw.rect(surf, (220, 180, 50), counter, border_radius=4)

        # Green Heart-shaped Paan Leaves
        for px in range(30, w - 30, 22):
            for py in range(90, 160, 22):
                pygame.draw.circle(surf, (40, 160, 50), (px, py), 7)
                pygame.draw.circle(surf, (30, 140, 40), (px + 6, py), 7)
                pygame.draw.polygon(surf, (40, 160, 50), [(px - 6, py + 3), (px + 12, py + 3), (px + 3, py + 14)])

        return surf

    def _create_poster_wall(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Exposed Brick Wall
        pygame.draw.rect(surf, (175, 75, 60), (0, 0, w, h))
        # Mortar lines
        for by in range(0, h, 14):
            pygame.draw.line(surf, (140, 60, 50), (0, by), (w, by), 1)
            offset = 12 if (by // 14) % 2 == 0 else 0
            for bx in range(offset, w, 24):
                pygame.draw.line(surf, (140, 60, 50), (bx, by), (bx, by + 14), 1)

        # Retro Bollywood Movie Posters pasted on wall
        # Poster 1: "SHOLAY"
        p1 = pygame.Rect(12, 18, 68, 85)
        pygame.draw.rect(surf, (245, 210, 40), p1)
        pygame.draw.rect(surf, (200, 30, 30), p1, 2)
        txt1 = self.font_small.render("SHOLAY", True, (180, 20, 20))
        surf.blit(txt1, (p1.centerx - txt1.get_width() // 2, 30))
        pygame.draw.rect(surf, (30, 30, 30), (18, 52, 56, 38))

        # Poster 2: "DHOOM"
        p2 = pygame.Rect(88, 30, 68, 80)
        pygame.draw.rect(surf, (230, 50, 40), p2)
        pygame.draw.rect(surf, (255, 255, 255), p2, 2)
        txt2 = self.font_small.render("DHOOM", True, (255, 255, 255))
        surf.blit(txt2, (p2.centerx - txt2.get_width() // 2, 45))

        # Poster 3: "DON"
        p3 = pygame.Rect(30, 118, 110, 75)
        pygame.draw.rect(surf, (20, 30, 60), p3)
        pygame.draw.rect(surf, (255, 215, 0), p3, 2)
        txt3 = self.font_medium.render("DON", True, (255, 220, 40))
        sub3 = self.font_tiny.render("11 Mulkon Ki Police...", True, (200, 200, 200))
        surf.blit(txt3, (p3.centerx - txt3.get_width() // 2, 130))
        surf.blit(sub3, (p3.centerx - sub3.get_width() // 2, 155))

        return surf

    def _create_heritage_building(self):
        w, h = 170, 220
        surf = pygame.Surface((w, h), pygame.SRCALPHA)

        # Jodhpur Blue Wall
        pygame.draw.rect(surf, (60, 140, 210), (0, 0, w, h))
        pygame.draw.rect(surf, (30, 90, 150), (0, 0, w, h), 3)

        # Intricate Jharokha / Rajasthani Balcony
        balcony = pygame.Rect(25, 40, w - 50, 110)
        pygame.draw.rect(surf, (240, 210, 160), balcony, border_radius=8)
        pygame.draw.rect(surf, (180, 140, 90), balcony, 2, border_radius=8)

        # Ornate Window Arch
        arch = pygame.Rect(45, 60, w - 90, 70)
        pygame.draw.rect(surf, (40, 40, 60), arch, border_radius=16)

        # Decorative Jaali Grid pattern
        for jx in range(50, w - 50, 12):
            for jy in range(65, 125, 12):
                pygame.draw.circle(surf, (240, 210, 160), (jx, jy), 2)

        # Clothesline with colorful hanging clothes (sari, shirt, kurta)
        pygame.draw.line(surf, (40, 40, 40), (10, 175), (w - 10, 175), 1)
        clothes_c = [(255, 90, 90), (255, 220, 50), (60, 200, 140), (200, 80, 220)]
        for i, cx in enumerate(range(18, w - 24, 32)):
            pygame.draw.rect(surf, clothes_c[i % len(clothes_c)], (cx, 176, 22, 28), border_radius=2)

        return surf

    # -------------------------------------------------------------
    # 3. ROADSIDE PROPS & GREENERY
    # -------------------------------------------------------------
    def _generate_props(self):
        # A. Lush Neem / Banyan Tree Canopy
        tree_surf = pygame.Surface((120, 120), pygame.SRCALPHA)
        # Foliage blobs
        leaf_colors = [(35, 130, 55), (45, 155, 65), (55, 175, 75), (70, 195, 85)]
        for _ in range(16):
            bx = random.randint(30, 90)
            by = random.randint(30, 90)
            r = random.randint(18, 30)
            c = random.choice(leaf_colors)
            pygame.draw.circle(tree_surf, c, (bx, by), r)
        self.props['tree'] = tree_surf

        # B. Highway Milestones
        self.props['milestone_mumbai'] = self._create_milestone("MUMBAI", "85 KM", (255, 215, 0))
        self.props['milestone_delhi'] = self._create_milestone("DELHI", "42 KM", (50, 170, 70))

        # C. Street Lamp Post with Tangled Cables
        lamp_surf = pygame.Surface((40, 90), pygame.SRCALPHA)
        pygame.draw.rect(lamp_surf, (80, 80, 90), (18, 10, 4, 80))
        pygame.draw.circle(lamp_surf, (255, 255, 200), (20, 12), 8)
        pygame.draw.circle(lamp_surf, (255, 220, 80, 100), (20, 12), 14)
        self.props['lamp'] = lamp_surf

        # D. Pothole / Road Hazard
        pothole_surf = pygame.Surface((50, 36), pygame.SRCALPHA)
        pygame.draw.ellipse(pothole_surf, (25, 25, 28), (4, 4, 42, 28))
        pygame.draw.ellipse(pothole_surf, (15, 15, 18), (10, 8, 30, 20))
        self.props['pothole'] = pothole_surf

        # E. Speed Breaker / Rumble Strips
        rumble_surf = pygame.Surface((440, 24), pygame.SRCALPHA)
        for rx in range(0, 440, 22):
            pygame.draw.polygon(rumble_surf, (255, 204, 0), [(rx, 24), (rx + 11, 0), (rx + 22, 0), (rx + 11, 24)])
            pygame.draw.polygon(rumble_surf, (20, 20, 20), [(rx + 11, 24), (rx + 22, 0), (rx + 33, 0), (rx + 22, 24)])
        self.props['speed_breaker'] = rumble_surf

    def _create_milestone(self, city, dist, top_color):
        surf = pygame.Surface((38, 55), pygame.SRCALPHA)
        # Rounded arch stone
        pygame.draw.rect(surf, (245, 245, 245), (4, 18, 30, 34), border_radius=3)
        pygame.draw.circle(surf, top_color, (19, 18), 15)
        pygame.draw.rect(surf, (30, 30, 30), (4, 4, 30, 48), 1, border_radius=12)

        # Text
        txt_city = self.font_tiny.render(city[:4], True, (0, 0, 0))
        txt_dist = self.font_tiny.render(dist[:5], True, (0, 0, 0))
        surf.blit(txt_city, (19 - txt_city.get_width() // 2, 22))
        surf.blit(txt_dist, (19 - txt_dist.get_width() // 2, 34))
        return surf

    # -------------------------------------------------------------
    # 4. PICKUPS (CHAI CUP & RUPEE COIN)
    # -------------------------------------------------------------
    def _generate_pickups(self):
        # A. Cutting Chai Glass with Turbo Steam Aura
        chai_surf = pygame.Surface((38, 48), pygame.SRCALPHA)
        # Glow ring
        pygame.draw.circle(chai_surf, (255, 180, 50, 90), (19, 24), 18)
        # Glass
        points = [(10, 16), (28, 16), (25, 42), (13, 42)]
        pygame.draw.polygon(chai_surf, (220, 240, 255), points)
        pygame.draw.polygon(chai_surf, (80, 120, 150), points, 1)
        # Chai liquid
        chai_points = [(11, 22), (27, 22), (24, 40), (14, 40)]
        pygame.draw.polygon(chai_surf, (215, 130, 50), chai_points)
        # Steam swirls
        pygame.draw.line(chai_surf, (255, 255, 255, 200), (16, 12), (19, 6), 2)
        pygame.draw.line(chai_surf, (255, 255, 255, 200), (22, 12), (25, 6), 2)
        self.pickups['chai'] = chai_surf

        # B. Gold Rupee Coin (₹)
        coin_surf = pygame.Surface((34, 34), pygame.SRCALPHA)
        # Glow
        pygame.draw.circle(coin_surf, (255, 215, 0, 100), (17, 17), 16)
        # Coin body
        pygame.draw.circle(coin_surf, (255, 210, 20), (17, 17), 13)
        pygame.draw.circle(coin_surf, (210, 150, 10), (17, 17), 13, 2)
        # Engraved ₹ symbol
        txt = self.font_small.render("₹", True, (130, 80, 10))
        coin_surf.blit(txt, (17 - txt.get_width() // 2, 17 - txt.get_height() // 2))
        self.pickups['coin'] = coin_surf

    # -------------------------------------------------------------
    # 5. UI ELEMENTS & TITLE LOGO
    # -------------------------------------------------------------
    def _generate_ui_elements(self):
        # A. Truck-Art Themed Logo: "INDIAN STREETS: TRAFFIC RUSH"
        logo_w, logo_h = 580, 110
        logo_surf = pygame.Surface((logo_w, logo_h), pygame.SRCALPHA)

        # Ornate Backplate
        pygame.draw.rect(logo_surf, (180, 25, 25), (10, 10, logo_w - 20, logo_h - 20), border_radius=14)
        pygame.draw.rect(logo_surf, (255, 215, 0), (10, 10, logo_w - 20, logo_h - 20), 4, border_radius=14)

        # Title Text in 3D effect
        # Shadow
        t1_shadow = self.font_title.render("INDIAN STREETS", True, (20, 20, 20))
        t1_main = self.font_title.render("INDIAN STREETS", True, (255, 230, 50))
        logo_surf.blit(t1_shadow, (logo_w // 2 - t1_main.get_width() // 2 + 3, 17 + 3))
        logo_surf.blit(t1_main, (logo_w // 2 - t1_main.get_width() // 2, 17))

        # Subtitle Banner
        sub_shadow = self.font_large.render("TRAFFIC RUSH  •  ट्रैफिक रश", True, (0, 0, 0))
        sub_main = self.font_large.render("TRAFFIC RUSH  •  ट्रैफिक रश", True, (255, 255, 255))
        logo_surf.blit(sub_shadow, (logo_w // 2 - sub_main.get_width() // 2 + 2, 62 + 2))
        logo_surf.blit(sub_main, (logo_w // 2 - sub_main.get_width() // 2, 62))

        # Decorative Corner Marigolds
        pygame.draw.circle(logo_surf, (255, 140, 0), (22, 22), 8)
        pygame.draw.circle(logo_surf, (255, 140, 0), (logo_w - 22, 22), 8)
        pygame.draw.circle(logo_surf, (255, 140, 0), (22, logo_h - 22), 8)
        pygame.draw.circle(logo_surf, (255, 140, 0), (logo_w - 22, logo_h - 22), 8)

        self.ui_elements['logo'] = logo_surf
