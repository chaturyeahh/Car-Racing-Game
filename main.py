import pygame
import sys
import random

# Import modular game systems
from sound_fx import SoundManager
from assets_generator import AssetGenerator
from environment import EnvironmentManager
from traffic import TrafficManager
from ui import UIManager

# -------------------------------------------------------------
# CONSTANTS & SETUP
# -------------------------------------------------------------
WIDTH = 860
HEIGHT = 650
FPS = 60

# Game States
STATE_MENU = 0
STATE_PLAYING = 1
STATE_PAUSED = 2
STATE_GAME_OVER = 3

def main():
    # Initialize Pygame & Audio
    pygame.init()
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Indian Streets: Traffic Rush | भारतीय सड़कें: ट्रैफिक रश")
    clock = pygame.time.Clock()

    # Initialize Core Systems
    sound_mgr = SoundManager()
    asset_gen = AssetGenerator().generate_all()
    env_manager = EnvironmentManager(WIDTH, HEIGHT, asset_gen)
    traffic_manager = TrafficManager(env_manager, asset_gen, sound_mgr)
    ui_manager = UIManager(WIDTH, HEIGHT, asset_gen, sound_mgr)

    # ---------------------------------------------------------
    # GAME SESSION VARIABLES
    # ---------------------------------------------------------
    game_state = STATE_MENU

    # Player Vehicle Variables
    player_car_sprite = None
    player_lane = 2
    car_x = float(env_manager.get_lane_center_x(player_lane))
    car_y = HEIGHT - 135
    car_w = 50
    car_h = 82

    # Speed & Physics
    base_speed = 6.0
    current_speed = base_speed
    min_speed = 3.5
    max_normal_speed = 10.0
    boost_speed = 13.5

    # Chai Boost Powerup
    boost_timer = 0
    max_boost = 240  # 4 seconds at 60 FPS

    # Scoring & Stats
    score = 0
    distance = 0.0
    near_miss_count = 0
    chai_collected = 0
    combo = 1
    combo_timer = 0

    # Horn
    honk_cooldown = 0

    def start_new_game():
        nonlocal game_state, player_lane, car_x, car_y, car_w, car_h, player_car_sprite
        nonlocal current_speed, boost_timer, score, distance, near_miss_count, chai_collected
        nonlocal combo, combo_timer, honk_cooldown

        # Load selected player vehicle
        selected_v = ui_manager.get_selected_vehicle()
        player_car_sprite = asset_gen.vehicles.get(selected_v['sprite_key'])
        car_w = player_car_sprite.get_width()
        car_h = player_car_sprite.get_height()

        player_lane = 2
        car_x = float(env_manager.get_lane_center_x(player_lane) - car_w // 2)
        car_y = HEIGHT - car_h - 30

        current_speed = base_speed
        boost_timer = 0
        score = 0
        distance = 0.0
        near_miss_count = 0
        chai_collected = 0
        combo = 1
        combo_timer = 0
        honk_cooldown = 0

        traffic_manager.reset()
        game_state = STATE_PLAYING

    # ---------------------------------------------------------
    # MAIN GAME LOOP
    # ---------------------------------------------------------
    running = True
    while running:
        # 1. Event Handling
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False

            # --- MENU STATE EVENTS ---
            elif game_state == STATE_MENU:
                if ui_manager.start_btn.handle_event(event):
                    start_new_game()
                elif ui_manager.prev_car_btn.handle_event(event):
                    ui_manager.selected_vehicle_idx = (ui_manager.selected_vehicle_idx - 1) % len(ui_manager.garage_vehicles)
                    sound_mgr.play('coin')
                elif ui_manager.next_car_btn.handle_event(event):
                    ui_manager.selected_vehicle_idx = (ui_manager.selected_vehicle_idx + 1) % len(ui_manager.garage_vehicles)
                    sound_mgr.play('coin')
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        start_new_game()
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        ui_manager.selected_vehicle_idx = (ui_manager.selected_vehicle_idx - 1) % len(ui_manager.garage_vehicles)
                        sound_mgr.play('coin')
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        ui_manager.selected_vehicle_idx = (ui_manager.selected_vehicle_idx + 1) % len(ui_manager.garage_vehicles)
                        sound_mgr.play('coin')

            # --- PLAYING STATE EVENTS ---
            elif game_state == STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    # Lane Navigation
                    if event.key in [pygame.K_LEFT, pygame.K_a] and player_lane > 0:
                        player_lane -= 1
                    elif event.key in [pygame.K_RIGHT, pygame.K_d] and player_lane < env_manager.lane_count - 1:
                        player_lane += 1
                    # Horn
                    elif event.key in [pygame.K_SPACE, pygame.K_h]:
                        if honk_cooldown <= 0:
                            traffic_manager.on_player_honk(car_x, car_y, player_lane)
                            honk_cooldown = 20
                    # Pause
                    elif event.key in [pygame.K_ESCAPE, pygame.K_p]:
                        game_state = STATE_PAUSED

            # --- PAUSED STATE EVENTS ---
            elif game_state == STATE_PAUSED:
                if ui_manager.resume_btn.handle_event(event) or (event.type == pygame.KEYDOWN and event.key in [pygame.K_ESCAPE, pygame.K_p]):
                    game_state = STATE_PLAYING
                elif ui_manager.restart_pause_btn.handle_event(event):
                    start_new_game()
                elif ui_manager.sound_toggle_btn.handle_event(event):
                    sound_mgr.toggle_sound()
                elif ui_manager.menu_pause_btn.handle_event(event):
                    game_state = STATE_MENU

            # --- GAME OVER STATE EVENTS ---
            elif game_state == STATE_GAME_OVER:
                if ui_manager.retry_btn.handle_event(event) or (event.type == pygame.KEYDOWN and event.key in [pygame.K_SPACE, pygame.K_RETURN]):
                    start_new_game()
                elif ui_manager.garage_btn.handle_event(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    game_state = STATE_MENU

        # -----------------------------------------------------
        # 2. STATE UPDATES
        # -----------------------------------------------------
        keys = pygame.key.get_pressed()

        if game_state == STATE_MENU:
            # Idle ambient scrolling on start screen
            env_manager.update(speed=3.0, distance=0)

        elif game_state == STATE_PLAYING:
            # Throttle & Brake Controls
            target_speed = base_speed + min(3.0, distance / 1000.0)  # Natural speed progression
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                target_speed += 3.5
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                target_speed = min_speed

            # Chai Boost override
            if boost_timer > 0:
                boost_timer -= 1
                current_speed = boost_speed
                # Boost particles
                env_manager.spawn_exhaust_smoke(car_x + car_w // 2, car_y + car_h - 4, count=2, is_boost=True)
            else:
                current_speed += (target_speed - current_speed) * 0.1
                # Normal exhaust smoke
                if random.random() < 0.3:
                    env_manager.spawn_exhaust_smoke(car_x + car_w // 2 - 8, car_y + car_h - 4, count=1, is_boost=False)

            # Smooth lane position interpolation
            target_x = env_manager.get_lane_center_x(player_lane) - (car_w // 2)
            car_x += (target_x - car_x) * 0.22

            # Horn cooldown
            if honk_cooldown > 0:
                honk_cooldown -= 1

            # Combo timer
            if combo > 1:
                combo_timer -= 1
                if combo_timer <= 0:
                    combo = 1

            # Distance & continuous score
            distance += (current_speed * 0.45)
            score += int(current_speed * 0.15 * combo)

            # Update Environment
            env_manager.update(current_speed, distance)

            # Player Hitbox
            player_rect = pygame.Rect(car_x + 6, car_y + 8, car_w - 12, car_h - 14)

            # Update Traffic & AI
            prev_notifs = len(traffic_manager.notifications)
            traffic_manager.update(current_speed, distance, player_rect, player_lane, is_boosting=(boost_timer > 0))

            # Check if close call occurred
            if len(traffic_manager.notifications) > prev_notifs:
                last_notif = traffic_manager.notifications[-1]
                if "CLOSE CALL" in last_notif['text']:
                    near_miss_count += 1
                    score += 100 * combo
                    combo = min(8, combo + 1)
                    combo_timer = 180  # 3 seconds to chain next close call

            # Check Pickups
            collected_items = traffic_manager.check_pickup_collection(player_rect)
            for item in collected_items:
                if item.p_type == 'chai':
                    boost_timer = max_boost
                    chai_collected += 1
                    score += 250 * combo
                    combo = min(8, combo + 1)
                    combo_timer = 240
                elif item.p_type == 'coin':
                    score += item.value * combo
                    combo = min(8, combo + 1)
                    combo_timer = 150

            # Check Collisions with Traffic
            collision, collided_obs = traffic_manager.check_player_collision(player_rect)
            if collision:
                if boost_timer > 0:
                    # Turbo Invulnerability: smash past obstacle with sparks!
                    sound_mgr.play('crash')
                    env_manager.spawn_sparks(player_rect.centerx, player_rect.top, count=16)
                    score += 500
                    if collided_obs in traffic_manager.obstacles:
                        traffic_manager.obstacles.remove(collided_obs)
                else:
                    # Normal Crash -> Game Over
                    sound_mgr.play('crash')
                    sound_mgr.play('screech')
                    env_manager.spawn_sparks(player_rect.centerx, player_rect.top, count=24)
                    game_state = STATE_GAME_OVER

        # -----------------------------------------------------
        # 3. RENDERING
        # -----------------------------------------------------
        screen.fill((30, 30, 30))

        # A. Scrolling Environment (Sidewalks, Shops, Road markings, Cables)
        env_manager.draw_background(screen)

        # B. Traffic & Pickups
        traffic_manager.draw(screen)

        # C. Player Vehicle
        if player_car_sprite:
            screen.blit(player_car_sprite, (int(car_x), int(car_y)))

        # D. Foreground Layer (Particles & Dynamic Night Lighting Shaders)
        player_pos = (car_x, car_y, car_w, car_h) if game_state == STATE_PLAYING else None
        env_manager.draw_foreground(screen, player_car_pos=player_pos)

        # E. UI Layer based on State
        if game_state == STATE_PLAYING:
            ui_manager.draw_hud(screen, score, distance, current_speed, combo, boost_timer, max_boost, honk_cooldown)
        elif game_state == STATE_MENU:
            ui_manager.draw_menu(screen, env_manager)
        elif game_state == STATE_PAUSED:
            ui_manager.draw_hud(screen, score, distance, current_speed, combo, boost_timer, max_boost, honk_cooldown)
            ui_manager.draw_pause_menu(screen)
        elif game_state == STATE_GAME_OVER:
            ui_manager.draw_game_over(screen, score, distance, near_miss_count, chai_collected)

        # Flip display & tick
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
