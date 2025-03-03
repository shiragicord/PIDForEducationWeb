import pygame
from PIL import Image
import math
import numpy as np

# 画面のサイズ
WIDTH, HEIGHT = 1280, 720
AREA_SIZE = 100

class PIDScreen:
    def __init__(self):
        # 初期化
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        self.init_sprite()
        self.prepare_screen()
        self.update_screen()

    def init_sprite(self, center=(640, 360)):
        # スプライトの読み込み
        self.sprite = pygame.image.load("res/sprite.png")  # 任意の画像
        self.sprite_rect = self.sprite.get_rect(center=center)  # 画面中央に配置
        self.angle = 0
    
    def rotate_sprite(self, angle):
        self.angle = angle
        self.sprite = pygame.transform.rotate(self.sprite, -angle)
        self.sprite_rect = self.sprite.get_rect(center=self.sprite_rect.center)

        self.update_screen()
    
    def draw_sprite(self):
        self.screen.blit(self.sprite, self.sprite_rect)

    def prepare_screen(self):
        self.screen.fill((255, 255, 255))
        self.draw_front_circle()
        pygame.display.flip()

    def update_screen(self):
        self.draw_sprite()
        pygame.display.flip()
    
    def fullupdate_screen(self):
        self.prepare_screen()
        self.update_screen()

    def draw_front_circle(self):
        front_x = self.sprite_rect.centerx + (self.sprite_rect.width // 2) * math.cos(math.radians(self.angle))
        front_y = self.sprite_rect.centery - (self.sprite_rect.width // 2) * math.sin(math.radians(self.angle))
        pygame.draw.circle(self.screen, (0, 0, 0), (int(front_x), int(front_y)), AREA_SIZE // 2, 2)
    
    def get_front_color(self):
        self.prepare_screen()

        front_x = self.sprite_rect.centerx + (self.sprite_rect.width // 2) * math.cos(math.radians(self.angle))
        front_y = self.sprite_rect.centery - (self.sprite_rect.width // 2) * math.sin(math.radians(self.angle))
        front_rect = pygame.Rect(front_x - AREA_SIZE // 2, front_y - AREA_SIZE // 2, AREA_SIZE, AREA_SIZE)
        front_surface = self.screen.subsurface(front_rect)

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

        # 原状復帰
        self.update_screen()

        return colors
    
    def loop(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
    
    def destroy(self):
        pygame.quit()

def main():
    screen = PIDScreen()
    screen.rotate_sprite(45)
    screen.fullupdate_screen()
    screen.loop()

if __name__ == "__main__":
    main()