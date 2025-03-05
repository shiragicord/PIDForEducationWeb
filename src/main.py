import pygame
from PIL import Image
import math
import numpy as np
import flet as ft

# 画面のサイズ
WIDTH, HEIGHT = 1280, 720
AREA_SIZE = 50
AREA_POSITION = 30
FPS = 30
FUTURE_ARROW_LENGTH = 150

class PIDSprite(pygame.sprite.Sprite):
    def __init__(self, center=(640, 360)):
        super().__init__()
        self.original_image = pygame.image.load("res/sprite.png")
        self.image = self.original_image
        self.rect = self.image.get_rect(center=center)
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
        self.rect.x += dx
        self.rect.y += dy
    
    def update(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT

class PIDScreen:
    def __init__(self):
        # 初期化
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("C:\Windows\Fonts\meiryo.ttc", 36)  # フォントを作成

        self.init_sprite()
        self.prepare_screen()

    def backup_screen(self):
        self.backscreen = self.screen.copy()

    def init_sprite(self, center=(640, 360)):
        self.sprite = PIDSprite(center=center)
    
    def rotate_sprite(self, angle):
        self.sprite.rotate(angle)


    def prepare_screen(self):
        self.background_image = pygame.image.load("res/background.png")
        self.screen.blit(self.background_image, (0, 0))
        self.backup_screen()
        pygame.display.flip()
    
    def refresh_screen(self):
        self.screen.blit(self.background_image, (0, 0))
        self.screen.blit(self.sprite.image, self.sprite.rect)
        self.draw_front_circle()
        self.draw_brightness()
        self.draw_future_path()  # 未来の軌跡を描画
        pygame.display.flip()

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
    
    def draw_brightness(self):
        brightness = self.get_brightness()
        text_surface = self.font.render(f"反射光: {brightness}", True, (0, 0, 0))
        self.screen.blit(text_surface, (10, 10))

    def draw_future_path(self):
        future_path = []
        temp_sprite = PIDSprite(center=self.sprite.rect.center)
        temp_sprite.angle = self.sprite.angle

        brightness = self.get_brightness()
        error = 50 - brightness
        angle = error * 0.1
        for _ in range(FUTURE_ARROW_LENGTH):  # 未来の100ステップを予測
            temp_sprite.move_forward(1, angle)
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
    
    def loop(self):
        running = True
        while running:
            self.sprite.update()  # スプライトの更新
            self.refresh_screen()

            # P制御
            brightness = self.get_brightness()
            error = 50 - brightness
            angle = error * 0.1
            self.sprite.move_forward(2, angle)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # マウスクリック位置にスプライトを移動
                    mouse_x, mouse_y = event.pos
                    self.sprite.rect.center = (mouse_x, mouse_y)
            
            pygame.display.update()
            self.clock.tick(FPS) 
    
    def destroy(self):
        pygame.quit()

        
def main(page: ft.Page):
    global screen, debug_forward_angle
    screen = PIDScreen()
    debug_forward_angle = 0

    page.window.width = 300
    page.window.height = 300

    def on_slider_change(event: ft.ControlEvent):
        global debug_forward_angle
        debug_forward_angle = event.control.value

    slider = ft.Slider(min=-100, max=100, divisions=200, label="{value}")
    slider.value = 0
    slider.on_change = on_slider_change
    page.add(
        ft.Column([
            ft.Switch(label="スイッチ", ),
        ])
        )

    screen.loop()

if __name__ == "__main__":
    ft.app(target=main)