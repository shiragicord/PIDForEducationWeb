import pygame
import pygame_widgets
from pygame_widgets.slider import Slider
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
import math
import numpy as np
import sys
import os

# 画面のサイズ
WIDTH, HEIGHT = 1280, 720
AREA_SIZE = 50
AREA_POSITION = 30
FPS = 30
FUTURE_ARROW_LENGTH = 150
CONTROLER_POSITION_START = 960
SCALE_FACTOR_SPEED = 0.06
SCALE_FACTOR_GAIN = 0.02

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("./res/"), relative_path)

class PIDSprite(pygame.sprite.Sprite):
    def __init__(self, center=(640, 360)):
        super().__init__()
        self.original_image = pygame.image.load(resource_path("sprite.png"))
        self.image = self.original_image
        self.rect = self.image.get_rect(center=center)
        self.x_float = float(self.rect.centerx)
        self.y_float = float(self.rect.centerx)
        self.angle = 0

    def rotate(self, angle):
        self.angle = (self.angle + angle) % 360
        self.image = pygame.transform.rotate(self.original_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def move_forward(self, distance, angle):
        self.rotate(angle)
        radian_angle = math.radians(self.angle)
        dx = distance * math.cos(radian_angle)
        dy = distance * math.sin(radian_angle)
        self.x_float += dx
        self.y_float += dy
        self.rect.centerx = round(self.x_float)
        self.rect.centery = round(self.y_float)
    
    def set_position(self, x, y):
        self.x_float = x
        self.y_float = y
        self.rect.centerx = round(self.x_float)
        self.rect.centery = round(self.y_float)
    
    def update(self):
        flag_position_changed = False
        if self.rect.left < 0:
            self.rect.left = 0
            flag_position_changed = True
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
            flag_position_changed = True
        if self.rect.top < 0:
            self.rect.top = 0
            flag_position_changed = True
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
            flag_position_changed = True
        
        if flag_position_changed:
            self.x_float = self.rect.centerx
            self.y_float = self.rect.centery

class PIDScreen:
    def __init__(self):
        # 初期化
        pygame.init()
        pygame.display.set_caption("P制御シミュレーター")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(resource_path("NotoSansJP-Regular.ttf"), 36)  # フォントを作成
        self.font_small = pygame.font.Font(resource_path("NotoSansJP-Regular.ttf"), 14)  # フォントを作成
        self.pid_angle = 0.0

        self.init_sprite()
        self.prepare_screen()
        self.init_controler()

    def backup_screen(self):
        self.backscreen = self.screen.copy()

    def init_sprite(self):
        self.sprite = PIDSprite(center=(((WIDTH - CONTROLER_POSITION_START) // (-2)), HEIGHT // 2))
    
    def rotate_sprite(self, angle):
        self.sprite.rotate(angle)


    def prepare_screen(self):
        self.background_image = pygame.image.load(resource_path("background.png"))
        self.screen.blit(self.background_image, ((WIDTH - CONTROLER_POSITION_START) // (-2), 0))
        self.backup_screen()
        pygame.display.flip()
    
    def init_controler(self):
        self.slider_speed = Slider(self.screen, CONTROLER_POSITION_START + 30, 70, 260, 20, min=0, max=100, step=1, initial=0)
        self.slider_gain = Slider(self.screen, CONTROLER_POSITION_START + 30, 170, 260, 20, min=-20, max=20, step=0.1, initial=0)
    
    def refresh_screen(self):
        self.screen.blit(self.background_image, ((WIDTH - CONTROLER_POSITION_START) // (-2), 0))
        self.screen.blit(self.sprite.image, self.sprite.rect)
        self.draw_front_circle()
        self.draw_future_path()  # 未来の軌跡を描画
        self.draw_controler()
    
    def draw_controler(self):
        pygame.draw.rect(self.screen, (140, 140, 140), (CONTROLER_POSITION_START, 0, WIDTH - CONTROLER_POSITION_START, HEIGHT))
        text_surface = self.font.render(f"スピード: {self.slider_speed.getValue()}", True, (0, 0, 0))
        self.screen.blit(text_surface, (CONTROLER_POSITION_START + 30, 10))
        text_surface = self.font.render(f"Pゲイン: {self.slider_gain.getValue():.1f}", True, (0, 0, 0))
        self.screen.blit(text_surface, (CONTROLER_POSITION_START + 30, 100))

        brightness = self.get_brightness()
        sign = " " if self.pid_angle >= 0 else "-"
        text_lines = [
            ("反射光", " はん  しゃ  こう", f": {brightness}"),
            ("中間値との差", "ちゅうかん　ち　　　　　　  さ", f": {brightness - 50}"),
            ("移動の角度", "　い　どう　　　　かくど", f": {sign}{abs(self.pid_angle / SCALE_FACTOR_GAIN):.1f}")
        ]
        y_offset = 400
        for line, furigana, value in text_lines:
            text_surface = self.font.render(line + value, True, (0, 0, 0))
            self.screen.blit(text_surface, (CONTROLER_POSITION_START + 20, y_offset))
            furigana_surface = self.font_small.render(furigana, True, (0, 0, 0))
            self.screen.blit(furigana_surface, (CONTROLER_POSITION_START + 20, y_offset - 8))
            y_offset += self.font.get_linesize() + 10

    def draw_front_circle(self):
        front_x = self.sprite.rect.centerx + AREA_POSITION * math.cos(math.radians(self.sprite.angle))
        front_y = self.sprite.rect.centery + AREA_POSITION * math.sin(math.radians(self.sprite.angle))
        pygame.draw.circle(self.screen, (0, 0, 0), (int(front_x), int(front_y)), AREA_SIZE // 2, 2)
    
    def get_front_color(self):
        front_x = self.sprite.rect.centerx + AREA_POSITION * math.cos(math.radians(self.sprite.angle))
        front_y = self.sprite.rect.centery + AREA_POSITION * math.sin(math.radians(self.sprite.angle))
        front_rect = pygame.Rect(front_x - AREA_SIZE // 2, front_y - AREA_SIZE // 2, AREA_SIZE, AREA_SIZE)
        front_surface = self.backscreen.subsurface(front_rect)

        image_array = pygame.surfarray.array3d(front_surface)

        # **円形マスクを作成（円の外側を無視する）**
        mask = np.zeros((AREA_SIZE, AREA_SIZE), dtype=bool)
        cx, cy = AREA_SIZE // 2, AREA_SIZE // 2  # 円の中心
        for y in range(AREA_SIZE):
            for x in range(AREA_SIZE):
                if (x - cx) ** 2 + (y - cy) ** 2 <= (AREA_SIZE // 2) ** 2:
                    mask[y, x] = True

        # **マスクを適用して円形領域内のピクセルを取得**
        circle_pixels = image_array[mask]

        # **PIL を使って色情報を取得**
        unique_colors, counts = np.unique(circle_pixels.reshape(-1, 3), axis=0, return_counts=True)
        colors = list(zip([tuple(c) for c in unique_colors], counts))

        return colors
    
    def get_brightness(self):
        colors = self.get_front_color()
        total_brightness = 0
        total_count = 0

        for color, count in colors:
            r, g, b = color
            # 明るさを計算 (加重平均)
            brightness = 0.2126 * r + 0.7152 * g + 0.0722 * b
            total_brightness += brightness * count
            total_count += count

        # 平均明るさを計算
        average_brightness = total_brightness / total_count if total_count > 0 else 0

        # 明るさを0から100の範囲にスケール
        brightness_percentage = (average_brightness / 255) * 100
        return int(brightness_percentage)

    def draw_future_path(self):
        future_path = []
        temp_sprite = PIDSprite(center=self.sprite.rect.center)
        temp_sprite.angle = self.sprite.angle
        temp_sprite.x_float = self.sprite.x_float
        temp_sprite.y_float = self.sprite.y_float

        speed = self.slider_speed.getValue() * SCALE_FACTOR_SPEED / 3
        gain = self.slider_gain.getValue() * SCALE_FACTOR_GAIN
        brightness = self.get_brightness()
        error = 50 - brightness
        angle = error * gain
        for _ in range(FUTURE_ARROW_LENGTH):  # 未来の100ステップを予測
            temp_sprite.move_forward(speed, angle)
            future_path.append(temp_sprite.rect.center)

        if len(future_path) > 1:
            pygame.draw.lines(self.screen, (255, 0, 0), False, future_path, 2)
            # 矢印を描画
            arrow_tip = future_path[-1]
            arrow_angle = math.radians(temp_sprite.angle)
            arrow_size = 10
            arrow_points = [
                (arrow_tip[0] + arrow_size * math.cos(arrow_angle), arrow_tip[1] + arrow_size * math.sin(arrow_angle)),
                (arrow_tip[0] + arrow_size * math.cos(arrow_angle + 2.5), arrow_tip[1] + arrow_size * math.sin(arrow_angle + 2.5)),
                (arrow_tip[0] + arrow_size * math.cos(arrow_angle - 2.5), arrow_tip[1] + arrow_size * math.sin(arrow_angle - 2.5))
            ]
            pygame.draw.polygon(self.screen, (255, 0, 0), arrow_points)
        
    def on_mouse_click(self, x, y):
        if x <= CONTROLER_POSITION_START:
            # マウスクリック位置にスプライトを移動
            self.sprite.set_position(x, y)
    
    def on_key_down(self, key):
        if key == pygame.K_LEFT:
            self.sprite.rotate(-10)
        elif key == pygame.K_RIGHT:
            self.sprite.rotate(10)
    
    def loop(self):
        running = True
        while running:
            self.sprite.update()  # スプライトの更新
            self.refresh_screen()

            # P制御
            speed = self.slider_speed.getValue() * SCALE_FACTOR_SPEED
            gain = self.slider_gain.getValue() * SCALE_FACTOR_GAIN
            brightness = self.get_brightness()
            error = 50 - brightness
            self.pid_angle = error * gain
            self.sprite.move_forward(speed, self.pid_angle)

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.on_mouse_click(event.pos[0], event.pos[1])
                elif event.type == pygame.KEYDOWN:
                    self.on_key_down(event.key)
            
            pygame_widgets.update(events)
            pygame.display.update()
            self.clock.tick(FPS) 
    
    def destroy(self):
        pygame.quit()

        
def main():
    screen = PIDScreen()
    screen.loop()

if __name__ == "__main__":
    main()