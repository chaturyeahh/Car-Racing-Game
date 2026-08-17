import math
import struct
import pygame

class SoundManager:
    def __init__(self):
        self.enabled = True
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.sounds = self._generate_sounds()
        except Exception as e:
            print(f"[Audio] Sound disabled or unavailable: {e}")
            self.enabled = False
            self.sounds = {}

    def _create_pcm_sound(self, generator_func, duration, sample_rate=22050, volume=0.8):
        num_samples = int(sample_rate * duration)
        samples = []
        for i in range(num_samples):
            t = i / sample_rate
            val = generator_func(t, duration)
            val = max(-1.0, min(1.0, val)) * volume
            sample_val = int(val * 32767)
            # Stereo (left, right)
            samples.append(struct.pack('<hh', sample_val, sample_val))
        raw_data = b''.join(samples)
        return pygame.mixer.Sound(buffer=raw_data)

    def _generate_sounds(self):
        sounds = {}

        # 1. Indian Dual-Tone Horn ("Pee-Poo")
        def horn_wave(t, dur):
            freq = 480 if t < dur * 0.45 else 580
            # Add subtle harmonic overtone for brassy horn timbre
            wave = 0.65 * math.sin(2 * math.pi * freq * t) + 0.35 * math.sin(2 * math.pi * freq * 2 * t)
            # Envelope
            env = 1.0 - math.exp(-t * 80)
            if t > dur - 0.05:
                env *= max(0.0, (dur - t) / 0.05)
            return wave * env

        # 2. Desi Highway Truck Air Horn ("BHOOO-HOOO")
        def truck_horn_wave(t, dur):
            freq = 220 if t < dur * 0.5 else 260
            wave = (0.5 * math.sin(2 * math.pi * freq * t) +
                    0.3 * math.sin(2 * math.pi * (freq * 1.5) * t) +
                    0.2 * math.sin(2 * math.pi * (freq * 2) * t))
            env = 1.0 if t < dur - 0.08 else max(0.0, (dur - t) / 0.08)
            return wave * env

        # 3. Near-Miss / Close Call Chime
        def chime_wave(t, dur):
            freq = 600 + 400 * (t / dur)
            wave = math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * freq * 1.5 * t)
            env = math.exp(-t * 9)
            return wave * env

        # 4. Chai Boost / Turbo Whoosh
        def boost_wave(t, dur):
            freq = 300 + 500 * (t / dur)
            noise = (math.sin(t * 8000) * 0.2)
            wave = (math.sin(2 * math.pi * freq * t) * 0.8 + noise)
            env = math.sin(math.pi * (t / dur))
            return wave * env

        # 5. Coin Collect ("Ting!")
        def coin_wave(t, dur):
            freq = 987.77 if t < 0.08 else 1318.51  # B5 -> E6
            wave = math.sin(2 * math.pi * freq * t) + 0.2 * math.sin(2 * math.pi * freq * 2 * t)
            env = math.exp(-t * 14)
            return wave * env

        # 6. Tire Screech
        def screech_wave(t, dur):
            # FM synthesis for squeal
            mod = math.sin(2 * math.pi * 70 * t) * 400
            carrier = math.sin(2 * math.pi * (900 + mod) * t)
            noise = (math.sin(t * 12345) % 1.0 - 0.5) * 0.3
            env = math.sin(math.pi * (t / dur))
            return (carrier * 0.7 + noise) * env

        # 7. Crash Thud
        def crash_wave(t, dur):
            noise = (math.sin(t * 9973 * (1 + t * 50)) % 1.0 - 0.5) * 2.0
            low_thump = math.sin(2 * math.pi * max(40, 150 - t * 400) * t)
            wave = 0.6 * noise + 0.4 * low_thump
            env = math.exp(-t * 8)
            return wave * env

        sounds['horn'] = self._create_pcm_sound(horn_wave, 0.32, volume=0.7)
        sounds['truck_horn'] = self._create_pcm_sound(truck_horn_wave, 0.5, volume=0.75)
        sounds['near_miss'] = self._create_pcm_sound(chime_wave, 0.28, volume=0.8)
        sounds['boost'] = self._create_pcm_sound(boost_wave, 0.45, volume=0.7)
        sounds['coin'] = self._create_pcm_sound(coin_wave, 0.25, volume=0.75)
        sounds['screech'] = self._create_pcm_sound(screech_wave, 0.35, volume=0.6)
        sounds['crash'] = self._create_pcm_sound(crash_wave, 0.6, volume=0.9)

        return sounds

    def play(self, sound_name):
        if not self.enabled:
            return
        snd = self.sounds.get(sound_name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def toggle_sound(self):
        self.enabled = not self.enabled
        return self.enabled
