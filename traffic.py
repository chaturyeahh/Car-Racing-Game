import pygame
import random
import math

class VehicleObstacle:
    def __init__(self, v_type, sprite, x, y, lane, speed, is_heavy=False, can_drift=False):
        self.v_type = v_type
        self.sprite = sprite
        self.w = sprite.get_width()
        self.h = sprite.get_height()
        self.x = float(x)
        self.y = float(y)
        self.target_x = float(x)
        self.lane = lane
        self.speed = speed
        self.base_speed = speed
        self.is_heavy = is_heavy
        self.can_drift = can_drift
        
        # Blinker / Honk reaction
        self.blinker_timer = 0
        self.drift_timer = random.randint(60, 200)
        self.has_given_close_call = False

    def update(self, road_speed, env_manager):
        # Move relative to player road scrolling speed
        # Obstacle moves down screen at (road_speed - obstacle_forward_speed)
        # Note: If obstacle moves forward at 3, and road scrolls at 7, net movement downwards is 4.
        self.y += (road_speed - self.speed)

        # Smooth lateral movement (e.g. changing lane on honk or gentle sway)
        if abs(self.target_x - self.x) > 0.5:
            self.x += (self.target_x - self.x) * 0.12

        # Auto-rickshaw playful sway
        if self.can_drift:
            self.drift_timer -= 1
            if self.drift_timer <= 0:
                self.drift_timer = random.randint(80, 180)
                sway_offset = random.choice([-14, 0, 14])
                base_center = env_manager.get_lane_center_x(self.lane)
                self.target_x = base_center - (self.w // 2) + sway_offset

        # Blinker tick
        if self.blinker_timer > 0:
            self.blinker_timer -= 1

    def react_to_honk(self, player_lane, env_manager):
        """When player honks, obstacle indicates and attempts to shift lane away."""
        self.blinker_timer = 45  # Flash blinkers
        # Shift away from player's lane
        new_lane = self.lane
        if player_lane == self.lane:
            if self.lane > 0 and self.lane < env_manager.lane_count - 1:
                new_lane = random.choice([self.lane - 1, self.lane + 1])
            elif self.lane == 0:
                new_lane = 1
            else:
                new_lane = self.lane - 1
        elif player_lane < self.lane and self.lane < env_manager.lane_count - 1:
            new_lane = self.lane + 1
        elif player_lane > self.lane and self.lane > 0:
            new_lane = self.lane - 1

        self.lane = new_lane
        self.target_x = env_manager.get_lane_center_x(self.lane) - (self.w // 2)

    def draw(self, screen):
        screen.blit(self.sprite, (int(self.x), int(self.y)))
        # Draw flashing orange blinker if reacting to honk
        if self.blinker_timer > 0 and (self.blinker_timer // 6) % 2 == 0:
            # Left & Right Orange Blinkers
            pygame.draw.circle(screen, (255, 160, 0), (int(self.x + 8), int(self.y + self.h - 10)), 3)
            pygame.draw.circle(screen, (255, 160, 0), (int(self.x + self.w - 8), int(self.y + self.h - 10)), 3)

    def get_rect(self):
        # Slightly inset collision hitbox for fair arcade gameplay
        inset_x = 6
        inset_y = 8
        return pygame.Rect(self.x + inset_x, self.y + inset_y, self.w - (inset_x * 2), self.h - (inset_y * 2))


class PickupItem:
    def __init__(self, p_type, sprite, x, y, value=100):
        self.p_type = p_type  # 'chai' or 'coin'
        self.sprite = sprite
        self.w = sprite.get_width()
        self.h = sprite.get_height()
        self.x = float(x)
        self.y = float(y)
        self.value = value
        self.bob_timer = random.uniform(0, 6.28)

    def update(self, road_speed):
        self.y += road_speed
        self.bob_timer += 0.1

    def draw(self, screen):
        bob_offset = math.sin(self.bob_timer) * 3
        screen.blit(self.sprite, (int(self.x), int(self.y + bob_offset)))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)


class TrafficManager:
    """Manages obstacle traffic, AI reactions, pickups, and collision checks."""

    def __init__(self, env_manager, asset_gen, sound_mgr):
        self.env_manager = env_manager
        self.asset_gen = asset_gen
        self.sound_mgr = sound_mgr

        self.obstacles = []
        self.pickups = []

        # Spawning parameters
        self.spawn_timer = 0
        self.spawn_interval = 85
        self.pickup_timer = 0

        # Close-call feedback notifications
        self.notifications = []  # {'text': str, 'x': int, 'y': int, 'alpha': int, 'color': tuple}

    def reset(self):
        self.obstacles.clear()
        self.pickups.clear()
        self.spawn_timer = 0
        self.spawn_interval = 85
        self.pickup_timer = 0
        self.notifications.clear()

    def update(self, road_speed, distance, player_rect, player_lane, is_boosting=False):
        # Gradually increase density and speed with distance
        self.spawn_interval = max(45, 85 - int(distance / 250))

        # Spawn obstacles
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval and len(self.obstacles) < 7:
            self.spawn_timer = 0
            self._spawn_random_vehicle(road_speed)

        # Spawn pickups (Coins and Chai)
        self.pickup_timer += 1
        if self.pickup_timer >= 120:
            self.pickup_timer = 0
            self._spawn_random_pickup()

        # Update obstacles
        for obs in self.obstacles[:]:
            obs.update(road_speed, self.env_manager)

            # Check for near-miss / close-call bonus
            if not obs.has_given_close_call:
                obs_rect = obs.get_rect()
                # Close proximity alongside without collision
                if (abs(player_rect.centerx - obs_rect.centerx) < 65 and
                    abs(player_rect.centery - obs_rect.centery) < 70 and
                    not player_rect.colliderect(obs_rect)):
                    if player_rect.centery < obs_rect.bottom and player_rect.top > obs_rect.top - 20:
                        obs.has_given_close_call = True
                        self._trigger_close_call(obs_rect.centerx, obs_rect.top)

            # Remove off-screen obstacles
            if obs.y > self.env_manager.height + 100 or obs.y < -400:
                self.obstacles.remove(obs)

        # Update pickups
        for pick in self.pickups[:]:
            pick.update(road_speed)
            if pick.y > self.env_manager.height + 60:
                self.pickups.remove(pick)

        # Update floating notifications
        for notif in self.notifications[:]:
            notif['y'] -= 1.8
            notif['alpha'] -= 4
            if notif['alpha'] <= 0:
                self.notifications.remove(notif)

    def _spawn_random_vehicle(self, road_speed):
        lane = random.randint(0, self.env_manager.lane_count - 1)
        lane_center_x = self.env_manager.get_lane_center_x(lane)

        # Check for overlap with existing obstacles in this lane near top
        lane_blocked = any(abs(obs.y - (-120)) < 160 for obs in self.obstacles if obs.lane == lane)
        if lane_blocked:
            return

        # Choose vehicle type with weighted probabilities
        types = [
            ('auto_green', 2.0, False, True, 25),
            ('auto_black', 2.0, False, True, 20),
            ('truck_blue', 0.8, True, False, 15),
            ('truck_red', 0.8, True, False, 15),
            ('taxi_mumbai', 2.4, False, False, 20),
            ('taxi_kolkata', 2.4, False, False, 15),
            ('scooter_mint', 3.2, False, False, 20),
            ('scooter_red', 3.2, False, False, 15),
            ('car_maruti_red', 2.6, False, False, 20),
            ('car_maruti_blue', 2.6, False, False, 15),
            ('car_sedan_white', 2.8, False, False, 15),
            ('car_suv_orange', 2.7, False, False, 15),
            ('thela', 0.4, False, False, 10 if (lane == 0 or lane == 3) else 0)  # Thelas mostly on side lanes
        ]

        valid_types = [t for t in types if t[4] > 0]
        weights = [t[4] for t in valid_types]
        chosen = random.choices(valid_types, weights=weights, k=1)[0]

        v_name, fwd_speed, is_heavy, can_drift, _ = chosen
        sprite = self.asset_gen.vehicles.get(v_name)
        if not sprite:
            return

        spawn_x = lane_center_x - (sprite.get_width() // 2)
        spawn_y = -sprite.get_height() - 20

        # Forward speed variation
        v_speed = fwd_speed + random.uniform(-0.3, 0.4)

        obstacle = VehicleObstacle(v_name, sprite, spawn_x, spawn_y, lane, v_speed, is_heavy, can_drift)
        self.obstacles.append(obstacle)

    def _spawn_random_pickup(self):
        lane = random.randint(0, self.env_manager.lane_count - 1)
        lane_center_x = self.env_manager.get_lane_center_x(lane)

        # 75% Coin, 25% Cutting Chai
        if random.random() < 0.3:
            p_type = 'chai'
            sprite = self.asset_gen.pickups['chai']
            value = 250
        else:
            p_type = 'coin'
            sprite = self.asset_gen.pickups['coin']
            value = 100

        px = lane_center_x - (sprite.get_width() // 2)
        py = -sprite.get_height() - 30
        self.pickups.append(PickupItem(p_type, sprite, px, py, value))

    def on_player_honk(self, player_x, player_y, player_lane):
        """Triggered when player presses horn."""
        self.sound_mgr.play('horn')
        # Check nearby vehicles ahead
        reacted = False
        for obs in self.obstacles:
            if obs.y < player_y and (player_y - obs.y) < 320:
                if abs(obs.lane - player_lane) <= 1:
                    obs.react_to_honk(player_lane, self.env_manager)
                    reacted = True

        if reacted and random.random() < 0.35:
            # Truck or auto occasionally honks back!
            self.sound_mgr.play('truck_horn')

    def _trigger_close_call(self, x, y):
        self.sound_mgr.play('near_miss')
        self.env_manager.spawn_sparks(x, y, count=8)
        self.notifications.append({
            'text': "CLOSE CALL! +100 ₹",
            'x': x,
            'y': y,
            'alpha': 255,
            'color': (255, 220, 50)
        })

    def check_player_collision(self, player_rect):
        for obs in self.obstacles:
            if player_rect.colliderect(obs.get_rect()):
                return True, obs
        return False, None

    def check_pickup_collection(self, player_rect):
        collected = []
        for pick in self.pickups[:]:
            if player_rect.colliderect(pick.get_rect()):
                collected.append(pick)
                self.pickups.remove(pick)
                if pick.p_type == 'chai':
                    self.sound_mgr.play('boost')
                    self.notifications.append({
                        'text': "CHAI TURBO BOOST! ⚡",
                        'x': pick.x,
                        'y': pick.y,
                        'alpha': 255,
                        'color': (255, 140, 40)
                    })
                elif pick.p_type == 'coin':
                    self.sound_mgr.play('coin')
                    self.env_manager.spawn_coin_burst(pick.x, pick.y, count=10)
                    self.notifications.append({
                        'text': f"+{pick.value} ₹",
                        'x': pick.x,
                        'y': pick.y,
                        'alpha': 255,
                        'color': (255, 215, 0)
                    })
        return collected

    def draw(self, screen):
        # Draw Pickups
        for pick in self.pickups:
            pick.draw(screen)

        # Draw Obstacles
        for obs in self.obstacles:
            obs.draw(screen)

        # Draw Floating Notifications
        font = self.asset_gen.font_small
        for notif in self.notifications:
            txt = font.render(notif['text'], True, notif['color'])
            txt.set_alpha(notif['alpha'])
            # Black shadow
            shadow = font.render(notif['text'], True, (0, 0, 0))
            shadow.set_alpha(int(notif['alpha'] * 0.7))
            screen.blit(shadow, (int(notif['x'] - txt.get_width() // 2 + 1), int(notif['y'] + 1)))
            screen.blit(txt, (int(notif['x'] - txt.get_width() // 2), int(notif['y'])))
