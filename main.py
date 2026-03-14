import pygame
import sys
import os
import time
import json
import subprocess

# --- GLOBAL CONFIGURATION ---
WIDTH, HEIGHT = 1280, 720
DEBUG_MODE = True # Set to false on TrimUI

DEFAULT_THEME = {
    "bg": [10, 10, 12],
    "header": [20, 15, 25],
    "card": [30, 25, 35],
    "accent": [255, 0, 255],
    "white": [255, 245, 255],
    "text_dim": [190, 170, 190]
}

class AnyxCC:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Anyx CC")
        
        self.colors = self.load_theme()
        
        # --- CUSTOM FONT LOADING ---
        font_path = "settings/wqy-microhei.ttf"
        if os.path.exists(font_path):
            self.f_logo = pygame.font.Font(font_path, 38)
            self.f_tab = pygame.font.Font(font_path, 26)
            self.f_btn = pygame.font.Font(font_path, 36)
            self.f_desc = pygame.font.Font(font_path, 20)
        else:
            self.f_logo = pygame.font.SysFont("sans-serif", 38, bold=True)
            self.f_tab = pygame.font.SysFont("sans-serif", 26, bold=True)
            self.f_btn = pygame.font.SysFont("sans-serif", 36, bold=True)
            self.f_desc = pygame.font.SysFont("sans-serif", 20)
        
        self.cat_idx = 0
        self.item_idx = 0
        
        self.scroll_y = 0
        self.target_scroll_y = 0
        self.transition_x = 0  
        
        self.show_popup = False
        self.running = True
        self.pending_exit = False

        # --- DATA & FUNCTIONS ---
        self.menu_data = {
            "SYSTEM": [
                {
                    "type": "cyclic", "name": "CPU Mode", "desc": "Adjust CPU scaling governor for performance or battery.",
                    "states": [
                        {"label": "Balanced", "cmd": "echo schedutil > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"},
                        {"label": "Performance", "cmd": "echo performance > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"},
                        {"label": "Power Save", "cmd": "echo powersave > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor"}
                    ], "current": 0
                },
                {
                    "type": "cyclic", "name": "ZRAM", "desc": "Toggle ZRAM for better RAM effectiveness.",
                    "states": [
                        {"label": "OFF", "cmd": "/mnt/SDCARD/Apps/AnyxCC/scripts/zram_off.sh"}, 
                        {"label": "ON", "cmd": "/mnt/SDCARD/Apps/AnyxCC/scripts/zram_on.sh"}  
                    ], "current": 0
                },
                {"type": "action", "name": "Flush System Cache", "desc": "Free up unused RAM memory.", "cmd": "sync; echo 3 > /proc/sys/vm/drop_caches"}
            ],
            "TOOLS": [
                {"type": "action", "name": "Fix SD Permissions", "desc": "Repair file access rights on the SD card.", "cmd": "chmod -R 777 /mnt/SDCARD"},
                {"type": "action", "name": "Clean macOS Junk", "desc": "Remove hidden ._* and .DS_Store files.", "cmd": "find /mnt/SDCARD -name '._*' -delete"}
            ],
            "SETTINGS": [
                {
                    "type": "cyclic", "name": "Background Music", "desc": "Toggle background music.",
                    "states": [
                        {"label": "ON", "cmd": "MUSIC_ON"},
                        {"label": "OFF", "cmd": "MUSIC_OFF"}
                    ], "current": 0
                },
                {"type": "action", "name": "Reload Theme", "desc": "Apply changes from settings/theme.json.", "cmd": "RELOAD_THEME"},
                {"type": "action", "name": "Update Anyx CC", "desc": "Download the latest version from GitHub.", "cmd": "/mnt/SDCARD/Apps/AnyxCC/scripts/update.sh"},
                {"type": "action", "name": "Reboot System", "desc": "Perform a complete console restart.", "cmd": "reboot"}
            ],
            "CREDITS": [
                {"type": "info", "name": "Anyx Control Center", "desc": "Created by altuux.", "cmd": "NONE"},
                {"type": "info", "name": "Version 0.2 beta", "desc": "Beta build for the TrimUI Smart Pro.", "cmd": "NONE"}
            ]
        }
        self.categories = list(self.menu_data.keys())

        try:
            pygame.mixer.music.load("sound/bg-music.mp3")
            pygame.mixer.music.set_volume(0.15)
            pygame.mixer.music.play(-1)
        except: 
            self.menu_data["SETTINGS"][0]["current"] = 1 

    def load_theme(self):
        if os.path.exists("settings/theme.json"):
            try:
                with open("settings/theme.json", "r") as f:
                    return json.load(f)
            except: pass
        return DEFAULT_THEME

    def get_battery(self):
        try:
            with open("/sys/class/power_supply/battery/capacity", "r") as f:
                return f.read().strip() + "%"
        except: return "100%"

    def draw_loading(self):
        self.screen.fill(self.colors["bg"])
        txt = self.f_btn.render("EXECUTING...", True, self.colors["accent"])
        self.screen.blit(txt, (WIDTH//2 - txt.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        time.sleep(0.4)

    def execute(self, cmd, is_cyclic=False):
        if cmd == "RELOAD_THEME":
            self.colors = self.load_theme()
        elif cmd == "MUSIC_ON":
            pygame.mixer.music.unpause()
            if not pygame.mixer.music.get_busy(): 
                 try: pygame.mixer.music.play(-1)
                 except: pass
        elif cmd == "MUSIC_OFF":
            pygame.mixer.music.pause()
        elif "update.sh" in cmd:
            self.draw_loading()
            if DEBUG_MODE:
                print(f"[DEBUG EXEC]: {cmd}")
            else:
                os.system(cmd)
            self.running = False
        elif cmd != "NONE":
            if not is_cyclic:
                self.draw_loading()
            if DEBUG_MODE:
                print(f"[DEBUG EXEC]: {cmd}")
            else:
                subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def update_scroll(self):
        item_h = 135
        header_h = 130
        bottom_margin = 20
        item_absolute_y = header_h + (self.item_idx * item_h)
        
        if item_absolute_y < self.target_scroll_y + header_h:
            self.target_scroll_y = item_absolute_y - header_h
        elif item_absolute_y + 115 > self.target_scroll_y + HEIGHT - bottom_margin:
            self.target_scroll_y = (item_absolute_y + 115) - (HEIGHT - bottom_margin)

    def draw(self):
        self.screen.fill(self.colors["bg"])
        
        if abs(self.transition_x) > 0.5:
            self.transition_x += (0 - self.transition_x) * 0.35
        else:
            self.transition_x = 0
            
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * 0.35
        
        # --- 1. Draw items ---
        items = self.menu_data[self.categories[self.cat_idx]]

        for i, item in enumerate(items):
            y_pos = 130 + (i * 135) - self.scroll_y
            x_pos = 80 + self.transition_x
            
            if -150 < y_pos < HEIGHT:
                rect = pygame.Rect(x_pos, y_pos, 1120, 115)
                is_sel = (i == self.item_idx)
                
                if is_sel:
                    bg_col = [min(255, c + 15) for c in self.colors["card"]]
                    pygame.draw.rect(self.screen, bg_col, rect, border_radius=12)
                    pygame.draw.rect(self.screen, self.colors["accent"], rect, 4, border_radius=12)
                else:
                    pygame.draw.rect(self.screen, self.colors["card"], rect, border_radius=12)

                self.screen.blit(self.f_btn.render(item["name"], True, self.colors["white"]), (x_pos + 40, y_pos + 25))
                self.screen.blit(self.f_desc.render(item["desc"], True, self.colors["text_dim"]), (x_pos + 40, y_pos + 68))

                if item["type"] == "cyclic":
                    state_label = item["states"][item["current"]]["label"]
                    state_color = self.colors["accent"] if is_sel else self.colors["text_dim"]
                    state_surf = self.f_btn.render(f"<  {state_label}  >", True, state_color)
                    
                    right_align_x = x_pos + 1120 - state_surf.get_width() - 40
                    self.screen.blit(state_surf, (right_align_x, y_pos + 25))

        # --- 2. Header ---
        pygame.draw.rect(self.screen, self.colors["header"], (0, 0, WIDTH, 100))
        
        self.screen.blit(self.f_logo.render("ANYX CC", True, self.colors["accent"]), (40, 30))
        bat_t = self.f_tab.render(f"BAT: {self.get_battery()}", True, self.colors["white"])
        self.screen.blit(bat_t, (WIDTH - bat_t.get_width() - 40, 35))

        tab_gap = 60
        total_tabs_width = sum([self.f_tab.size(c)[0] for c in self.categories]) + (len(self.categories) - 1) * tab_gap
        current_x = (WIDTH - total_tabs_width) // 2
        
        for i, cat in enumerate(self.categories):
            is_sel = (i == self.cat_idx)
            color = self.colors["white"] if is_sel else self.colors["text_dim"]
            txt = self.f_tab.render(cat, True, color)
            self.screen.blit(txt, (current_x, 35))
            
            if is_sel:
                pygame.draw.rect(self.screen, self.colors["accent"], (current_x, 80, txt.get_width(), 4))
            
            current_x += txt.get_width() + tab_gap

        # --- 3. Popup overlay ---
        if self.show_popup:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            
            p_rect = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 120, 500, 240)
            pygame.draw.rect(self.screen, self.colors["card"], p_rect, border_radius=20)
            pygame.draw.rect(self.screen, self.colors["accent"], p_rect, 3, border_radius=20)
            
            msg = self.f_btn.render("Confirm Action?", True, self.colors["white"])
            self.screen.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2 - 60))
            
            hint = self.f_btn.render("(A) YES   (B) NO", True, self.colors["accent"])
            self.screen.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT//2 + 20))

    def main_loop(self):
        clock = pygame.time.Clock()
        needs_redraw = True

        while self.running:
            is_animating = (abs(self.scroll_y - self.target_scroll_y) > 0.5) or (abs(self.transition_x) > 0.5)
            
            if is_animating:
                needs_redraw = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    self.running = False
                
                if event.type == pygame.KEYDOWN:
                    needs_redraw = True 
                    current_cat_name = self.categories[self.cat_idx]
                    current_cat_items = self.menu_data[current_cat_name]
                    items_in_cat = len(current_cat_items)
                    
                    if self.show_popup:
                        if event.key == pygame.K_RETURN:
                            if self.pending_exit:
                                self.running = False
                            else:
                                selected_item = current_cat_items[self.item_idx]
                                self.execute(selected_item.get("cmd", "NONE"))
                            self.show_popup = False
                            self.pending_exit = False
                                
                        elif event.key == pygame.K_ESCAPE:
                            self.show_popup = False
                            self.pending_exit = False
                        continue 

                    if event.key == pygame.K_UP: 
                        self.item_idx = (self.item_idx - 1) % items_in_cat
                        self.update_scroll()
                            
                    elif event.key == pygame.K_DOWN: 
                        self.item_idx = (self.item_idx + 1) % items_in_cat
                        self.update_scroll()
                        
                    elif event.key in [pygame.K_q, pygame.K_LEFT]: 
                        self.cat_idx = (self.cat_idx - 1) % len(self.categories)
                        self.item_idx = 0
                        self.target_scroll_y = 0
                        self.transition_x = -WIDTH 
                        
                    elif event.key in [pygame.K_e, pygame.K_RIGHT]: 
                        self.cat_idx = (self.cat_idx + 1) % len(self.categories)
                        self.item_idx = 0 
                        self.target_scroll_y = 0
                        self.transition_x = WIDTH 
                        
                    elif event.key == pygame.K_RETURN:
                        selected_item = current_cat_items[self.item_idx]
                        if selected_item["type"] == "cyclic":
                            selected_item["current"] = (selected_item["current"] + 1) % len(selected_item["states"])
                            cmd = selected_item["states"][selected_item["current"]]["cmd"]
                            self.execute(cmd, is_cyclic=True) 
                            
                        elif selected_item["type"] == "action":
                            self.show_popup = True
                            self.pending_exit = False
                            
                    elif event.key == pygame.K_ESCAPE:
                        self.show_popup = True
                        self.pending_exit = True

            if needs_redraw:
                self.draw()
                pygame.display.flip()
                if not is_animating:
                    needs_redraw = False

            clock.tick(60)

if __name__ == "__main__":
    AnyxCC().main_loop()