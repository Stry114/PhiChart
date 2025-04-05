import pygame
import random
import time
import math
import wave

import cv2
import numpy as np

import analyzer
import chart
import autoMatch
import traceback


timerClock = time.time()
def mytimer(msg: str):
    global timerClock
    current = time.time()
    cost = current - timerClock
    timerClock = current
    # print(msg, cost*1000, "ms")
    return cost

def get_wav_duration(wav_path):
    with wave.open(wav_path, 'rb') as wav_file:
        # 获取帧数 (nframes) 和帧率 (framerate)
        frames = wav_file.getnframes()
        rate = wav_file.getframerate()

        # 计算时长（秒）
        duration = frames / float(rate)
        return duration


# 添加高斯模糊
def cv2_blur(surface, radius: float):
    # 确保半径是正奇数
    radius = int(max(1, radius))
    if radius % 2 == 0:
        radius += 1
    # 将Pygame Surface转换为OpenCV格式
    rgb_array = pygame.surfarray.array3d(surface)
    # 应用高斯模糊
    blurred = cv2.GaussianBlur(rgb_array, (radius, radius), 0)
    # 转换回Pygame Surface
    return pygame.surfarray.make_surface(blurred)


# 调整图像亮度
def apply_darken(surface, factor=0.5):
    dark = surface.copy()
    dark.fill((factor * 255, factor * 255, factor * 255), special_flags=pygame.BLEND_MULT)
    return dark


