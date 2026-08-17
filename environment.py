import pygame
import random
import math

class Particle:
    def __init__(self, x, y, vx, vy, color, size, life, decay=1.0, shape='circle'):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.size = size
        self.max_life = life
        self.life = life
        self.decay = decay
        self.shape = shape

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= self.decay
        self.size = max(0.5, self.size * 0.96)

    def draw(self, surf):
        if self.life <= 0 or self.size <= 0.5:
            return
        alpha = int((self.life / self.max_life) * 255)
        alpha = max(0, min(255, alpha))
        
        c = self.color
        if len(c) == 3:
            draw_color = (c[0], c[1], c[2], alpha)
        else:
            draw_color = (c[0], c[1], c[2], min(c[3], alpha))

        p_surf = pygame.Surface((int(self.size * 2 + 2), int(self.size * 2 + 2)), pygame.SRCALPHA)
        if self.shape == 'circle':
            pygame.draw.circle(p_surf, draw_color, (int(self.size + 1), int(self.size + 1)), int(self.size))
        elif self.shape == 'spark':
            pts = [
                (self.size + 1, 0),
                (self.size + 1 + self.size, self.size + 1),
                (self.size + 1, self.size * 2 + 2),
                (0, self.size + 1)
            ]
            pygame.draw.polygon(p_surf, draw_color, pts)
        surf.blit(p_surf, (self.x - self.size - 1, self.y - self.size - 1))


