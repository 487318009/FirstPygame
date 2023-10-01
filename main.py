# 导入必要的模块
import random
import pygame
from pygame.locals import *
from sys import exit

# 初始化 Pygame
pygame.init()

# 设置窗口大小和标题
screen = pygame.display.set_mode((800, 400))
pygame.display.set_caption('Pixel Runner')

# 创建时钟对象来控制帧率
clock = pygame.time.Clock()

# 设置文本文字的大小和字体样式
font = pygame.font.Font(None, 36)

# 游戏状态常量
GAME_OVER = 0
GAME_ACTIVE = 1

# 定义游戏状态
game_state = GAME_OVER

# 加载背景音乐
pygame.mixer.music.load('audio/music.wav')
pygame.mixer.music.set_volume(0.5)  # 设置音乐音量（可选）
# 播放背景音乐（-1 表示无限循环播放）
pygame.mixer.music.play(-1)

# 定义玩家类
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # 加载玩家的动画帧和跳跃图片
        self.player_walk_1 = pygame.image.load('graphics/Player/player_walk_1.png').convert_alpha()
        self.player_walk_2 = pygame.image.load('graphics/Player/player_walk_2.png').convert_alpha()
        self.player_walk = [self.player_walk_1, self.player_walk_2]
        self.player_index = 0
        self.player_jump = pygame.image.load('graphics/Player/jump.png').convert_alpha()
        self.image = self.player_walk[self.player_index]
        self.rect = self.image.get_rect(midbottom=(200, 300))
        self.gravity = 0
        # 加载跳跃音效并设置音量
        self.jump_sound = pygame.mixer.Sound('audio/jump.mp3')
        self.jump_sound.set_volume(0.5)

    def player_input(self):
        # 检测空格键是否按下以触发跳跃
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and self.rect.bottom >= 300:
            self.gravity = -20
            self.jump_sound.play()

    def apply_gravity(self):
        # 模拟重力作用，使玩家下落
        self.gravity += 1
        self.rect.y += self.gravity
        if self.rect.bottom >= 300:
            self.rect.bottom = 300

    def animation_state(self):
        if self.rect.bottom < 300:
            # 当玩家在空中时显示跳跃图片
            self.image = self.player_jump
        else:
            # 播放玩家行走的动画
            self.player_index += 0.1
            if self.player_index >= len(self.player_walk):
                self.player_index = 0
            self.image = self.player_walk[int(self.player_index)]

    def update(self):
        # 更新玩家状态
        self.player_input()
        self.apply_gravity()
        self.animation_state()

# 定义障碍物类
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, type):
        super().__init__()
        if type == 'fly':
            # 如果是飞行障碍物，加载飞行动画帧
            self.frames = [
                pygame.image.load('graphics/Fly/Fly1.png').convert_alpha(),
                pygame.image.load('graphics/Fly/Fly2.png').convert_alpha()
            ]
            y_pos = 210
        else:
            # 如果是蜗牛障碍物，加载蜗牛动画帧
            self.frames = [
                pygame.image.load('graphics/snail/snail1.png').convert_alpha(),
                pygame.image.load('graphics/snail/snail2.png').convert_alpha()
            ]
            y_pos = 300
        self.animation_index = 0
        self.image = self.frames[self.animation_index]
        self.rect = self.image.get_rect(midbottom=(random.randint(800, 1000), y_pos))

    def animation_state(self):
        # 更新障碍物动画状态
        self.animation_index += 0.1
        if self.animation_index >= len(self.frames):
            self.animation_index = 0
        self.image = self.frames[int(self.animation_index)]

    def update(self):
        # 更新障碍物状态，使其向左移动
        self.animation_state()
        self.rect.x -= 6
        if self.rect.right < 0:
            self.kill()

# 显示游戏分数
def display_score(score):
    score_surf = font.render(f'Score: {score}', True, (64, 64, 64))
    score_rect = score_surf.get_rect(center=(400, 50))
    screen.blit(score_surf, score_rect)

# 创建玩家精灵组
player = pygame.sprite.GroupSingle()
player.add(Player())

# 创建障碍物精灵组
obstacles = pygame.sprite.Group()

# 加载背景和地面图片
sky_surface = pygame.image.load('graphics/Sky.png').convert()
ground_surface = pygame.image.load('graphics/ground.png').convert()

# 游戏主循环
score = 0
obstacle_spawn_counter = 0
start_time = pygame.time.get_ticks()

def calculate_score():
    if game_state == GAME_ACTIVE:
        # 计算并返回分数，基于游戏时间
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - start_time) // 1000  # 将毫秒转换为秒
        return score + elapsed_time
    else:
        return score  # 返回已经计算的分数

def set_final_score():
    global score
    score = calculate_score()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if game_state == GAME_ACTIVE:
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and player.sprite.rect.bottom >= 300:
            player.sprite.gravity = -20
            player.sprite.jump_sound.play()

        # 控制障碍物生成速率
        obstacle_spawn_counter += 1
        if obstacle_spawn_counter > 60:
            obstacles.add(Obstacle(random.choice(['fly', 'snail'])))
            obstacle_spawn_counter = 0

        for obstacle in obstacles:
            if pygame.sprite.spritecollide(player.sprite, obstacles, False):
                game_state = GAME_OVER

        screen.blit(sky_surface, (0, 0))
        screen.blit(ground_surface, (0, 300))
        player.update()
        obstacles.update()
        player.draw(screen)
        obstacles.draw(screen)

        # 删除越界的障碍物并增加分数
        for obstacle in obstacles:
            if obstacle.rect.right < 0:
                obstacle.kill()
                score += 1

        # 根据游戏时间增加分数
        current_time = (pygame.time.get_ticks() - start_time) // 1000
        display_score(score + current_time)

    elif game_state == GAME_OVER:
        # 游戏结束状态下的逻辑
        screen.fill((255, 0, 0))
        game_over_text = font.render("Game Over", True, (255, 255, 255))
        game_over_rect = game_over_text.get_rect(center=(400, 200))
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(400, 250))
        screen.blit(game_over_text, game_over_rect)
        screen.blit(score_text, score_rect)
        set_final_score()  # 更新最终得分
        keys = pygame.key.get_pressed()
        if keys[K_SPACE]:
            # 如果玩家按下空格键，重置游戏状态
            game_state = GAME_ACTIVE
            player.sprite.rect.midbottom = (200, 300)
            player.sprite.gravity = 0
            obstacles.empty()
            start_time = pygame.time.get_ticks()  # 重置游戏时间
            set_final_score()  # 更新分数
    pygame.display.update()
    clock.tick(60)
