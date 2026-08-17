import pygame
import math

class Button:
    def __init__(self, rect, text, bg_color=(230, 60, 40), hover_color=(255, 90, 60), text_color=(255, 255, 255), border_color=(255, 215, 0), font=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.border_color = border_color
        self.font = font or pygame.font.SysFont("arial", 18, bold=True)
        self.is_hovered = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.bg_color
        # Drop shadow
        pygame.draw.rect(screen, (0, 0, 0, 100), (self.rect.x + 3, self.rect.y + 4, self.rect.width, self.rect.height), border_radius=8)
        # Main Button Body
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        if self.border_color:
            pygame.draw.rect(screen, self.border_color, self.rect, 2, border_radius=8)

        # Text
        txt_surf = self.font.render(self.text, True, self.text_color)
        screen.blit(txt_surf, (self.rect.centerx - txt_surf.get_width() // 2, self.rect.centery - txt_surf.get_height() // 2))


class UIManager:
    """Manages Menu/Garage, HUD, Pause Screen, and E-Challan Game Over Screen."""

    def __init__(self, screen_width, screen_height, asset_gen, sound_mgr):
        self.width = screen_width
        self.height = screen_height
        self.asset_gen = asset_gen
        self.sound_mgr = sound_mgr

        # Fonts
        self.font_huge = pygame.font.SysFont("impact", 44)
        self.font_title = pygame.font.SysFont("impact", 32)
        self.font_large = pygame.font.SysFont("arial", 22, bold=True)
        self.font_medium = pygame.font.SysFont("arial", 16, bold=True)
        self.font_small = pygame.font.SysFont("arial", 13, bold=True)
        self.font_tiny = pygame.font.SysFont("arial", 11)

        # Player Garage Selection
        self.garage_vehicles = [
            {
                'id': 'player_800',
                'name': 'The Legend 800',
                'desc': 'Agile, classic Indian hatchback. Balanced speed and razor-sharp steering.',
                'speed': 8.5,
                'handling': 9.0,
                'horn_power': 7.5,
                'sprite_key': 'player_800'
            },
            {
                'id': 'auto_super',
                'name': 'Turbo Super Auto',
                'desc': 'Customized gold rickshaw! Weaves tightly between traffic with instant horn.',
                'speed': 7.8,
                'handling': 10.0,
                'horn_power': 9.5,
                'sprite_key': 'auto_super'
            },
            {
                'id': 'player_ambassador',
                'name': 'Grand Ambassador',
                'desc': 'Sturdy retro highway VIP cruiser. Heavy road grip and commanding presence.',
                'speed': 9.2,
                'handling': 7.0,
                'horn_power': 8.5,
                'sprite_key': 'player_ambassador'
            }
        ]
        self.selected_vehicle_idx = 0

        # Menu Buttons
        self.start_btn = Button(
            (self.width // 2 - 120, self.height - 105, 240, 52),
            "START RACE  🏁",
            bg_color=(20, 160, 60),
            hover_color=(35, 195, 80),
            font=self.font_large
        )
        self.prev_car_btn = Button(
            (self.width // 2 - 170, self.height - 230, 44, 44),
            "◀",
            bg_color=(50, 50, 60),
            hover_color=(80, 80, 100),
            font=self.font_large
        )
        self.next_car_btn = Button(
            (self.width // 2 + 126, self.height - 230, 44, 44),
            "▶",
            bg_color=(50, 50, 60),
            hover_color=(80, 80, 100),
            font=self.font_large
        )

        # Pause Buttons
        self.resume_btn = Button(
            (self.width // 2 - 110, self.height // 2 - 40, 220, 44),
            "RESUME RACE  ▶",
            bg_color=(20, 150, 60),
            font=self.font_medium
        )
        self.restart_pause_btn = Button(
            (self.width // 2 - 110, self.height // 2 + 15, 220, 44),
            "RESTART RACE  🔄",
            bg_color=(210, 110, 20),
            font=self.font_medium
        )
        self.sound_toggle_btn = Button(
            (self.width // 2 - 110, self.height // 2 + 70, 220, 44),
            "SOUND: ON  🔊",
            bg_color=(50, 90, 160),
            font=self.font_medium
        )
        self.menu_pause_btn = Button(
            (self.width // 2 - 110, self.height // 2 + 125, 220, 44),
            "MAIN MENU  🏠",
            bg_color=(180, 40, 40),
            font=self.font_medium
        )

        # Game Over Buttons
        self.retry_btn = Button(
            (self.width // 2 - 170, self.height - 115, 160, 48),
            "PAY FINE & RETRY",
            bg_color=(200, 35, 35),
            hover_color=(235, 55, 55),
            font=self.font_medium
        )
        self.garage_btn = Button(
            (self.width // 2 + 10, self.height - 115, 160, 48),
            "GARAGE / MENU",
            bg_color=(45, 100, 180),
            hover_color=(60, 125, 220),
            font=self.font_medium
        )

        # High score
        self.high_score = 0

    def get_selected_vehicle(self):
        return self.garage_vehicles[self.selected_vehicle_idx]

    def draw_hud(self, screen, score, distance, speed, combo, boost_timer, max_boost, honk_cooldown):
        # 1. Top Retro Instrument Dashboard Bar
        dash_h = 58
        dash_rect = pygame.Rect(0, 0, self.width, dash_h)
        # Wooden/Carbon finish with gold border
        pygame.draw.rect(screen, (32, 28, 25), dash_rect)
        pygame.draw.line(screen, (255, 204, 0), (0, dash_h), (self.width, dash_h), 3)

        # A. Score & Cash in Rupees (₹)
        score_box = pygame.Rect(20, 8, 190, 42)
        pygame.draw.rect(screen, (20, 20, 20), score_box, border_radius=6)
        pygame.draw.rect(screen, (255, 215, 0), score_box, 1, border_radius=6)

        lbl_score = self.font_tiny.render("TOTAL CASH EARNED", True, (200, 200, 200))
        val_score = self.font_large.render(f"₹ {score:,}", True, (255, 220, 40))
        screen.blit(lbl_score, (28, 11))
        screen.blit(val_score, (28, 24))

        # B. Odometer (Distance covered)
        dist_km = distance / 1000.0
        dist_box = pygame.Rect(225, 8, 160, 42)
        pygame.draw.rect(screen, (20, 20, 20), dist_box, border_radius=6)
        pygame.draw.rect(screen, (100, 200, 255), dist_box, 1, border_radius=6)

        lbl_dist = self.font_tiny.render("DISTANCE", True, (200, 200, 200))
        val_dist = self.font_large.render(f"{dist_km:.2f} KM", True, (130, 225, 255))
        screen.blit(lbl_dist, (233, 11))
        screen.blit(val_dist, (233, 24))

        # C. Speedometer Display
        speed_kmh = int(speed * 14.5)
        spd_box = pygame.Rect(self.width - 200, 8, 180, 42)
        pygame.draw.rect(screen, (20, 20, 20), spd_box, border_radius=6)
        pygame.draw.rect(screen, (255, 100, 50), spd_box, 1, border_radius=6)

        lbl_spd = self.font_tiny.render("SPEED", True, (200, 200, 200))
        val_spd = self.font_large.render(f"{speed_kmh} KM/H", True, (255, 120, 60))
        screen.blit(lbl_spd, (self.width - 192, 11))
        screen.blit(val_spd, (self.width - 192, 24))

        # D. Chai Turbo Boost Meter (Center)
        if boost_timer > 0:
            boost_pct = boost_timer / max_boost
            b_box = pygame.Rect(self.width // 2 - 110, 10, 220, 38)
            pygame.draw.rect(screen, (40, 20, 10), b_box, border_radius=6)
            pygame.draw.rect(screen, (255, 140, 30), b_box, 2, border_radius=6)

            # Fill bar
            fill_w = int((220 - 6) * boost_pct)
            pygame.draw.rect(screen, (255, 160, 40), (self.width // 2 - 107, 13, fill_w, 32), border_radius=4)

            b_text = self.font_medium.render("⚡ CHAI TURBO BOOST! ⚡", True, (255, 255, 255))
            screen.blit(b_text, (self.width // 2 - b_text.get_width() // 2, 18))
        else:
            # Horn Prompt & Combo Status
            h_box = pygame.Rect(self.width // 2 - 110, 10, 220, 38)
            pygame.draw.rect(screen, (25, 25, 25), h_box, border_radius=6)
            pygame.draw.rect(screen, (100, 100, 110), h_box, 1, border_radius=6)

            if combo > 1:
                c_text = self.font_medium.render(f"🔥 CHAOS COMBO x{combo}!", True, (255, 215, 0))
                screen.blit(c_text, (self.width // 2 - c_text.get_width() // 2, 18))
            else:
                horn_text = self.font_small.render("[SPACE] - BLOW HORN 🎺", True, (230, 230, 230))
                screen.blit(horn_text, (self.width // 2 - horn_text.get_width() // 2, 20))

    def draw_menu(self, screen, env_manager):
        # 1. Overlay for background visibility
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        screen.blit(overlay, (0, 0))

        # 2. Main Title Banner
        logo = self.asset_gen.ui_elements.get('logo')
        if logo:
            screen.blit(logo, (self.width // 2 - logo.get_width() // 2, 35))

        # 3. Vehicle Garage Card
        garage_w, garage_h = 440, 240
        garage_rect = pygame.Rect(self.width // 2 - garage_w // 2, 175, garage_w, garage_h)
        pygame.draw.rect(screen, (30, 32, 40), garage_rect, border_radius=12)
        pygame.draw.rect(screen, (255, 204, 0), garage_rect, 3, border_radius=12)

        # Header
        g_header = self.font_large.render("SELECT YOUR VEHICLE • गैराज", True, (255, 215, 0))
        screen.blit(g_header, (self.width // 2 - g_header.get_width() // 2, 188))

        curr_v = self.get_selected_vehicle()
        sprite = self.asset_gen.vehicles.get(curr_v['sprite_key'])

        # Draw vehicle preview
        if sprite:
            # Soft shadow
            pygame.draw.ellipse(screen, (0, 0, 0, 120), (self.width // 2 - 40, 260, 80, 30))
            screen.blit(sprite, (self.width // 2 - sprite.get_width() // 2, 230))

        # Vehicle Name & Description
        v_name = self.font_large.render(curr_v['name'], True, (255, 255, 255))
        screen.blit(v_name, (self.width // 2 - v_name.get_width() // 2, 335))

        v_desc = self.font_tiny.render(curr_v['desc'], True, (200, 200, 210))
        screen.blit(v_desc, (self.width // 2 - v_desc.get_width() // 2, 365))

        # Stats Bars (Speed, Handling, Horn)
        stats = [
            ("Speed", curr_v['speed'], (240, 80, 50)),
            ("Handling", curr_v['handling'], (50, 180, 100)),
            ("Horn", curr_v['horn_power'], (255, 200, 40))
        ]
        for idx, (label, val, col) in enumerate(stats):
            bx = self.width // 2 - 160 + (idx * 115)
            by = 388
            lbl = self.font_tiny.render(label, True, (220, 220, 220))
            screen.blit(lbl, (bx, by))
            pygame.draw.rect(screen, (60, 60, 70), (bx, by + 14, 85, 6), border_radius=3)
            pygame.draw.rect(screen, col, (bx, by + 14, int(85 * (val / 10.0)), 6), border_radius=3)

        # High Score notice
        if self.high_score > 0:
            hs_surf = self.font_small.render(f"🏆 HIGH SCORE: ₹ {self.high_score:,}", True, (255, 215, 0))
            screen.blit(hs_surf, (self.width // 2 - hs_surf.get_width() // 2, 430))

        # Controls Overview Card
        ctrl_rect = pygame.Rect(self.width // 2 - 200, 460, 400, 80)
        pygame.draw.rect(screen, (20, 22, 28, 220), ctrl_rect, border_radius=8)
        pygame.draw.rect(screen, (80, 90, 110), ctrl_rect, 1, border_radius=8)

        c1 = self.font_small.render("CONTROLS • कैसे खेलें:", True, (255, 204, 0))
        c2 = self.font_tiny.render("• [LEFT / RIGHT] or [A / D] : Steer Lanes", True, (230, 230, 230))
        c3 = self.font_tiny.render("• [UP / W] : Accelerate  |  [DOWN / S] : Brake", True, (230, 230, 230))
        c4 = self.font_tiny.render("• [SPACE] or [H] : Blow Horn (Move Traffic Aside!)", True, (230, 230, 230))
        screen.blit(c1, (ctrl_rect.x + 12, ctrl_rect.y + 8))
        screen.blit(c2, (ctrl_rect.x + 12, ctrl_rect.y + 28))
        screen.blit(c3, (ctrl_rect.x + 12, ctrl_rect.y + 44))
        screen.blit(c4, (ctrl_rect.x + 12, ctrl_rect.y + 60))

        # Draw Buttons
        self.prev_car_btn.draw(screen)
        self.next_car_btn.draw(screen)
        self.start_btn.draw(screen)

    def draw_pause_menu(self, screen):
        # Dark blur overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 175))
        screen.blit(overlay, (0, 0))

        # Dhaba Board Frame
        bw, bh = 340, 360
        board = pygame.Rect(self.width // 2 - bw // 2, self.height // 2 - bh // 2, bw, bh)
        pygame.draw.rect(screen, (42, 34, 26), board, border_radius=12)
        pygame.draw.rect(screen, (220, 160, 40), board, 4, border_radius=12)

        # Title
        p_title = self.font_huge.render("GAME PAUSED", True, (255, 220, 50))
        p_sub = self.font_small.render("CHAI BREAK • विश्राम", True, (240, 240, 240))
        screen.blit(p_title, (self.width // 2 - p_title.get_width() // 2, board.y + 20))
        screen.blit(p_sub, (self.width // 2 - p_sub.get_width() // 2, board.y + 65))

        # Buttons
        self.sound_toggle_btn.text = f"SOUND: {'ON 🔊' if self.sound_mgr.enabled else 'OFF 🔇'}"
        self.resume_btn.draw(screen)
        self.restart_pause_btn.draw(screen)
        self.sound_toggle_btn.draw(screen)
        self.menu_pause_btn.draw(screen)

    def draw_game_over(self, screen, score, distance, near_misses, chai_boosts):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        # E-Challan Official Notice Board
        cw, ch = 480, 480
        challan = pygame.Rect(self.width // 2 - cw // 2, self.height // 2 - ch // 2 - 20, cw, ch)
        pygame.draw.rect(screen, (248, 244, 235), challan, border_radius=10)
        pygame.draw.rect(screen, (180, 30, 30), challan, 4, border_radius=10)

        # Header Banner
        header_rect = pygame.Rect(challan.x, challan.y, cw, 58)
        pygame.draw.rect(screen, (180, 25, 25), header_rect, border_top_left_radius=10, border_top_right_radius=10)

        t_head = self.font_large.render("🚨 TRAFFIC POLICE E-CHALLAN 🚨", True, (255, 255, 255))
        t_sub = self.font_tiny.render("GOVERNMENT OF DESI STREETS • e-Challan Dept.", True, (255, 220, 220))
        screen.blit(t_head, (self.width // 2 - t_head.get_width() // 2, challan.y + 10))
        screen.blit(t_sub, (self.width // 2 - t_sub.get_width() // 2, challan.y + 36))

        # Violation Notice
        v_title = self.font_medium.render("VIOLATION: Reckless Arcade Driving & High Chaos!", True, (160, 20, 20))
        screen.blit(v_title, (challan.x + 24, challan.y + 75))

        # Stats Breakdown
        dist_km = distance / 1000.0
        rows = [
            ("Distance Covered:", f"{dist_km:.2f} KM"),
            ("Near Misses / Close Calls:", f"{near_misses}"),
            ("Chai Boosts Drank:", f"{chai_boosts}"),
            ("FINAL SCORE (Cash):", f"₹ {score:,}")
        ]

        for idx, (lbl, val) in enumerate(rows):
            ry = challan.y + 115 + (idx * 34)
            # Alternating subtle row tint
            if idx % 2 == 0:
                pygame.draw.rect(screen, (235, 230, 220), (challan.x + 18, ry - 4, cw - 36, 28), border_radius=4)

            t_l = self.font_medium.render(lbl, True, (40, 40, 40))
            is_final = (idx == len(rows) - 1)
            t_v = self.font_large.render(val, True, (180, 20, 20) if is_final else (10, 10, 10))
            screen.blit(t_l, (challan.x + 30, ry))
            screen.blit(t_v, (challan.right - 30 - t_v.get_width(), ry - (3 if is_final else 0)))

        # High Score Notice Stamp
        is_new_high = score > self.high_score
        if is_new_high:
            self.high_score = score
            stamp_surf = self.font_large.render("⭐ NEW HIGH SCORE RECORD! ⭐", True, (200, 140, 10))
            screen.blit(stamp_surf, (self.width // 2 - stamp_surf.get_width() // 2, challan.y + 265))
        else:
            hs_lbl = self.font_medium.render(f"Best Record: ₹ {self.high_score:,}", True, (100, 100, 100))
            screen.blit(hs_lbl, (self.width // 2 - hs_lbl.get_width() // 2, challan.y + 265))

        # Humorous Remark
        remarks = [
            "\"Aage dekh ke chalao bhai!\"",
            "\"Horn bajane se rasta nahi milta!\"",
            "\"Chai piyo, brake lagao!\"",
            "\"Kripya line mein chalein!\""
        ]
        rem = remarks[(score // 100) % len(remarks)]
        rem_surf = self.font_small.render(rem, True, (80, 80, 80))
        screen.blit(rem_surf, (self.width // 2 - rem_surf.get_width() // 2, challan.y + 300))

        # Action Buttons
        self.retry_btn.draw(screen)
        self.garage_btn.draw(screen)
