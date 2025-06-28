import json
import os
import zipfile
import pygame
import random
import time
import math
import cv2
import analyzer
import chart
import autoMatch
import traceback
import subprocess


def open_explorer_and_select_file(file_path):
    """
    打开文件资源管理器并选中指定文件（支持相对路径）

    参数:
        file_path (str): 要选中的文件路径（相对或绝对路径）

    返回:
        bool: 操作是否成功
    """
    try:
        # 将路径转换为绝对路径
        abs_path = os.path.abspath(file_path)

        # 检查文件是否存在
        if not os.path.exists(abs_path):
            raise FileNotFoundError(f"文件不存在: {abs_path}")

        # 规范化路径（统一分隔符）
        normalized_path = os.path.normpath(abs_path)

        # 使用subprocess运行命令（更安全）
        subprocess.Popen(f'explorer /select,"{normalized_path}"', shell=True)
        return True

    except Exception as e:
        print(f"操作失败: {e}")
        return False


def clear_directory(directory, clear=True):
    """
    清空指定目录下的所有文件（不包含子目录）
    如果目录不存在则自动创建

    参数:
        directory (str): 要清空的目录路径
    """
    try:
        # 如果目录不存在则创建
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"目录不存在，已创建: {directory}")
            return

        if not clear:
            return

        # 遍历目录下的所有内容
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)

            try:
                # 如果是文件则删除
                if os.path.isfile(file_path):
                    os.unlink(file_path)
                # 如果是符号链接则删除
                elif os.path.islink(file_path):
                    os.unlink(file_path)
                # 忽略子目录
                elif os.path.isdir(file_path):
                    continue
            except Exception as e:
                print(f"删除 {file_path} 失败: {e}")

        print(f"目录 {directory} 下的文件已清空")

    except Exception as e:
        print(f"操作失败: {e}")


timerClock = time.time()
running = False


def mytimer(msg: str):
    global timerClock
    current = time.time()
    cost = current - timerClock
    timerClock = current
    # print(msg, cost*1000, "ms")
    return cost


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
        self.holdTopImage = pygame.transform.scale(self.holdTopImage, (
        self.noteWidth, self.noteWidth * (self.hhh / self.holdTopImage.get_width())))
        bottomRect = pygame.Rect(0, self.holdOriginalImage.get_height() - self.hhh, self.holdOriginalImage.get_width(),
                                 self.hhh)
        self.holdBottomImage = self.holdOriginalImage.subsurface(bottomRect)
        self.holdBottomImage = pygame.transform.scale(self.holdBottomImage, (
        self.noteWidth, self.noteWidth * (self.hhh / self.holdTopImage.get_width())))

        # 把body分成3份
        bodyRect = pygame.Rect(0, self.hhh, self.holdOriginalImage.get_width(),
                               self.holdOriginalImage.get_height() - self.hhh * 2)
        self.holdBodyImage = self.holdOriginalImage.subsurface(bodyRect)
        self.holdBodyImage = pygame.transform.scale(self.holdBodyImage,
                                                    (self.noteWidth, self.holdBodyImage.get_height()))
        self.hhb = self.holdBodyImage.get_height()  # height of hold body
        self.div3HoldImages: list[pygame.Surface] = []
        for i in range(3):
            tempRect = pygame.Rect(0, (i / 3) * self.hhb, noteWidth, self.hhb / 3)
            tempSurf = self.holdBodyImage.subsurface(tempRect)
            self.div3HoldImages.append(tempSurf)

        # 把body分成10份
        bodyRect = pygame.Rect(0, self.hhh, self.holdOriginalImage.get_width(),
                               self.holdOriginalImage.get_height() - self.hhh * 2)
        self.holdBodyImage = self.holdOriginalImage.subsurface(bodyRect)
        self.holdBodyImage = pygame.transform.scale(self.holdBodyImage,
                                                    (self.noteWidth, self.holdBodyImage.get_height()))
        self.hhb = self.holdBodyImage.get_height()  # height of hold body
        self.div10HoldImages: list[pygame.Surface] = []
        for i in range(10):
            tempRect = pygame.Rect(0, (i / 10) * self.hhb, noteWidth, self.hhb / 10)
            tempSurf = self.holdBodyImage.subsurface(tempRect)
            self.div10HoldImages.append(tempSurf)

        # 把body分成100份
        bodyRect = pygame.Rect(0, self.hhh, self.holdOriginalImage.get_width(),
                               self.holdOriginalImage.get_height() - self.hhh * 2)
        self.holdBodyImage = self.holdOriginalImage.subsurface(bodyRect)
        self.holdBodyImage = pygame.transform.scale(self.holdBodyImage,
                                                    (self.noteWidth, self.holdBodyImage.get_height()))
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
        self.flickHLOriginalImage = pygame.transform.scale(self.flickHLOriginalImage,
                                                           (self.noteWidth, flickHLNoteHeight))

        # 击中特效
        self.hitOriginalImage = pygame.image.load("assets/Hit.png").convert_alpha()
        self.hitOriginalImage = colorize_grayscale(self.hitOriginalImage, (255, 243, 163))
        self.hitOriginalImage = pygame.transform.smoothscale(self.hitOriginalImage, (hitWidth * 7, hitWidth * 6))
        self.hitImageWidth = self.hitOriginalImage.get_width()
        self.hitImageHeight = self.hitOriginalImage.get_height()

        for y in range(6):
            for x in range(7):
                rect = (x / 7 * self.hitImageWidth, y / 6 * self.hitImageHeight,
                        self.hitImageWidth / 7, self.hitImageHeight / 6)
                surface = self.hitOriginalImage.subsurface(rect)
                self.preRendHit.append(surface)

        # for file in os.listdir("assets/hitEffect"):
        #     image = pygame.image.load("assets/hitEffect/" + file).convert_alpha()
        #     image = pygame.transform.smoothscale(image, (hitWidth, hitWidth))
        #     self.preRendHit.append(image)

    def tap(self, angle) -> pygame.Surface:
        angle = int((angle + 180) % 180)
        if angle not in self.preRendTap:
            surf = pygame.transform.rotate(self.tapOriginalImage, angle)
            self.preRendTap[angle] = surf
            return surf
        else:
            return self.preRendTap[angle]

    def tapHL(self, angle) -> pygame.Surface:
        angle = int((angle + 180) % 180)
        if angle not in self.preRendTapHL:
            surf = pygame.transform.rotate(self.tapHLOriginalImage, angle)
            self.preRendTapHL[angle] = surf
            return surf
        else:
            return self.preRendTapHL[angle]

    def drag(self, angle) -> pygame.Surface:
        angle = int((angle + 180) % 180)
        if angle not in self.preRendDrag:
            surf = pygame.transform.rotate(self.dragOriginalImage, angle)
            self.preRendDrag[angle] = surf
            return surf
        else:
            return self.preRendDrag[angle]

    def dragHL(self, angle) -> pygame.Surface:
        angle = int((angle + 180) % 180)
        if angle not in self.preRendDragHL:
            surf = pygame.transform.rotate(self.dragHLOriginalImage, angle)
            self.preRendDragHL[angle] = surf
            return surf
        else:
            return self.preRendDragHL[angle]

    def flick(self, angle) -> pygame.Surface:
        angle = int((angle + 180) % 180)
        if angle not in self.preRendFlick:
            surf = pygame.transform.rotate(self.flickOriginalImage, angle)
            self.preRendFlick[angle] = surf
            return surf
        else:
            return self.preRendFlick[angle]

    def flickHL(self, angle) -> pygame.Surface:
        angle = int((angle + 180) % 180)
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
        surface.fill((0, 0, 0, 0), (0, totalHeight - headHeight, self.noteWidth, headHeight))
        surface.blit(self.holdTopImage, (0, 0), special_flags=pygame.BLENDMODE_NONE)
        surface.blit(self.holdBottomImage, (0, totalHeight - headHeight), special_flags=pygame.BLENDMODE_NONE)

        if above:
            surface = pygame.transform.rotate(surface, angle)
        else:
            surface = pygame.transform.rotate(surface, angle + 180)
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
            angle = random.uniform(0, 2 * math.pi)
            radio = random.uniform(0.8, 1)
            self.xList.append(math.sin(angle))
            self.yList.append(math.cos(angle))
            self.rList.append(radio)


