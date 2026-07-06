import enum
import zipfile
import toml

import subprocess
import threading
import multiprocessing as mp

from tkinter import filedialog
from tkinter import messagebox
from tk.FastBezierLookup import *
from tk.chartException import *
from tk.cubic_spline import *
import tk.tomlIO as tomlIO
from tk.mixer import *
from tk.mytk import *
from libs.chart import *

import player

clear_directory = player.clear_directory
open_explorer_and_select_file = player.open_explorer_and_select_file


class ScreenMode(enum.Enum):
    NOTE = 0
    MOVE1 = 1
    MOVE2 = 2
    SPEED = 3
    ALPHA = 4
    ROTATE = 5
    THETA = 6
    MOVE3 = 7


def timeTtoBeat(timeT: float):
    if timeT % 32 == 0:
        return f"{timeT // 32:.0f}+0/1"
    elif timeT % 32 == 4:
        return f"{timeT // 32:.0f}+1/8"
    elif timeT % 32 == 8:
        return f"{timeT // 32:.0f}+1/4"
    elif timeT % 32 == 12:
        return f"{timeT // 32:.0f}+3/8"
    elif timeT % 32 == 16:
        return f"{timeT // 32:.0f}+1/2"
    elif timeT % 32 == 20:
        return f"{timeT // 32:.0f}+5/8"
    elif timeT % 32 == 24:
        return f"{timeT // 32:.0f}+3/4"
    elif timeT % 32 == 28:
        return f"{timeT // 32:.0f}+7/8"
    else:
        return f"{timeT // 32:.0f}+{timeT % 32:.0f}/32"


def PlayerProcess(chart: Chart, audioFile, illuFile, startTime: float, enable3D: bool):
    from player import Player

    chart.fastCalcFloorPos()

    player = Player(w=1000, h=800, fps=120)
    player.enable3D = enable3D
    player.displacementY = 1.0
    player.audioFile = audioFile
    player.illuFile = illuFile
    player.BPM = chart.bpm

    # 设置副标题
    player.name = chart.name
    player.level = chart.level
    player.subtitle = "PREVIEW"
    player.chartDelay = 0.0

    # 跳转起始时间
    player.startTimeS = startTime / chart.bpm * 1.875

    player.initPlayer()
    player.chart = chart
    player.mainloop()


def cmrCast(cmrX: float, cmrY: float, cmrZ: float, x, y, z):
    x0 = (-cmrZ * x + cmrX * z) / (z - cmrZ)
    y0 = (-cmrZ * y + cmrY * z) / (z - cmrZ)
    return (x0, y0)

def AnyTime2OffTime(rpeT: str) -> float:
    rpeSymb = (" ", ":", "：", "+", "/", "，")
    for symb in rpeSymb:
        if symb in rpeT:
            rpeT = rpeT.replace(" ", ",")
            rpeT = rpeT.replace(":", ",")
            rpeT = rpeT.replace("：", ",")
            rpeT = rpeT.replace("+", ",")
            rpeT = rpeT.replace("/", ",")
            rpeT = rpeT.replace("，", ",")
            rpeT = rpeT.split(",")
            try:
                rpeT[0] = int(rpeT[0])
                rpeT[1] = int(rpeT[1])
                rpeT[2] = int(rpeT[2])
            except ValueError:
                raise ValueError("RPE时间格式有误。")
            except IndexError:
                raise ValueError("RPE时间格式有误。")
            return (rpeT[0] + rpeT[1] / rpeT[2]) * 32
    try:
        return float(rpeT)
    except ValueError:
        raise ValueError("时间格式有误。")

def OffTime2RpeTime(timeT: float) -> str:
    return timeTtoBeat(timeT)


with open("tk/assets/key.txt", encoding="utf-8") as f:
    TIP_TEXT = f.read()
with open("tk/assets/about.txt", encoding="utf-8") as f:
    ABOUT_TEXT = f.read()


class Handle:
    def isObj(self, obj: Note | Event) -> bool:
        return False


class EventHandle(Handle):
    def __init__(self, lineTimer: LineTimer, index: int, type_: ScreenMode, x1: float, x2: float, y1: float, y2: float):
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2
        self.lineTimer = lineTimer
        self.index = index
        self.type_ = type_

    def isObj(self, obj: Note | Event) -> bool:
        if isinstance(obj, Note):
            return False
        elif isinstance(obj, Event):
            return obj.isHandle(self)


class NoteHandle(Handle):
    def __init__(self, note: Note, x: float, y: float, width: int, lineIndex=None):
        self.x = x
        self.y = y
        self.note = note
        self.width = width
        self.lineIndex = lineIndex

    def isObj(self, obj: Note | Event) -> bool:
        return obj is self.note


class HoldHandle(Handle):
    def __init__(self, note: Note, x: float, y1: float, y2: float, lineIndex=None):
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.note = note
        self.lineIndex = lineIndex

    def isObj(self, obj: Note | Event) -> bool:
        return obj is self.note


class Event:
    def __init__(self, handle: "EventHandle" = None, lineTimer=None, index=None):
        if handle is not None:
            self.lineTimer: LineTimer = handle.lineTimer
            self.index: int = handle.index
        elif lineTimer is not None:
            self.lineTimer: LineTimer = lineTimer
            self.index: int = index
        else:
            raise ValueError("Either handle or lineTimer must be set")

    def isHandle(self, handle: "EventHandle"):
        return handle.lineTimer is self.lineTimer and handle.index == self.index

    @property
    def st(self):
        return self.lineTimer.startTimeList[self.index]

    @property
    def et(self):
        return self.lineTimer.endTimeList[self.index]

    @property
    def sv(self):
        return self.lineTimer.startValueList[self.index]

    @property
    def ev(self):
        return self.lineTimer.endValueList[self.index]

    def easing(self):
        return self.lineTimer.easingTypeList[self.index]

    def setSt(self, st):
        self.lineTimer.startTimeList[self.index] = st

    def setEt(self, et):
        self.lineTimer.endTimeList[self.index] = et

    def setSv(self, sv):
        self.lineTimer.startValueList[self.index] = sv

    def setEv(self, ev):
        self.lineTimer.endValueList[self.index] = ev

    def setEasing(self, easing: int):
        self.lineTimer.easingTypeList[self.index] = easing

class Arange:
    def __init__(self, start, stop, step):
        self.start = start
        self.stop = stop
        self.step = step
        self.current = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current >= self.stop:
            raise StopIteration
        self.current += self.step
        return self.current


