import pygame
import numpy as np

# 初始化 Pygame 和隐藏窗口
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)  # 关键步骤！

# 加载灰度图并确保是 RGBA 格式
gray_image = pygame.image.load("assets/hit.png").convert_alpha()

# 目标颜色（红色）
color = (254, 255, 169)

# 创建着色层
colored_layer = pygame.Surface(gray_image.get_size(), pygame.SRCALPHA)
colored_layer.fill(color)

# 混合灰度图和颜色（乘法混合）
final_image = gray_image.copy()
final_image.blit(colored_layer, (0, 0), special_flags=pygame.BLEND_MULT)

# 正式显示（可选）
pygame.display.quit()  # 关闭隐藏窗口
screen = pygame.display.set_mode((800, 600))
screen.blit(final_image, (100, 100))
pygame.display.flip()

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
pygame.quit()