class Player:
    def __init__(self, matcher: autoMatch.Matcher = None, w: int = 1200, h: int = 600, fps: int = 60,
                 subtitle="AUTOPLAY", level="Un Lv.?", chartName="Unknown", chartDelay: float = 0,
                 debug: bool = False, displayUI: bool = True, enableMapping: bool = False, doubleHitEffect: bool = True,
                 brightness: float = 0.4, blurRadius: int = 300):

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
        self.lineLength = 3.6 * self.height
        self.lineWidth = 0.006 * self.height
        # 键大小
        self.noteSize = int(self.width / 8)
        self.hitEffectSize = int(self.width / 6)
        # 单位
        self.X = 0.05626 * self.width
        self.Y = 0.6 * self.height
        # UI文字
        self.subtitle = subtitle
        self.level = level
        self.name = chartName
        # 显示UI
        self.displayDebug = debug
        self.displayUI = displayUI
        # 双押提示
        self.doubleHitEffect = doubleHitEffect

        ### 播放相关数据

        # 帧率
        self.FPS = fps
        # 节奏
        self.BPM = ...
        # 播放进度
        self.timeS = 0
        self.timeT = 0
        # 播放起始时间
        self.startTimeS = 0
        # 铺面延迟（秒）
        self.chartDelay = chartDelay
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
        # 映射
        self.targetRectOfMapping: tuple = (w / 5 * 2, h / 5 * 2, w / 5 * 3, h / 5 * 3)
        self.enableMapping: bool = enableMapping
        self.mx1: int | None = None
        self.mx2: int | None = None
        self.my1: int | None = None
        self.my2: int | None = None
        self.mw: int | None = None
        self.mh: int | None = None
        # 3D
        self.enable3D = False
        # 3D倍速
        self.speed: float = 2.5
        # 渲染最远处
        self.boundary: float = self.height * 3.0
        # 摄像头位置（设定值）
        self.cmrB: float = 1.0
        self.cmrH: float = 1.0
        self.lower: float = 0.4  # 低视角，按下Shift触发，便于录制天地键
        self.lowerTimeS = [(10, 15), (122.02, 123.67), (126.80, 128.65), (138.40, 999)]
        # 摄像头位置（实际值）
        self.h: float = self.cmrH
        self.cmrX: float = self.width / 2
        self.cmrY: float = self.height / 2


        # 3D转谱
        self.enableCompiler = False
        self.tempLineList: list[chart.Line] = []
        self.tempLineListBG: list[chart.Line] = []
        self.allTempLines: list[chart.Line] = []
        self.allTempLinesBG: list[chart.Line] = []

        ### 固有对象

        # 初始化铺面文件
        self.matcher = matcher
        if matcher is not None:
            self.illuFile = matcher.illuFile
            self.chartFile = matcher.chartFile
            self.audioFile = matcher.audioFile
        else:
            self.illuFile = None
            self.chartFile = None
            self.audioFile = None

        # pygame变量
        self.screen = pygame.display.set_mode((w, h), pygame.HWSURFACE | pygame.DOUBLEBUF)
        # 铺面对象
        self.chart: chart.Chart = ...
        # 静态背景图层
        self.background_layer = pygame.Surface((w, h), )
        self.background_brightness = brightness
        self.background_blurRadius = blurRadius
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
        self.images: PreRendCache = ...
        # 特效列表
        self.hitEffectList: list[HitEffect] = []
        # 音效
        self.tapSound: pygame.mixer.Sound = ...
        self.dragSound: pygame.mixer.Sound = ...
        self.flickSound: pygame.mixer.Sound = ...

    def getNoteHitPos(self, line: chart.Line, note: chart.Note):
        x = line.move1(note.time_) * self.width
        y = line.move2(note.time_) * self.height
        r = line.rotate(note.time_)
        Vsin = math.sin(math.radians(r))
        Vcos = math.cos(math.radians(r))

        dx = note.posX * self.X
        dy = note.speed * (note.floorPos - line.pos(note.time_)) * self.Y

        if note.above:
            xn = x + dx * Vcos - dy * Vsin
            yn = y + dx * Vsin + dy * Vcos
        else:
            xn = x + dx * Vcos + dy * Vsin
            yn = y + dx * Vsin - dy * Vcos

        return xn, yn

    def getTempLine(self):
        if len(self.tempLineList) > 0:
            line = self.tempLineList[-1]
            self.tempLineList.pop(-1)
            return line
        else:
            line = chart.Line(self.chart.bpm)
            line.rotate.addPeriod(0, self.timeT, 0, 0)
            line.alpha.addPeriod(0, self.timeT, 0, 0)
            line.move1.addPeriod(0, self.timeT, 0, 0)
            line.move2.addPeriod(0, self.timeT, 0, 0)
            line.scaleX.addPeriod(0, self.timeT, 1.0, 1.0)
            line.scaleY.addPeriod(0, self.timeT, 1.0, 1.0)
            line.color.addPeriod(0, self.timeT, [255,255,255], [255,255,255])
            line.speed.addPeriod(0, 9999999, 1, 1)
            self.allTempLines.append(line)
            return line

    def getTempLineBG(self):
        if len(self.tempLineListBG) > 0:
            line = self.tempLineListBG[-1]
            self.tempLineListBG.pop(-1)
            return line
        else:
            line = chart.Line(self.chart.bpm)
            line.rotate.addPeriod(0, self.timeT, 0, 0)
            line.alpha.addPeriod(0, self.timeT, 0, 0)
            line.move1.addPeriod(0, self.timeT, 0, 0)
            line.move2.addPeriod(0, self.timeT, 0, 0)
            line.scaleX.addPeriod(0, self.timeT, 1.0, 1.0)
            line.scaleY.addPeriod(0, self.timeT, 1.0, 1.0)
            line.color.addPeriod(0, self.timeT, [255,255,255], [255,255,255])
            line.speed.addPeriod(0, 9999999, 1, 1)
            self.allTempLinesBG.append(line)
            return line

    def freeTempLine(self, line: chart.Line, note, isOutLine=False):
        self.tempLineList.append(line)
        if note.type_ == 1 or note.type_ == 3:
            colorFill = [10, 195, 255]
        elif note.type_ == 2:
            colorFill = [240, 237, 105]
        else:
            colorFill = [245, 67, 101]
        line.color.addPeriod(line.color.latestTimeT(), self.timeT, colorFill, colorFill)

    def freeTempLineBG(self, line: chart.Line, note, isOutLine=False):
        self.tempLineListBG.append(line)
        if note.doubleHit:
            colorFill = [254, 254, 102]
        else:
            colorFill = [255, 255, 255]
        line.color.addPeriod(line.color.latestTimeT(), self.timeT, colorFill, colorFill)

    def render(self):

        self.lineCount = 0
        self.noteCount = 0
        self.holdCount = 0

        mytimer("初始化")

        # print(len(self.tempLineList), len(self.allTempLines))

        # 击中特效的方块飞舞
        for effect in self.hitEffectList:
            for i in range(len(effect.xList)):
                size = self.hitEffectSize // 20
                color = (254, 255, 169, int(200 - 200 * effect.frame / len(self.images.preRendHit)))
                rate = 1 - (effect.frame / len(self.images.preRendHit) - 1) ** 4
                x = int(effect.x + effect.xList[i] * effect.rList[i] * self.hitEffectSize * rate)
                y = int(effect.y + effect.yList[i] * effect.rList[i] * self.hitEffectSize * rate)
                y = self.height - y
                if self.enableMapping:
                    x, y = self.mappingX(x), self.mappingY(y)
                pygame.draw.rect(self.foreground_layer, color, (x - size, y - size, size * 2, size * 2))

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

            if self.chart.RPE_Chart:
                scaleX = line.scaleX(self.timeT)
                scaleY = line.scaleY(self.timeT)
                color = (line.color(self.timeT)).copy()
                color.append(min(int(255 * a), 255))
            else:
                scaleY = 1.0
                scaleX = 1.0
                color = (254, 255, 169, min(int(255 * a), 255))

            x1 = int(x - Vcos * self.lineLength / 2 * scaleX)
            y1 = int(y - Vsin * self.lineLength / 2 * scaleX)
            x2 = int(x + Vcos * self.lineLength / 2 * scaleX)
            y2 = int(y + Vsin * self.lineLength / 2 * scaleX)

            y1 = self.height - y1
            y2 = self.height - y2

            if self.enableMapping:
                x1 = self.mappingX(x1)
                y1 = self.mappingY(y1)
                x2 = self.mappingX(x2)
                y2 = self.mappingY(y2)

            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)

            skip = max(x_min, 0) > min(x_max, self.width) or max(y_min, 0) > min(y_max, self.height)

            if not skip and a > 0.01:
                self.lineCount += 1
                pygame.draw.line(
                    self.foreground_layer, color,
                    start_pos=(x1, y1),
                    end_pos=(x2, y2),
                    width=round(self.lineWidth * scaleY),
                )

            if self.enable3D:
                line.cmrDx = -math.cos(math.radians(r)) * (self.cmrX - x) - math.sin(math.radians(r)) * (self.height - self.cmrY -y)
                line.cmrH = -(math.sin(math.radians(r)) * (self.cmrX - x) - math.cos(math.radians(r)) * (self.height - self.cmrY -y)) / self.Y

        self.lineCost = mytimer("判定线")

        for line in self.chart.lineList:
            x = line.move1(self.timeT) * self.width
            y = line.move2(self.timeT) * self.height
            r = line.rotate(self.timeT)
            self.h = line.cmrH

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
                if self.chart.RPE_Chart:
                    dyt = (note.floorPosT - line.pos(self.timeT)) * self.Y

                if self.enable3D:

                    xt = x + dx * Vcos
                    yt = y + dx * Vsin
                    if not (-self.noteSize*0.5 < xt < self.width+self.noteSize*0.5
                            and -self.noteSize*0.5 < yt < self.height+self.noteSize*0.5):
                        continue

                    # 3D修正
                    dyo = dy * self.speed
                    dyto = min(dyt * self.speed, self.boundary)
                    dy = dy * self.speed
                    dyt = min(dyt * self.speed, self.boundary)
                    # dxt = dx * (self.Y * self.cmrB / (dyto + self.Y * self.cmrB))
                    # dx = dx * (self.Y * self.cmrB / (dyo + self.Y * self.cmrB))
                    dxt = dx - (dx + line.cmrDx) * (1 - self.Y * self.cmrB / (dyto + self.Y * self.cmrB))
                    dx = dx - (dx + line.cmrDx) * (1 - self.Y * self.cmrB / (dyo + self.Y * self.cmrB))
                    dy = (dy * self.Y * self.h) / (self.Y * self.cmrB + dy)
                    dyt = (dyt * self.Y * self.h) / (self.Y * self.cmrB + dyt)

                    if not note.above:
                        dy = -dy
                        dyt = -dyt

                else:
                    dxt = dx

                if note.above:
                    xn = x + dx * Vcos - dy * Vsin
                    yn = y + dx * Vsin + dy * Vcos
                    xnt = x + dxt * Vcos - dyt * Vsin
                    ynt = y + dxt * Vsin + dyt * Vcos
                else:
                    xn = x + dx * Vcos + dy * Vsin
                    yn = y + dx * Vsin - dy * Vcos
                    xnt = x + dxt * Vcos + dyt * Vsin
                    ynt = y + dxt * Vsin - dyt * Vcos

                # 根据时间判断，跳过渲染还是添加特效
                frameDelta = 0.5 / self.FPS * self.BPM / 1.875 * 0

                if note.time_ < self.timeT + frameDelta < note.time_ + note.holdTime:
                    if self.frameIndex % 10 == 0:
                        effect = HitEffect(xn, yn)
                        self.hitEffectList.append(effect)

                elif note.time_ + note.holdTime < self.timeT + frameDelta:
                    note.hit = True
                    self.combo += 1
                    self.score += 1 * 10 ** 6 / self.chart.noteCount
                if note.time_ < self.timeT + frameDelta and not note.begin:
                    note.begin = True
                    self.tapSound.play()

                if note.alpha == 0:
                    continue

                if self.enable3D and (dyo > self.boundary or dyo < -self.cmrB * self.Y):
                    continue

                if self.enable3D:
                    ns1 = self.noteSize * (self.Y * self.cmrB / (dyo + self.Y * self.cmrB))
                    nst = self.noteSize * (self.Y * self.cmrB / (dyto + self.Y * self.cmrB))
                else:
                    ns1, nst = self.noteSize, self.noteSize

                x1 = int(xn - Vcos * ns1 / 2)
                y1 = int(yn - Vsin * ns1 / 2)
                x2 = int(xn + Vcos * ns1 / 2)
                y2 = int(yn + Vsin * ns1 / 2)
                x3 = int(xnt - Vcos * nst / 2)
                y3 = int(ynt - Vsin * nst / 2)
                x4 = int(xnt + Vcos * nst / 2)
                y4 = int(ynt + Vsin * nst / 2)

                y1 = self.height - y1
                y2 = self.height - y2
                y3 = self.height - y3
                y4 = self.height - y4

                if self.enableMapping:
                    x1 = self.mappingX(x1)
                    x2 = self.mappingX(x2)
                    x3 = self.mappingX(x3)
                    x4 = self.mappingX(x4)
                    y1 = self.mappingY(y1)
                    y2 = self.mappingY(y2)
                    y3 = self.mappingY(y3)
                    y4 = self.mappingY(y4)

                if self.enable3D:
                    self.holdRender3D(x1, x2, x3, x4, y1, y2, y3, y4, r, note.above)
                else:
                    self.holdRender(x1, x2, x3, x4, y1, y2, y3, y4, r, note.above)
                # pygame.draw.polygon(self.foreground_layer, self.BLACK, ((x1, y1), (x2, y2), (x3, y3), (x4, y4)))

        self.holdCost = mytimer("hold")

        for line in self.chart.lineList:
            x = line.move1(self.timeT) * self.width
            y = line.move2(self.timeT) * self.height
            r = line.rotate(self.timeT)
            self.h = line.cmrH

            Vsin = math.sin(math.radians(r))
            Vcos = math.cos(math.radians(r))

            for note in line.noteList:

                if note.type_ == 3:
                    continue
                if note.hit:
                    continue

                dx = note.posX * self.X
                dy = note.speed * (note.floorPos - line.pos(self.timeT)) * self.Y

                if self.enable3D:

                    xt = x + dx * Vcos
                    yt = y + dx * Vsin
                    if not (-self.noteSize*0.5 < xt < self.width+self.noteSize*0.5
                            and -self.noteSize*0.5 < yt < self.height+self.noteSize*0.5):
                        if self.enableCompiler and note.tempLine1 is not None:
                            self.freeTempLine(note.tempLine1, note)
                            self.freeTempLineBG(note.tempLine2, note, True)
                            note.tempLine1 = None
                            note.tempLine2 = None
                        continue

                    # 3D修正
                    dyo = dy * self.speed
                    dy = dy * self.speed
                    # dx = dx * (self.Y * self.cmrB / (dyo + self.Y * self.cmrB))
                    dx = dx - (dx + line.cmrDx) * (1 - self.Y * self.cmrB / (dyo + self.Y * self.cmrB))
                    dy = (dy * self.h * self.Y) / (self.Y * self.cmrB + dy)

                    if not note.above:
                        dy = -dy

                if note.above:
                    xn = x + dx * Vcos - dy * Vsin
                    yn = y + dx * Vsin + dy * Vcos
                else:
                    xn = x + dx * Vcos + dy * Vsin
                    yn = y + dx * Vsin - dy * Vcos

                # 根据时间判断，跳过渲染还是添加特效
                frameDelta = 0.5 / self.FPS * self.BPM / 1.875 * 0
                if note.time_ < self.timeT + frameDelta:
                    effect = HitEffect(*self.getNoteHitPos(line, note))
                    self.hitEffectList.append(effect)
                    note.hit = True
                    self.combo += 1
                    self.score += 1 * 10 ** 6 / self.chart.noteCount

                    # 播放音效
                    if note.type_ == 1:
                        self.tapSound.play()
                    elif note.type_ == 2:
                        self.dragSound.play()
                    elif note.type_ == 4:
                        self.flickSound.play()

                if self.timeT > note.time_ and self.enableCompiler:
                    self.freeTempLine(note.tempLine1, note)
                    self.freeTempLineBG(note.tempLine2, note, True)
                    note.tempLine1 = None
                    note.tempLine2 = None
                    continue

                if note.alpha == 0:
                    continue

                if self.enable3D and (dyo > self.boundary or dyo < -self.cmrB * self.Y):
                    continue

                if self.enableMapping:
                    xn = self.mappingX(xn)
                    yn = self.mappingY(yn)

                if (xn < -self.noteSize or xn > self.width + self.noteSize)\
                        or (yn < -self.noteSize or yn > self.height + self.noteSize):
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

                if self.enable3D:
                    try:
                        sr = self.Y * self.cmrB / (dyo + self.Y * self.cmrB)
                        # sr = self.Y / (dy + self.Y)
                        surface = pygame.transform.scale(
                            surface,
                            (surface.get_width() * sr, surface.get_height() * sr),
                        )
                    except ValueError as e:
                        print(f"渲染错误: {e}, note: {note}, timeT: {self.timeT}, xn: {xn}, yn: {yn}")
                        continue

                if self.enableCompiler:

                    if note.tempLine1 is None:
                        tmpL1 = self.getTempLine()
                        tmpL2 = self.getTempLineBG()
                        note.tempLine1 = tmpL1
                        note.tempLine2 = tmpL2

                        tmpL1.alpha.addPeriod(tmpL1.alpha.latestTimeT(), self.timeT, 0, 0)
                        tmpL1.move1.addPeriod(tmpL1.move1.latestTimeT(), self.timeT, -100, xn/self.width)
                        tmpL1.move2.addPeriod(tmpL1.move2.latestTimeT(), self.timeT, -100, yn/self.height)
                        tmpL1.scaleX.addPeriod(tmpL1.scaleX.latestTimeT(), self.timeT, 1.0, self.noteSize/1.06*sr/self.lineLength)
                        tmpL1.scaleY.addPeriod(tmpL1.scaleY.latestTimeT(), self.timeT, 1.0, self.noteSize/10*sr/self.lineWidth)
                        tmpL1.rotate.addPeriod(tmpL1.rotate.latestTimeT(), self.timeT, 0, r)

                        tmpL2.alpha.addPeriod(tmpL2.alpha.latestTimeT(), self.timeT, 0, 0)
                        tmpL2.move1.addPeriod(tmpL2.move1.latestTimeT(), self.timeT, -100, xn/self.width)
                        tmpL2.move2.addPeriod(tmpL2.move2.latestTimeT(), self.timeT, -100, yn/self.height)
                        tmpL2.scaleX.addPeriod(tmpL2.scaleX.latestTimeT(), self.timeT, 1.0, self.noteSize*sr/self.lineLength)
                        tmpL2.scaleY.addPeriod(tmpL2.scaleY.latestTimeT(), self.timeT, 1.0, self.noteSize/10*sr/self.lineWidth)
                        tmpL2.rotate.addPeriod(tmpL2.rotate.latestTimeT(), self.timeT, 0, r)

                    else:

                        tmpL1 = note.tempLine1
                        tmpL1.alpha.addPeriod(tmpL1.alpha.latestTimeT(), self.timeT, 1.0, 1.0)
                        tmpL1.move1.addPeriod(tmpL1.move1.latestTimeT(), self.timeT, tmpL1.move1.latestValue(), xn/self.width)
                        tmpL1.move2.addPeriod(tmpL1.move2.latestTimeT(), self.timeT, tmpL1.move2.latestValue(), yn/self.height)
                        tmpL1.scaleX.addPeriod(tmpL1.scaleX.latestTimeT(), self.timeT, tmpL1.scaleX.latestValue(), self.noteSize/1.06*sr/self.lineLength)
                        tmpL1.scaleY.addPeriod(tmpL1.scaleY.latestTimeT(), self.timeT, tmpL1.scaleY.latestValue(), self.noteSize/10*sr/self.lineWidth)
                        tmpL1.rotate.addPeriod(tmpL1.rotate.latestTimeT(), self.timeT, tmpL1.rotate.latestValue(), r)

                        tmpL2 = note.tempLine2
                        tmpL2.alpha.addPeriod(tmpL2.alpha.latestTimeT(), self.timeT, 1.0, 1.0)
                        tmpL2.move1.addPeriod(tmpL2.move1.latestTimeT(), self.timeT, tmpL2.move1.latestValue(), xn/self.width)
                        tmpL2.move2.addPeriod(tmpL2.move2.latestTimeT(), self.timeT, tmpL2.move2.latestValue(), yn/self.height)
                        tmpL2.scaleX.addPeriod(tmpL2.scaleX.latestTimeT(), self.timeT, tmpL2.scaleX.latestValue(), self.noteSize*sr/self.lineLength)
                        tmpL2.scaleY.addPeriod(tmpL2.scaleY.latestTimeT(), self.timeT, tmpL2.scaleY.latestValue(), self.noteSize/10*sr/self.lineWidth)
                        tmpL2.rotate.addPeriod(tmpL2.rotate.latestTimeT(), self.timeT, tmpL2.rotate.latestValue(), r)


                x0 = int(xn - surface.get_width() / 2)
                y0 = int(yn + surface.get_height() / 2)
                y0 = self.height - y0

                # 显示非 above 键
                # if self.displayDebug and not note.above:
                #     pygame.draw.rect(
                #         self.foreground_layer,
                #         rect=(x0, y0, surface.get_width(), surface.get_height()),
                #         color=self.RED,
                #         width=1,
                #     )

                self.foreground_layer.blit(surface, (x0, y0))
                self.noteCount += 1

        self.noteCost = mytimer("note")


        # 绘制进度条
        pygame.draw.rect(
            self.foreground_layer,
            (255, 255, 255, 100),
            (0, 0, self.width * (self.timeS / self.waveDurationS), 8),
            width=0,
        )
        pygame.draw.rect(
            self.foreground_layer,
            (255, 255, 255, 200),
            (self.width * (self.timeS / self.waveDurationS), 0, 5, 8),
            width=0,
        )


        for effect in self.hitEffectList:
            if self.enableMapping:
                x = self.mappingX(effect.x) - self.hitEffectSize // 2
                y = self.mappingY(self.height - effect.y) - self.hitEffectSize // 2
            else:
                x = effect.x - self.hitEffectSize // 2
                y = self.height - effect.y - self.hitEffectSize // 2

            self.foreground_layer.blit(self.images.hit(effect.frame), (x, y))
            effect.frame += 1
        self.hitEffectList = [effect for effect in self.hitEffectList if effect.frame < len(self.images.preRendHit)]

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
                d = ((i / 100) * bodyHeight + topHeight) / height
                e = (((i + 1) / 100) * bodyHeight + topHeight) / height
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
                    image = pygame.transform.scale(self.images.div100HoldImages[i],
                                                   (self.images.noteWidth, bodyHeight / 100 + 1))
                    image = pygame.transform.rotate(image, angle)
                else:
                    image = pygame.transform.scale(self.images.div100HoldImages[i],
                                                   (self.images.noteWidth, bodyHeight / 100 + 1))
                    image = pygame.transform.rotate(image, angle + 180)

                self.foreground_layer.blit(image, (minX, minY))
                self.holdCount += 1
        elif height > 3000:
            for i in range(10):
                d = ((i / 10) * bodyHeight + topHeight) / height
                e = (((i + 1) / 10) * bodyHeight + topHeight) / height
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
                    image = pygame.transform.scale(self.images.div10HoldImages[i], (self.images.noteWidth, bodyHeight / 10 + 1))
                    image = pygame.transform.rotate(image, angle)
                else:
                    image = pygame.transform.scale(self.images.div10HoldImages[i], (self.images.noteWidth, bodyHeight / 10 + 1))
                    image = pygame.transform.rotate(image, angle + 180)

                self.foreground_layer.blit(image, (minX, minY))
                self.holdCount += 1
        elif height > 1000:
            for i in range(3):
                d = ((i / 3) * bodyHeight + topHeight) / height
                e = (((i + 1) / 3) * bodyHeight + topHeight) / height
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
                    image = pygame.transform.scale(self.images.div3HoldImages[i], (self.images.noteWidth, bodyHeight / 3 + 1))
                    image = pygame.transform.rotate(image, angle)
                else:
                    image = pygame.transform.scale(self.images.div3HoldImages[i], (self.images.noteWidth, bodyHeight / 3 + 1))
                    image = pygame.transform.rotate(image, angle + 180)

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
                image = pygame.transform.scale(self.images.holdOriginalImage, (self.images.noteWidth, bodyHeight))
                image = pygame.transform.rotate(image, angle)
            else:
                image = pygame.transform.scale(self.images.holdOriginalImage, (self.images.noteWidth, bodyHeight))
                image = pygame.transform.rotate(image, angle + 180)

            self.foreground_layer.blit(image, (minX, minY))
            self.holdCount += 1

    def holdRender3D(self, x1, x2, x3, x4, y1, y2, y3, y4, angle: float, above):

        aw = x4 - x3
        a1 = x3 + aw * 0.00
        a2 = x3 + aw * 0.02
        a3 = x3 + aw * 0.08
        a4 = x3 + aw * 0.15
        a5 = x3 + aw * 0.20
        a6 = x3 + aw * 0.80
        a7 = x3 + aw * 0.85
        a8 = x3 + aw * 0.92
        a9 = x3 + aw * 0.98
        a0 = x3 + aw * 1.00

        tw = x2 - x1
        t1 = x1 + tw * 0.00
        t2 = x1 + tw * 0.02
        t3 = x1 + tw * 0.08
        t4 = x1 + tw * 0.15
        t5 = x1 + tw * 0.20
        t6 = x1 + tw * 0.80
        t7 = x1 + tw * 0.85
        t8 = x1 + tw * 0.92
        t9 = x1 + tw * 0.98
        t0 = x1 + tw * 1.00

        ah = y4 - y3
        ay1 = y3 + ah * 0.00
        ay2 = y3 + ah * 0.02
        ay3 = y3 + ah * 0.08
        ay4 = y3 + ah * 0.15
        ay5 = y3 + ah * 0.20
        ay6 = y3 + ah * 0.80
        ay7 = y3 + ah * 0.85
        ay8 = y3 + ah * 0.92
        ay9 = y3 + ah * 0.98
        ay0 = y3 + ah * 1.00

        th = y2 - y1
        ty1 = y1 + th * 0.00
        ty2 = y1 + th * 0.02
        ty3 = y1 + th * 0.08
        ty4 = y1 + th * 0.15
        ty5 = y1 + th * 0.20
        ty6 = y1 + th * 0.80
        ty7 = y1 + th * 0.85
        ty8 = y1 + th * 0.92
        ty9 = y1 + th * 0.98
        ty0 = y1 + th * 1.00



        # 绘制白色多边形
        pygame.draw.polygon(
            self.foreground_layer, (255, 255, 255),
            ((t1, ty1), (t2, ty2), (a2, ay2), (a1, ay1),)
        )

        pygame.draw.polygon(
            self.foreground_layer, (255, 255, 255),
            ((t0, ty0), (t9, ty9), (a9, ay9), (a0, ay0),)
        )

        pygame.draw.polygon(
            self.foreground_layer, (212, 255, 255, 200),
            ((t3, ty3), (t8, ty8), (a8, ay8), (a3, ay3),)
        )

        pygame.draw.polygon(
            self.foreground_layer, (212, 255, 255),
            ((t4, ty4), (t5, ty5), (a5, ay5), (a4, ay4),)
        )

        pygame.draw.polygon(
            self.foreground_layer, (212, 255, 255),
            ((t6, ty6), (t7, ty7), (a7, ay7), (a6, ay6),)
        )

    def titleMsg(self, msg: str, subtitle: str = None):
        self.screen.blit(self.background_layer, (0, 0))

        draw_text(
            self.screen, msg,
            self.font48, self.WHITE,
            pos=(int(self.width / 2), int(self.height / 2 - 40)),
            align="C",
        )

        if subtitle is not None:
            draw_text(
                self.screen,
                subtitle,
                self.font18, self.WHITE,
                pos=(int(self.width / 2), int(self.height / 2 + 30)),
                align="C",
            )

        # 更新窗口
        pygame.display.flip()
        pygame.display.update()

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

    def mappingX(self, x) -> float:
        return self.mx1 + self.mw / self.width * x

    def mappingY(self, y) -> float:
        return self.my1 + self.mh / self.height * y

    def UIrender(self):

        if not self.displayUI:
            return

        if self.combo >= 3:
            draw_text(
                self.foreground_layer,
                str(self.combo),
                self.font48, self.WHITE,
                pos=(self.width // 2, 30),
                align="N",
            )
            draw_text(
                self.foreground_layer,
                self.subtitle,
                self.font18, self.WHITE,
                pos=(self.width // 2, 100),
                align="N",
            )

        draw_text(
            self.foreground_layer,
            f"{self.score:07.0f}",
            self.font36, self.WHITE,
            pos=(self.width - 30, 30),
            align="NE",
        )

        draw_text(
            self.foreground_layer,
            self.name,
            self.font24, self.WHITE,
            pos=(30, self.height - 30),
            align="SW",
        )

        draw_text(
            self.foreground_layer,
            self.level,
            self.font24, self.WHITE,
            pos=(self.width - 30, self.height - 30),
            align="SE",
        )

        if self.enableCompiler:
            draw_text(
                self.foreground_layer,
                f"转谱中"+"."*int(self.timeS%3),
                self.font48, self.WHITE,
                pos=(int(self.width/2), int(self.height/2-40)),
                align="C",
            )

            draw_text(
                self.foreground_layer,
                f"请静置等待完成",
                self.font18, self.WHITE,
                pos=(int(self.width/2), int(self.height/2+10)),
                align="C",
            )

            draw_text(
                self.foreground_layer,
                f"判定线总数：{len(self.allTempLinesBG)+len(self.allTempLines)+len(self.chart.lineList)}",
                self.font18, self.WHITE,
                pos=(int(self.width/2), int(self.height/2+60)),
                align="C",
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

        if self.timeCost * self.FPS > 1:
            color = self.RED
        elif self.timeCost * self.FPS > 0.8:
            color = self.YELLOW
        else:
            color = self.WHITE
        draw_text(
            self.foreground_layer,
            f"cost: {self.timeCost * 1000:.2f} ms ({self.timeCost * self.FPS:.2%})",
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
            f"hit: {self.hitBlockCost * 1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 60),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"effect: {self.effectCost * 1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 80),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"note: {self.noteCost * 1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 100),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"line: {self.lineCost * 1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 120),
            align="NW",
        )
        draw_text(
            self.foreground_layer,
            f"hold: {self.holdCost * 1000: .2f} ms",
            self.font18, self.WHITE,
            pos=(20, 140),
            align="NW",
        )

        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 60, self.hitBlockCost / (1 / self.FPS) * 100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 80, self.effectCost / (1 / self.FPS) * 100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 100, self.noteCost / (1 / self.FPS) * 100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 120, self.lineCost / (1 / self.FPS) * 100, 16))
        pygame.draw.rect(self.foreground_layer, self.WHITE, (200, 140, self.holdCost / (1 / self.FPS) * 100, 16))

    def initPlayer(self):
        # 初始化 pygame
        pygame.init()
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.set_num_channels(32)

        # 初始化营销
        self.tapSound = pygame.mixer.Sound("assets/click.wav")
        self.dragSound = pygame.mixer.Sound("assets/drag.wav")
        self.flickSound = pygame.mixer.Sound("assets/flick.wav")

        # 初始化映射
        if self.enableMapping:
            self.mx1 = self.targetRectOfMapping[0]
            self.mx2 = self.targetRectOfMapping[2]
            self.my1 = self.targetRectOfMapping[1]
            self.my2 = self.targetRectOfMapping[3]
            self.mw = self.mx2 - self.mx1
            self.mh = self.my2 - self.my1
            # self.noteSize *= self.mw / self.width
            self.hitEffectSize *= self.mw / self.width
            self.lineWidth = round(self.lineWidth * self.mw / self.width)

        # 初始化背景图
        try:
            if self.enableMapping:
                self.bgImage = pygame.image.load(self.illuFile).convert()
                self.bgImage = pygame.transform.scale(self.bgImage,
                                                               (self.width / self.FOM, self.height / self.FOM))
                self.bgImage1 = cv2_blur(self.bgImage, self.background_blurRadius / self.FOM)
                self.bgImage1 = apply_darken(self.bgImage1, self.background_brightness*0.4)
                self.bgImage1 = pygame.transform.smoothscale(self.bgImage1, (self.width, self.height))

                self.bgImage2 = cv2_blur(self.bgImage, self.background_blurRadius / self.FOM)
                self.bgImage2 = apply_darken(self.bgImage2, self.background_brightness)
                self.bgImage2 = pygame.transform.smoothscale(self.bgImage2, (self.mw, self.mh))
                self.bgImage1.blit(self.bgImage2, (self.mx1, self.my1), )
                self.background_layer = self.bgImage1
            else:
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
            self.font36 = pygame.font.Font('assets/phigros.ttf', 48)
            self.font24 = pygame.font.Font('assets/phigros.ttf', 32)
            self.font18 = pygame.font.Font('assets/phigros.ttf', 24)
            self.font48 = pygame.font.Font('assets/phigros.ttf', 64)
        except Exception as e:
            traceback.print_exc()
            self.font36 = pygame.font.SysFont(None, 48)
            self.font24 = pygame.font.SysFont(None, 32)
            self.font18 = pygame.font.SysFont(None, 24)
            self.font48 = pygame.font.SysFont(None, 64)

        # 预渲染缓存器
        if self.enableMapping:
            self.images = PreRendCache(self.noteSize * self.mw / self.width, self.hitEffectSize)
        else:
            self.images = PreRendCache(self.noteSize, self.hitEffectSize)

        # 加载bgm
        pygame.mixer.music.load(self.audioFile)
        self.waveDurationS = pygame.mixer.Sound(self.audioFile).get_length()

        # 显示消息
        self.titleMsg("读取谱面中", "少女祈祷中...")

        # 加载铺面数据
        self.chart = analyzer.analyzeJson(self.chartFile)
        self.BPM = self.chart.lineList[0].bpm

        # 转谱处理Hold
        if self.enableCompiler:
            self.subtitle = "COMPILER"

            for line in self.chart.lineList:
                for note in line.noteList:
                    if note.type_ == 3:
                        note.holdTime = 0
                        note.type_ = 1
                        note.speed = 1.0

    def mainloop(self):

        global running
        running = True
        clock = pygame.time.Clock()
        # 计时器，用于评估性能
        timer = time.time()
        self.timeCost = 10 ** -6
        delta = 10 ** -6
        # 用于统计平均帧数
        frameCount = 0
        self.frameIndex = 0
        self.secondCount = self.FPS
        # 计算铺面延迟
        self.timeS = - self.chartDelay + self.startTimeS
        self.timeT = self.timeS * self.BPM / 1.875
        # 是否处于低镜头模式
        pressDown: bool = False

        # 播放bgm
        pygame.mixer.music.play(start=self.startTimeS)

        # 处理startTimeS前的所有note
        for note in self.chart.noteList:
            if note.time_ < self.timeT:
                note.hit = True

        while running:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    # return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.pause = not self.pause

            if self.pause:
                clock.tick(self.FPS)
                continue

            if self.timeS > self.waveDurationS:
                running = False
                break

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
                print(f"Render Error at timeT={self.timeT}, timeS={self.timeS}")

            # 3. 更新显示
            self.screen.blit(self.background_layer, (0, 0))
            self.screen.blit(self.foreground_layer, (0, 0))
            pygame.display.flip()

            if self.enableCompiler:
                self.timeS += 1 / self.FPS
                self.timeT = self.timeS * self.BPM / 1.875
            else:
                # 控制帧率
                self.timeCost = time.time() - timer + 0.00001
                clock.tick(self.FPS)
                # 统计帧数
                frameCount += 1
                self.frameIndex += 1
                if timer // 1 != time.time() // 1:
                    self.secondCount = frameCount
                    frameCount = 0

                current = time.time()
                delta = current - timer
                timer = current
                self.timeS += delta
                self.timeT = self.timeS * self.BPM / 1.875

        # 导出谱面
        if self.enableCompiler:
            print("output here")
            self.outputChart()

        # 退出窗口
        pygame.quit()

    def outputChart(self):

        self.titleMsg("编码中", "请勿关闭窗口")

        for line in self.chart.lineList:
            for note in line.noteList:
                note.alpha = 0

        for tmpL in self.allTempLinesBG + self.allTempLines:
            tmpL.alpha.addPeriod(tmpL.alpha.latestTimeT(), 99999999, 0, 0)
            tmpL.move1.addPeriod(tmpL.move1.latestTimeT(), 99999999, -1, -1)
            tmpL.move2.addPeriod(tmpL.move2.latestTimeT(), 99999999, -1, -1)
            tmpL.scaleX.addPeriod(tmpL.scaleX.latestTimeT(), 99999999, 1.0, 1.0)
            tmpL.scaleY.addPeriod(tmpL.scaleY.latestTimeT(), 99999999, 1.0, 1.0)
            tmpL.rotate.addPeriod(tmpL.rotate.latestTimeT(), 99999999, 0, 0)
            tmpL.color.addPeriod(tmpL.color.latestTimeT(), 99999999, [255, 255, 255], [255, 255, 255])
            self.chart.addLine(tmpL)

        # RPE META 数据
        self.chart.RPE_level = 160
        self.chart.name = self.name
        self.chart.level = self.level
        self.chart.song = os.path.basename(self.audioFile)
        self.chart.bg = os.path.basename(self.illuFile)
        self.chart.duration = self.waveDurationS
        self.chart.chartTime = self.waveDurationS

        info = f"""#
Name: {self.chart.name}
Path: {self.chart.id}
Song: {self.chart.song}
Picture: {self.chart.bg}
Chart: 3dChart.json
Level: {self.chart.level}
Composer: {self.chart.composer}
Charter: {self.chart.charter}
Illustrator: {self.chart.illustration}"""

        clear_directory("temp")
        clear_directory("output", clear=False)

        with open("temp/3dChart.json", "w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(self.chart.toRPEJson(), ensure_ascii=False))
            print("成功导出")

        with open("temp/info.txt", "w", encoding="utf-8") as outfile:
            outfile.write(info)
            print("成功导出")

        self.titleMsg("打包中", "请勿关闭窗口")

        # 创建一个新的 ZIP 文件并添加文件
        with zipfile.ZipFile("output/"+self.name+'.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write("temp/3dChart.json", "3dChart.json")
            zipf.write("temp/info.txt", "info.txt")
            zipf.write(self.audioFile, self.chart.song)
            zipf.write(self.illuFile, self.chart.bg)

            # 使用explorer的/select参数
            open_explorer_and_select_file("output/"+self.name+'.zip')