def colorize_grayscale(surface, color):
    """将灰度图着色为指定颜色"""
    colored = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    for x in range(surface.get_width()):
        for y in range(surface.get_height()):
            gray = surface.get_at((x, y))[0]  # 取 R 值（灰度图 R=G=B）
            if gray > 0:  # 如果不是纯黑
                r = min(255, (gray * color[0]) // 255)
                g = min(255, (gray * color[1]) // 255)
                b = min(255, (gray * color[2]) // 255)
                colored.set_at((x, y), (r, g, b, gray))  # 保留 Alpha 通道
    return colored


def colorize_grayscale(surface, color):

    colored_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    if len(color) == 3:
        color = (*color, 255)

    colored_surface.fill(color)
    result = surface.copy()
    result.blit(colored_surface, (0, 0), special_flags=pygame.BLEND_MULT)
    return result


def draw_text(surface, text, font, color, pos, align='left', aa=True, bg=None):
    """
    在指定位置绘制对齐文本

    参数:
        surface - 要绘制到的目标Surface
        text - 要渲染的文本内容
        font - 使用的字体对象
        color - 文本颜色(RGB或RGBA)
        pos - 文本位置(x,y)，根据对齐方式解释
        align - 对齐方式('left', 'center', 'right')
        aa - 是否使用抗锯齿
        bg - 背景色(可选，None表示透明背景)

    返回:
        实际渲染文本的矩形区域
    """
    # 渲染文本
    text_surface = font.render(text, aa, color, bg)
    text_rect = text_surface.get_rect()

    # 根据对齐方式调整位置
    x, y = pos
    if align == 'N':
        text_rect.midtop = (x, y)
    elif align == "W":
        text_rect.midleft = (x, y)
    elif align == "E":
        text_rect.midright = (x, y)
    elif align == "S":
        text_rect.midbottom = (x, y)
    elif align == "NW":
        text_rect.topleft = (x, y)
    elif align == "NE":
        text_rect.topright = (x, y)
    elif align == "SE":
        text_rect.bottomright = (x, y)
    elif align == "SW":
        text_rect.bottomleft = (x, y)
    elif align == "C":
        text_rect.center = (x, y)
    else:
        raise ValueError("align参数错误.")

    # 绘制文本
    surface.blit(text_surface, text_rect)

    return text_rect


class PreRendCache:
    def __init__(self, noteWidth: int, hitWidth: int):
        self.noteWidth: int = noteWidth
        self.preRendHit: list[pygame.Surface] = []
        self.preRendTap: dict[int: pygame.Surface] = {}
        self.preRendDrag: dict[int: pygame.Surface] = {}
        self.preRendFlick: dict[int: pygame.Surface] = {}
        self.preRendTapHL: dict[int: pygame.Surface] = {}
        self.preRendDragHL: dict[int: pygame.Surface] = {}
        self.preRendFlickHL: dict[int: pygame.Surface] = {}

        # 三键
        self.tapOriginalImage = pygame.image.load("assets/Tap.png").convert_alpha()
        self.dragOriginalImage = pygame.image.load("assets/Drag.png").convert_alpha()
        self.flickOriginalImage = pygame.image.load("assets/Flick.png").convert_alpha()
        self.tapHLOriginalImage = pygame.image.load("assets/TapHL.png").convert_alpha()
        self.dragHLOriginalImage = pygame.image.load("assets/DragHL.png").convert_alpha()
        self.flickHLOriginalImage = pygame.image.load("assets/FlickHL.png").convert_alpha()

        self.hhh = 50  # height of hold head
        self.holdOriginalImage = pygame.image.load("assets/Hold.png").convert_alpha()
        topRect = pygame.Rect(0, 0, self.holdOriginalImage.get_width(), self.hhh)
        self.holdTopImage = self.holdOriginalImage.subsurface(topRect)
        self.holdTopImage = pygame.transform.scale(self.holdTopImage, (self.noteWidth, self.noteWidth*(self.hhh/self.holdTopImage.get_width())))
        bottomRect = pygame.Rect(0, self.holdOriginalImage.get_height()-self.hhh, self.holdOriginalImage.get_width(), self.hhh)
        self.holdBottomImage = self.holdOriginalImage.subsurface(bottomRect)
        self.holdBottomImage = pygame.transform.scale(self.holdBottomImage, (self.noteWidth, self.noteWidth*(self.hhh/self.holdTopImage.get_width())))

        # 把body分成3份
        bodyRect = pygame.Rect(0, self.hhh, self.holdOriginalImage.get_width(), self.holdOriginalImage.get_height()-self.hhh*2)
        self.holdBodyImage = self.holdOriginalImage.subsurface(bodyRect)
        self.holdBodyImage = pygame.transform.scale(self.holdBodyImage, (self.noteWidth, self.holdBodyImage.get_height()))
        self.hhb = self.holdBodyImage.get_height()  # height of hold body
        self.div3HoldImages: list[pygame.Surface] = []
        for i in range(3):
            tempRect = pygame.Rect(0, (i/3)*self.hhb, noteWidth, self.hhb/3)
            tempSurf = self.holdBodyImage.subsurface(tempRect)
            self.div3HoldImages.append(tempSurf)

        # 把body分成10份
        bodyRect = pygame.Rect(0, self.hhh, self.holdOriginalImage.get_width(), self.holdOriginalImage.get_height()-self.hhh)
        self.holdBodyImage = self.holdOriginalImage.subsurface(bodyRect)
        self.holdBodyImage = pygame.transform.scale(self.holdBodyImage, (self.noteWidth, self.holdBodyImage.get_height()))
        self.hhb = self.holdBodyImage.get_height()  # height of hold body
        self.div10HoldImages: list[pygame.Surface] = []
        for i in range(10):
            tempRect = pygame.Rect(0, (i/10)*self.hhb, noteWidth, self.hhb/10)
            tempSurf = self.holdBodyImage.subsurface(tempRect)
            self.div10HoldImages.append(tempSurf)

        # 把body分成100份
        bodyRect = pygame.Rect(0, self.hhh, self.holdOriginalImage.get_width(),self.holdOriginalImage.get_height() - self.hhh)
        self.holdBodyImage = self.holdOriginalImage.subsurface(bodyRect)
        self.holdBodyImage = pygame.transform.scale(self.holdBodyImage,(self.noteWidth, self.holdBodyImage.get_height()))
        self.hhb = self.holdBodyImage.get_height()  # height of hold body
        self.div100HoldImages: list[pygame.Surface] = []
        for i in range(100):
            tempRect = pygame.Rect(0, (i / 100) * self.hhb, noteWidth, self.hhb / 100)
            tempSurf = self.holdBodyImage.subsurface(tempRect)
            self.div100HoldImages.append(tempSurf)

        tapNoteHeight = self.tapOriginalImage.get_height() / self.tapOriginalImage.get_width() * self.noteWidth
        self.tapOriginalImage = pygame.transform.scale(self.tapOriginalImage, (self.noteWidth, tapNoteHeight))
        dragNoteHeight = self.dragOriginalImage.get_height() / self.dragOriginalImage.get_width() * self.noteWidth
        self.dragOriginalImage = pygame.transform.scale(self.dragOriginalImage, (self.noteWidth, dragNoteHeight))
        flickNoteHeight = self.flickOriginalImage.get_height() / self.flickOriginalImage.get_width() * self.noteWidth
        self.flickOriginalImage = pygame.transform.scale(self.flickOriginalImage, (self.noteWidth, flickNoteHeight))

        tapHLNoteHeight = self.tapHLOriginalImage.get_height() / self.tapHLOriginalImage.get_width() * self.noteWidth
        self.tapHLOriginalImage = pygame.transform.scale(self.tapHLOriginalImage, (self.noteWidth, tapHLNoteHeight))
        dragHLNoteHeight = self.dragHLOriginalImage.get_height() / self.dragHLOriginalImage.get_width() * self.noteWidth
        self.dragHLOriginalImage = pygame.transform.scale(self.dragHLOriginalImage, (self.noteWidth, dragHLNoteHeight))
        flickHLNoteHeight = self.flickHLOriginalImage.get_height() / self.flickHLOriginalImage.get_width() * self.noteWidth
        self.flickHLOriginalImage = pygame.transform.scale(self.flickHLOriginalImage, (self.noteWidth, flickHLNoteHeight))

        # 击中特效
        self.hitOriginalImage = pygame.image.load("assets/Hit.png").convert_alpha()
        self.hitOriginalImage = colorize_grayscale(self.hitOriginalImage, (254, 255, 169))
        self.hitOriginalImage = pygame.transform.smoothscale(self.hitOriginalImage, (hitWidth*7, hitWidth*6))
        self.hitImageWidth = self.hitOriginalImage.get_width()
        self.hitImageHeight = self.hitOriginalImage.get_height()

        for y in range(6):
            for x in range(7):
                rect = (x/7*self.hitImageWidth, y/6*self.hitImageHeight,
                        self.hitImageWidth/7, self.hitImageHeight/6)
                surface = self.hitOriginalImage.subsurface(rect)
                self.preRendHit.append(surface)

    def tap(self, angle) -> pygame.Surface:
        angle = int((angle+180)%180)
        if angle not in self.preRendTap:
            surf = pygame.transform.rotate(self.tapOriginalImage, angle)
            self.preRendTap[angle] = surf
            return surf
        else:
            return self.preRendTap[angle]

    def tapHL(self, angle) -> pygame.Surface:
        angle = int((angle+180)%180)
        if angle not in self.preRendTapHL:
            surf = pygame.transform.rotate(self.tapHLOriginalImage, angle)
            self.preRendTapHL[angle] = surf
            return surf
        else:
            return self.preRendTapHL[angle]

    def drag(self, angle) -> pygame.Surface:
        angle = int((angle+180)%180)
        if angle not in self.preRendDrag:
            surf = pygame.transform.rotate(self.dragOriginalImage, angle)
            self.preRendDrag[angle] = surf
            return surf
        else:
            return self.preRendDrag[angle]

    def dragHL(self, angle) -> pygame.Surface:
        angle = int((angle+180)%180)
        if angle not in self.preRendDragHL:
            surf = pygame.transform.rotate(self.dragHLOriginalImage, angle)
            self.preRendDragHL[angle] = surf
            return surf
        else:
            return self.preRendDragHL[angle]

    def flick(self, angle) -> pygame.Surface:
        angle = int((angle+180)%180)
        if angle not in self.preRendFlick:
            surf = pygame.transform.rotate(self.flickOriginalImage, angle)
            self.preRendFlick[angle] = surf
            return surf
        else:
            return self.preRendFlick[angle]

    def flickHL(self, angle) -> pygame.Surface:
        angle = int((angle+180)%180)
        if angle not in self.preRendFlickHL:
            surf = pygame.transform.rotate(self.flickHLOriginalImage, angle)
            self.preRendFlickHL[angle] = surf
            return surf
        else:
            return self.preRendFlickHL[angle]

    def hold(self, angle, totalHeight, above=False) -> pygame.Surface:
        # surface = pygame.Surface((self.noteWidth, totalHeight), pygame.SRCALPHA)
        # headHeight = self.holdTopImage.get_height()
        # body = pygame.transform.scale(self.holdBodyImage, (self.noteWidth, totalHeight-headHeight))
        # surface.blit(self.holdTopImage, (0, 0))
        # surface.blit(body, (0, headHeight))
        # surface.blit(self.holdBottomImage, (0, totalHeight - headHeight))

        headHeight = self.holdTopImage.get_height()
        surface = pygame.transform.scale(self.holdBodyImage, (self.noteWidth, totalHeight))
        surface.fill((0, 0, 0, 0), (0, 0, self.noteWidth, headHeight))
        surface.fill((0, 0, 0, 0), (0, totalHeight-headHeight, self.noteWidth, headHeight))
        surface.blit(self.holdTopImage, (0, 0), special_flags=pygame.BLENDMODE_NONE)
        surface.blit(self.holdBottomImage, (0, totalHeight - headHeight), special_flags=pygame.BLENDMODE_NONE)

        if above:
            surface = pygame.transform.rotate(surface, angle)
        else:
            surface = pygame.transform.rotate(surface, angle+180)
        return surface

    def hit(self, frame: int) -> pygame.Surface:
        return self.preRendHit[frame]


class HitEffect:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.frame = 0
        self.pos = (x, y)

        self.xList = []
        self.yList = []
        self.rList = []

        for i in range(random.randint(3, 6)):
            angle = random.uniform(1, 2*math.pi)
            radio = random.uniform(0.8, 1)
            self.xList.append(math.sin(angle))
            self.yList.append(math.cos(angle))
            self.rList.append(radio)



class Player:
    def __init__(self, matcher: autoMatch.Matcher, w: int = 1200, h: int = 600, fps: int = 60):

        self.width = w
        self.height = h

        ### 铺面显示相关

        # 基本颜色
        self.RED = (255, 0, 0, 255)
        self.YELLOW = (255, 255, 0, 255)
        self.ZERO = (0, 0, 0, 0)
        self.BLACK = (0, 0, 0, 255)
        self.WHITE = (255, 255, 255, 255)
        # 判定线长度/粗细
        self.lineLength = 5000
        self.lineWidth = 5
        # 键大小
        self.noteSize = int(self.width / 8)
        self.hitEffectSize = int(self.width / 6)
        # 单位
        self.X = 0.05626 * self.width
        self.Y = 0.6 * self.height
        # UI文字
        self.subtitle = "PHICHART"
        self.level = "AT Lv.16"
        self.name = "Antithese"
        # 显示UI
        self.displayDebug = True
        self.displayUI = True
        # 双押提示
        self.doubleHitEffect = True

        ### 播放相关数据

        # 帧率
        self.FPS = fps
        # 节奏
        self.BPM = ...
        # 播放进度
        self.timeS = 0
        self.timeT = 0
        # 铺面延迟（秒）
        self.chartDelay = 0
        # 连击数统计
        self.combo = 0
        self.score = 0
        # 暂停
        self.pause = False
        # 性能计时器
        self.noteCost = None
        self.holdCost = None
        self.lineCost = None
        self.effectCost = None
        self.hitBlockCost = None
        # 音频长度
        self.waveDurationS = None

        ### 固有对象

        # 初始化铺面文件
        self.matcher = matcher
        self.illuFile = matcher.illuFile
        self.chartFile = matcher.chartFile
        self.audioFile = matcher.audioFile

        # pygame变量
        self.screen = pygame.display.set_mode((w, h), pygame.HWSURFACE | pygame.DOUBLEBUF)
        # 铺面对象
        self.chart: chart.Chart = ...
        # 静态背景图层
        self.background_layer = pygame.Surface((w, h), )
        self.background_brightness = 0.4
        self.background_blurRadius = 300
        # fuzzyOptimizationMultiplier，模糊化前先缩小图像以提高性能
        self.FOM = 20
        # 动态前景层
        self.foreground_layer = pygame.Surface((w, h), pygame.SRCALPHA)
        # 字体
        self.font36: pygame.font.Font = ...
        self.font24: pygame.font.Font = ...
        self.font18: pygame.font.Font = ...
        self.font48: pygame.font.Font = ...
        # 图像旋转缓存器
        self.images = PreRendCache(self.noteSize, self.hitEffectSize)
        # 特效列表
        self.hitEffectList: list[HitEffect] = []
        # 音效
        self.tapSound: pygame.mixer.Sound = ...
        self.dragSound: pygame.mixer.Sound = ...
        self.flickSound: pygame.mixer.Sound = ...

    def render(self):

        self.lineCount = 0
        self.noteCount = 0
        self.holdCount = 0

        mytimer("初始化")

        # 绘制进度条
        pygame.draw.rect(
            self.foreground_layer,
            (255, 255, 255, 100),
            (0, 0, self.width*(self.timeS/self.waveDurationS), 8),
            width=0,
        )
        pygame.draw.rect(
            self.foreground_layer,
            (255, 255, 255, 200),
            (self.width*(self.timeS/self.waveDurationS), 0, 5 , 8),
            width=0,
        )

        # 击中特效的方块飞舞
        for effect in self.hitEffectList:
            for i in range(len(effect.xList)):
                size = self.hitEffectSize // 20
                color = (254, 255, 169, int(200 - 200 * effect.frame / 42))
                rate = 1-(effect.frame / 42-1)**4
                x = int(effect.x + effect.xList[i] * effect.rList[i] * self.hitEffectSize * rate)
                y = int(effect.y + effect.yList[i] * effect.rList[i] * self.hitEffectSize * rate)
                y = self.height - y
                pygame.draw.rect(self.foreground_layer, color, (x-size, y-size, size*2, size*2))

        self.hitBlockCost = mytimer("特效方块")

        for line in self.chart.lineList:
            x = line.move1(self.timeT) * self.width
            y = line.move2(self.timeT) * self.height
            a = line.alpha(self.timeT)
            r = line.rotate(self.timeT)
            Vsin = math.sin(math.radians(r))
            Vcos = math.cos(math.radians(r))

            line.tempX = x
            line.tempY = y
            line.tempR = r
            line.tempS = Vsin
            line.tempC = Vcos

            x1 = int(x - Vcos * self.lineLength / 2)
            y1 = int(y - Vsin * self.lineLength / 2)
            x2 = int(x + Vcos * self.lineLength / 2)
            y2 = int(y + Vsin * self.lineLength / 2)

            y1 = self.height - y1
            y2 = self.height - y2

            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)
            skip = max(x_min, 0) > min(x_max, self.width) or max(y_min, 0) > min(y_max, self.height)

            if not skip and a > 0.01:
                self.lineCount += 1
                color = (254, 255, 169, int(255 * a))
                pygame.draw.line(
                    self.foreground_layer, color,
                    start_pos=(x1, y1),
                    end_pos=(x2, y2),
                    width=self.lineWidth
                )

        self.lineCost = mytimer("判定线")

        for line in self.chart.lineList:
            x = line.move1(self.timeT) * self.width
            y = line.move2(self.timeT) * self.height
            r = line.rotate(self.timeT)

            Vsin = math.sin(math.radians(r))
            Vcos = math.cos(math.radians(r))

            for note in line.noteList:
                if note.type_ != 3:
                    continue
                if note.hit:
                    continue

                if self.timeT > note.time_:
                    dx = note.posX * self.X
                    dy = (note.floorPos - line.pos(self.timeT)) * self.Y
                    dyt = dy + (note.speed * note.holdTime * 1.875 / line.bpm) * self.Y
                    dy = 0
                else:
                    dx = note.posX * self.X
                    dy = (note.floorPos - line.pos(self.timeT)) * self.Y
                    dyt = dy + (note.speed * note.holdTime * 1.875 / line.bpm) * self.Y

                if note.above:
                    xn = x + dx * Vcos - dy * Vsin
                    yn = y + dx * Vsin + dy * Vcos
                    xnt = x + dx * Vcos - dyt * Vsin
                    ynt = y + dx * Vsin + dyt * Vcos
                else:
                    xn = x + dx * Vcos + dy * Vsin
                    yn = y + dx * Vsin - dy * Vcos
                    xnt = x + dx * Vcos + dyt * Vsin
                    ynt = y + dx * Vsin - dyt * Vcos

                # 根据时间判断，跳过渲染还是添加特效
                frameDelta = 0.5/self.FPS * self.BPM / 1.875 * 0

                if note.time_ < self.timeT + frameDelta < note.time_ + note.holdTime:
                    if random.random() < 1 / 10:
                        effect = HitEffect(xn, yn)
                        self.hitEffectList.append(effect)

                elif note.time_ + note.holdTime < self.timeT + frameDelta:
                    note.hit = True
                    self.combo += 1
                    self.score += 1*10**6 / self.chart.noteCount
                if note.time_ < self.timeT + frameDelta and not note.begin:
                    note.begin = True
                    self.tapSound.play()

                x1 = int(xn - Vcos * self.noteSize / 2)
                y1 = int(yn - Vsin * self.noteSize / 2)
                x2 = int(xn + Vcos * self.noteSize / 2)
                y2 = int(yn + Vsin * self.noteSize / 2)
                x3 = int(xnt - Vcos * self.noteSize / 2)
                y3 = int(ynt - Vsin * self.noteSize / 2)
                x4 = int(xnt + Vcos * self.noteSize / 2)
                y4 = int(ynt + Vsin * self.noteSize / 2)

                y1 = self.height - y1
                y2 = self.height - y2
                y3 = self.height - y3
                y4 = self.height - y4

                self.holdRender(x1, x2, x3, x4, y1, y2, y3, y4, r, note.above)

        self.holdCost = mytimer("hold")

        for line in self.chart.lineList:
            x = line.move1(self.timeT) * self.width
            y = line.move2(self.timeT) * self.height
            r = line.rotate(self.timeT)

            Vsin = math.sin(math.radians(r))
            Vcos = math.cos(math.radians(r))

            for note in line.noteList:

                if note.type_ == 3:
                    continue
                if note.hit:
                    continue

                dx = note.posX * self.X
                dy = note.speed * (note.floorPos - line.pos(self.timeT)) * self.Y


                if note.above:
                    xn = x + dx * Vcos - dy * Vsin
                    yn = y + dx * Vsin + dy * Vcos
                else:
                    xn = x + dx * Vcos + dy * Vsin
                    yn = y + dx * Vsin - dy * Vcos

                # 根据时间判断，跳过渲染还是添加特效
                frameDelta = 0.5/self.FPS * self.BPM / 1.875 * 0
                if note.time_ < self.timeT + frameDelta:
                    effect = HitEffect(xn, yn)
                    self.hitEffectList.append(effect)
                    note.hit = True
                    self.combo += 1
                    self.score += 1*10**6 / self.chart.noteCount

                    # 播放音效
                    if note.type_ == 1:
                        self.tapSound.play()
                    elif note.type_ == 2:
                        self.dragSound.play()
                    elif note.type_ == 4:
                        self.flickSound.play()

                if xn < -self.noteSize or xn > self.width+self.noteSize:
                    continue
                elif yn < -self.noteSize or yn > self.height+self.noteSize:
                    continue

                if note.doubleHit and self.doubleHitEffect:
                    if note.type_ == 1:
                        surface = self.images.tapHL(r)
                    elif note.type_ == 2:
                        surface = self.images.dragHL(r)
                    elif note.type_ == 4:
                        surface = self.images.flickHL(r)
                else:
                    if note.type_ == 1:
                        surface = self.images.tap(r)
                    elif note.type_ == 2:
                        surface = self.images.drag(r)
                    elif note.type_ == 4:
                        surface = self.images.flick(r)

                x0 = int(xn - surface.get_width() / 2)
                y0 = int(yn + surface.get_height() / 2)
                y0 = self.height - y0
                self.foreground_layer.blit(surface, (x0, y0))
                self.noteCount += 1

        self.noteCost = mytimer("note")

        for effect in self.hitEffectList:
            x = effect.x - self.hitEffectSize // 2
            y = self.height - effect.y - self.hitEffectSize // 2
            self.foreground_layer.blit(self.images.hit(effect.frame), (x, y))
            effect.frame += 1
        self.hitEffectList = [effect for effect in self.hitEffectList if effect.frame < 42]

        self.effectCost = mytimer("特效")

    def holdRender(self, x1, x2, x3, x4, y1, y2, y3, y4, angle: float, above):
        height = math.sqrt((x1 - x3) ** 2 + (y1 - y3) ** 2)
        topHeight = self.images.holdTopImage.get_height()
        topHeight = 0
        bodyHeight = height - topHeight * 2

        if bodyHeight <= 0:
            return

        if height > 10000:
            for i in range(100):
                d = ((i/100)*bodyHeight+topHeight) / height
                e = (((i+1)/100)*bodyHeight+topHeight) / height
                xi1 = x1 * d + x3 * (1 - d)
                yi1 = y1 * d + y3 * (1 - d)
                xi2 = x2 * d + x4 * (1 - d)
                yi2 = y2 * d + y4 * (1 - d)
                xi3 = x1 * e + x3 * (1 - e)
                yi3 = y1 * e + y3 * (1 - e)
                xi4 = x2 * e + x4 * (1 - e)
                yi4 = y2 * e + y4 * (1 - e)

                minX = min(xi1, xi2, xi3, xi4)
                maxX = max(xi1, xi2, xi3, xi4)
                minY = min(yi1, yi2, yi3, yi4)
                maxY = max(yi1, yi2, yi3, yi4)

                if maxX < 0 or minX > self.width or maxY < 0 or minY > self.height:
                    continue

                if above:
                    image = pygame.transform.scale(self.images.div100HoldImages[i], (self.noteSize, bodyHeight/100))
                    image = pygame.transform.rotate(image, angle)
                else:
                    image = pygame.transform.scale(self.images.div100HoldImages[i], (self.noteSize, bodyHeight/100))
                    image = pygame.transform.rotate(image, angle+180)

                self.foreground_layer.blit(image, (minX, minY))
                self.holdCount += 1
        elif height > 3000:
            for i in range(10):
                d = ((i/10)*bodyHeight+topHeight) / height
                e = (((i+1)/10)*bodyHeight+topHeight) / height
                xi1 = x1 * d + x3 * (1 - d)
                yi1 = y1 * d + y3 * (1 - d)
                xi2 = x2 * d + x4 * (1 - d)
                yi2 = y2 * d + y4 * (1 - d)
                xi3 = x1 * e + x3 * (1 - e)
                yi3 = y1 * e + y3 * (1 - e)
                xi4 = x2 * e + x4 * (1 - e)
                yi4 = y2 * e + y4 * (1 - e)

                minX = min(xi1, xi2, xi3, xi4)
                maxX = max(xi1, xi2, xi3, xi4)
                minY = min(yi1, yi2, yi3, yi4)
                maxY = max(yi1, yi2, yi3, yi4)

                if maxX < 0 or minX > self.width or maxY < 0 or minY > self.height:
                    continue

                if above:
                    image = pygame.transform.scale(self.images.div10HoldImages[i], (self.noteSize, bodyHeight/10))
                    image = pygame.transform.rotate(image, angle)
                else:
                    image = pygame.transform.scale(self.images.div10HoldImages[i], (self.noteSize, bodyHeight/10))
                    image = pygame.transform.rotate(image, angle+180)

                self.foreground_layer.blit(image, (minX, minY))
                self.holdCount += 1
        elif height > 1000:
            for i in range(3):
                d = ((i/3)*bodyHeight+topHeight) / height
                e = (((i+1)/3)*bodyHeight+topHeight) / height
                xi1 = x1 * d + x3 * (1 - d)
                yi1 = y1 * d + y3 * (1 - d)
                xi2 = x2 * d + x4 * (1 - d)
                yi2 = y2 * d + y4 * (1 - d)
                xi3 = x1 * e + x3 * (1 - e)
                yi3 = y1 * e + y3 * (1 - e)
                xi4 = x2 * e + x4 * (1 - e)
                yi4 = y2 * e + y4 * (1 - e)

                minX = min(xi1, xi2, xi3, xi4)
                maxX = max(xi1, xi2, xi3, xi4)
                minY = min(yi1, yi2, yi3, yi4)
                maxY = max(yi1, yi2, yi3, yi4)

                if maxX < 0 or minX > self.width or maxY < 0 or minY > self.height:
                    continue

                if above:
                    image = pygame.transform.scale(self.images.div3HoldImages[i], (self.noteSize, bodyHeight/3))
                    image = pygame.transform.rotate(image, angle)
                else:
                    image = pygame.transform.scale(self.images.div3HoldImages[i], (self.noteSize, bodyHeight/3))
                    image = pygame.transform.rotate(image, angle+180)

                self.foreground_layer.blit(image, (minX, minY))
                self.holdCount += 1
        else:
            # d = (0*bodyHeight+topHeight) / height
            # e = (1*bodyHeight+topHeight) / height
            # xi1 = x1 * d + x3 * (1-d)
            # yi1 = y1 * d + y3 * (1-d)
            # xi2 = x2 * d + x4 * (1-d)
            # yi2 = y2 * d + y4 * (1-d)
            # xi3 = x1 * e + x3 * (1-e)
            # yi3 = y1 * e + y3 * (1-e)
            # xi4 = x2 * e + x4 * (1-e)
            # yi4 = y2 * e + y4 * (1-e)
            #
            # minX = min(xi1, xi2, xi3, xi4)
            # maxX = max(xi1, xi2, xi3, xi4)
            # minY = min(yi1, yi2, yi3, yi4)
            # maxY = max(yi1, yi2, yi3, yi4)

            minX = min(x1, x2, x3, x4)
            maxX = max(x1, x2, x3, x4)
            minY = min(y1, y2, y3, y4)
            maxY = max(y1, y2, y3, y4)

            if maxX < 0 or minX > self.width or maxY < 0 or minY > self.height:
                return

            if above:
                image = pygame.transform.scale(self.images.holdOriginalImage, (self.noteSize, bodyHeight))
                image = pygame.transform.rotate(image, angle)
            else:
                image = pygame.transform.scale(self.images.holdOriginalImage, (self.noteSize, bodyHeight))
                image = pygame.transform.rotate(image, angle + 180)

            self.foreground_layer.blit(image, (minX, minY))
            self.holdCount += 1

    def is_rect_off_screen(self, x1, y1, x2, y2):
        left = min(x1, x2)
        right = max(x1, x2)
        top = min(y1, y2)
        bottom = max(y1, y2)

        # 判断是否完全超出屏幕
        if (right < 0 or  # 完全在左侧
                left > self.width or  # 完全在右侧
                bottom < 0 or  # 完全在上方
                top > self.height):  # 完全在下方
            return True
        return False

    def UIrender(self):

        if not self.displayUI:
            return

        if self.combo >= 3:
            draw_text(
                self.foreground_layer,
                str(self.combo),
                self.font48, self.WHITE,
                pos=(self.width//2, 20),
                align="N",
            )
            draw_text(
                self.foreground_layer,
                self.subtitle,
                self.font18, self.WHITE,
                pos=(self.width//2, 70),
                align="N",
            )

        draw_text(
            self.foreground_layer,
            f"{self.score:07.0f}",
            self.font36, self.WHITE,
            pos=(self.width-20, 20),
            align="NE",
        )

        draw_text(
            self.foreground_layer,
            self.name,
            self.font24, self.WHITE,
            pos=(20, self.height - 20),
            align="SW",
        )

        draw_text(
            self.foreground_layer,
            self.level,
            self.font24, self.WHITE,
            pos=(self.width-20, self.height - 20),
            align="SE",
        )

        if not self.displayDebug:
            return

        draw_text(
            self.foreground_layer,
            f"FPS: {self.secondCount}",
            self.font18, self.WHITE,
            pos=(20, 20),
            align="NW",
        )

        if self.timeCost*self.FPS > 1:
            color = self.RED
        elif self.timeCost*self.FPS > 0.8:
            color = self.YELLOW
        else:
            color = self.WHITE
        draw_text(
            self.foreground_layer,
            f"cost: {self.timeCost*1000:.2f} ms ({self.timeCost*self.FPS:.2%})",
            self.font18, color,
            pos=(20, 40),
            align="NW",
        )

        draw_text(
            self.foreground_layer,
            f"lines: {self.lineCount}",
            self.font18, self.WHITE,
            pos=(20, 170),
            align="NW",
        )

        draw_text(
            self.foreground_layer,
            f"notes: {self.noteCount}",
            self.font18, self.WHITE,
            pos=(20, 190),
            align="NW",
        )

        draw_text(
            self.foreground_layer,
            f"holds: {self.holdCount}",
            self.font18, self.WHITE,
            pos=(20, 210),
            align="NW",
        )

        draw_text(
            self.foreground_layer,
            f"effects: {len(self.hitEffectList)}",
            self.font18, self.WHITE,
            pos=(20, 230),
            align="NW",
        )

        draw_text(
            self.foreground_layer,
            f"pre-rendered images cache:",
            self.font18, self.WHITE,
            pos=(20, 260),
            align="NW",
        )

        cacheCount = len(self.images.preRendTap) + len(self.images.preRendTapHL)
        draw_text(
            self.foreground_layer,
            f"tap: {cacheCount}",
            self.font18, self.WHITE,
            pos=(20, 280),
            align="NW",
        )

        cacheCount = len(self.images.preRendDrag) + len(self.images.preRendDragHL)
        draw_text(
            self.foreground_layer,
            f"drag: {cacheCount}",
            self.font18, self.WHITE,
            pos=(20, 300),
            align="NW",
        )

        cacheCount = len(self.images.preRendFlick) + len(self.images.preRendFlickHL)
        draw_text(
            self.foreground_layer,
            f"flick: {cacheCount}",
            self.font18, self.WHITE,
            pos=(20, 320),
            align="NW",
        )

        draw_text(
            self.foreground_layer,
            f"timeT: {self.timeT: .02f}",
            self.font18, self.WHITE,
            pos=(20, 350),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"timeS: {self.timeS: .02f} s",
            self.font18, self.WHITE,
            pos=(20, 370),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"beats: {self.timeT // 32: .0f}",
            self.font18, self.WHITE,
            pos=(20, 390),
            align="NW",
        )

        draw_text(
            self.foreground_layer,
            f"hit: {self.hitBlockCost*1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 60),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"effect: {self.effectCost*1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 80),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"note: {self.noteCost*1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 100),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"line: {self.lineCost*1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 120),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"hold: {self.holdCost*1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 140),
            align="NW",
        )

        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 60, self.hitBlockCost/(1/self.FPS)*100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 80, self.effectCost/(1/self.FPS)*100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 100, self.noteCost/(1/self.FPS)*100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 120, self.lineCost/(1/self.FPS)*100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 140, self.holdCost/(1/self.FPS)*100, 16))

    def initPlayer(self):
        # 初始化 pygame
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)

        # 初始化营销
        self.tapSound = pygame.mixer.Sound("assets/click.wav")
        self.dragSound = pygame.mixer.Sound("assets/drag.wav")
        self.flickSound = pygame.mixer.Sound("assets/flick.wav")

        # 计算音频长度
        self.waveDurationS = get_wav_duration(self.audioFile)

        # 初始化背景图
        try:
            self.background_layer = pygame.image.load(self.illuFile).convert()
            self.background_layer = pygame.transform.scale(self.background_layer,
                                                           (self.width / self.FOM, self.height / self.FOM))
            self.background_layer = cv2_blur(self.background_layer, self.background_blurRadius / self.FOM)
            self.background_layer = apply_darken(self.background_layer, self.background_brightness)
            self.background_layer = pygame.transform.smoothscale(self.background_layer, (self.width, self.height))

        except Exception as e:
            traceback.print_exc()
            self.background_layer = pygame.Surface((self.width, self.height))
            self.background_layer.fill((30, 30, 60))

        # 初始化字体
        try:
            self.font36 = pygame.font.Font('assets/phigros.ttf', 36)
            self.font24 = pygame.font.Font('assets/phigros.ttf', 24)
            self.font18 = pygame.font.Font('assets/phigros.ttf', 18)
            self.font48 = pygame.font.Font('assets/phigros.ttf', 48)
        except Exception as e:
            traceback.print_exc()
            self.font36 = pygame.font.SysFont(None, 36)
            self.font24 = pygame.font.SysFont(None, 24)
            self.font18 = pygame.font.SysFont(None, 18)
            self.font48 = pygame.font.SysFont(None, 48)

        # 加载铺面数据
        self.chart = analyzer.analyzeJson(self.chartFile)
        self.BPM = self.chart.lineList[0].bpm

        # 加载bgm
        pygame.mixer.music.load(self.audioFile)

    def mainloop(self):

        running = True
        clock = pygame.time.Clock()
        # 计时器，用于评估性能
        timer = time.time()
        self.timeCost = 10 ** -6
        delta = 10 ** -6
        # 用于统计平均帧数
        frameCount = 0
        self.secondCount = self.FPS
        # 计算铺面延迟
        self.timeS = - self.chartDelay
        self.timeT = self.timeS * self.BPM / 1.875

        # 播放bgm
        pygame.mixer.music.play()

        while running:

            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.pause = not self.pause
            if self.pause:
                clock.tick(self.FPS)
                continue

            # 清空屏幕（用白色填充）
            # 绘制当前帧的所有内容
            try:
                self.screen.fill(self.WHITE)
                if self.timeT > 0:
                    self.foreground_layer.fill(self.ZERO)
                    self.render()
                    self.UIrender()
            except Exception as e:
                traceback.print_exc()
                print(f"Render Error at timeT={self.timeT}")

            # 3. 更新显示
            self.screen.blit(self.background_layer, (0, 0))
            self.screen.blit(self.foreground_layer, (0, 0))
            pygame.display.flip()

            # 控制帧率
            self.timeCost = time.time() - timer + 0.00001
            clock.tick(self.FPS)

            frameCount += 1
            if timer//1 != time.time()//1:
                self.secondCount = frameCount
                frameCount = 0

            current = time.time()
            delta = current - timer
            timer = current
            self.timeS += delta
            self.timeT = self.timeS * self.BPM / 1.875


if __name__ == '__main__':
    player = Player(autoMatch.Matcher("charts/rr/"), h=720, w=1280, fps=90)
    player.initPlayer()
    player.mainloop()