class TimelineEditor:
    def __init__(self, chart: Chart, audioFile: str, illuFile: str, projectDir: str):
        self.lineIndex = 0
        self.chart = chart
        self.line = chart.lineList[0]

        # 当前底部时间
        self.t0 = 0
        # 最大时间
        self.t1 = 9999
        # 底部到顶部的时间差
        self.dt = 128
        # 编辑器的时间
        self.ts = 64
        # canvas 高度
        self.h0 = 720
        self.w0 = 500
        # 被选中的 note
        self.selected = []
        # 自动吸附
        self.adsorption = True
        self.Xrecord = set()
        # 当前编辑器的操作对象
        self.screenMode: ScreenMode = ScreenMode.NOTE
        # 当前编辑器的渲染对象
        self.handles: list[Handle] = []

        # 启用新ui
        self.enableClassicUI = False

        # 显示判定范围
        self.displayJudgeArea = False

        # 设置横竖线
        self.lineXNum = 10
        self.lineTNum = 8

        # 正在播放
        self.playing = None
        self.playStartTime = 0

        # 音乐文件
        self.audioFile = audioFile
        self.audioFile_025x = None
        self.audioFile_075x = None
        self.audioFile_050x = None
        # 音乐文件
        self.illuFile = illuFile
        # 项目之所在地
        self.projectDir = projectDir

        # 换线的Frame
        self.altFrame: Frame | None = None
        self.alfFrameLabelList: list[LabelDark] = []

        # 绘制长条等时，拖动产生的临时数据
        self.startCast: list | None = None
        self.highlightNote: Note | None = None
        self.highlightHandle: Handle | None = None

        # 左键操作时，产生的临时数据
        self.mouseStartCast: tuple | None = None
        self.mouseOperationType: Handle | None = None
        # 左键框选时，出现的框框数据
        self.selectingRectP1: tuple | None = None
        self.selectingRectP2: tuple | None = None

        # 剪贴板
        self.clipboard: Period | None = None
        self.copyFrom: float | None = None

        # 屏幕
        self.sw0 = None
        self.sh0 = None
        self.sw1 = None
        self.sh1 = None

        # tab切线相关
        self.tabDragStartPos: tuple | None = None
        self.tabFrame: Canvas|None = None

        # 曲线锚点
        self.acr1T: float | None = None
        self.acr2T: float | None = None
        self.acr1V: float | None = None
        self.acr2V: float | None = None
        self.bezierCurve: None | FastBezierLookup = None
        self.curvingHandle: EventHandle | None = None

        # # 播放器
        mixer.init()
        mixer.music.load(self.audioFile)
        mixer.music.play()
        mixer.music.pause()

        # 当前倍率
        self.speed = 1.0

        # self.audioPlayer = PygameAudioPlayer.NonBlockingAudioPlayer(self.audioFile)
        # self.audioPlayer.play(speed=1.0)
        # self.audioPlayer.pause()
        # 初始化营销
        self.tapSound = mixer.Sound("assets/click.wav")
        self.dragSound = mixer.Sound("assets/drag.wav")
        self.flickSound = mixer.Sound("assets/flick.wav")
        self.lastFrameTime = time.time()

        # 撤销
        self.operationRecord: list[tuple[int, Line, str]] = []
        self.undoRecord: list[tuple[int, Line, str]] = []
        ## 避免拖动时频繁记录撤销
        self.dragCD: bool = False
        ## 自动保存触发器
        self.lastTimeOfAutoSave = time.time()

        # 报错窗口
        self.checkWindows = None

        self.top = Tk()
        self.top.title("时间轴编辑器")
        self.top.geometry("1200x800")
        self.top.iconbitmap("assets/logo.ico")
        self.top.minsize(1200, 800)
        self.top.config(padx=40, pady=30)
        self.top.config(bg="#222")

        # 工具栏
        self.toolFrame = FrameDark(self.top, height=30)
        self.toolFrame.pack(side=TOP, fill=X)
        self.toolFrameSpace = FrameDark(self.top, height=10)
        self.toolFrameSpace.pack(side=TOP, fill=X)
        # 属性栏
        self.attrFrame = FrameDark(self.top)
        self.attrFrame.pack(side=RIGHT, fill=Y)
        ## 键类型选择
        noteFgList = (TAP_COLOR, DRAG_COLOR, HOLD_COLOR, FLICK_COLOR)
        noteList = ("Tap", "Drag", "Hold", "Flick")
        self.tf0rb1 = LiToolBox(self.toolFrame, noteList, noteFgList, lambda x: self.changeScreenMode(ScreenMode.NOTE))
        self.tf0rb1.build(0, 0, 200, 30)
        ## 吸附
        # self.tf0tb0 = LiToolBotton(self.toolFrame)
        # self.tf0tb0.build(210, 0, 40, 30, text="吸附", value=True)
        # self.tf0bt1 = LiButtonDark(self.toolFrame, text="属性", command=self.button2Event)
        # self.tf0bt1.place(x=250, y=0, width=40, height=30)
        # self.tf0bt1 = LiButtonDark(self.toolFrame, text="缩放", command=self.setScale)
        # self.tf0bt1.place(x=290, y=0, width=70, height=30)
        # self.tf0bt1 = LiButtonDark(self.toolFrame, text="导出与错误检查", command=self.export)
        # self.tf0bt1.place(x=360, y=0, width=100, height=30)

        ## 选中
        noteFgList = (None, MOVE1_COLOR, MOVE2_COLOR, MOVE3_COLOR, ALPHA_COLOR, ROTATE_COLOR, SPEED_COLOR, THETA_COLOR)
        noteList = ("Note", "move1", "move2", "move3", "Alpha", "Rotate", "Speed", "Theta")
        self.tf0rb2 = LiToolBox(self.toolFrame, noteList, noteFgList, self.changeScreenModeByToolBox)
        self.tf0rb2.build(210, 0, 400, 30)
        self.bt1 = LiButtonDark(self.toolFrame, text="预览（PhiChart Player）", height=2, command=self.launchPlayer, var=0)
        self.bt1.place(x=620, y=0, width=200, height=30)
        self.bt2 = ButtonDark(self.toolFrame, text="1.0x", height=2, command=self.changeSpeed)
        self.bt2.place(x=830, y=0, width=60, height=30)
        self.bt3 = ButtonDark(self.toolFrame, text="+关键帧", height=2, command=self.addKeyFrame)
        self.bt3.place(x=900, y=0, width=80, height=30)
        self.bt3 = ButtonDark(self.toolFrame, text="喵~", height=2, command=self.changeUI)
        self.bt3.place(x=990, y=0, width=40, height=30)

        self.canvas = Canvas(self.top, width=self.w0, height=self.h0, bg="#333", highlightthickness=0)
        self.canvas.pack(side=LEFT, fill=Y)
        self.scroller = Canvas(self.top, width=20, height=self.h0, bg="#333", highlightthickness=0)
        self.scroller.pack(side=LEFT, padx=5, fill=Y)
        self.sp1 = LabelDark(self.top, width=1)
        self.sp1.pack(side=LEFT)
        self.fr1 = FrameDark(self.top)
        self.fr1.pack(side=RIGHT, fill=BOTH, expand=1)
        self.lf1 = FrameDark(self.fr1, height=200)
        self.lf1.pack(side=TOP, fill=X)

        self.if0 = FrameDark(self.fr1)
        self.if0.pack(side=TOP, fill=X)
        self.if0.columnconfigure(0, weight=1)
        self.if0.rowconfigure(0, weight=1)

        self.lf0 = LabelFrameDark(self.if0, height=200, text="时间轴", padx=10, pady=5)
        self.lf0.grid(row=0, column=0, sticky=NSEW, padx=5, pady=5)
        self.lf2 = LabelFrameDark(self.if0, height=200, text="显示与编辑", padx=10, pady=5)
        self.lf2.grid(row=1, column=0, sticky=NSEW, padx=5, pady=5)
        self.lf3 = LabelFrameDark(self.if0, height=200, text="快捷键", padx=10, pady=5, width=300)
        self.lf3.grid(row=0, column=1, rowspan=2, sticky=NSEW, padx=10, pady=5)

        LabelDark(self.lf3, text=TIP_TEXT, justify=LEFT).pack(side=TOP, fill=X, expand=1)

        self.lf2fr2 = FrameDark(self.lf2, pady=5)
        self.lf2fr2.pack(side=TOP, fill=X)
        self.hooked = LiToolBotton(self.lf2fr2, text="钩定开关（G/Ctrl+H）", value=False)
        self.hooked.pack(side=LEFT, fill=BOTH, expand=1, ipadx=10)
        self.judge = LiToolBotton(self.lf2fr2, text="判定/可见范围", value=True, command=self.setDisplayJudgeArea)
        self.judge.pack(side=LEFT, fill=BOTH, expand=1, ipadx=10)
        self.lf2fr1 = FrameDark(self.lf2, pady=5)
        self.lf2fr1.pack(side=TOP, fill=X)
        self.xAds = LiToolBotton(self.lf2fr1, text="对齐到竖线", value=True)
        self.xAds.pack(side=LEFT, fill=BOTH, expand=1)
        self.tAds = LiToolBotton(self.lf2fr1, text="对齐到横线", value=False)
        self.tAds.pack(side=LEFT, fill=BOTH, expand=1, padx=10)
        self.ads = LiToolBotton(self.lf2fr1, text="自动对齐", value=False)
        self.ads.pack(side=LEFT, fill=BOTH, expand=1)

        LabelDark(self.lf2, text="横线数", anchor=W).pack(side=TOP, fill=X, expand=1)
        self.tf0et1 = LiIntEntryDark(self.lf2, self.lineTNum, command=self.setLineNumber, min=4, max=16)
        self.tf0et1.pack(side=TOP, fill=X)
        LabelDark(self.lf2, text="竖线数", anchor=W).pack(side=TOP, fill=X, expand=1)
        self.tf0et2 = LiIntEntryDark(self.lf2, self.lineXNum, command=self.setLineNumber, min=4, max=20)
        self.tf0et2.pack(side=TOP, fill=X)
        LabelDark(self.lf2, text="纵向显示拍数", anchor=W).pack(side=TOP, fill=X, expand=1)
        self.tf0et3 = LiFloatEntryDark(self.lf2, self.dt//32, command=self.setLineNumber, min=1, max=16)
        self.tf0et3.pack(side=TOP, fill=X)
        #lb1
        self.screen = Canvas(self.lf1, bg="#282828", highlightthickness=0)
        self.screen.pack(side=TOP, fill=BOTH, expand=1)

        # lb0
        self.font1 = font.Font(size=16, weight="bold")
        self.lf0lb1 = LabelDark(self.lf0, text="底部时间 Time(Beat)", anchor=W)
        self.lf0lb1.pack(side=TOP, fill=X)
        self.lf0et1 = LabelDark(self.lf0, anchor=W, font=self.font1)
        self.lf0et1.pack(side=TOP, fill=X)
        self.lf0lb2 = LabelDark(self.lf0, text="光标时间 Time(Beat)", anchor=W)
        self.lf0lb2.pack(side=TOP, fill=X)
        self.lf0et2 = LabelDark(self.lf0, anchor=W, font=self.font1)
        self.lf0et2.pack(side=TOP, fill=X)
        self.lf0lb3 = LabelDark(self.lf0, text="光标值 PosX", anchor=W)
        self.lf0lb3.pack(side=TOP, fill=X)
        self.lf0et3 = LabelDark(self.lf0, anchor=W, font=self.font1)
        self.lf0et3.pack(side=TOP, fill=X)

        ### 菜单栏
        self.menubar = Menu(self.top)
        self.top.config(menu=self.menubar)
        # 创建文件菜单
        file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="文件(F)", menu=file_menu)
        file_menu.add_command(label="保存", accelerator="Ctrl+S", command=self.save)
        file_menu.add_separator()
        file_menu.add_command(label="错误检查", accelerator="Ctrl+E", command=self.export)
        file_menu.add_command(label="导出为官谱格式", command=self.exportAsOfficial)
        file_menu.add_command(label="导出为RPE格式", command=self.exportAsRPE)
        file_menu.add_command(label="编译3D表演", command=self.exportAs3DPEZ)
        file_menu.add_separator()
        file_menu.add_command(label="打开项目所在的目录", command=self.openFileByExplorer)
        file_menu.add_command(label="恢复到自动保存的记录", command=self.recoverToAutoSave)
        file_menu.add_separator()
        file_menu.add_command(label="从Json文件导入", command=self.loadFromJson)
        file_menu.add_separator()
        file_menu.add_command(label="优化官谱", command=self.officialChartRefine)
        file_menu.add_separator()
        file_menu.add_command(label="关于", accelerator="F2", command=self.about)
        file_menu.add_separator()
        file_menu.add_command(label="退出", accelerator="Alt+F4", command=self.top.destroy)
        # 创建文件菜单
        edit_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="编辑(E)", menu=edit_menu)
        edit_menu.add_command(label="撤销", accelerator="Ctrl+Z", command=self.undo)
        edit_menu.add_command(label="重做", accelerator="Ctrl+Shift+Z", command=self.redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="复制", accelerator="Ctrl+C", command=self.copy)
        edit_menu.add_command(label="剪切", accelerator="Ctrl+X", command=self.cut)
        edit_menu.add_command(label="粘贴", accelerator="Ctrl+V", command=self.paste)
        edit_menu.add_separator()
        edit_menu.add_command(label="全选", accelerator="Ctrl+A", command=self.selectAll)
        edit_menu.add_command(label="删除", accelerator="Backspace", command=self.onBackspacePressed)
        edit_menu.add_separator()
        edit_menu.add_command(label="复制所有等时事件", accelerator="Ctrl+Shift+C", command=self.copyAll)
        edit_menu.add_command(label="粘贴到相同时间", accelerator="Ctrl+Shift+V", command=self.pasteBy)
        edit_menu.add_separator()
        edit_menu.add_command(label="踩音工具", accelerator="B", command=self.beater)
        edit_menu.add_command(label="Mixer", accelerator="M", command=self.star_mixer)
        edit_menu.add_separator()

        key_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="键(N)", menu=key_menu)
        key_menu.add_command(label="反转", command=self.mirrorX)
        key_menu.add_command(label="启用/禁用3D", command=self.ban3D)
        key_menu.add_separator()
        key_menu.add_command(label="键属性与参数", accelerator="中键", command=self.noteAttribute)
        key_menu.add_command(label="键高级筛选", accelerator="Ctrl+F", command=self.noteFilter)
        key_menu.add_separator()
        key_menu.add_command(label="切换下落方向", command=self.setNoteAbove)

        event_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="事件(M)", menu=event_menu)
        event_menu.add_command(label="反转", command=self.mirrorX)
        event_menu.add_separator()
        event_menu.add_command(label="属性与参数", accelerator="中键/右键", command=self.eventAttribute)
        event_menu.add_command(label="事件高级筛选", accelerator="Ctrl+F", command=self.noteFilter)
        event_menu.add_separator()
        event_menu.add_command(label="平滑（三次样条插值）", accelerator="Ctrl+Q", command=lambda: self.smooth(0))
        event_menu.add_command(label="平滑（贝塞尔曲线）", accelerator="Ctrl+W", command=lambda: self.smooth(1))
        event_menu.add_command(label="平滑（插值后三次样条）", accelerator="Ctrl+R", command=lambda: self.smooth(2))
        event_menu.add_command(label="平滑（插值后贝塞尔）", accelerator="Ctrl+T", command=lambda: self.smooth(3))
        event_menu.add_command(label="平滑（二次样条插值类）", command=lambda: self.smooth(4))
        event_menu.add_command(label="平滑（移动平均平滑）", command=lambda: self.smooth(5))
        event_menu.add_separator()
        event_menu.add_command(label="平滑（三次样条插值）", accelerator="Ctrl+Q", command=lambda: self.smooth(0))

        # 创建文件菜单
        view_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="视图(V)", menu=view_menu)
        view_menu.add_command(label="播放/暂停", accelerator="Space", command=self.play)
        view_menu.add_command(label="预览", accelerator="Ctrl+P", command=self.launchPlayer)
        view_menu.add_command(label="预览（启用3D）", command=lambda:self.launchPlayer(enable3D=True))

        self.top.bind("<Configure>", self.onConfigure)

        self.scroller.bind("<ButtonRelease-1>", self.onScrollerReleased)
        self.scroller.bind("<Button-1>", self.onScrollerPressed)
        self.scroller.bind("<MouseWheel>", self.onWheel)

        self.top.bind("<Key>", self.onKeyPressed)
        self.top.bind("<BackSpace>", self.onBackspacePressed)
        self.top.bind("<Delete>", self.onDeletePressed)

        self.top.bind("<KeyPress-Alt_L>", self.onAltPressed)
        self.top.bind("<KeyRelease-Alt_L>", self.onAltReleased)
        self.canvas.bind("<Control-Button-1>", self.onMouseControlPressed)
        self.canvas.bind("<Button-1>", self.onMousePressed)
        self.canvas.bind("<ButtonRelease-1>", self.onMouseReleased)
        self.canvas.bind("<Motion>", self.onMouseMotion)

        self.canvas.bind("<Button-3>", self.onRightButtonPressed)
        self.canvas.bind("<Button-2>", self.button2Event)
        self.top.bind("<space>", self.play)
        self.top.bind("<Return>", self.onEnterPressed)
        self.top.bind("<F2>", self.about)
        self.top.bind("<F2>", self.about)

        self.top.bind("<Control-Z>", self.undo)
        self.top.bind("<Control-z>", self.undo)
        self.top.bind("<Control-Shift-Z>", self.redo)
        self.top.bind("<Control-Shift-z>", self.redo)

        self.top.bind("<Control-X>", self.cut)
        self.top.bind("<Control-x>", self.cut)
        self.top.bind("<Control-S>", self.save)
        self.top.bind("<Control-s>", self.save)
        self.top.bind("<Control-C>", self.copy)
        self.top.bind("<Control-c>", self.copy)
        self.top.bind("<Control-B>", self.ban3D)
        self.top.bind("<Control-b>", self.ban3D)
        self.top.bind("<Control-V>", self.paste)
        self.top.bind("<Control-v>", self.paste)
        self.top.bind("<Control-F>", self.filter)
        self.top.bind("<Control-f>", self.filter)
        self.top.bind("<Control-E>", self.export)
        self.top.bind("<Control-e>", self.export)
        self.top.bind("<Control-M>", self.mirrorX)
        self.top.bind("<Control-m>", self.mirrorX)
        self.top.bind("<Control-A>", self.selectAll)
        self.top.bind("<Control-a>", self.selectAll)
        self.top.bind("<Control-P>", self.launchPlayer)
        self.top.bind("<Control-p>", self.launchPlayer)
        self.top.bind("<Control-Shift-C>", self.copyAll)
        self.top.bind("<Control-Shift-c>", self.copyAll)
        self.top.bind("<Control-Shift-V>", self.pasteBy)
        self.top.bind("<Control-Shift-v>", self.pasteBy)
        self.top.bind("<Control-H>", self.hooked.setvalue)
        self.top.bind("<Control-h>", self.hooked.setvalue)
        self.top.bind("<KeyPress-Tab>", self.onTabPressed)
        self.top.bind("<KeyRelease-Tab>", self.onTabReleased)
        self.top.bind("<KeyPress-y>", self.onT_Pressed)
        self.top.bind("<KeyRelease-y>", self.onT_Released)

        self.top.bind("<Control-Q>", lambda args: self.smooth(0))
        self.top.bind("<Control-q>", lambda args: self.smooth(0))
        self.top.bind("<Control-W>", lambda args: self.smooth(1))
        self.top.bind("<Control-w>", lambda args: self.smooth(1))
        self.top.bind("<Control-R>", lambda args: self.smooth(2))
        self.top.bind("<Control-r>", lambda args: self.smooth(2))
        self.top.bind("<Control-T>", lambda args: self.smooth(3))
        self.top.bind("<Control-t>", lambda args: self.smooth(3))

        self.canvas.bind("<Button-4>", self.onWheel)
        self.canvas.bind("<Button-5>", self.onWheel)
        self.canvas.bind("<MouseWheel>", self.onWheel)

        self.screen.bind("<Motion>", self.onScreenMotion)
        self.screen.bind("<Button-1>", self.onScreenPressed)
        self.screen.bind("<ButtonRelease-1>", self.onScreenReleased)

        # 获取总长
        self.t1 = mixer.Sound(self.audioFile).get_length() / 1.875 * self.chart.bpm

        self.top.after(200, self.calcHandle)
        self.top.after(300, self.update)

        # ffmpeg 子进程
        t1 = threading.Thread(target=self.ffmpegThread, daemon=True)
        t1.start()

    def changeUI(self, *args):
        self.enableClassicUI = not self.enableClassicUI
        self.changeScreenMode(ScreenMode.MOVE1)
        self.calcHandle()
        self.update()

        if self.enableClassicUI:
            self.message("欢迎使用RPE经典UI(@cmdysj)喵，此功能是为了减少此制谱器的学习成本喵。")
        else:
            self.message("打回原形了喵。")


    def addKeyFrame(self, *args):
        self.record("添加关键帧")
        if self.screenMode is ScreenMode.SPEED:
            getEventIndexByTime(self.line.speed, self.ts)
        elif self.screenMode is ScreenMode.ALPHA:
            getEventIndexByTime(self.line.alpha, self.ts)
        elif self.screenMode is ScreenMode.THETA:
            getEventIndexByTime(self.line.theta, self.ts)
        elif self.screenMode is ScreenMode.NOTE:
            pass
        else:
            getEventIndexByTime(self.line.move1, self.ts)
            getEventIndexByTime(self.line.move2, self.ts)
            getEventIndexByTime(self.line.move3, self.ts)
            getEventIndexByTime(self.line.rotate, self.ts)
        self.calcHandle()
        self.update()

    def changeSpeed(self):
        if self.playing:
            return
        if self.speed == 1.0 and self.audioFile_075x is not None:
            self.speed = 0.75
            self.bt2.config(text="0.75x")
            mixer.music.load(self.audioFile_075x)
            mixer.music.play()
            mixer.music.pause()
        elif self.speed == 0.75 and self.audioFile_075x is not None:
            self.speed = 0.5
            self.bt2.config(text="0.5x")
            mixer.music.load(self.audioFile_05x)
            mixer.music.play()
            mixer.music.pause()
        elif self.speed == 0.5 and self.audioFile_075x is not None:
            self.speed = 0.25
            self.bt2.config(text="0.25x")
            mixer.music.load(self.audioFile_025x)
            mixer.music.play()
            mixer.music.pause()
        elif self.speed == 0.25 and self.audioFile is not None:
            self.speed = 1.0
            self.bt2.config(text="1.0x")
            mixer.music.load(self.audioFile)
            mixer.music.play()
            mixer.music.pause()
        else:
            self.message("切换倍速失败：ffmpeg异常")

    def ffmpegThread(self):
        cacheDir = os.path.join(self.projectDir, "cache")

        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)

        ffmpeg_exec = "bin/ffmpeg.exe"

        audioFile_05x = os.path.join(cacheDir, "0.5x_"+os.path.basename(self.audioFile))
        self.audioFile_05x = audioFile_05x
        if not os.path.exists(audioFile_05x):
            self.message("ffmpeg在正后台加载音频")
            command = [ffmpeg_exec,"-i", self.audioFile,"-filter:a", f"atempo={0.5}","-y",audioFile_05x]
            result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            if result.returncode != 0:
                raise Exception(f"ffmpeg执行失败: {result.stderr}")

        audioFile_075x = os.path.join(cacheDir, "0.75x_"+os.path.basename(self.audioFile))
        self.audioFile_075x = audioFile_075x
        if not os.path.exists(audioFile_075x):
            self.message("ffmpeg在正后台加载音频")
            command = [ffmpeg_exec,"-i", self.audioFile,"-filter:a", f"atempo={0.75}","-y",audioFile_075x]
            result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            if result.returncode != 0:
                raise Exception(f"ffmpeg执行失败: {result.stderr}")

        audioFile_025x = os.path.join(cacheDir, "0.25x_"+os.path.basename(self.audioFile))
        self.audioFile_025x = audioFile_025x
        if not os.path.exists(audioFile_025x):
            self.message("ffmpeg在正后台加载音频")
            command = [ffmpeg_exec,"-i", self.audioFile_05x,"-filter:a", f"atempo={0.5}","-y",audioFile_025x]
            result = subprocess.run(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
            if result.returncode != 0:
                raise Exception(f"ffmpeg执行失败: {result.stderr}")

        self.message("音频加载就绪")

    def officialChartRefine(self):
        for line in self.chart.lineList:
            lineTimers = (line.move1, line.move2, line.rotate, line.alpha)
            for lineTimer in lineTimers:

                i = 0
                while i < lineTimer.periodCount - 1:
                    st = lineTimer.startTimeList[i]
                    et = lineTimer.endTimeList[i]

                    if lineTimer.endValueList[i] == lineTimer.startValueList[i+1] and et-st<4:
                        lineTimer.endTimeList[i] = lineTimer.endTimeList[i+1]
                        lineTimer.endValueList[i] = lineTimer.endValueList[i+1]
                        lineTimer.popPeriod(i+1)
                    else:
                        i += 1

    def loadFromJson(self, *event):
        file = filedialog.askopenfilename(title="从Json导入", filetypes=(("Json文件", "*.json"), ("所有类型", "*.*")))
        if not file:
            return

        try:
            from libs import analyzer
            newChart = analyzer.analyzeJson(file)
            self.chart = newChart
            self.line = newChart.lineList[0]
            self.calcHandle()
            self.update()
        except Exception as e:
            messagebox.showerror("错误", "导入时遇到未知的错误：\n"+str(e))

    def onTabPressed(self, event):

        if not self.tabFrame is None:
            return 'break'

        xn, yn = self.top.winfo_pointerx(), self.top.winfo_pointery()
        self.tabDragStartPos = (xn, yn)
        x = self.top.winfo_width() / 2 - 200
        y = self.top.winfo_height() / 2 - 200

        self.tabFrame = CanvasDark(self.top)
        self.tabFrame.place(x=x, y=y, width=400, height=400)
        self.onTabDrag(event)

        self.canvas.unbind("<Motion>")
        self.screen.unbind("<Motion>")
        self.top.unbind("<Motion>")

        return 'break'

    def onTabDrag(self, *event):

        if self.tabFrame is None:
            return 'break'
        else:
            self.top.after(20, self.onTabDrag)

        xn, yn = self.top.winfo_pointerx(), self.top.winfo_pointery()
        dx = xn - self.tabDragStartPos[0]
        dy = yn - self.tabDragStartPos[1]

        if abs(dy) + abs(dx) == 0:
            index = self.chart.lineList.index(self.line)
            a = 0
        else:
            r = math.atan2(dy, dx) + math.pi / 2
            a = math.sqrt(dx**2 + dy**2)
            index = round(12 * r / (math.pi*2))
            index = (index + 12) % 12
            level = max(min(int(a // 400), int((len(self.chart.lineList)+1)//12)-1), 0)
            index += 12 * level
            print(index, level)

        self.tabFrame.delete("all")
        for i in range(int((len(self.chart.lineList)+1)//12)+1):
            r = 80 + 40*i
            self.tabFrame.create_oval(
                200 - r, 200 - r,
                200 + r, 200 + r,
                outline="#ddd",
                width=max(1, 4-i*2)
            )
        self.tabFrame.create_text(
            200, 245, text="快速切线\n移动鼠标",
            anchor="center",
            fill="#fff",
        )
        for i in range(len(self.chart.lineList)):
            rL = i/12 * math.pi * 2
            l = i // 12
            xL = 200 + math.sin(rL) * (100 + 40 * l)
            yL = 200 - math.cos(rL) * (100 + 40 * l)

            if index == i and a > 60:
                self.tabFrame.create_text(
                    xL, yL, text=str(i),
                    anchor="center",
                    font=("microsoft yahei", 20),
                    fill="#fff",
                )
                self.tabFrame.create_text(
                    200, 190, text=str(i),
                    anchor="center",
                    font=("microsoft yahei", 48),
                    fill="#fff",
                )


                line = self.chart.lineList[index]
                if line is not self.line:
                    self.line = line
                    self.calcHandle()
                    self.update()
                    self.message(f"Line {index}.")
            else:
                self.tabFrame.create_text(
                    xL, yL, text=str(i),
                    anchor="center",
                    font=("microsoft yahei", 12),
                    fill="#ddd",
                )

        if index == self.chart.lineList.index(self.line) or a <= 60:
            self.tabFrame.create_text(
                200, 190, text=str(self.chart.lineList.index(self.line)),
                anchor="center",
                font=("microsoft yahei", 48),
                fill="#fff",
            )

        self.tabFrame.config(cursor="none")
        self.canvas.config(cursor="none")
        self.screen.config(cursor="none")
        self.top.config(cursor="none")

    def onTabReleased(self, event):
        self.top.config(cursor="arrow")
        self.canvas.bind("<Motion>", self.onMouseMotion)
        self.screen.bind("<Motion>", self.onScreenMotion)
        self.top.unbind("<Motion>")
        if self.tabFrame is not None:
            self.tabFrame.destroy()
            self.tabFrame = None

    def setDisplayJudgeArea(self, *args):
        if self.judge.get() is True and self.dt < 32*8 and self.screenMode is ScreenMode.NOTE:
            self.displayJudgeArea = True
        else:
            self.displayJudgeArea = False
        self.calcHandle()
        self.update()


    def setLineNumber(self, *args):
        self.lineTNum = self.tf0et1.getValue()
        self.lineXNum = self.tf0et2.getValue()
        self.dt = 32 * self.tf0et3.getValue()
        self.calcHandle()
        self.update()

    def setNoteAbove(self, *args):
        if len(self.selected) == 0:
            return
        if not isinstance(self.selected[0], Note):
            return
        above = not self.selected[0].above
        for obj in self.selected:
            if isinstance(obj, Note):
                obj.above = above
        self.calcHandle()
        self.update()

    def setScale(self, *args):
        self.dt *= 2
        if self.dt >= 1024:
            self.dt = 64
        self.calcHandle()
        self.update()

    def message(self, msg):
        self.renderMessageBox(msg)

    def record(self, message=""):
        self.undoRecord = []
        self.operationRecord.append((self.chart.lineList.index(self.line), copy.deepcopy(self.line), message), )
        if len(self.operationRecord) > 1000:
            self.operationRecord = [self.operationRecord[i] for i in range(0, 10, 500)] + self.operationRecord[500:]

        if time.time() - self.lastTimeOfAutoSave > 60:
            self.lastTimeOfAutoSave = time.time()
            self.top.after(500, self.autoSave)

    def undo(self, *args):
        if len(self.operationRecord) <= 0:
            self.message("没有更多可撤销的项目了")
            return False
        index, line, message = self.operationRecord.pop()
        self.undoRecord.append((self.lineIndex, copy.deepcopy(self.line), "撤销"), )
        self.chart.lineList[index] = line
        self.line = line
        self.lineIndex = index
        self.calcHandle()
        self.update()
        self.message("已撤销："+message)

    def redo(self, *args):
        if len(self.undoRecord) <= 0:
            return False

        index, line, message = self.undoRecord.pop()
        self.operationRecord.append((self.lineIndex, copy.deepcopy(self.line), "重做"), )
        self.chart.lineList[index] = line
        self.line = line
        self.lineIndex = index
        self.calcHandle()
        self.update()

    def selectAll(self, *args):
        minTime = float("inf")
        maxTime = 0
        for obj in self.selected:
            if not isinstance(obj, Event):
                return
            minTime = min(minTime, obj.st)
            maxTime = max(maxTime, obj.et)
        if maxTime == 0:
            return

        self.selected = []
        for handle in self.handles:
            if not isinstance(handle, EventHandle):
                continue
            event = Event(handle)
            if minTime <= event.st < event.et <= maxTime:
                self.selected.append(event)

        self.update()

    def copy(self, *args):

        if len(self.selected) == 0:
            return False

        minTime = float("inf")
        maxTime = 0
        for obj in self.selected:
            if isinstance(obj, Event):
                st = obj.lineTimer.startTimeList[obj.index]
                et = obj.lineTimer.endTimeList[obj.index]
                minTime = min(minTime, st)
                maxTime = max(maxTime, et)
            elif isinstance(obj, Note):
                minTime = min(minTime, obj.time_)
                maxTime = max(maxTime, obj.time_ + obj.holdTime)

        self.clipboard = Period(maxTime - minTime, "clipboard")
        self.copyFrom = minTime

        for obj in self.selected:
            if isinstance(obj, Event):
                if obj.lineTimer == self.line.alpha:
                    ltr = self.clipboard.alpha
                elif obj.lineTimer == self.line.move1:
                    ltr = self.clipboard.move1
                elif obj.lineTimer == self.line.move2:
                    ltr = self.clipboard.move2
                elif obj.lineTimer == self.line.speed:
                    ltr = self.clipboard.speed
                elif obj.lineTimer == self.line.theta:
                    ltr = self.clipboard.theta
                elif obj.lineTimer == self.line.rotate:
                    ltr = self.clipboard.rotate
                else:
                    raise ValueError("unknown event type.")
                ltr.addPeriod(
                    obj.lineTimer.startTimeList[obj.index] - minTime,
                    obj.lineTimer.endTimeList[obj.index] - minTime,
                    obj.lineTimer.startValueList[obj.index],
                    obj.lineTimer.endValueList[obj.index],
                )
            if isinstance(obj, Note):
                newNote = Note(
                    type_=obj.type_,
                    time_=obj.time_ - minTime,
                    holdTime=obj.holdTime,
                    floorPos=0,
                    posX=obj.posX,
                    speed=obj.speed,
                    above=obj.above,
                )
                self.clipboard.notes.append(newNote)

    def copyAll(self, *args):

        if len(self.selected) == 0:
            return False

        minTime = float("inf")
        maxTime = 0
        for obj in self.selected:
            if isinstance(obj, Event):
                st = obj.lineTimer.startTimeList[obj.index]
                et = obj.lineTimer.endTimeList[obj.index]
                minTime = min(minTime, st)
                maxTime = max(maxTime, et)
            elif isinstance(obj, Note):
                minTime = min(minTime, obj.time_)
                maxTime = max(maxTime, obj.time_ + obj.holdTime)

        period = Period(maxTime - minTime, "clipboard")

        ltrs1 = (self.line.alpha, self.line.move1, self.line.move2, self.line.speed, self.line.theta, self.line.rotate)
        ltrs2 = (period.alpha, period.move1, period.move2, period.speed, period.theta, period.rotate)
        for i in range(len(ltrs1)):
            ltr1: LineTimer = ltrs1[i]
            ltr2: LineTimer = ltrs2[i]
            for j in range(len(ltr1.startTimeList)):
                st = ltr1.startTimeList[j]
                et = ltr1.endTimeList[j]
                sv = ltr1.startValueList[j]
                ev = ltr1.endValueList[j]
                if minTime <= st < et <= maxTime:
                    ltr2.addPeriod(st - minTime, et - minTime, sv, ev)

        self.clipboard = period
        self.copyFrom = minTime

    def cut(self, *args):

        # 撤销记录
        self.record("剪切")

        self.copy()
        self.onBackspacePressed()

    def pasteBy(self, *args):
        self.paste(ts=self.copyFrom)

    def paste(self, *args, ts=None):
        ts = self.ts if ts is None else ts

        if self.clipboard is None or self.copyFrom is None:
            return

        # 撤销记录
        self.record("粘贴")

        appendLineTimer(self.line.alpha, self.clipboard.alpha, ts)
        appendLineTimer(self.line.move1, self.clipboard.move1, ts)
        appendLineTimer(self.line.move2, self.clipboard.move2, ts)
        appendLineTimer(self.line.speed, self.clipboard.speed, ts)
        appendLineTimer(self.line.theta, self.clipboard.theta, ts)
        appendLineTimer(self.line.rotate, self.clipboard.rotate, ts)

        for obj in self.clipboard.notes:
            newNote = Note(
                type_=obj.type_,
                time_=obj.time_ + ts,
                holdTime=obj.holdTime,
                floorPos=0,
                posX=obj.posX,
                speed=obj.speed,
                above=obj.above,
            )
            self.line.addNote(newNote)

        if abs(self.t0 - (ts - 32)) > 128:
            self.set_to(ts - 32)

        self.calcHandle()
        self.update()

    def mirrorX(self, *args):

        # 撤销记录
        self.record("反转")

        for obj in self.selected:
            if isinstance(obj, Event):
                sv = obj.lineTimer.startValueList[obj.index]
                ev = obj.lineTimer.endValueList[obj.index]
                obj.lineTimer.startValueList[obj.index] = ev
                obj.lineTimer.endValueList[obj.index] = sv
            if isinstance(obj, Note):
                obj.posX = -obj.posX
        self.calcHandle()
        self.update()

    def ban3D(self, *args):

        # 撤销记录
        self.record("启用/禁用3D")

        for obj in self.selected:
            if isinstance(obj, Note):
                obj.ban3D = (obj.ban3D + 1) % 2
        self.calcHandle()
        self.update()

    def onAltPressed(self, *args):
        if self.altFrame is not None:
            return
        h = 20 * len(self.chart.lineList) + 30
        x = (self.top.winfo_width() - 600) // 2
        y = (self.top.winfo_height() - h) // 2
        self.altFrame = LabelFrameDark(self.top, text=f"共{len(self.chart.lineList)}根判定线")
        self.altFrame.place(x=x, y=y, width=600, height=h)

        self.alfFrameLabelList = []
        for i in range(len(self.chart.lineList)):
            str = f"line {i}\tNote数：{len(self.chart.lineList[i].noteList)}"
            this = LabelDark(self.altFrame, text=str, anchor=W)
            this.place(x=20, y=20 * i)
            self.alfFrameLabelList.append(this)
        for i in range(len(self.alfFrameLabelList)):
            if i == self.lineIndex:
                self.alfFrameLabelList[i].config(bg="#777")
            else:
                self.alfFrameLabelList[i].config(bg="#222")
        self.top.update()
        self.altFrame.bind("<MouseWheel>", self.changeLine)

    def onAltReleased(self, args):
        self.altFrame.destroy()
        self.altFrame = None

    def changeLine(self, event):
        if event.delta < 0:
            self.lineIndex = (self.lineIndex + 1) % len(self.chart.lineList)
        else:
            self.lineIndex = (self.lineIndex - 1) % len(self.chart.lineList)
        for i in range(len(self.alfFrameLabelList)):
            if i == self.lineIndex:
                self.alfFrameLabelList[i].config(bg="#777")
            else:
                self.alfFrameLabelList[i].config(bg="#222")
        self.line = self.chart.lineList[self.lineIndex]
        self.calcHandle()
        self.update()

    def export(self, *event):
        root = Toplevel()
        root.geometry("800x680")
        root.title("导出与错误检查")
        root.config(padx=30, pady=30, background="#222")
        self.checkWindows = root

        lb1 = LabelDark(root, text="导出/编译 选项")
        lb1.place(x=20, y=10)
        lb2 = LabelDark(root, text="请选择一个方式另存为。")
        lb2.place(x=20, y=30)

        bt1 = LiButtonDark(root, "保存", self.save, height=2)
        bt1.place(x=20, y=60, width=180, height=40)
        bt2 = LiButtonDark(root, "导出为官谱格式", self.exportAsOfficial, height=2)
        bt2.place(x=20, y=110, width=180, height=40)
        bt3 = LiButtonDark(root, "导出为RPE格式", self.exportAsRPE, height=2)
        bt3.place(x=20, y=160, width=180, height=40)
        bt4 = LiButtonDark(root, "编译3D效果", self.exportAs3DPEZ, height=2)
        bt4.place(x=20, y=220, width=180, height=40)

        Tooltip(bt1, "保存为PhiChart Editor的内部格式。\n将以toml格式保存所有数据。")
        Tooltip(bt2, "官谱格式。\n所有3D效果、RPE扩展项将会全部丢失！")
        Tooltip(bt3, "RPE格式。\n将所有3D效果以增添字段的方式保存到Json中。\n只有特制的渲染器可以正确读取3D效果。")
        Tooltip(bt4, "RPE格式。\n将所有3D效果编译成判定线表演。\n保证3D效果可以被模拟器正确读取。")

        i = 0
        for exception in check(self.chart):
            if i < 10:
                this = Frame(root, bg="#333")
                this.place(x=240, y=20 + 55 * i, width=460, height=50)
                lbt = Label(this, text=exception.name, bg="#333", fg="#ddd")
                lbt.place(x=20, y=5)
                lbm = Label(this, text=str(exception), bg="#333", fg="#777")
                lbm.place(x=20, y=25)
                btt = LiButtonDark(this, ">", self.turnToException, var=exception)
                btt.place(x=410, y=0, width=50, height=50)
                btm = LiButtonDark(this, "√", self.turnToException, var=exception)
                btm.place(x=360, y=0, width=50, height=50)
                Tooltip(btt, "定位到异常处")
                Tooltip(btm, "尝试自动修正")

            i += 1

        if i == 0:
            lbt = Label(root, text="未发现谱面异常！", bg="#292929", fg="#ddd")
            lbt.place(x=240, y=20, width=460, height=460)
        else:
            lbt = Label(root, text=f"显示前10个异常。共计发现{i}个异常.\n请修复所有异常后再导出！（无视风险继续导出！）",
                        bg="#442929", fg="#f66")
            lbt.place(x=240, y=20 + 55 * min(10, i), width=460, height=45)

    def turnToException(self, exception: ChartException):

        self.line = exception.line
        self.set_to(exception.time - 64)
        self.calcHandle()
        self.update()

        assert self.checkWindows
        self.top.after(100, self.checkWindows.destroy)

    def calcHandle(self):

        self.handles: list[Handle] = []
        sorted(self.chart)

        if self.enableClassicUI:
            if self.screenMode is ScreenMode.NOTE:
                self.calcNoteHandleToRender()
            else:
                self.calcEventHandleToRender(self.line.alpha, minValue=0, maxValue=1, screenMode=ScreenMode.ALPHA)
                self.calcEventHandleToRender(self.line.move1, minValue=0, maxValue=1, screenMode=ScreenMode.MOVE1)
                self.calcEventHandleToRender(self.line.move2, minValue=0, maxValue=1, screenMode=ScreenMode.MOVE2)
                self.calcEventHandleToRender(self.line.move3, minValue=-1, maxValue=4, screenMode=ScreenMode.MOVE3)
                self.calcEventHandleToRender(self.line.speed, minValue=0, maxValue=10, screenMode=ScreenMode.SPEED)
                self.calcEventHandleToRender(self.line.theta, minValue=-180, maxValue=180, screenMode=ScreenMode.THETA)
                self.calcEventHandleToRender(self.line.rotate, minValue=-360, maxValue=360, screenMode=ScreenMode.ROTATE)
        else:
            self.calcEventHandleToRender(self.line.alpha, minValue=0, maxValue=1, screenMode=ScreenMode.ALPHA)
            self.calcEventHandleToRender(self.line.move1, minValue=0, maxValue=1, screenMode=ScreenMode.MOVE1)
            self.calcEventHandleToRender(self.line.move2, minValue=0, maxValue=1, screenMode=ScreenMode.MOVE2)
            self.calcEventHandleToRender(self.line.move3, minValue=-1, maxValue=4, screenMode=ScreenMode.MOVE3)
            self.calcEventHandleToRender(self.line.speed, minValue=0, maxValue=10, screenMode=ScreenMode.SPEED)
            self.calcEventHandleToRender(self.line.theta, minValue=-180, maxValue=180, screenMode=ScreenMode.THETA)
            self.calcEventHandleToRender(self.line.rotate, minValue=-360, maxValue=360, screenMode=ScreenMode.ROTATE)
            self.calcNoteHandleToRender()

        # 刷新编辑区
        self.renderScreen()

    def update(self):
        self.top.focus_set()
        self.canvas.delete("all")
        self.renderSelectingRect()
        self.renderFrame()
        self.renderScroller()
        self.renderHandle()
        self.renderGlobalNotes()

    def renderGlobalNotes(self, *args):
        for line in self.chart.lineList:
            if line is self.line:
                continue
            for note in line.noteList:
                if self.t0 <= note.time_ <= self.t0 + self.dt:
                    if note.type_ == 1 or note.type_ == 3:
                        color = TAP_COLOR
                        x = 24
                    elif note.type_ == 2:
                        color = DRAG_COLOR
                        x = 32
                    elif note.type_ == 4:
                        color = FLICK_COLOR
                        x = 40
                    else:
                        raise ValueError(f"Unknown note type: {note.type_}")

                    y = self.h0 * (1 - (note.time_ - self.t0) / self.dt)
                    self.canvas.create_oval(
                        x-2, y-2,
                        x+2, y+2,
                        fill=color,
                        width=0
                    )

    def calcNoteHandleToRender(self):
        # 记录 note 的 x 值，方便吸附
        self.Xrecord = set()

        # if self.displayJudgeArea:
        #     for i in range(len(self.chart.lineList)):
        #         line = self.chart.lineList[i]
        #         if line is not self.line:
        #             for note in line.noteList:
        #                 handle = self.calcEachNoteHandleToRender(note, i)
        #                 if i is not False:
        #                     self.handles.append(handle)

        for note in self.line.noteList:
            i = self.calcEachNoteHandleToRender(note)
            if i is not False:
                self.handles.append(i)
            else:
                continue

    def calcEachNoteHandleToRender(self, note, lineIndex=None):

        X = 0.06525 * self.w0
        b1 = self.t0
        b2 = self.t0 + self.dt

        a1 = note.time_
        a2 = note.time_ + note.holdTime
        if max(a1, b1) > min(a2, b2):
            return False

        y0 = (1 - (note.time_ - self.t0) / self.dt) * self.h0
        y1 = (1 - (note.time_ + note.holdTime - self.t0) / self.dt) * self.h0
        y0 = min(y0, self.h0)
        y1 = max(y1, 0)
        x = note.posX * X + 0.5 * self.w0
        # self.Xrecord.add(note.posX)

        if note.type_ == 1:
            handle = NoteHandle(note, x, y0, 4, lineIndex)
        elif note.type_ == 2:
            handle = NoteHandle(note, x, y0, 2, lineIndex)
        elif note.type_ == 4:
            handle = NoteHandle(note, x, y0, 4, lineIndex)
        elif note.type_ == 3:
            handle = HoldHandle(note, x, y0, y1, lineIndex)
        else:
            return False
        return handle

    def calcEventHandleToRender(self, lineTimer: LineTimer, minValue: float, maxValue: float, screenMode: ScreenMode):

        t1 = self.t0
        t2 = self.t0 + self.dt

        for i in range(len(lineTimer.startValueList)):

            startValue: float = lineTimer.startValueList[i]
            startTimeT: float = lineTimer.startTimeList[i]
            endValue: float = lineTimer.endValueList[i]
            endTimeT: float = lineTimer.endTimeList[i]

            if max(startTimeT, t1) > min(endTimeT, t2):
                continue

            # 最大范围的1.2倍， 720*1.2
            x1 = ((startValue - minValue) / (maxValue - minValue) + 0.1) * self.w0 / 1.2
            x2 = ((endValue - minValue) / (maxValue - minValue) + 0.1) * self.w0 / 1.2
            y1 = (1 - (startTimeT - self.t0) / self.dt) * self.h0
            y2 = (1 - (endTimeT - self.t0) / self.dt) * self.h0
            handle = EventHandle(lineTimer, i, screenMode, x1, x2, y1, y2)
            self.handles.append(handle)

    def renderMessageBox(self, message):
        width = self.w0 - 40
        height = 40
        self.canvas.create_rectangle(
            20, 20, self.w0-20, 55,
            fill="#333", outline="#ddd",
            width=1
        )
        self.canvas.create_text(
            30, 30, text=message,
            fill="#ddd", anchor=NW,
        )

    def renderFrame(self):

        if not self.playing:
            self.canvas.create_text(
                self.w0/2, self.h0/2, anchor=CENTER,
                text=self.chart.lineList.index(self.line),
                fill="#3b3b3b", font=("microsoft yahei", 256)
            )
        self.canvas.create_text(
            5, 0, anchor=NW,
            text="时间 Time",
            fill="#ddd"
        )
        self.canvas.create_text(
            self.w0 - 5, 0, anchor=NE,
            text="节拍 Beat",
            fill="#ddd"
        )
        self.canvas.create_text(
            5, self.h0, anchor=SW,
            text=f"{self.t0:.2f}",
            fill="#ddd"
        )
        self.canvas.create_text(
            self.w0 - 5, self.h0, anchor=SE,
            text=f"{self.t0 / 32:.2f}",
            fill="#ddd"
        )

        if not self.enableClassicUI or self.screenMode is ScreenMode.NOTE:
            for i in range(1, self.lineXNum):
                x = (0.1 + i/self.lineXNum) / 1.2 * self.w0
                self.canvas.create_line(
                    x, 0, x, self.h0,
                    fill="#444"
                )

        i = 32 / self.lineTNum
        t = ((self.t0 - 1e-9) // i) * i
        while t < self.t0 + self.dt:
            t += i
            y = (1 - (t - self.t0) / self.dt) * self.h0
            if abs(t/32 - round(t/32)) < 0.01:
                self.canvas.create_line(
                    0, y, self.w0, y,
                    fill="#666"
                )
                self.canvas.create_text(
                    5, y, anchor=NW,
                    text=str(round(t)),
                    fill="#ddd"
                )
                self.canvas.create_text(
                    self.w0 - 5, y, anchor=NE,
                    text=str(round(t/32)),
                    fill="#ddd"
                )
            else:
                self.canvas.create_line(
                    50, y, self.w0 - 50, y,
                    fill="#555"
                )

        y = (1 - (self.ts - self.t0) / self.dt) * self.h0
        self.canvas.create_line(
            0, y, self.w0, y,
            fill="#666",
            width=4
        )

        for t in self.chart.beats:
            y = (1 - (t - self.t0) / self.dt) * self.h0
            self.canvas.create_oval(
                20, y - 8, 36, y + 8,
                outline="#ddd",
                fill="",
                width=4
            )

    def renderHandle(self):

        NS = 0.05 * self.w0

        if self.startCast is not None:
            handles = self.handles + [self.highlightHandle]
        else:
            handles = self.handles

        for handle in handles:
            if isinstance(handle, HoldHandle):

                if self.screenMode is ScreenMode.NOTE and handle.lineIndex is None:
                    color = HOLD_COLOR
                    fill = color if handle.note.above and not handle.note.ban3D else ""
                else:
                    color = HOLD_COLOR_DARK
                    fill = color if handle.note.above and not handle.note.ban3D else ""

                self.canvas.create_rectangle(
                    handle.x - NS, handle.y1,
                    handle.x + NS, handle.y2,
                    fill=fill, outline=color,
                    width=1,
                )

                # 绘制判定区域
                self.renderNoteJudgeArea(handle)

                for obj in self.selected:
                    if isinstance(obj, Note) and obj is handle.note:
                        self.canvas.create_rectangle(
                            handle.x - 6 - NS, handle.y1 + 6,
                            handle.x + 6 + NS, handle.y2 - 6,
                            outline="#ddd",
                            width=4,
                        )

        for handle in handles:
            if isinstance(handle, EventHandle):
                if handle.type_ is not self.screenMode:
                    self.renderEventHandle(handle)

            elif isinstance(handle, NoteHandle):

                if self.screenMode is ScreenMode.NOTE and handle.lineIndex is None:
                    if handle.note.type_ == 1:
                        color = TAP_COLOR
                    elif handle.note.type_ == 2:
                        color = DRAG_COLOR
                    elif handle.note.type_ == 4:
                        color = FLICK_COLOR
                    else:
                        raise ValueError(f"Unknown handle type {handle.note.type_}")
                else:
                    if handle.note.type_ == 1:
                        color = TAP_COLOR_DARK
                    elif handle.note.type_ == 2:
                        color = DRAG_COLOR_DARK
                    elif handle.note.type_ == 4:
                        color = FLICK_COLOR_DARK
                    else:
                        raise ValueError(f"Unknown handle type {handle.note.type_}")
                fill = color if handle.note.above and not handle.note.ban3D else ""

                self.canvas.create_rectangle(
                    handle.x - NS, handle.y - handle.width/2,
                    handle.x + NS, handle.y + handle.width/2,
                    fill=fill, outline=color,
                    width=1,
                )
                if handle.lineIndex is not None:
                    self.canvas.create_text(handle.x - NS + 15, handle.y - 12, text="Line "+str(handle.lineIndex), fill="#ddd")

                # 绘制判定区域
                self.renderNoteJudgeArea(handle)

                for obj in self.selected:
                    if isinstance(obj, Note) and obj is handle.note:
                        self.canvas.create_rectangle(
                            handle.x - 6 - NS, handle.y - 8,
                            handle.x + 6 + NS, handle.y + 8,
                            outline="#ddd",
                            width=4,
                        )

        for handle in handles:
            if isinstance(handle, EventHandle):
                if handle.type_ is self.screenMode:
                    self.renderEventHandle(handle)

    def renderNoteJudgeArea(self, handle: NoteHandle|HoldHandle):
        if not self.displayJudgeArea or handle.lineIndex is not None:
            return
        if isinstance(handle, NoteHandle):
            y = handle.y
        else:
            y = handle.y1
        if handle.note.type_ <= 4:
            jy1 = y + (0.08 * self.chart.bpm / 1.875) / self.dt * self.h0
            jy2 = y - (0.08 * self.chart.bpm / 1.875) / self.dt * self.h0
        else:
            jy1, jy2 = None, None
        if handle.note.type_ == 1 or handle.note.type_ == 3:
            jb1 = y + (0.16 * self.chart.bpm / 1.875) / self.dt * self.h0
            jb2 = y - (0.16 * self.chart.bpm / 1.875) / self.dt * self.h0
        else:
            jb1, jb2 = None, None
        if handle.note.type_ == 1:
            jr1 = y + (0.18 * self.chart.bpm / 1.875) / self.dt * self.h0
            jr2 = y - (0.18 * self.chart.bpm / 1.875) / self.dt * self.h0
        else:
            jr1, jr2 = None, None
        if handle.note.visibleTime <= 999:
            jw1 = y + (handle.note.visibleTime * self.chart.bpm / 1.875) / self.dt * self.h0
        else:
            jw1 = None

        if jr1 is not None:
            self.canvas.create_line(handle.x, jr1, handle.x, jr2, fill=FLICK_COLOR)
            self.canvas.create_line(handle.x-10, jr1, handle.x+10, jr1, fill=FLICK_COLOR)
            self.canvas.create_line(handle.x-10, jr2, handle.x+10, jr2, fill=FLICK_COLOR)
        if jb1 is not None:
            self.canvas.create_line(handle.x, jb1, handle.x, jb2, fill=TAP_COLOR)
            self.canvas.create_line(handle.x-10, jb1, handle.x+10, jb1, fill=TAP_COLOR)
            self.canvas.create_line(handle.x-10, jb2, handle.x+10, jb2, fill=TAP_COLOR)
        if jy1 is not None:
            self.canvas.create_line(handle.x, jy1, handle.x, jy2, fill=DRAG_COLOR)
            self.canvas.create_line(handle.x-10, jy1, handle.x+10, jy1, fill=DRAG_COLOR)
            self.canvas.create_line(handle.x-10, jy2, handle.x+10, jy2, fill=DRAG_COLOR)
        if jw1 is not None:
            self.canvas.create_line(handle.x, y, handle.x, jw1, fill="#fff")
            self.canvas.create_line(handle.x-10, jw1, handle.x+10, jw1, fill="#fff")

    def renderEventHandle(self, handle):
        return self.renderEventHandle_Classic(handle) if self.enableClassicUI else self.renderEventHandle_Default(handle)

    def renderEventHandle_Default(self, handle: EventHandle):
        if abs(handle.y2 - handle.y1) < 40:
            handleSize = 5
        else:
            handleSize = 8

        if handle.type_ is self.screenMode:
            if handle.type_ is ScreenMode.SPEED:
                color = SPEED_COLOR
            elif handle.type_ is ScreenMode.ALPHA:
                color = ALPHA_COLOR
            elif handle.type_ is ScreenMode.MOVE1:
                color = MOVE1_COLOR
            elif handle.type_ is ScreenMode.MOVE2:
                color = MOVE2_COLOR
            elif handle.type_ is ScreenMode.MOVE3:
                color = MOVE3_COLOR
            elif handle.type_ is ScreenMode.THETA:
                color = THETA_COLOR
            elif handle.type_ is ScreenMode.ROTATE:
                color = ROTATE_COLOR
            else:
                raise ValueError(f"Unknown handle type {handle.type_}")
        else:
            if handle.type_ is ScreenMode.SPEED:
                color = SPEED_COLOR_DARK
            elif handle.type_ is ScreenMode.ALPHA:
                color = ALPHA_COLOR_DARK
            elif handle.type_ is ScreenMode.MOVE1:
                color = MOVE1_COLOR_DARK
            elif handle.type_ is ScreenMode.MOVE2:
                color = MOVE2_COLOR_DARK
            elif handle.type_ is ScreenMode.MOVE3:
                color = MOVE3_COLOR_DARK
            elif handle.type_ is ScreenMode.THETA:
                color = THETA_COLOR_DARK
            elif handle.type_ is ScreenMode.ROTATE:
                color = ROTATE_COLOR_DARK
            else:
                raise ValueError(f"Unknown handle type {handle.type_}")

        # 处理缓动
        if 0 <= handle.lineTimer.easingTypeList[handle.index] <= 1:
            points = [handle.x1, handle.y1, handle.x2, handle.y2]
        else:
            easing = handle.lineTimer.easingTypeList[handle.index]
            points = []
            size = int((handle.y1 - handle.y2) // 3)
            for i in range(size + 1):
                r = ease_funcs[easing](i / size)
                x = r * handle.x2 + (1 - r) * handle.x1
                y = (i / size) * handle.y2 + (1 - i / size) * handle.y1
                points.append(x)
                points.append(y)

        for obj in self.selected:
            if isinstance(obj, Event) and obj.isHandle(handle):
                self.canvas.create_line(
                    *points,
                    fill="#ddd",
                    width=6,
                )

                self.canvas.create_rectangle(
                    handle.x1 - handleSize - 4, handle.y1 - handleSize - 4,
                    handle.x1 + handleSize + 4, handle.y1,
                    fill="#ddd",
                    width=0,
                )

                self.canvas.create_rectangle(
                    handle.x2 - handleSize - 4, handle.y2,
                    handle.x2 + handleSize + 4, handle.y2 + handleSize + 4,
                    fill="#ddd",
                    width=0,
                )

        # 绘制线条
        self.canvas.create_line(
            *points,
            fill=color,
            width=3,
        )

        if handle == self.curvingHandle:
            if self.acr1T is not None:
                # 画两个锚点
                acr1X = handle.x1 * self.acr1V + handle.x2 * (1 - self.acr1V)
                acr1Y = handle.y1 * self.acr1T + handle.y2 * (1 - self.acr1T)
                acr2X = handle.x1 * self.acr2V + handle.x2 * (1 - self.acr2V)
                acr2Y = handle.y1 * self.acr2T + handle.y2 * (1 - self.acr2T)

                self.canvas.create_line(
                    handle.x2, handle.y2,
                    acr1X, acr1Y,
                    fill="#ddd",
                    width=4,
                )

                self.canvas.create_line(
                    handle.x1, handle.y1,
                    acr2X, acr2Y,
                    fill="#ddd",
                    width=4,
                )

                self.canvas.create_oval(
                    acr1X - 10, acr1Y - 10,
                    acr1X + 10, acr1Y + 10,
                    outline="#ddd", fill="#333",
                    width=4,
                )

                self.canvas.create_oval(
                    acr2X - 10, acr2Y - 10,
                    acr2X + 10, acr2Y + 10,
                    outline="#ddd", fill="#333",
                    width=4,
                )

            if self.bezierCurve is not None:

                self.message("按Enter确认；按数字1~9切换预设")

                points = []
                for i in range(len(self.bezierCurve.x_samples)):
                    x = handle.x2 + self.bezierCurve.y_samples[i] * (handle.x1 - handle.x2)
                    y = handle.y2 + self.bezierCurve.x_samples[i] * (handle.y1 - handle.y2)
                    points.append(x)
                    points.append(y)
                self.canvas.create_line(
                    points, fill="#ddd", width=4,
                )

        if abs(handle.y2 - handle.y1) < 16:
            return

        self.canvas.create_polygon(
            (
                handle.x2 - handleSize, handle.y2 - 0,
                handle.x2 - 0, handle.y2 - handleSize,
                handle.x2 + handleSize, handle.y2 - 0,
                handle.x2 + 0, handle.y2 + handleSize,
            ),
            outline=color,
            width=1,
            fill="",
        )

        self.canvas.create_polygon(
            (
                handle.x2 - handleSize, handle.y2 - 0,
                handle.x2 + handleSize, handle.y2 - 0,
                handle.x2 + 0, handle.y2 + handleSize,
            ),
            fill=color,
            width=1,
        )

        self.canvas.create_polygon(
            (
                handle.x1 - handleSize, handle.y1 - 0,
                handle.x1 - 0, handle.y1 - handleSize,
                handle.x1 + handleSize, handle.y1 - 0,
                handle.x1 + 0, handle.y1 + handleSize,
            ),
            outline=color,
            width=1,
            fill="",
        )

        self.canvas.create_polygon(
            (
                handle.x1 - handleSize, handle.y1 - 0,
                handle.x1 - 0, handle.y1 - handleSize,
                handle.x1 + handleSize, handle.y1 - 0,
            ),
            fill=color,
            width=1,
        )

    def renderEventHandle_Classic(self, handle: EventHandle):
        if handle.type_ is ScreenMode.SPEED:
            index = 6
            color = SPEED_COLOR
            colorDark = SPEED_COLOR_DARK
        elif handle.type_ is ScreenMode.ALPHA:
            index = 5
            color = ALPHA_COLOR
            colorDark = ALPHA_COLOR_DARK
        elif handle.type_ is ScreenMode.MOVE1:
            index = 0
            color = MOVE1_COLOR
            colorDark = MOVE1_COLOR_DARK
        elif handle.type_ is ScreenMode.MOVE2:
            index = 1
            color = MOVE2_COLOR
            colorDark = MOVE2_COLOR_DARK
        elif handle.type_ is ScreenMode.MOVE3:
            index = 2
            color = MOVE3_COLOR
            colorDark = MOVE3_COLOR_DARK
        elif handle.type_ is ScreenMode.THETA:
            index = 3
            color = THETA_COLOR
            colorDark = THETA_COLOR_DARK
        elif handle.type_ is ScreenMode.ROTATE:
            index = 4
            color = ROTATE_COLOR
            colorDark = ROTATE_COLOR_DARK
        else:
            raise ValueError(f"Unknown handle type {handle.type_}")

        l = self.w0*((index+0.7)/8)
        r = self.w0*((index+1.3)/8)

        points = []
        easingType = handle.lineTimer.easingTypeList[handle.index]
        if easingType <= 1:
            points = [l+(r-l)*handle.x1/self.w0, handle.y1, l+(r-l)*handle.x2/self.w0, handle.y2]
        else:
            size = int((handle.y1 - handle.y2) // 3)
            for i in range(size + 1):
                ratio = ease_funcs[easingType](i / size)
                x = l+(r-l)*(ratio * handle.x2 + (1 - ratio) * handle.x1)/self.w0
                y = (i / size) * handle.y2 + (1 - i / size) * handle.y1
                points.append(x)
                points.append(y)


        self.canvas.create_rectangle(
            l, handle.y1,
            r, handle.y2,
            fill=colorDark,
            width=0
        )
        self.canvas.create_line(
            l, handle.y1,
            r, handle.y1,
            fill=color,
        )
        self.canvas.create_line(
            *points,
            fill=color, width=3
        )

        if any(isinstance(obj, Event) and obj.isHandle(handle) for obj in self.selected):
            self.canvas.create_rectangle(
                l+3, handle.y1-3,
                r-3, handle.y2+3,
                outline="white",
                width=6
            )
        if abs(handle.y2 - handle.y1) > 50:
            self.canvas.create_text(
                (l+r)/2, min(handle.y1, self.h0)-10,
                text=f"{Event(handle).sv: .2f}",
                fill="white"
            )
            self.canvas.create_text(
                (l+r)/2, max(handle.y2, 0)+10,
                text=f"{Event(handle).ev: .2f}",
                fill="white"
            )

    def renderScreen(self):
        self.screen.delete("all")

        try:
            sw = self.sw0
            sh = self.sh0
        except AttributeError:
            return

        if self.mouseOperationType == "screenMove":
            self.screen.create_line(
                self.sw0 * 0.0, self.sh0 * 0.5,
                self.sw0 * 1.0, self.sh0 * 0.5,
                fill=MOVE2_COLOR_DARK, width=1,
                dash=(10, 10),
            )

            self.screen.create_line(
                self.sw0 * 0.5, self.sh0 * 0.0,
                self.sw0 * 0.5, self.sh0 * 1.0,
                fill=MOVE2_COLOR_DARK, width=1,
                dash=(10, 10),
            )
            self.screen.create_rectangle(
                *self.posToScreen(0.2, 0.2),
                *self.posToScreen(0.8, 0.8),
                outline=MOVE2_COLOR_DARK, width=1,
                dash=(10, 10),
            )

        if self.mouseOperationType == "screenRotate":
            self.screen.create_line(
                self.sw0 * 0.0, self.sh0 * 0.5,
                self.sw0 * 1.0, self.sh0 * 0.5,
                fill=ROTATE_COLOR_DARK, width=1,
                dash=(10, 10),
            )

            self.screen.create_line(
                self.sw0 * 0.5, self.sh0 * 0.0,
                self.sw0 * 0.5, self.sh0 * 1.0,
                fill=ROTATE_COLOR_DARK, width=1,
                dash=(10, 10),
            )

        # 渲染外框
        self.screen.create_rectangle(
            *self.posToScreen(0, 0),
            *self.posToScreen(1, 1),
            fill="#333", width=0
        )

        # 渲染主线
        self.renderEachLineOnScreen(self.line, False, True)

        for line in self.chart.lineList:
            a = line.alpha(self.ts)
            if line is not self.line and a < 0.5:
                self.renderEachLineOnScreen(line, False, False, a)

        for line in self.chart.lineList:
            a = line.alpha(self.ts)
            if line is not self.line and a > 0.5:
                self.renderEachLineOnScreen(line, False, False, a)

        # 渲染主线
        self.renderEachLineOnScreen(self.line, True, False)

    def renderEachLineOnScreen(self, line, foreRender: bool, thetaRender: bool, a=1):

        sw = self.sw0
        sh = self.sh0

        halfLength = 1 * sw
        lineLength = 1 * sw

        x = line.move1(self.ts)
        y = line.move2(self.ts)
        r = line.rotate(self.ts)

        xn, yn = self.posToScreen(x, y)
        Vcos = math.cos(r / 180 * math.pi)
        Vsin = math.sin(r / 180 * math.pi)
        x1 = xn - Vcos * halfLength
        x2 = xn + Vcos * halfLength
        y1 = yn + Vsin * halfLength
        y2 = yn - Vsin * halfLength
        xR = xn + math.cos((r + 90) / 180 * math.pi) * 50
        yR = yn - math.sin((r + 90) / 180 * math.pi) * 50

        # 渲染note
        if self.screenMode is ScreenMode.NOTE:
            line.fastCalcFloorPos()
            self.renderEachNoteOnLine(line, xn, yn, r)

        # yn, yR = sh - yn, sh - yR
        # y1, y2 = sh - y1, sh - y2

        # if thetaRender and self.screenMode is ScreenMode.THETA:
        #     Y = 0.6 * self.sh0
        #     theta_rad = line.theta(self.ts) / 180 * math.pi
        #     l = 0.99 * Y if abs(theta_rad) > math.pi / 2 else 3 * Y
        #     h = math.sin(theta_rad) * l
        #     d = math.cos(theta_rad) * l
        #
        #     xl = xn + Vcos * -halfLength / 2.4
        #     xr = xn + Vcos * halfLength / 2.4
        #     yl = yn - Vsin * -halfLength / 2.4
        #     yr = yn - Vsin * halfLength / 2.4
        #
        #     xil = xl - h * Vsin
        #     yil = yl - h * Vcos
        #     xir = xr - h * Vsin
        #     yir = yr - h * Vcos
        #
        #     cmrX = self.sw0 * 0.5
        #     cmrY = self.sh0 * 0.5
        #     Lp = cmrCast(cmrX, cmrY, -Y, xil, yil, d)
        #     Rp = cmrCast(cmrX, cmrY, -Y, xir, yir, d)
        #
        #     self.screen.create_polygon(
        #         (
        #             xl, yl,
        #             xr, yr,
        #             Rp[0], Rp[1],
        #             Lp[0], Lp[1],
        #         ),
        #         fill=THETA_COLOR_DARK,
        #         width=0,
        #     )
        #
        #     self.screen.create_line(
        #         xl, yl, Lp[0], Lp[1],
        #         fill=THETA_COLOR,
        #         width=2,
        #     )
        #     self.screen.create_line(
        #         xr, yr, Rp[0], Rp[1],
        #         fill=THETA_COLOR,
        #         width=2,
        #     )

        if foreRender:
            self.screen.create_line(
                x1, y1, x2, y2,
                fill="#ddd",
                width=5,
            )

            self.screen.create_line(
                xn, yn, xR, yR,
                fill=ROTATE_COLOR,
                width=2,
            )

            self.screen.create_oval(
                xn - 10, yn - 10,
                xn + 10, yn + 10,
                outline="#ddd",
                fill="#333",
                width=3,
            )

            self.screen.create_oval(
                xR - 8, yR - 8,
                xR + 8, yR + 8,
                outline=ROTATE_COLOR,
                fill="#333",
                width=2,
            )


        else:
            if a > 0.5:
                self.screen.create_line(
                    x1, y1, x2, y2,
                    fill="#777",
                    width=3,
                )

                self.screen.create_oval(
                    xn - 5, yn - 5,
                    xn + 5, yn + 5,
                    outline="#777",
                    fill="",
                    width=2,
                )
            else:
                self.screen.create_line(
                    x1, y1, x2, y2,
                    fill="#3d3d3d",
                    width=2,
                )

                self.screen.create_oval(
                    xn - 5, yn - 5,
                    xn + 5, yn + 5,
                    outline="#3d3d3d",
                    fill="",
                    width=1,
                )

    def renderEachNoteOnLine(self, line, x, y, r):

        X = 0.05626 * self.sw1
        Y = 0.6 * self.sh1
        NS = self.sw1 / 8

        Vsin = math.sin(math.radians(-r))
        Vcos = math.cos(math.radians(-r))
        pos = line.pos(self.ts)
        pos = 0 if pos is None else pos

        for note in line.noteList:

            if self.ts > note.time_ + note.holdTime:
                continue

            dx1 = note.posX * X + NS/2
            dx2 = note.posX * X - NS/2
            dy = note.speed * (note.floorPos - pos) * Y

            if note.above:
                x1 = x + dx1 * Vcos + dy * Vsin
                y1 = y + dx1 * Vsin - dy * Vcos
                x2 = x + dx2 * Vcos + dy * Vsin
                y2 = y + dx2 * Vsin - dy * Vcos
            else:
                x1 = x + dx1 * Vcos - dy * Vsin
                y1 = y + dx1 * Vsin + dy * Vcos
                x2 = x + dx2 * Vcos - dy * Vsin
                y2 = y + dx2 * Vsin + dy * Vcos

            if note.type_ == 3:

                dyt = note.speed * (note.floorPosT - pos) * Y

                if note.above:
                    if note.time_ < self.ts < note.time_ + note.holdTime:
                        x1 = x + dx1 * Vcos
                        y1 = y + dx1 * Vsin
                        x2 = x + dx2 * Vcos
                        y2 = y + dx2 * Vsin
                    x3 = x + dx1 * Vcos + dyt * Vsin
                    y3 = y + dx1 * Vsin - dyt * Vcos
                    x4 = x + dx2 * Vcos + dyt * Vsin
                    y4 = y + dx2 * Vsin - dyt * Vcos
                else:
                    if note.time_ < self.ts < note.time_ + note.holdTime:
                        x1 = x + dx1 * Vcos
                        y1 = y + dx1 * Vsin
                        x2 = x + dx2 * Vcos
                        y2 = y + dx2 * Vsin
                    x3 = x + dx1 * Vcos - dyt * Vsin
                    y3 = y + dx1 * Vsin + dyt * Vcos
                    x4 = x + dx2 * Vcos - dyt * Vsin
                    y4 = y + dx2 * Vsin + dyt * Vcos

                if not (0 < x1 < self.sw0 and 0 < y1 < self.sh0) and not (0 < x2 < self.sw0 and 0 < y2 < self.sh0)\
                        and not (0 < x3 < self.sw0 and 0 < y3 < self.sh0) and not (0 < x4 < self.sw0 and 0 < y4 < self.sh0):
                    continue

                self.screen.create_polygon(
                    x1, y1, x2, y2, x4, y4, x3, y3,
                    fill=HOLD_COLOR,
                    width=2,
                )

            else:

                if not (0 < x1 < self.sw0 and 0 < y1 < self.sh0) and not (0 < x2 < self.sw0 and 0 < y2 < self.sh0):
                    continue

                if note.type_ == 1:
                    self.screen.create_line(
                        x1, y1, x2, y2,
                        fill=TAP_COLOR,
                        width=3,
                    )
                elif note.type_ == 2:
                    self.screen.create_line(
                        x1, y1, x2, y2,
                        fill=DRAG_COLOR,
                        width=2,
                    )
                elif note.type_ == 4:
                    self.screen.create_line(
                        x1, y1, x2, y2,
                        fill=FLICK_COLOR,
                        width=4,
                    )
                else:
                    raise ValueError(f"Unexpected note type: {note.type_}")

    def renderScroller(self):
        y0 = self.h0 * (1 - (self.t0 / self.t1))
        ys = self.h0 * (1 - (self.ts / self.t1))
        y1 = self.h0 * (1 - ((self.t0 + self.dt) / self.t1))
        self.scroller.delete("all")
        self.scroller.create_rectangle(
            0, y0, 20, y1,
            fill="#666",
            width=0
        )
        self.scroller.create_line(
            0, ys, 20, ys,
            fill="#ddd",
            width=2,
        )
        # self.scroller.create_line(
        #     0, y0, 20, y0,
        #     fill="#ddd",
        #     width=3,
        # )

    def renderSelectingRect(self):
        if self.mouseOperationType == "selectingNote":
            self.canvas.create_rectangle(
                self.selectingRectP1[0], self.selectingRectP1[1],
                self.selectingRectP2[0], self.selectingRectP2[1],
                fill="#393939",
                width=0
            )
        elif self.mouseOperationType == "selectingEvent":
            self.canvas.create_rectangle(
                0, self.selectingRectP1[1],
                self.w0, self.selectingRectP2[1],
                fill="#393939",
                width=0
            )

    def mouseMatch(self, event):
        return self.mouseMatch_Classic(event) if self.enableClassicUI else self.mouseMatch_Default(event)

    def mouseMatch_Default(self, event):

        minDistance: float = 20
        matchedObj: Handle | None = None
        NS = 0.05 * self.w0

        for handle in self.handles:
            if isinstance(handle, NoteHandle):
                d = math.sqrt((event.x - handle.x) ** 2 + (event.y - handle.y) ** 2)
                d -= 5 if self.screenMode is ScreenMode.NOTE else 0
            if isinstance(handle, HoldHandle):
                if abs(handle.x - event.x) < NS and handle.y2 < event.y < handle.y1:
                    d = 0
                else:
                    d = float('inf')
                if self.screenMode is ScreenMode.NOTE:
                    d -= 5
            if isinstance(handle, EventHandle):
                if not handle.y2 <= event.y <= handle.y1:
                    d = float('inf')
                else:
                    easingType = handle.lineTimer.easingTypeList[handle.index]
                    r = (event.y - handle.y1) / (handle.y2 - handle.y1)
                    r = ease_funcs[easingType](r) if easingType >= 2 else r
                    xp = r * (handle.x2 - handle.x1) + handle.x1
                    d = abs(event.x - xp)
            if d < minDistance:
                minDistance = d
                matchedObj = handle
        return matchedObj

    def mouseMatch_Classic(self, event):
        minDistance: float = 20
        matchedObj: Handle | None = None
        NS = 0.05 * self.w0

        if self.screenMode is ScreenMode.NOTE:
            for handle in self.handles:
                if isinstance(handle, NoteHandle):
                    d = math.sqrt((event.x - handle.x) ** 2 + (event.y - handle.y) ** 2)
                    d -= 5 if self.screenMode is ScreenMode.NOTE else 0
                if isinstance(handle, HoldHandle):
                    if abs(handle.x - event.x) < NS and handle.y2 < event.y < handle.y1:
                        d = 0
                    else:
                        d = float('inf')
                    if self.screenMode is ScreenMode.NOTE:
                        d -= 5
                if d < minDistance:
                    minDistance = d
                    matchedObj = handle
            if matchedObj is not None:
                return matchedObj

        lineTimerDic = {
            0: self.line.move1,
            1: self.line.move2,
            2: self.line.move3,
            3: self.line.theta,
            4: self.line.rotate,
            5: self.line.alpha,
            6: self.line.speed,
        }
        index: int = round(8*event.x/self.w0 - 1)
        if index > 6 or index < 0:
            return None

        lineTimer: LineTimer = lineTimerDic[index]
        for handle in self.handles:
            if not isinstance(handle, EventHandle):
                continue
            if lineTimer is handle.lineTimer:
                if handle.y2 <= event.y <= handle.y1:
                    return handle
        return None

    def mouseCast(self, event):
        # 将鼠标位置转换为时间和位置数据

        if self.screenMode is ScreenMode.NOTE:

            X = 0.06525 * self.w0
            posX = (event.x - 0.5 * self.w0) / X
            time_ = self.dt + self.t0 - self.dt * event.y / self.h0

            if self.xAds.get():
                w0 = self.w0 / 1.2
                x = round((event.x - self.w0/2) / w0 * self.lineXNum) * w0 / self.lineXNum
                posX = x / X

            if self.tAds.get():
                d = 32 / self.lineTNum
                time_ = round(time_ / d) * d

            return round(posX, 2), round(time_, 2)

        else:

            if self.ads:
                for handle in self.handles:
                    if not isinstance(handle, EventHandle):
                        continue
                    if abs(event.x - handle.x1) + abs(event.y - handle.y1) <= 16:
                        event.x, event.y = handle.x1, handle.y1
                    elif abs(event.x - handle.x2) + abs(event.y - handle.y2) <= 16:
                        event.x, event.y = handle.x2, handle.y2

            time_ = self.dt + self.t0 - self.dt * event.y / self.h0
            r = (event.x - self.w0 / 12) / (self.w0 / 1.2)

            if self.xAds.get():
                r = round(r * self.lineXNum) / self.lineXNum
            if self.tAds.get():
                d = 32/self.lineTNum
                time_ = round(time_ / d) * d

            if self.screenMode is ScreenMode.ALPHA:
                value = 0 + r * (1 - 0)
            elif self.screenMode is ScreenMode.MOVE1:
                value = 0 + r * (1 - 0)
            elif self.screenMode is ScreenMode.MOVE2:
                value = 0 + r * (1 - 0)
            elif self.screenMode is ScreenMode.MOVE3:
                value = -1 + r * (4 + 1)
            elif self.screenMode is ScreenMode.SPEED:
                value = 0 + r * (10 - 0)
            elif self.screenMode is ScreenMode.THETA:
                value = -180 + r * 360
            elif self.screenMode is ScreenMode.ROTATE:
                value = -360 + r * 720
            else:
                raise ValueError('Invalid screen mode')

            return round(value, 2), round(time_, 2)

    def onMousePressed(self, event):

        if self.curvingHandle is not None:
            # 画两个锚点
            matched: EventHandle = self.curvingHandle
            acr1X = matched.x1 * self.acr1V + matched.x2 * (1 - self.acr1V)
            acr1Y = matched.y1 * self.acr1T + matched.y2 * (1 - self.acr1T)
            acr2X = matched.x1 * self.acr2V + matched.x2 * (1 - self.acr2V)
            acr2Y = matched.y1 * self.acr2T + matched.y2 * (1 - self.acr2T)

            if acr1X - 16 < event.x < acr1X + 16 and acr1Y - 16 < event.y < acr1Y + 16:
                self.mouseStartCast = matched
                self.mouseOperationType = 'pullAcr1'
                self.canvas.bind("<Motion>", self.onMouseDrag)
                return
            elif acr2X - 16 < event.x < acr2X + 16 and acr2Y - 16 < event.y < acr2Y + 16:
                self.mouseStartCast = matched
                self.mouseOperationType = 'pullAcr2'
                self.canvas.bind("<Motion>", self.onMouseDrag)
                return

        matched = self.mouseMatch(event)

        if matched is None:
            # 拖动选定
            self.selected = []

            self.bezierCurve = None
            self.curvingHandle = None
            self.acr1V, self.acr1T = None, None
            self.acr2V, self.acr2T = None, None

            if self.screenMode is ScreenMode.NOTE:
                self.mouseOperationType = 'selectingNote'
            else:
                self.mouseOperationType = 'selectingEvent'
            self.selectingRectP1 = (event.x, event.y)
            self.canvas.bind("<Motion>", self.onMouseDrag)

        elif not any(matched.isObj(obj) for obj in self.selected):

            self.curvingHandle = None
            self.bezierCurve = None
            self.acr1V = None
            self.acr1T = None
            self.acr2V = None
            self.acr2T = None

            # 选定新的obj
            if isinstance(matched, (HoldHandle, NoteHandle)):
                self.changeScreenMode(ScreenMode.NOTE)
                self.selected = [matched.note]
            elif isinstance(matched, EventHandle):
                self.changeScreenMode(matched.type_)
                self.selected = [Event(matched)]

                # 准备编辑贝塞尔曲线
                t1 = matched.lineTimer.startTimeList[matched.index]
                t2 = matched.lineTimer.endTimeList[matched.index]
                v1 = matched.lineTimer.startValueList[matched.index]
                v2 = matched.lineTimer.endValueList[matched.index]
                if t2 - t1 >= 32 and v1 != v2:
                    self.curvingHandle = matched
                    self.acr1V = 0.2
                    self.acr1T = 0.2
                    self.acr2V = 0.8
                    self.acr2T = 0.8

            self.onMouseMotion(event)
            self.update()
            return
        else:
            # 操作
            # 操作类型检定

            if self.screenMode is ScreenMode.NOTE:
                NS = 0.05 * self.w0
                assert isinstance(matched, (NoteHandle, HoldHandle))
                # 操作位置检定
                if matched.note.type_ != 3 and matched.x - NS < event.x < matched.x + NS and matched.y - 10 < event.y < matched.y + 10:
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullNote'
                elif matched.note.type_ == 3 and matched.x - NS < event.x < matched.x + NS and matched.y2 + 10 < event.y < matched.y1 - 10:
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullNote'
                elif matched.note.type_ == 3 and matched.x - NS < event.x < matched.x + NS and matched.y2 < event.y < matched.y2 + 10:
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullHold8'
                elif matched.note.type_ == 3 and matched.x - NS < event.x < matched.x + NS and matched.y1 - 10 < event.y < matched.y1:
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullHold2'
            else:
                assert isinstance(matched, EventHandle)
                if self.hooked.get():
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullEvent'
                elif matched.y1 - 10 < event.y < matched.y1 + 10:
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullEvent2'
                elif matched.y2 - 10 < event.y < matched.y2 + 10:
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullEvent8'
                else:
                    self.mouseStartCast = self.mouseCast(event)
                    self.mouseOperationType = 'pullEvent'

            self.canvas.bind("<Motion>", self.onMouseDrag)

    def onMouseReleased(self, event):
        # 刷新撤销记录的cd
        self.dragCD = False

        self.ts = self.mouseCast(event)[1]
        self.renderScreen()

        self.canvas.bind("<Motion>", self.onMouseMotion)
        self.mouseOperationType = None
        self.mouseStartCast = None
        self.update()

    def onMouseDrag(self, event):

        if not self.dragCD:
            self.dragCD = True
            self.record("鼠标拖动")

        if self.mouseOperationType == 'pullNote':
            cast = self.mouseCast(event)
            for obj in self.selected:
                assert isinstance(obj, Note)
                obj.time_ += cast[1] - self.mouseStartCast[1]
                obj.posX += cast[0] - self.mouseStartCast[0]
            self.mouseStartCast = cast
        elif self.mouseOperationType == 'pullHold8':
            cast = self.mouseCast(event)
            for obj in self.selected:
                assert isinstance(obj, Note)
                obj.holdTime += cast[1] - self.mouseStartCast[1]
                obj.holdTime = max(4, obj.holdTime)
            self.mouseStartCast = cast
        elif self.mouseOperationType == 'pullHold2':
            cast = self.mouseCast(event)
            for obj in self.selected:
                assert isinstance(obj, Note)
                obj.holdTime -= cast[1] - self.mouseStartCast[1]
                obj.time_ += cast[1] - self.mouseStartCast[1]
                obj.holdTime = max(4, obj.holdTime)
            self.mouseStartCast = cast
        elif self.mouseOperationType == 'pullEvent':
            cast = self.mouseCast(event)
            for obj in self.selected:
                assert isinstance(obj, Event)
                obj.lineTimer.startTimeList[obj.index] += cast[1] - self.mouseStartCast[1]
                obj.lineTimer.endTimeList[obj.index] += cast[1] - self.mouseStartCast[1]
                obj.lineTimer.startValueList[obj.index] += cast[0] - self.mouseStartCast[0]
                obj.lineTimer.endValueList[obj.index] += cast[0] - self.mouseStartCast[0]
            self.mouseStartCast = cast
            self.ts = cast[1]
        elif self.mouseOperationType == 'pullEvent2':
            cast = self.mouseCast(event)
            for obj in self.selected:
                assert isinstance(obj, Event)
                obj.lineTimer.startTimeList[obj.index] += cast[1] - self.mouseStartCast[1]
                obj.lineTimer.startValueList[obj.index] += cast[0] - self.mouseStartCast[0]
            self.mouseStartCast = cast
            self.ts = cast[1] + 0.1
        elif self.mouseOperationType == 'pullEvent8':
            cast = self.mouseCast(event)
            for obj in self.selected:
                assert isinstance(obj, Event)
                obj.lineTimer.endTimeList[obj.index] += cast[1] - self.mouseStartCast[1]
                obj.lineTimer.endValueList[obj.index] += cast[0] - self.mouseStartCast[0]
            self.mouseStartCast = cast
            self.ts = cast[1] - 0.1
        elif self.mouseOperationType == 'selectingNote':
            self.selectingRectP2 = (event.x, event.y)
            # self.ts = self.mouseCast(event)[1]
            self.selected = []

            self.bezierCurve = None
            self.curvingHandle = None
            self.acr1V, self.acr1T = None, None
            self.acr2V, self.acr2T = None, None

            p1x, p1y = self.selectingRectP2
            p2x, p2y = self.selectingRectP1
            p1x, p2x = min(p1x, p2x), max(p1x, p2x)
            p1y, p2y = min(p1y, p2y), max(p1y, p2y)
            for handle in self.handles:
                if isinstance(handle, NoteHandle):
                    if p1x < handle.x < p2x and p1y < handle.y < p2y:
                        self.selected.append(handle.note)
                if isinstance(handle, HoldHandle):
                    if p1x < handle.x < p2x and max(p1y, handle.y2) <= min(p2y, handle.y1):
                        self.selected.append(handle.note)

        elif self.mouseOperationType == 'selectingEvent':
            self.selectingRectP2 = (event.x, event.y)
            self.ts = self.mouseCast(event)[1]

            self.selected = []

            self.bezierCurve = None
            self.curvingHandle = None
            self.acr1V, self.acr1T = None, None
            self.acr2V, self.acr2T = None, None


            p1x, p1y = self.selectingRectP2
            p2x, p2y = self.selectingRectP1
            p1y, p2y = min(p1y, p2y), max(p1y, p2y)
            for handle in self.handles:
                if isinstance(handle, EventHandle) and handle.type_ is self.screenMode:
                    if max(p1y, handle.y2) <= min(p2y, handle.y1):
                        self.selected.append(Event(handle))

        elif self.mouseOperationType == 'pullAcr1':
            handle = self.mouseStartCast
            assert isinstance(handle, EventHandle)
            self.acr1V = (event.x - handle.x2) / (handle.x1 - handle.x2)
            self.acr1T = (event.y - handle.y2) / (handle.y1 - handle.y2)
            self.acr1T = max(min(self.acr2T, self.acr1T), 0.0)
            self.bezierCurve = FastBezierLookup((0, 0), (self.acr1T, self.acr1V), (self.acr2T, self.acr2V), (1, 1))
            self.update()
            return

        elif self.mouseOperationType == 'pullAcr2':
            handle = self.mouseStartCast
            assert isinstance(handle, EventHandle)
            self.acr2V = (event.x - handle.x2) / (handle.x1 - handle.x2)
            self.acr2T = (event.y - handle.y2) / (handle.y1 - handle.y2)
            self.acr2T = max(min(1.0, self.acr2T), self.acr1T)
            self.bezierCurve = FastBezierLookup((0, 0), (self.acr1T, self.acr1V), (self.acr2T, self.acr2V), (1, 1))
            self.update()
            return

        self.calcHandle()
        self.update()

    def changeScreenMode(self, screenMode):

        if self.screenMode is screenMode:
            return

        self.screenMode = screenMode
        self.selected = []
        self.renderScreen()
        self.calcHandle() if self.enableClassicUI else None
        self.update()

        if screenMode is ScreenMode.NOTE:
            self.tf0rb2.set(0)
        elif screenMode is ScreenMode.MOVE1:
            self.tf0rb2.set(1)
        elif screenMode is ScreenMode.MOVE2:
            self.tf0rb2.set(2)
        elif screenMode is ScreenMode.MOVE3:
            self.tf0rb2.set(3)
        elif screenMode is ScreenMode.ALPHA:
            self.tf0rb2.set(4)
        elif screenMode is ScreenMode.ROTATE:
            self.tf0rb2.set(5)
        elif screenMode is ScreenMode.SPEED:
            self.tf0rb2.set(6)
        elif screenMode is ScreenMode.THETA:
            self.tf0rb2.set(7)

    def changeScreenModeByToolBox(self, index):
        if index == 0:
            self.screenMode = ScreenMode.NOTE
        elif index == 1:
            self.screenMode = ScreenMode.MOVE1
        elif index == 2:
            self.screenMode = ScreenMode.MOVE2
        elif index == 3:
            self.screenMode = ScreenMode.MOVE3
        elif index == 4:
            self.screenMode = ScreenMode.ALPHA
        elif index == 5:
            self.screenMode = ScreenMode.ROTATE
        elif index == 6:
            self.screenMode = ScreenMode.SPEED
        elif index == 7:
            self.screenMode = ScreenMode.THETA

        self.selected = []
        self.renderScreen()
        self.calcHandle() if self.enableClassicUI else None
        self.update()
        


    def onRightButtonPressed(self, event):

        matched = self.mouseMatch(event)
        if matched is not None:
            for obj in self.selected:
                if matched.isObj(obj):
                    self.button2Event(event)
                    return

        if self.screenMode is ScreenMode.NOTE:
            if self.tf0rb1.get() == 2:
                cast = self.mouseCast(event)
                if self.startCast is None:
                    self.startCast = self.mouseCast(event)
                    self.highlightNote = Note(
                        type_=3,
                        time_=cast[1],
                        posX=cast[0],
                        floorPos=0,
                    )
                else:
                    if not self.startCast[1] == cast[1]:
                        self.record("添加新的Hold")
                        self.highlightNote.holdTime = abs(self.startCast[1] - cast[1])
                        self.line.addNote(self.highlightNote)
                        self.selected = [self.highlightNote]

                    self.highlightNote = None
                    self.highlightHandle = None
                    self.startCast = None
                    self.calcHandle()
                    self.update()
            else:
                self.record("添加新的Note")
                cast = self.mouseCast(event)
                newNote = Note(
                    type_=self.tf0rb1.get() + 1,
                    time_=cast[1],
                    posX=cast[0],
                    floorPos=0,
                )
                self.line.addNote(newNote)
                self.calcHandle()
                self.update()
        else:
            cast = self.mouseCast(event)
            if self.screenMode is ScreenMode.ALPHA:
                lineTimer: LineTimer = self.line.alpha
            elif self.screenMode is ScreenMode.MOVE1:
                lineTimer: LineTimer = self.line.move1
            elif self.screenMode is ScreenMode.MOVE2:
                lineTimer: LineTimer = self.line.move2
            elif self.screenMode is ScreenMode.MOVE3:
                lineTimer: LineTimer = self.line.move3
            elif self.screenMode is ScreenMode.SPEED:
                lineTimer: LineTimer = self.line.speed
            elif self.screenMode is ScreenMode.THETA:
                lineTimer: LineTimer = self.line.theta
            elif self.screenMode is ScreenMode.ROTATE:
                lineTimer: LineTimer = self.line.rotate
            else:
                raise ValueError

            if self.startCast is None:
                self.startCast = cast
            else:
                if self.startCast[1] > cast[1]:
                    self.ts = cast[1] + 0.1
                    self.startCast, cast = cast, self.startCast
                else:
                    self.ts = cast[1] - 0.1
                if self.startCast[1] == cast[1]:
                    self.startCast = None
                    self.calcHandle()
                    self.update()
                    return

                self.record("添加新的事件")
                lineTimer.addPeriod(self.startCast[1], cast[1], self.startCast[0], cast[0])

                # 为了选中新创建的事件
                newEvent = Event(self.highlightHandle)
                newEvent.lineTimer = lineTimer
                newEvent.index = len(lineTimer.startTimeList) - 1
                self.selected = [newEvent]

                self.startCast = None
                self.calcHandle()
                self.update()

    def onKeyPressed(self, event):
        if str.upper(event.char) == "T":
            self.tf0rb1.set(0)
        elif str.upper(event.char) == "D":
            self.tf0rb1.set(1)
        elif str.upper(event.char) == "H":
            self.tf0rb1.set(2)
        elif str.upper(event.char) == "F":
            self.tf0rb1.set(3)

        if str.upper(event.char) == "N":
            self.tf0rb2.set(0)
        elif str.upper(event.char) == "X":
            self.tf0rb2.set(1)
        elif str.upper(event.char) == "Y":
            self.tf0rb2.set(2)
        elif str.upper(event.char) == "A":
            self.tf0rb2.set(3)
        elif str.upper(event.char) == "R":
            self.tf0rb2.set(4)
        elif str.upper(event.char) == "S":
            self.tf0rb2.set(5)
        elif str.upper(event.char) == "M":
            self.star_mixer()
        elif str.upper(event.char) == "B":
            self.beater()
        elif str.upper(event.char) == "G":
            self.hooked.setvalue()

        if self.acr2T is not None:
            if event.char == "1":
                self.acr1T = 0.0
                self.acr1V = 0.5
                self.acr2T = 0.5
                self.acr2V = 1.0
            elif event.char == "2":
                self.acr1T = 0.5
                self.acr1V = 0.0
                self.acr2T = 1.0
                self.acr2V = 0.5
            elif event.char == "3":
                self.acr1T = 0.0
                self.acr1V = 0.5
                self.acr2T = 0.0
                self.acr2V = 1.0
            elif event.char == "4":
                self.acr1T = 1.0
                self.acr1V = 0.0
                self.acr2T = 1.0
                self.acr2V = 0.5
            elif event.char == "5":
                self.acr1T = 0.5
                self.acr1V = 0.0
                self.acr2T = 0.5
                self.acr2V = 1.0
            elif event.char == "6":
                self.acr1T = 0.0
                self.acr1V = 0.5
                self.acr2T = 1.0
                self.acr2V = 0.5
            elif event.char == "7":
                self.acr1T = 0.0
                self.acr1V = 1.0
                self.acr2T = 1.0
                self.acr2V = 0.0
            elif event.char == "8":
                self.acr1T = 0.0
                self.acr1V = 0.5
                self.acr2T = 0.5
                self.acr2V = 1.5

            self.bezierCurve = FastBezierLookup((0, 0), (self.acr1T, self.acr1V), (self.acr2T, self.acr2V), (1, 1))
            self.update()

    def onBackspacePressed(self, *event):

        # 撤销记录
        self.record("删除")

        for i in range(len(self.selected)):
            obj = self.selected[i]
            try:
                if isinstance(obj, Note):
                    self.line.noteList.remove(obj)
                if isinstance(obj, Event):
                    obj.lineTimer.popPeriod(obj.index)

                    for k in range(i + 1, len(self.selected)):
                        obk = self.selected[k]
                        if isinstance(obk, Event) and obk.index > obj.index:
                            obk.index -= 1

            except Exception as e:
                pass
        self.selected = []
        self.calcHandle()
        self.update()

    def onDeletePressed(self, *event):

        if len(self.selected) <= 2:
            return self.onBackspacePressed()

        for obj in self.selected:
            if not isinstance(obj, Event):
                return self.onBackspacePressed()

        self.selected.sort(key=lambda x: x.index)
        for i in range(len(self.selected) - 1):
            if self.selected[i].index != self.selected[i + 1].index - 1:
                return self.onBackspacePressed()

        # 撤销记录
        self.record("合并事件/删除")

        self.selected: list[Event]
        t1 = self.selected[0].lineTimer.startTimeList[self.selected[0].index]
        t2 = self.selected[-1].lineTimer.endTimeList[self.selected[-1].index]
        v1 = self.selected[0].lineTimer.startValueList[self.selected[0].index]
        v2 = self.selected[-1].lineTimer.endValueList[self.selected[-1].index]
        self.selected[0].lineTimer.addPeriod(t1, t2, v1, v2)

        index = self.selected[0].index
        for i in range(len(self.selected)):
            self.selected[0].lineTimer.popPeriod(index)
        self.calcHandle()
        self.update()

    def onEnterPressed(self, event):

        if self.bezierCurve is None:
            return

        # 撤销记录
        self.record("添加缓动")

        event = self.selected[0]
        t1 = event.lineTimer.startTimeList[event.index]
        t2 = event.lineTimer.endTimeList[event.index]
        v1 = event.lineTimer.startValueList[event.index]
        v2 = event.lineTimer.endValueList[event.index]
        for i in range(int((t2 - t1) // 4)):
            x1 = i / int((t2 - t1) // 4)
            x2 = (i + 1) / int((t2 - t1) // 4)
            y1 = self.bezierCurve.get_y(x1)
            y2 = self.bezierCurve.get_y(x2)
            event.lineTimer.addPeriod(
                t1 * x2 + t2 * (1 - x2),
                t1 * x1 + t2 * (1 - x1),
                v1 * y2 + v2 * (1 - y2),
                v1 * y1 + v2 * (1 - y1),
            )
        sorted(self.chart)
        event.lineTimer.popPeriod(event.index)

        self.selected = []
        self.curvingHandle = None
        self.bezierCurve = None
        self.acr1V = None
        self.acr1T = None
        self.acr2V = None
        self.acr2T = None
        self.calcHandle()
        self.update()

    def smooth(self, curve: int, *args):
        if len(self.selected) <= 1:
            self.message("应当至少选择两个事件")
            return
        for obj in self.selected:
            if not isinstance(obj, Event):
                self.message("应当至少选择两个事件")
                return
        self.selected.sort(key=lambda x: x.index)

        t1 = self.selected[0].lineTimer.startTimeList[self.selected[0].index]
        t2 = self.selected[-1].lineTimer.endTimeList[self.selected[-1].index]
        v1 = self.selected[0].lineTimer.startValueList[self.selected[0].index]
        v2 = self.selected[-1].lineTimer.endValueList[self.selected[-1].index]

        tPoints = [t1, ]
        vPoints = [v1, ]
        for i in range(len(self.selected) - 1):
            if self.selected[i].index != self.selected[i + 1].index - 1:
                self.message("事件不连续")
                return
        for i in range(len(self.selected)):
            st = self.selected[i].lineTimer.startTimeList[self.selected[i].index]
            et = self.selected[i].lineTimer.endTimeList[self.selected[i].index]
            sv = self.selected[i].lineTimer.startValueList[self.selected[i].index]
            ev = self.selected[i].lineTimer.endValueList[self.selected[i].index]
            tPoints.append(et)
            vPoints.append(ev)

        index = self.selected[0].index
        for i in range(len(self.selected)):
            self.selected[0].lineTimer.popPeriod(index)

        if curve == 0:
            cubicSpline = CubicSpline(tPoints, vPoints)
        elif curve == 1:
            cubicSpline = BezierCurve(tPoints, vPoints)
        elif curve == 2:
            tPoints, vPoints = insert_mid_points(tPoints, vPoints)
            cubicSpline = CubicSpline(tPoints, vPoints, )
        elif curve == 3:
            tPoints, vPoints = insert_mid_points(tPoints, vPoints)
            cubicSpline = BezierCurve(tPoints, vPoints)
        elif curve == 4:
            cubicSpline = QuadraticSpline(tPoints, vPoints)
        elif curve == 5:
            cubicSpline = MovingAverage(tPoints, vPoints)

        t = t1
        while t < t2:
            self.selected[0].lineTimer.addPeriod(t, t + 4, cubicSpline(t), cubicSpline(t + 4))
            t += 4

        self.calcHandle()
        self.update()

    def onMouseControlPressed(self, event):

        self.curvingHandle = None
        self.bezierCurve = None
        self.acr1V = None
        self.acr1T = None
        self.acr2V = None
        self.acr2T = None

        matched: Handle = self.mouseMatch(event)
        if isinstance(matched, (HoldHandle, NoteHandle)):
            obj = matched.note
        elif isinstance(matched, EventHandle):
            obj = Event(matched)
        else:
            raise TypeError

        if matched is None:
            return
        if len(self.selected) == 0:
            return self.onMousePressed(event)
        if type(obj) is not type(self.selected[0]):
            return self.onMousePressed(event)
        if isinstance(obj, Event) and obj.lineTimer is not self.selected[0].lineTimer:
            return self.onMousePressed(event)

        self.selected.append(obj)
        self.onMouseMotion(event)
        self.update()

    def onMouseMotion(self, event):

        cast = self.mouseCast(event)
        self.lf0et1.config(text=f"{int(self.ts)} ({timeTtoBeat(int(self.ts))})")
        self.lf0et2.config(text=f"{cast[1]} ({timeTtoBeat(cast[1])})")
        self.lf0et3.config(text=f"{cast[0]}")

        if self.startCast is not None:

            self.canvas.config(cursor="crosshair")

            if self.screenMode is ScreenMode.NOTE:
                self.highlightNote.posX = cast[0]
                self.highlightNote.time_ = min(self.startCast[1], cast[1])
                self.highlightNote.holdTime = abs(self.startCast[1] - cast[1])
                self.highlightHandle = self.calcEachNoteHandleToRender(self.highlightNote)
                self.update()
            else:
                if self.screenMode is ScreenMode.ALPHA:
                    minValue, maxValue = 0, 1
                    lineTimer: LineTimer = self.line.alpha
                elif self.screenMode is ScreenMode.MOVE1:
                    minValue, maxValue = 0, 1
                    lineTimer: LineTimer = self.line.move1
                elif self.screenMode is ScreenMode.MOVE2:
                    minValue, maxValue = 0, 1
                    lineTimer: LineTimer = self.line.move2
                elif self.screenMode is ScreenMode.MOVE3:
                    minValue, maxValue = -1, 4
                    lineTimer: LineTimer = self.line.move3
                elif self.screenMode is ScreenMode.SPEED:
                    minValue, maxValue = 0, 10
                    lineTimer: LineTimer = self.line.speed
                elif self.screenMode is ScreenMode.THETA:
                    minValue, maxValue = -180, 180
                    lineTimer: LineTimer = self.line.theta
                elif self.screenMode is ScreenMode.ROTATE:
                    minValue, maxValue = -360, 360
                    lineTimer: LineTimer = self.line.rotate
                else:
                    raise ValueError

                if self.hooked.get():
                    self.startCast = list(self.startCast)
                    self.startCast[0] = cast[0]

                x1 = ((self.startCast[0] - minValue) / (maxValue - minValue) + 0.1) * self.w0 / 1.2
                x2 = ((cast[0] - minValue) / (maxValue - minValue) + 0.1) * self.w0 / 1.2
                y1 = (1 - (self.startCast[1] - self.t0) / self.dt) * self.h0
                y2 = (1 - (cast[1] - self.t0) / self.dt) * self.h0
                self.highlightHandle = EventHandle(lineTimer, 0, self.screenMode, x1, x2, y1, y2)
                self.update()
            return

        if self.curvingHandle is not None:
            # 画两个锚点
            matched: EventHandle = self.curvingHandle
            acr1X = matched.x1 * self.acr1V + matched.x2 * (1 - self.acr1V)
            acr1Y = matched.y1 * self.acr1T + matched.y2 * (1 - self.acr1T)
            acr2X = matched.x1 * self.acr2V + matched.x2 * (1 - self.acr2V)
            acr2Y = matched.y1 * self.acr2T + matched.y2 * (1 - self.acr2T)

            if acr1X - 16 < event.x < acr1X + 16 and acr1Y - 16 < event.y < acr1Y + 16:
                self.canvas.config(cursor="crosshair")
                return
            elif acr2X - 16 < event.x < acr2X + 16 and acr2Y - 16 < event.y < acr2Y + 16:
                self.canvas.config(cursor="crosshair")
                return

        matched: Handle | None = self.mouseMatch(event)
        if matched is None:
            self.canvas.config(cursor="arrow")
        elif not any(matched.isObj(obj) for obj in self.selected):
            # 选定
            self.canvas.config(cursor="hand2")
        else:
            # 操作
            if self.screenMode is ScreenMode.NOTE:
                NS = 0.05 * self.w0
                assert isinstance(matched, (NoteHandle, HoldHandle))
                # 操作位置检定
                if matched.note.type_ != 3 and matched.x - NS < event.x < matched.x + NS and matched.y - 10 < event.y < matched.y + 10:
                    self.canvas.config(cursor="fleur")
                elif matched.note.type_ == 3 and matched.x - NS < event.x < matched.x + NS and matched.y2 + 10 < event.y < matched.y1 - 10:
                    self.canvas.config(cursor="fleur")
                elif matched.note.type_ == 3 and matched.x - NS < event.x < matched.x + NS and matched.y2 < event.y < matched.y2 + 10:
                    self.canvas.config(cursor="sb_v_double_arrow")
                elif matched.note.type_ == 3 and matched.x - NS < event.x < matched.x + NS and matched.y1 - 10 < event.y < matched.y1:
                    self.canvas.config(cursor="sb_v_double_arrow")
            else:
                assert isinstance(matched, EventHandle)
                if matched.y1 - 10 < event.y < matched.y1 + 10:
                    self.canvas.config(cursor="sb_h_double_arrow")
                elif matched.y2 - 10 < event.y < matched.y2 + 10:
                    self.canvas.config(cursor="sb_h_double_arrow")
                else:
                    self.canvas.config(cursor="fleur")

    def set_to(self, t0):
        t0 = max(t0, 0)
        t0 = min(self.t1, t0)
        self.t0 = round(t0)
        self.calcHandle()
        self.update()

    def onScrollerPressed(self, event):
        self.scroller.bind("<Motion>", self.onScrollerDrag)

    def onScrollerDrag(self, event):
        t = self.t1 * (1 - (event.y / self.h0))
        self.set_to(t)

    def onScrollerReleased(self, event):
        self.scroller.unbind("<Motion>")
        self.onScrollerDrag(event)

    def onWheel(self, event):

        wheelBan = ("selectingNote", "selectingEvent", "pullAcr1", "pullAcr2")
        if self.mouseOperationType in wheelBan:
            return

        if event.delta:
            self.set_to(event.delta / 10 + self.t0)
            self.onMouseMotion(event)
        else:
            if event.num == 4:
                self.set_to(10 + self.t0)
                self.onMouseMotion(event)
            elif event.num == 5:
                self.set_to(self.t0 - 10)
                self.onMouseMotion(event)

    def onConfigure(self, event):
        # 适配竖轴
        self.h0 = self.canvas.winfo_height()

        # 适配编辑区
        self.sw0 = self.lf1.winfo_width()
        self.sh0 = min(self.top.winfo_height() - 550, self.sw0 * 0.5)
        self.sh1 = 0.8 * self.sh0
        self.sw1 = 4/3 * self.sh1
        self.lf1.config(height=self.sh0)
        # self.calcHandle()
        # self.update()

    def about(self, *args):
        aboutWin = Toplevel(self.top)
        aboutWin.title("关于、致谢、声明与开源")
        aboutWin.config(padx=30, pady=30, bg="#222")
        aboutWin.geometry("600x600+300+100")
        aboutWin.minsize(600, 600)

        t1 = Text(aboutWin, bg="#222", fg="white", bd=0)
        t1.pack(side=TOP, fill=BOTH, expand=True)
        t1.insert(0.0, ABOUT_TEXT)
        t1.config(state=DISABLED)

    def beater(self, *args):
        beater = Beater(self.top, self.chart, self.audioFile, self.update)
        beater.mainloop()

    def star_mixer(self, *args):
        def callback():
            self.calcHandle()
            self.update()

        prList = []
        mixer = Mixer(self.top, self.chart, prList, callback, self.t0)
        mixer.mainloop()

    def play(self, *event):
        self.playing = not self.playing

        if self.playing:

            if not mixer.get_busy():
                mixer.music.play()
            self.lastFrameTime = time.time()
            # 校准到整秒
            second = int(self.ts / self.speed / self.chart.bpm * 1.875)
            self.ts = second * self.speed * self.chart.bpm / 1.875

            mixer.music.set_pos(second)
            mixer.music.unpause()
            self.loop()
        else:
            mixer.music.pause()
            self.calcHandle()
            self.update()

    def onT_Pressed(self, event):
        if self.playing:
            return
        else:
            self.playing = True
        if not mixer.get_busy():
            mixer.music.play()

        self.playStartTime = self.ts
        self.lastFrameTime = time.time()
        # 校准到整秒
        second = int(self.ts / self.speed / self.chart.bpm * 1.875)
        self.ts = second * self.speed * self.chart.bpm / 1.875
        mixer.music.set_pos(second)
        mixer.music.unpause()
        self.loop()

    def onT_Released(self, event):
        mixer.music.pause()
        self.playing = False
        self.set_to(self.playStartTime - 64)
        self.ts = self.playStartTime
        self.calcHandle()
        self.update()

    def loop(self):


        ct = time.time()
        dt = ct - self.lastFrameTime
        self.lastFrameTime = ct

        for line in self.chart.lineList:
            for note in line.noteList:
                if self.ts <= note.time_ < self.ts + dt / 1.875 * self.line.bpm * self.speed:
                    if note.type_ == 1 or note.type_ == 3:
                        self.tapSound.play()
                    elif note.type_ == 2:
                        self.dragSound.play()
                    elif note.type_ == 4:
                        self.flickSound.play()

        self.ts += dt / 1.875 * self.line.bpm * self.speed
        self.t0 = max(self.t0, self.ts - 64)
        self.lf0et1.config(text=f"{int(self.ts)} ({timeTtoBeat(int(self.ts))})")
        self.calcHandle()
        self.update()
        self.top.update()

        if self.playing:
            self.top.after(1, self.loop)
        else:
            return

    def launchPlayer(self, *args, enable3D=False):
        p = mp.Process(target=PlayerProcess, args=(self.chart, self.audioFile, self.illuFile, self.ts, enable3D))
        p.start()

    def save(self, *args):
        try:
            f = open(os.path.join(self.projectDir, "PCdata.toml"), "w", encoding="utf-8")
            f.write(toml.dumps(tomlIO.chart2toml(self.chart)))
            f.close()
            self.message("已成功保存到："+os.path.join(self.projectDir, "PCdata.toml"))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.message("自动保存时遇到错误："+str(e))

    def autoSave(self, *args):
        try:
            f = open(os.path.join(self.projectDir, "AutoSave.toml"), "w", encoding="utf-8")
            f.write(toml.dumps(tomlIO.chart2toml(self.chart)))
            f.close()
            self.message("已完成自动保存备份："+os.path.join(self.projectDir, "AutoSave.toml"))
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.message("自动保存时遇到错误："+str(e))


    def recoverToAutoSave(self, *args):
        if not os.path.exists(os.path.join(self.projectDir, "AutoSave.toml")):
            messagebox.showerror("Error", "没有自动保存的记录。")
            return
        if not messagebox.askokcancel("自动保存", "你确定要恢复到自动保存的记录？\n当前文件将被覆盖，此操作不可逆！"):
            return

        os.rename(os.path.join(self.projectDir, "PCdata.toml"), os.path.join(self.projectDir, "temp.toml"))
        os.rename(os.path.join(self.projectDir, "AutoSave.toml"), os.path.join(self.projectDir, "PCdata.toml"))
        os.remove(os.path.join(self.projectDir, "temp.toml"))
        messagebox.showinfo("自动保存", "恢复成功！\n重新启动程序后生效。")
        self.top.destroy()

    def open(self, tomlFile: str):
        f = open(os.path.join(self.projectDir, "PCdata.toml"), "r", encoding="utf-8")
        dic = toml.loads(f.read())
        f.close()

        self.chart = tomlIO.toml2chart(dic)
        self.calcHandle()
        self.update()

    def exportAsOfficial(self, *args):
        file = filedialog.asksaveasfilename(title="导出格式", filetypes=(("压缩包", "*.zip"),),
                                            initialfile=f"{self.chart.name}.zip")
        if not file:
            return

        # RPE META 数据
        self.chart.song = os.path.basename(self.audioFile)
        self.chart.bg = os.path.basename(self.illuFile)

        info = f"""#
Name: {self.chart.name}
Path: {self.chart.id}
Song: {self.chart.song}
Picture: {self.chart.bg}
Chart: chart.json
Level: {self.chart.level}
Composer: {self.chart.composer}
Charter: {self.chart.charter}
Illustrator: {self.chart.illustration}"""

        clear_directory("temp", clear=True)
        clear_directory("output", clear=False)

        with open("temp/chart.json", "w", encoding="utf-8") as outfile:
            outfile.write(self.chart.toJson())

        with open("temp/info.txt", "w", encoding="utf-8") as outfile:
            outfile.write(info)

        # 创建一个新的 ZIP 文件并添加文件
        with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write("temp/chart.json", "chart.json")
            zipf.write("temp/info.txt", "info.txt")
            zipf.write(self.audioFile, self.chart.song)
            zipf.write(self.illuFile, self.chart.bg)

            # 使用explorer的/select参数
            open_explorer_and_select_file(file)

    def exportAsRPE(self, *args):
        file = filedialog.asksaveasfilename(title="导出格式", filetypes=(("压缩包", "*.zip"), ("PEZ压缩包", "*.pez")),
                                            initialfile=f"{self.chart.name}.zip")
        if not file:
            return

        # RPE META 数据
        self.chart.song = os.path.basename(self.audioFile)
        self.chart.bg = os.path.basename(self.illuFile)

        info = f"""#
Name: {self.chart.name}
Path: {self.chart.id}
Song: {self.chart.song}
Picture: {self.chart.bg}
Chart: chart.json
Level: {self.chart.level}
Composer: {self.chart.composer}
Charter: {self.chart.charter}
Illustrator: {self.chart.illustration}"""

        clear_directory("temp", clear=True)
        clear_directory("output", clear=False)

        with open("temp/chart.json", "w", encoding="utf-8") as outfile:
            outfile.write(json.dumps(self.chart.toRPEJson(), ensure_ascii=False))

        with open("temp/info.txt", "w", encoding="utf-8") as outfile:
            outfile.write(info)

        # 创建一个新的 ZIP 文件并添加文件
        with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write("temp/chart.json", "chart.json")
            zipf.write("temp/info.txt", "info.txt")
            zipf.write(self.audioFile, self.chart.song)
            zipf.write(self.illuFile, self.chart.bg)

            # 使用explorer的/select参数
            open_explorer_and_select_file(file)

    def exportAs3DPEZ(self, *args):
        messagebox.showerror("Error", "暂时不支持。")

    def openFileByExplorer(self, *args):
        open_explorer_and_select_file(os.path.join(self.projectDir, "PCdata.toml"))









    def posToScreen(self, x, y):
        x1 = (x - 0) * self.sw1 + (self.sw0 - self.sw1) / 2
        y1 = self.sh0 - (y - 0) * self.sh1 - (self.sh0 - self.sh1) / 2
        return x1, y1

    def screenToPos(self, x1, y1):
        x = (x1 - (self.sw0 - self.sw1) / 2) / self.sw1
        y = (self.sh0 - (self.sh0 - self.sh1) / 2 - y1) / self.sh1
        return x, y

    def screenMatch(self, event):

        for line in self.chart.lineList:
            try:
                sw = self.sw0
                sh = self.sh0
            except AttributeError:
                return

            halfLength = 1 * sw
            lineLength = 1 * sw

            x = line.move1(self.ts)
            y = line.move2(self.ts)
            r = line.rotate(self.ts)

            xn, yn = self.posToScreen(x, y)
            xr = xn + math.cos((r + 90) / 180 * math.pi) * 50
            yr = yn - math.sin((r + 90) / 180 * math.pi) * 50

            a_rad = -r / 180 * math.pi
            distance = abs(math.sin(a_rad) * (event.x - xn) - math.cos(a_rad) * (event.y - yn))
            line.distance = distance

            if line is self.line:
                if abs(event.x - xn) + abs(event.y - yn) < 20:
                    return "move"
                if abs(event.x - xr) + abs(event.y - yr) < 15:
                    return "rotate"
        for line in self.chart.lineList:
            if line.distance < 8:
                return line

        return 0

    def onScreenMotion(self, event):
        matched = self.screenMatch(event)
        if isinstance(matched, Line):
            self.screen.config(cursor="hand2")
        elif matched == "move":
            self.screen.config(cursor="fleur")
        elif matched == "rotate":
            self.screen.config(cursor="exchange")
        else:
            self.screen.config(cursor="arrow")

    def onScreenPressed(self, event):
        matched = self.screenMatch(event)
        if isinstance(matched, Line):
            self.line = matched
            self.calcHandle()
            self.update()
        elif matched == "move":
            self.mouseOperationType = "screenMove"
            self.screen.bind("<Motion>", self.onScreenDrag)
        elif matched == "rotate":
            self.mouseOperationType = "screenRotate"
            self.screen.bind("<Motion>", self.onScreenDrag)

    def onScreenDrag(self, event):

        self.ts = round(self.ts)

        if self.mouseOperationType == "screenMove":

            if not self.dragCD:
                self.dragCD = True
                self.record("拖动判定线")

            move1, move2 = self.screenToPos(event.x, event.y)

            if self.ads.get():
                move1 = 0.5 if abs(move1 - 0.5) < 0.03 else move1
                move2 = 0.5 if abs(move2 - 0.5) < 0.03 else move2
                move1 = 0.2 if abs(move1 - 0.2) < 0.03 else move1
                move2 = 0.2 if abs(move2 - 0.2) < 0.03 else move2
                move1 = 0.8 if abs(move1 - 0.8) < 0.03 else move1
                move2 = 0.8 if abs(move2 - 0.8) < 0.03 else move2

            index = getEventIndexByTime(self.line.move1, self.ts)
            self.line.move1.endValueList[index] = move1
            self.line.move1.endTimeList[index] = self.ts
            if self.hooked.get():
                self.line.move1.startValueList[index] = move1

            index = getEventIndexByTime(self.line.move2, self.ts)
            self.line.move2.endValueList[index] = move2
            self.line.move2.endTimeList[index] = self.ts
            if self.hooked.get():
                self.line.move2.startValueList[index] = move2

            self.ts -= 0.1
            self.changeScreenMode(ScreenMode.MOVE1)
            self.calcHandle()
            self.update()

        elif self.mouseOperationType == "screenRotate":

            if not self.dragCD:
                self.dragCD = True
                self.record("旋转判定线")

            x = self.line.move1(self.ts)
            y = self.line.move2(self.ts)
            xn, yn = self.posToScreen(x, y)

            rotate = - math.atan2(event.y - yn, event.x - xn) / math.pi * 180 - 90

            if self.ads.get():
                rotate = 0 if abs(rotate - 0) < 9 else rotate
                rotate = 90 if abs(rotate - 90) < 9 else rotate
                rotate = 180 if abs(rotate - 180) < 9 else rotate
                rotate = -90 if abs(rotate + 90) < 9 else rotate
                rotate = -180 if abs(rotate + 180) < 9 else rotate

            index = getEventIndexByTime(self.line.rotate, self.ts)
            self.line.rotate.endValueList[index] = rotate
            self.line.rotate.endTimeList[index] = self.ts
            if self.hooked.get():
                self.line.rotate.startValueList[index] = rotate

            self.ts -= 0.1
            self.changeScreenMode(ScreenMode.ROTATE)
            self.calcHandle()
            self.update()

    def onScreenReleased(self, event):
        self.onScreenDrag(event)
        self.dragCD = False
        self.screen.bind("<Motion>", self.onScreenMotion)
        self.mouseOperationType = None
        self.renderScreen()













    def button2Event(self, event=None):
        if len(self.selected) == 0:
            pass
        elif self.screenMode is ScreenMode.NOTE:
            self.noteAttribute(event)
        else:
            self.eventAttribute(event)

    def noteAttribute(self, event=None):

        noteWin = Toplevel()
        noteWin.title("键属性")
        noteWin.config(padx=30, pady=30, bg="#222")
        noteWin.attributes("-toolwindow", True)
        noteWin.attributes("-topmost", True)
        noteWin.minsize(400, 700)

        if event is not None:
            dy = self.top.winfo_y() + event.y
            dx = self.top.winfo_x() + event.x
            noteWin.geometry("+%d+%d" % (dx, dy))

        def updateNoteAttribute():
            et1.delete(0, END)
            et2.delete(0, END)
            et3.delete(0, END)
            et4.delete(0, END)
            et5.delete(0, END)
            et6.delete(0, END)
            et7.delete(0, END)
            et8.delete(0, END)
            et9.delete(0, END)
            et10.delete(0, END)

            if len(self.selected) == 1 and isinstance(self.selected[0], Note):
                note = self.selected[0]
                et1.insert(0, note.type_)
                et2.insert(0, note.time_)
                et3.insert(0, note.posX)
                et4.insert(0, note.holdTime)
                et5.insert(0, note.speed)
                et6.insert(0, note.above)
                et7.insert(0, note.alpha)
                et8.insert(0, note.isFake)
                et9.insert(0, note.size)
                et10.insert(0, note.visibleTime)
                et11.insert(0, note.ban3D)

        def submitNoteAttribute(*event):
            self.record("编辑键的属性")
            if et1.get() != "":
                for note in self.selected:
                    note.type_ = int(float(et1.get()))
            if et2.get() != "":
                for note in self.selected:
                    note.time_ = float(et2.get())
            if et3.get() != "":
                for note in self.selected:
                    note.posX = float(et3.get())
            if et4.get() != "":
                for note in self.selected:
                    note.holdTime = float(et4.get())
            if et5.get() != "":
                for note in self.selected:
                    note.speed = float(et5.get())
            if et6.get() != "":
                for note in self.selected:
                    note.above = int(et6.get())
            if et7.get() != "":
                for note in self.selected:
                    note.alpha = float(et7.get())
            if et8.get() != "":
                for note in self.selected:
                    note.isFake = int(et8.get())
            if et9.get() != "":
                for note in self.selected:
                    note.size = float(et9.get())
            if et10.get() != "":
                for note in self.selected:
                    note.visibleTime = float(et10.get())
            if et11.get() != "":
                for note in self.selected:
                    note.ban3D = round(float(et11.get()))

            self.calcHandle()
            self.update()
            noteWin.destroy()
            # 触发Frame重新计算大小
            self.attrFrame.update_idletasks()

        lf1 = LabelFrameDark(noteWin, text="原生属性", padx=10, pady=10, width=360)
        lf1.pack(side=TOP, fill=X)
        lf2 = LabelFrameDark(noteWin, text="RPE属性", padx=10, pady=10)
        lf2.pack(side=TOP, fill=X, pady=10)
        lf3 = LabelFrameDark(noteWin, text="PhiChart属性", padx=10, pady=10, width=360)
        lf3.pack(side=TOP, fill=X)

        lb1 = LabelDark(lf1, anchor=W, text="类型 type")
        lb1.pack(side=TOP, fill=X)
        et1 = EntryDark(lf1)
        et1.pack(side=TOP, fill=X)

        lb2 = LabelDark(lf1, anchor=W, text="时间 time")
        lb2.pack(side=TOP, fill=X)
        et2 = EntryDark(lf1)
        et2.pack(side=TOP, fill=X)

        lb3 = LabelDark(lf1, anchor=W, text="水平位置 positionX")
        lb3.pack(side=TOP, fill=X)
        et3 = EntryDark(lf1)
        et3.pack(side=TOP, fill=X)

        lb4 = LabelDark(lf1, anchor=W, text="持续时间 holdTime")
        lb4.pack(side=TOP, fill=X)
        et4 = EntryDark(lf1)
        et4.pack(side=TOP, fill=X)

        lb5 = LabelDark(lf1, anchor=W, text="速度倍率 speed")
        lb5.pack(side=TOP, fill=X)
        et5 = EntryDark(lf1)
        et5.pack(side=TOP, fill=X)

        lb6 = LabelDark(lf1, anchor=W, text="下落方向（无对应字段）")
        lb6.pack(side=TOP, fill=X)
        et6 = EntryDark(lf1)
        et6.pack(side=TOP, fill=X)

        lb7 = LabelDark(lf2, anchor=W, text="不透明度 alpha")
        lb7.pack(side=TOP, fill=X)
        et7 = EntryDark(lf2)
        et7.pack(side=TOP, fill=X)

        lb8 = LabelDark(lf2, anchor=W, text="假键 isFake")
        lb8.pack(side=TOP, fill=X)
        et8 = EntryDark(lf2)
        et8.pack(side=TOP, fill=X)

        lb9 = LabelDark(lf2, anchor=W, text="缩放 size")
        lb9.pack(side=TOP, fill=X)
        et9 = EntryDark(lf2)
        et9.pack(side=TOP, fill=X)

        lb10 = LabelDark(lf2, anchor=W, text="可视时长 visibleTime")
        lb10.pack(side=TOP, fill=X)
        et10 = EntryDark(lf2)
        et10.pack(side=TOP, fill=X)

        lb11 = LabelDark(lf3, anchor=W, text="禁用3D ban3D")
        lb11.pack(side=TOP, fill=X)
        et11 = EntryDark(lf3)
        et11.pack(side=TOP, fill=X)

        bt2 = ButtonDark(noteWin, text="确认", command=submitNoteAttribute, height=2)
        bt2.pack(side=BOTTOM, fill=X)
        bt1 = ButtonDark(noteWin, text="转换时间单位制", command=..., height=2)
        bt1.pack(side=BOTTOM, fill=X, pady=10)

        noteWin.bind("<Return>", submitNoteAttribute)
        updateNoteAttribute()

    def eventAttribute(self, event=None):
        self.root = Toplevel()
        self.root.title("事件属性")
        self.root.config(padx=30, pady=30, bg="#222")
        self.root.attributes("-topmost", True)
        self.root.attributes("-toolwindow", True)
        self.root.minsize(400, 500)

        if event is not None:
            dy = self.top.winfo_y() + event.y
            dx = self.top.winfo_x() + event.x
            self.root.geometry("+%d+%d" % (dx, dy))

        def addSt(t: float):
            minTime = float("inf")
            maxTime = float(0)
            for event in self.selected:
                assert isinstance(event, Event)
                maxTime = max(event.et, maxTime)
                minTime = min(event.st, minTime)
            r = (maxTime - (minTime + t)) / (maxTime - minTime)
            timeSt(r)

        def addEt(t: float):
            minTime = float("inf")
            maxTime = float(0)
            for event in self.selected:
                assert isinstance(event, Event)
                maxTime = max(event.et, maxTime)
                minTime = min(event.st, minTime)
            r = ((maxTime + t) - minTime) / (maxTime - minTime)
            timeEt(r)

        def addSv(v: float):
            minTime = float("inf")
            maxTime = float(0)
            for event in self.selected:
                assert isinstance(event, Event)
                maxTime = max(event.ev, maxTime)
                minTime = min(event.sv, minTime)
            r = (maxTime - (minTime + v)) / (maxTime - minTime)
            timeEv(r)

        def addEv(v: float):
            minTime = float("inf")
            maxTime = float(0)
            for event in self.selected:
                assert isinstance(event, Event)
                maxTime = max(event.ev, maxTime)
                minTime = min(event.sv, minTime)
            r = ((maxTime + v) - minTime) / (maxTime - minTime)
            timeSv(r)

        def timeEt(r: float):
            r = float(r)
            minTime = float("inf")
            if len(self.selected) == 0:
                return
            for event in self.selected:
                assert isinstance(event, Event)
                minTime = min(event.st, minTime)
            for event in self.selected:
                assert isinstance(event, Event)
                event.setSt((event.st - minTime)* r + minTime)
                event.setEt((event.et - minTime)* r + minTime)
            self.calcHandle()
            self.update()

        def timeSt(r: float):
            r = float(r)
            maxTime = float(0)
            if len(self.selected) == 0:
                return
            for event in self.selected:
                assert isinstance(event, Event)
                maxTime = max(event.et, maxTime)
            for event in self.selected:
                assert isinstance(event, Event)
                event.setSt(maxTime - (maxTime - event.st)* r)
                event.setEt(maxTime - (maxTime - event.et)* r)
            self.calcHandle()
            self.update()

        def timeSv(r: float):
            r = float(r)
            minTime = float("inf")
            if len(self.selected) == 0:
                return
            for event in self.selected:
                assert isinstance(event, Event)
                minTime = min(event.sv, minTime)
            for event in self.selected:
                assert isinstance(event, Event)
                event.setSv((event.sv - minTime)* r + minTime)
                event.setEv((event.ev - minTime)* r + minTime)
            self.calcHandle()
            self.update()

        def timeEv(r: float):
            r = float(r)
            maxTime = float(0)
            if len(self.selected) == 0:
                return
            for event in self.selected:
                assert isinstance(event, Event)
                maxTime = max(event.ev, maxTime)
            for event in self.selected:
                assert isinstance(event, Event)
                event.setSv(maxTime - (maxTime - event.sv)* r)
                event.setEv(maxTime - (maxTime - event.ev)* r)
            self.calcHandle()
            self.update()

        def updateEventAttribute():
            et1.delete(0, END)
            et2.delete(0, END)
            et3.delete(0, END)
            et4.delete(0, END)

            if len(self.selected) == 1 and isinstance(self.selected[0], Event):
                event = self.selected[0]
                et1.insert(0, event.lineTimer.startTimeList[event.index])
                et2.insert(0, event.lineTimer.endTimeList[event.index])
                et3.insert(0, event.lineTimer.startValueList[event.index])
                et4.insert(0, event.lineTimer.endValueList[event.index])
                et5.setValue(event.easing())

        def submitEventAttribute(*event):
            self.record("编辑事件属性")

            if et1.get() != "":
                if et1.get()[0] == "*":
                    timeSt(float(et1.get()[1:]))
                elif et1.get()[0] == "/":
                    timeSt(1/float(et1.get()[1:]))
                elif et1.get()[0] == "+":
                    addSt(AnyTime2OffTime(et1.get()[1:]))
                elif et1.get()[0] == "-":
                    addSt(-AnyTime2OffTime(et1.get()[1:]))
                else:
                    for event in self.selected:
                        event.setSt(AnyTime2OffTime(et1.get()))
            if et2.get() != "":
                if et2.get()[0] == "*":
                    timeEt(float(et2.get()[1:]))
                elif et2.get()[0] == "/":
                    timeEt(1/float(et2.get()[1:]))
                elif et2.get()[0] == "+":
                    addEt(AnyTime2OffTime(et2.get()[1:]))
                elif et2.get()[0] == "-":
                    addEt(-AnyTime2OffTime(et2.get()[1:]))
                else:
                    for event in self.selected:
                        event.setEt(AnyTime2OffTime(et2.get()))
            if et3.get() != "":
                if et3.get()[0] == "*":
                    timeEv(float(et3.get()[1:]))
                if et3.get()[0] == "/":
                    timeEv(1/float(et3.get()[1:]))
                elif et3.get()[0] == "+":
                    addSv(float(et3.get()[1:]))
                elif et3.get()[0] == "-":
                    addSv(-float(et3.get()[1:]))
                else:
                    for event in self.selected:
                        event.setSv(float(et3.get()))
            if et4.get() != "":
                if et4.get()[0] == "*":
                    timeSv(float(et4.get()[1:]))
                if et4.get()[0] == "/":
                    timeSv(1/float(et4.get()[1:]))
                elif et4.get()[0] == "+":
                    addEv(float(et4.get()[1:]))
                elif et4.get()[0] == "-":
                    addEv(-float(et4.get()[1:]))
                else:
                    for event in self.selected:
                        event.setEv(float(et4.get()))

            for event in self.selected:
                event.setEasing(int(et5.getValue()))
            self.calcHandle()
            self.update()
            self.root.destroy()

        def updateLb6(*args):
            for event in self.selected:
                event.setEasing(int(et5.getValue()))
            self.update()
            lb6.config(text=easing_dict[et5.getValue()])

        lf1 = LabelFrameDark(self.root, text="原生属性", padx=10, pady=10)
        lf1.pack(side=TOP, fill=X)
        lf2 = LabelFrameDark(self.root, text="RPE属性", padx=10, pady=10)
        lf2.pack(side=TOP, fill=X, pady=10)

        lf1 = LabelFrameDark(self.root, text="原生属性", padx=10, pady=10)
        lf1.pack(side=TOP, fill=X)
        lf2 = LabelFrameDark(self.root, text="RPE属性", padx=10, pady=10)
        lf2.pack(side=TOP, fill=X, pady=10)

        lb1 = LabelDark(lf1, anchor=W, text="起始时间 startTime")
        lb1.pack(side=TOP, fill=X)
        et1 = EntryDark(lf1)
        et1.pack(side=TOP, fill=X)

        lb2 = LabelDark(lf1, anchor=W, text="结束时间 endTime")
        lb2.pack(side=TOP, fill=X)
        et2 = EntryDark(lf1)
        et2.pack(side=TOP, fill=X)

        lb3 = LabelDark(lf1, anchor=W, text="起始值 start")
        lb3.pack(side=TOP, fill=X)
        et3 = EntryDark(lf1)
        et3.pack(side=TOP, fill=X)

        lb4 = LabelDark(lf1, anchor=W, text="结束值 end")
        lb4.pack(side=TOP, fill=X)
        et4 = EntryDark(lf1)
        et4.pack(side=TOP, fill=X)

        lb5 = LabelDark(lf2, anchor=W, text="缓动编号")
        lb5.pack(side=TOP, fill=X)
        lb6 = LabelDark(lf2, anchor=W, text="Unknown")
        lb6.pack(side=TOP, fill=X)
        et5 = LiIntEntryDark(lf2, min=0, max=29, command=updateLb6)
        et5.pack(side=TOP, fill=X)

        # lb8 = LabelDark(lf2, anchor=CENTER, text="抱歉暂不支持。\n作者写代码写傻了")
        # lb8.pack(side=TOP, fill=X)

        bt2 = ButtonDark(self.root, text="确认", command=submitEventAttribute, height=2)
        bt2.pack(side=BOTTOM, fill=X)
        bt1 = ButtonDark(self.root, text="转换时间单位制", command=submitEventAttribute, height=2)
        bt1.pack(side=BOTTOM, fill=X, pady=10)

        self.root.bind("<Return>", submitEventAttribute)
        updateEventAttribute()
        updateLb6()










    def filter(self, *args):
        if self.screenMode is ScreenMode.NOTE:
            self.noteFilter()
        else:
            self.eventFilter()

    def noteFilter(self, *args):
        def match(pop=False):
            if not pop:
                matched = []
                for line in self.chart.lineList:
                    matched += line.noteList
            else:
                matched = self.selected.copy()

            et11v = et11.get()
            et21v = et21.get()
            et22v = et22.get()
            et31v = et31.get()
            et32v = et32.get()
            et41v = et41.get()
            et42v = et42.get()
            et51v = et51.get()
            et52v = et52.get()
            et61v = et61.get()
            et81v = et81.get()
            et91v = et91.get()
            et92v = et92.get()
            et101v = et101.get()
            et102v = et102.get()

            i = 0
            while i < len(matched):
                tick = False
                note: Note = matched[i]

                if et11v != "" and not int(et11v) == note.type_:
                    tick = True
                if et21v != "" and not float(et21v) <= note.time_:
                    tick = True
                elif et22v != "" and not note.time_ <= float(et22v):
                    tick = True
                if et31v != "" and not float(et31v) <= note.posX:
                    tick = True
                elif et32v != "" and not note.posX <= float(et32v):
                    tick = True
                if et41v != "" and not float(et41v) <= note.holdTime:
                    tick = True
                elif et42v != "" and not note.holdTime <= float(et42v):
                    tick = True
                if et51v != "" and not float(et51v) <= note.speed:
                    tick = True
                elif et52v != "" and not note.speed <= float(et52v):
                    tick = True
                if et61v != "" and not int(float(et61v)) == note.above:
                    tick = True
                if et81v != "" and not int(float(et81v)) == note.isFake:
                    tick = True
                if et81v != "" and not int(float(et81v)) == note.isFake:
                    tick = True
                if et91v != "" and not float(et91v) <= note.size:
                    tick = True
                elif et92v != "" and not note.size <= float(et92v):
                    tick = True
                if et101v != "" and not float(et101v) <= note.visibleTime:
                    tick = True
                elif et102v != "" and not note.visibleTime <= float(et102v):
                    tick = True

                if pop ^ tick:
                    matched.pop(i)
                else:
                    i += 1

            if pop:
                self.selected = matched
            else:
                self.selected += matched
            self.update()

        filterWin = Toplevel()
        filterWin.title("键高级筛选")
        filterWin.config(padx=30, pady=30, bg="#222")
        filterWin.minsize(500, 600)

        filterWin.columnconfigure(0, weight=3)
        filterWin.columnconfigure(1, weight=1)
        filterWin.columnconfigure(2, weight=2)
        filterWin.columnconfigure(3, weight=1)
        filterWin.columnconfigure(4, weight=2)
        filterWin.rowconfigure(10, weight=1)

        LabelDark(filterWin, text="类型 type").grid(row=0, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="等于").grid(row=0, column=1, sticky=W, padx=10, pady=5)
        et11 = EntryDark(filterWin)
        et11.grid(row=0, column=2, sticky=EW, columnspan=3)

        LabelDark(filterWin, text="时间 time").grid(row=1, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=1, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=1, column=3, padx=10, pady=5)
        et21 = EntryDark(filterWin)
        et21.grid(row=1, column=2, sticky=EW)
        et22 = EntryDark(filterWin)
        et22.grid(row=1, column=4, sticky=EW)

        LabelDark(filterWin, text="水平位置 positionX").grid(row=2, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=2, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=2, column=3, padx=10, pady=5)
        et31 = EntryDark(filterWin)
        et31.grid(row=2, column=2, sticky=EW)
        et32 = EntryDark(filterWin)
        et32.grid(row=2, column=4, sticky=EW)

        LabelDark(filterWin, text="持续时间 holdTime").grid(row=3, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=3, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=3, column=3, padx=10, pady=5)
        et41 = EntryDark(filterWin)
        et41.grid(row=3, column=2, sticky=EW)
        et42 = EntryDark(filterWin)
        et42.grid(row=3, column=4, sticky=EW)

        LabelDark(filterWin, text="速度倍率 speed").grid(row=4, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=4, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=4, column=3, padx=10, pady=5)
        et51 = EntryDark(filterWin)
        et51.grid(row=4, column=2, sticky=EW)
        et52 = EntryDark(filterWin)
        et52.grid(row=4, column=4, sticky=EW)

        LabelDark(filterWin, text="下落方向（无对应字段）").grid(row=5, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="等于").grid(row=5, column=1, sticky=W, padx=10, pady=5)
        et61 = EntryDark(filterWin)
        et61.grid(row=5, column=2, sticky=EW, columnspan=3)

        LabelDark(filterWin, text="假键 isFake").grid(row=7, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="等于").grid(row=7, column=1, sticky=W, padx=10, pady=5)
        et81 = EntryDark(filterWin)
        et81.grid(row=7, column=2, sticky=EW, columnspan=3)

        LabelDark(filterWin, text="缩放 size").grid(row=8, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=8, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=8, column=3, padx=10, pady=5)
        et91 = EntryDark(filterWin)
        et91.grid(row=8, column=2, sticky=EW)
        et92 = EntryDark(filterWin)
        et92.grid(row=8, column=4, sticky=EW)

        LabelDark(filterWin, text="可视时长 visibleTime").grid(row=9, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=9, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=9, column=3, padx=10, pady=5)
        et101 = EntryDark(filterWin)
        et101.grid(row=9, column=2, sticky=EW)
        et102 = EntryDark(filterWin)
        et102.grid(row=9, column=4, sticky=EW)

        bt1 = ButtonDark(filterWin, text="从选区中减去", height=2, command=lambda: match(True))
        bt1.grid(row=11, column=0, sticky=EW, columnspan=5, pady=5)
        bt2 = ButtonDark(filterWin, text="添加到选区", height=2, command=match)
        bt2.grid(row=12, column=0, sticky=EW, columnspan=5, pady=5)


    def eventFilter(self, *args):

        def match(pop=False):

            if not pop:
                if self.screenMode is ScreenMode.ALPHA:
                    lineTimer = self.line.alpha
                elif self.screenMode is ScreenMode.MOVE1:
                    lineTimer = self.line.move1
                elif self.screenMode is ScreenMode.MOVE2:
                    lineTimer = self.line.move2
                elif self.screenMode is ScreenMode.MOVE3:
                    lineTimer = self.line.move3
                elif self.screenMode is ScreenMode.THETA:
                    lineTimer = self.line.theta
                elif self.screenMode is ScreenMode.SPEED:
                    lineTimer = self.line.speed
                elif self.screenMode is ScreenMode.ROTATE:
                    lineTimer = self.line.rotate
                else:
                    raise ValueError(self.screenMode)
                    return

                matched = []
                for i in range(len(lineTimer.startValueList)):
                    matched.append(Event(lineTimer=lineTimer, index=i))

            else:
                matched = self.selected.copy()

            et11v = et11.get()
            et12v = et12.get()
            et21v = et21.get()
            et22v = et22.get()
            et31v = et31.get()
            et32v = et32.get()
            et41v = et41.get()
            et42v = et42.get()

            i = 0
            while i < len(matched):
                tick = False
                event: Event = matched[i]

                if et11v != "" and not float(et11v) <= event.st:
                    tick = True
                elif et12v != "" and not event.st <= float(et12v):
                    tick = True
                if et21v != "" and not float(et21v) <= event.et:
                    tick = True
                elif et22v != "" and not event.et <= float(et22v):
                    tick = True
                if et31v != "" and not float(et31v) <= event.sv:
                    tick = True
                elif et32v != "" and not event.sv <= float(et32v):
                    tick = True
                if et41v != "" and not float(et41v) <= event.ev:
                    tick = True
                elif et42v != "" and not event.ev <= float(et42v):
                    tick = True

                if pop ^ tick:
                    matched.pop(i)
                else:
                    i += 1

            if pop:
                self.selected = matched
            else:
                self.selected += matched
            self.update()

        filterWin = Toplevel()
        filterWin.title("事件高级筛选")
        filterWin.config(padx=30, pady=30, bg="#222")
        filterWin.minsize(500, 400)

        filterWin.columnconfigure(0, weight=3)
        filterWin.columnconfigure(1, weight=1)
        filterWin.columnconfigure(2, weight=2)
        filterWin.columnconfigure(3, weight=1)
        filterWin.columnconfigure(4, weight=2)
        filterWin.rowconfigure(4, weight=1)

        LabelDark(filterWin, text="开始时间 StartTime").grid(row=0, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=0, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=0, column=3, padx=10, pady=5)
        et11 = EntryDark(filterWin)
        et11.grid(row=0, column=2, sticky=EW)
        et12 = EntryDark(filterWin)
        et12.grid(row=0, column=4, sticky=EW)

        LabelDark(filterWin, text="结束时间 EndTime").grid(row=1, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=1, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=1, column=3, padx=10, pady=5)
        et21 = EntryDark(filterWin)
        et21.grid(row=1, column=2, sticky=EW)
        et22 = EntryDark(filterWin)
        et22.grid(row=1, column=4, sticky=EW)

        LabelDark(filterWin, text="开始值 StartValue").grid(row=2, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=2, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=2, column=3, padx=10, pady=5)
        et31 = EntryDark(filterWin)
        et31.grid(row=2, column=2, sticky=EW)
        et32 = EntryDark(filterWin)
        et32.grid(row=2, column=4, sticky=EW)

        LabelDark(filterWin, text="结束值 EndValue").grid(row=3, column=0, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="大于等于").grid(row=3, column=1, sticky=W, padx=10, pady=5)
        LabelDark(filterWin, text="小于等于").grid(row=3, column=3, padx=10, pady=5)
        et41 = EntryDark(filterWin)
        et41.grid(row=3, column=2, sticky=EW)
        et42 = EntryDark(filterWin)
        et42.grid(row=3, column=4, sticky=EW)

        bt1 = ButtonDark(filterWin, text="从选区中减去", height=2, command=lambda: match(True))
        bt1.grid(row=5, column=0, sticky=EW, columnspan=5, pady=5)
        bt2 = ButtonDark(filterWin, text="添加到选区", height=2, command=match)
        bt2.grid(row=6, column=0, sticky=EW, columnspan=5, pady=5)


if __name__ == '__main__':
    from libs.analyzer import analyzeJson
    from libs.autoMatch import Matcher

    matcher = Matcher("charts/白复生 AT")
    # chart = newDefaultChart(174, 24)
    chart = analyzeJson(r"D:\Projects\PygamePhiChart\charts\白复生 AT\Chart_AT #3649.json")
    editor = TimelineEditor(chart, matcher.audioFile, matcher.illuFile, "tk/projects/白复生AT/")

    mainloop()