class EnvironmentManager:
    """Manages road scrolling, roadside buildings, props, lighting transitions, and particles."""

    def __init__(self, screen_width, screen_height, asset_gen):
        self.width = screen_width
        self.height = screen_height
        self.asset_gen = asset_gen

        # Layout Geometry
        self.sidewalk_width = 175
        self.road_x = self.sidewalk_width
        self.road_width = self.width - (self.sidewalk_width * 2)  # typically 510px
        self.lane_count = 4
        self.lane_width = self.road_width // self.lane_count

        # Scrolling positions
        self.scroll_y = 0
        self.shop_height = 220
        
        # Build seamless building strips
        self.left_buildings = []
        self.right_buildings = []
        self._init_building_strips()

        # Road Features (Zebra crossings, road markings, hazards)
        self.road_features = []
        self.next_zebra_y = -300
        self.next_hazard_y = -800

        # Lighting & Time of Day
        # 0: Day (0-1500m), 1: Sunset (1500-3000m), 2: Night (3000m+)
        self.time_phase = 0.0  # 0.0 to 1.0 (Day -> Sunset -> Night)
        self.night_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.sunset_overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Particles
        self.particles = []

    def _init_building_strips(self):
        # We populate enough buildings to cover screen height + buffer
        total_slots = (self.height // self.shop_height) + 4
        building_pool = self.asset_gen.buildings

        for i in range(total_slots):
            y_pos = (i - 2) * self.shop_height
            b_left = random.choice(building_pool)
            b_right = random.choice(building_pool)
            self.left_buildings.append({'surf': b_left, 'y': y_pos})
            self.right_buildings.append({'surf': b_right, 'y': y_pos})

    def update(self, speed, distance):
        self.scroll_y = (self.scroll_y + speed) % 80  # For dashed road lines

        # Update buildings position
        for b in self.left_buildings:
            b['y'] += speed
            if b['y'] > self.height + 50:
                min_y = min(item['y'] for item in self.left_buildings)
                b['y'] = min_y - self.shop_height
                b['surf'] = random.choice(self.asset_gen.buildings)

        for b in self.right_buildings:
            b['y'] += speed
            if b['y'] > self.height + 50:
                min_y = min(item['y'] for item in self.right_buildings)
                b['y'] = min_y - self.shop_height
                b['surf'] = random.choice(self.asset_gen.buildings)

        # Time of day calculation based on distance
        # 0 - 1500m: Day (0.0 to 0.3)
        # 1500 - 3000m: Sunset (0.3 to 0.7)
        # 3000m+: Night (0.7 to 1.0)
        cycle_dist = distance % 6000
        if cycle_dist < 2000:
            self.time_phase = cycle_dist / 2000.0 * 0.3  # Bright day transitioning
        elif cycle_dist < 4000:
            self.time_phase = 0.3 + ((cycle_dist - 2000) / 2000.0) * 0.4  # Golden sunset
        else:
            self.time_phase = 0.7 + ((cycle_dist - 4000) / 2000.0) * 0.3  # Atmospheric night

        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0 or p.size <= 0.5:
                self.particles.remove(p)

    def spawn_exhaust_smoke(self, x, y, count=1, is_boost=False):
        for _ in range(count):
            vx = random.uniform(-0.6, 0.6)
            vy = random.uniform(2.0, 4.5) if not is_boost else random.uniform(4.0, 7.5)
            color = (255, 160, 40, 200) if is_boost else (200, 200, 200, 150)
            size = random.uniform(3.0, 6.0) if not is_boost else random.uniform(4.5, 9.0)
            life = random.uniform(15, 25)
            self.particles.append(Particle(x, y, vx, vy, color, size, life))

    def spawn_sparks(self, x, y, count=8):
        for _ in range(count):
            vx = random.uniform(-4.0, 4.0)
            vy = random.uniform(-3.0, 3.0)
            color = (255, random.randint(180, 240), 20)
            size = random.uniform(2.0, 4.0)
            life = random.uniform(10, 20)
            self.particles.append(Particle(x, y, vx, vy, color, size, life, shape='spark'))

    def spawn_coin_burst(self, x, y, count=12):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            spd = random.uniform(2.0, 5.5)
            vx = math.cos(angle) * spd
            vy = math.sin(angle) * spd
            color = (255, 215, 0)
            size = random.uniform(2.5, 4.5)
            life = random.uniform(15, 30)
            self.particles.append(Particle(x, y, vx, vy, color, size, life, shape='spark'))

    def get_lane_center_x(self, lane_index):
        lane_index = max(0, min(self.lane_count - 1, lane_index))
        return self.road_x + (lane_index * self.lane_width) + (self.lane_width // 2)

    def draw_background(self, screen):
        # 1. Sidewalk Footpaths (Pavement texture)
        pygame.draw.rect(screen, (165, 155, 140), (0, 0, self.sidewalk_width, self.height))
        pygame.draw.rect(screen, (165, 155, 140), (self.width - self.sidewalk_width, 0, self.sidewalk_width, self.height))

        # Pavement tile grid lines
        for py in range(int(self.scroll_y % 40) - 40, self.height, 40):
            pygame.draw.line(screen, (140, 130, 118), (0, py), (self.sidewalk_width, py), 1)
            pygame.draw.line(screen, (140, 130, 118), (self.width - self.sidewalk_width, py), (self.width, py), 1)

        # 2. Roadside Buildings & Shopfronts
        for b in self.left_buildings:
            screen.blit(b['surf'], (2, int(b['y'])))

        for b in self.right_buildings:
            screen.blit(b['surf'], (self.width - self.sidewalk_width + 3, int(b['y'])))

        # 3. Asphalt Roadway
        road_rect = pygame.Rect(self.road_x, 0, self.road_width, self.height)
        pygame.draw.rect(screen, (45, 48, 54), road_rect)

        # Road shoulder / oil wear streaks
        pygame.draw.line(screen, (38, 40, 46), (self.road_x + 20, 0), (self.road_x + 20, self.height), 4)
        pygame.draw.line(screen, (38, 40, 46), (self.road_x + self.road_width - 20, 0), (self.road_x + self.road_width - 20, self.height), 4)

        # 4. Yellow & Black Hazard Curbs (Edge of road)
        curb_h = 24
        curb_offset = int(self.scroll_y % (curb_h * 2))
        for y_pos in range(-curb_h * 2 + curb_offset, self.height + curb_h * 2, curb_h * 2):
            # Left Curb
            pygame.draw.rect(screen, (255, 210, 0), (self.road_x - 8, y_pos, 8, curb_h))
            pygame.draw.rect(screen, (25, 25, 25), (self.road_x - 8, y_pos + curb_h, 8, curb_h))
            # Right Curb
            pygame.draw.rect(screen, (255, 210, 0), (self.road_x + self.road_width, y_pos, 8, curb_h))
            pygame.draw.rect(screen, (25, 25, 25), (self.road_x + self.road_width, y_pos + curb_h, 8, curb_h))

        # 5. Dashed Lane Dividers
        dash_len = 34
        gap_len = 38
        step = dash_len + gap_len
        line_offset = int(self.scroll_y % step)

        for lane_i in range(1, self.lane_count):
            lx = self.road_x + (lane_i * self.lane_width)
            for ly in range(-step + line_offset, self.height + step, step):
                # Dashed white/yellow road line
                pygame.draw.line(screen, (245, 245, 230), (lx, ly), (lx, ly + dash_len), 3)

        # 6. Overhead Tangled Electric Cables
        for wy in [140, 360, 580]:
            wire_y = (wy + self.scroll_y * 0.2) % (self.height + 200) - 100
            pygame.draw.line(screen, (30, 30, 35), (0, wire_y - 15), (self.width, wire_y + 15), 1)
            pygame.draw.line(screen, (25, 25, 30), (0, wire_y + 10), (self.width, wire_y - 10), 1)

    def draw_foreground(self, screen, player_car_pos=None):
        # 1. Particles (Smoke, Sparks, Confetti)
        for p in self.particles:
            p.draw(screen)

        # 2. Dynamic Time-of-Day Lighting Shader
        if self.time_phase > 0.1:
            if self.time_phase < 0.65:
                # Sunset Golden Haze
                factor = (self.time_phase - 0.1) / 0.55
                alpha = int(factor * 95)
                self.sunset_overlay.fill((230, 110, 30, alpha))
                screen.blit(self.sunset_overlay, (0, 0))
            else:
                # Atmospheric Indigo Night
                factor = (self.time_phase - 0.65) / 0.35
                alpha = int(90 + factor * 80)
                self.night_overlay.fill((12, 16, 38, alpha))

                # If night, draw dynamic glowing headlight beam from player car
                if player_car_pos:
                    px, py, pw, ph = player_car_pos
                    # Headlight cones
                    beam_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    # Left beam
                    left_cone = [(px + 10, py + 8), (px - 25, py - 200), (px + 35, py - 200)]
                    pygame.draw.polygon(beam_surf, (255, 255, 220, 120), left_cone)
                    # Right beam
                    right_cone = [(px + pw - 10, py + 8), (px + pw - 35, py - 200), (px + pw + 25, py - 200)]
                    pygame.draw.polygon(beam_surf, (255, 255, 220, 120), right_cone)

                    # Subtract beam from night darkness
                    screen.blit(self.night_overlay, (0, 0))
                    screen.blit(beam_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
                else:
                    screen.blit(self.night_overlay, (0, 0))
