import enum
import math
from tkinter import *
from tkinter import font
from tkinter import ttk
from tk.color255 import *
from tk.pullbar import *
from tk.mytk import *
from chart import *


class ScreenMode(enum.Enum):
    NOTE = 0
    MOVE1 = 1
    MOVE2 = 2
    SPEED = 3
    ALPHA = 4
    ROTATE = 5

BG_COLOR = Color("#333")
MOVE1_COLOR_obj = Color("#ffd700")
MOVE2_COLOR_obj = Color("#ffd700")
SPEED_COLOR_obj = Color("#1e90ff")
ALPHA_COLOR_obj = Color("#00FA9A")
ROTATE_COLOR_obj = Color("#FF1493")
MOVE1_COLOR = MOVE1_COLOR_obj.toRRGGBB()
MOVE2_COLOR = MOVE2_COLOR_obj.toRRGGBB()
SPEED_COLOR = SPEED_COLOR_obj.toRRGGBB()
ALPHA_COLOR = ALPHA_COLOR_obj.toRRGGBB()
ROTATE_COLOR = ROTATE_COLOR_obj.toRRGGBB()
MOVE1_COLOR_DARK = MOVE1_COLOR_obj.mix(BG_COLOR, 0.3).toRRGGBB()
MOVE2_COLOR_DARK = MOVE2_COLOR_obj.mix(BG_COLOR, 0.3).toRRGGBB()
SPEED_COLOR_DARK = SPEED_COLOR_obj.mix(BG_COLOR, 0.3).toRRGGBB()
ALPHA_COLOR_DARK = ALPHA_COLOR_obj.mix(BG_COLOR, 0.3).toRRGGBB()
ROTATE_COLOR_DARK = ROTATE_COLOR_obj.mix(BG_COLOR, 0.3).toRRGGBB()

TAP_COLOR_obj = Color("#00BFFF")
DRAG_COLOR_obj = Color("#FFD700")
HOLD_COLOR_obj = Color("#4682B4")
FLICK_COLOR_obj = Color("#FF1493")
TAP_COLOR = TAP_COLOR_obj.toRRGGBB()
DRAG_COLOR = DRAG_COLOR_obj.toRRGGBB()
HOLD_COLOR = HOLD_COLOR_obj.toRRGGBB()
FLICK_COLOR = FLICK_COLOR_obj.toRRGGBB()
TAP_COLOR_DARK = TAP_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
DRAG_COLOR_DARK = DRAG_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
HOLD_COLOR_DARK = HOLD_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
FLICK_COLOR_DARK = FLICK_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()



class Handle:
    pass

class EventHandle(Handle):
    def __init__(self, lineTimer: LineTimer, index: int, type_: ScreenMode, x1: float, x2: float, y1: float, y2: float, color: str):
        self.x1, self.x2, self.y1, self.y2 = x1, x2, y1, y2
        self.lineTimer = lineTimer
        self.index = index
        self.color = color
        self.type_ = type_

class NoteHandle(Handle):
    def __init__(self, note: Note, x: float, y: float, color: str, width: int):
        self.x = x
        self.y = y
        self.note = note
        self.width = width
        self.color = color

class HoldHandle(Handle):
    def __init__(self, note: Note, x: float, y1: float, y2:float, color: str):
        self.x = x
        self.y1 = y1
        self.y2 = y2
        self.note = note
        self.color = color


class Arange:
    def __init__(self,start,stop,step):
        self.start=start
        self.stop=stop
        self.step=step
        self.current=0

    def __iter__(self):
        return self

    def __next__(self):
        if self.current>=self.stop:
            raise StopIteration
        self.current+=self.step
        return self.current


class TimelineEditor:
    def __init__(self, master, chart: Chart, lineIndex:int):
        self.lineIndex = lineIndex
        self.chart = chart
        self.line = chart.lineList[lineIndex]

        # 当前底部时间
        self.t0 = 1600
        # 最大时间
        self.t1 = 0
        # 底部到顶部的时间差
        self.dt = 80
        # canvas 高度
        self.h0 = 720
        self.w0 = 600
        # 被选中的 note
        self.selected = []
        # 自动吸附
        self.adsorption = True
        self.Xrecord = set()
        # 当前编辑器的操作对象
        self.screenMode: ScreenMode = ScreenMode.SPEED
        # 当前编辑器的渲染对象
        self.handles: list[Handle] = []

        # 换线的Frame
        self.altFrame: Frame|None = None
        self.alfFrameLabelList: list[LabelDark] = []

        self.top = Toplevel(master)
        self.top.title("时间轴编辑器")
        self.top.geometry("1000x800")
        self.top.minsize(1000, 800)
        self.top.config(padx=40, pady=30)
        self.top.config(bg="#222")

        # 工具栏
        self.toolFrame = FrameDark(self.top, height=30)
        self.toolFrame.pack(side=TOP, fill=X)
        self.toolFrameSpace = FrameDark(self.top, height=10)
        self.toolFrameSpace.pack(side=TOP, fill=X)
        ## 键类型选择
        noteFgList = (TAP_COLOR, DRAG_COLOR, HOLD_COLOR, FLICK_COLOR)
        noteList = ("Tap", "Drag", "Hold", "Flick")
        self.tf0rb1 = LiToolbox(self.toolFrame)
        self.tf0rb1.build(0, 0, 200, 30, noteList, noteFgList)
        ## 吸附
        self.tf0tb0 = LiToolBotton(self.toolFrame)
        self.tf0tb0.build(210, 0, 40, 30, text=">|<")
        noteList = ("1", "1/2", "1/4", "1/8")
        self.tf0rb2 = LiToolbox(self.toolFrame)
        self.tf0rb2.build(250, 0, 160, 30, noteList)
        ## 选中
        noteFgList = (None, None, MOVE1_COLOR, MOVE2_COLOR, ALPHA_COLOR, ROTATE_COLOR, SPEED_COLOR, None)
        noteList = ("Line", "Note", "MoveX", "MoveY", "Alpha", "Rotate", "Speed", "3D")
        self.tf0rb2 = LiToolbox(self.toolFrame)
        self.tf0rb2.build(420, 0, 400, 30, noteList, noteFgList)

        self.canvas = Canvas(self.top, width=self.w0, height=self.h0, bg="#333", highlightthickness=0)
        self.canvas.pack(side=LEFT, fill=Y)
        self.scroller = Canvas(self.top, width=20, height=self.h0, bg="#333", highlightthickness=0)
        self.scroller.pack(side=LEFT, padx=5, fill=Y)
        self.sp1 = LabelDark(self.top, width=1)
        self.sp1.pack(side=LEFT)
        self.fr1 = FrameDark(self.top)
        self.fr1.pack(side=RIGHT, fill=BOTH, expand=1)
        self.lf0 = LabelFrameDark(self.fr1, height=200, text="时间轴", padx=10, pady=5)
        self.lf0.pack(side=TOP, fill=X)
        self.lf1 = LabelFrameDark(self.fr1, height=200, text="判定线数据", padx=10, pady=5)
        self.lf1.pack(side=TOP, fill=X, ipady=5)
        self.lf2 = LabelFrameDark(self.fr1, height=200, text="键数据", padx=10, pady=5)
        self.lf2.pack(side=TOP, fill=X)
        self.lf3 = LabelFrameDark(self.fr1, height=120, text="添加新 note 时", padx=10, pady=5)
        self.lf3.pack(side=TOP, fill=X, ipady=5)

        # lb0
        self.font1 = font.Font(size=24, weight="bold")
        self.lf0lb1 = LabelDark(self.lf0, text="底部时间 Time", anchor=W)
        self.lf0lb1.pack(side=TOP, fill=X)
        self.lf0et1 = LabelDark(self.lf0, anchor=W, font=self.font1)
        self.lf0et1.pack(side=TOP, fill=X)
        self.lf0lb2 = LabelDark(self.lf0, text="底部秒数 Second", anchor=W)
        self.lf0lb2.pack(side=TOP, fill=X)
        self.lf0et2 = LabelDark(self.lf0, anchor=W, font=self.font1)
        self.lf0et2.pack(side=TOP, fill=X)
        self.lf0lb3 = LabelDark(self.lf0, text="底部节拍 Beat", anchor=W)
        self.lf0lb3.pack(side=TOP, fill=X)
        self.lf0et3 = LabelDark(self.lf0, anchor=W, font=self.font1)
        self.lf0et3.pack(side=TOP, fill=X)
        # lb1
        self.lf1lb1 = LabelDark(self.lf1, text="BPM", anchor=W)
        self.lf1lb1.pack(side=TOP, fill=X)
        self.lf1et1 = EntryFloatDark(self.lf1)
        self.lf1et1.pack(side=TOP, fill=X)
        # lb2
        self.lf2lb1 = LabelDark(self.lf2, text="类型 Type", anchor=W)
        self.lf2lb1.pack(side=TOP, fill=X)
        self.lf2et1 = EntryIntDark(self.lf2)
        self.lf2et1.pack(side=TOP, fill=X)
        self.lf2lb2 = LabelDark(self.lf2, text="时间 Time", anchor=W)
        self.lf2lb2.pack(side=TOP, fill=X)
        self.lf2et2 = EntryFloatDark(self.lf2)
        self.lf2et2.pack(side=TOP, fill=X)
        self.lf2lb3 = LabelDark(self.lf2, text="位置 PositionX", anchor=W)
        self.lf2lb3.pack(side=TOP, fill=X)
        self.lf2et3 = EntryFloatDark(self.lf2)
        self.lf2et3.pack(side=TOP, fill=X)
        self.lf2lb4 = LabelDark(self.lf2, text="持续 HoldTime", anchor=W)
        self.lf2lb4.pack(side=TOP, fill=X)
        self.lf2et4 = EntryFloatDark(self.lf2)
        self.lf2et4.pack(side=TOP, fill=X)
        self.lf2lb5 = LabelDark(self.lf2, text="倍速 Speed", anchor=W)
        self.lf2lb5.pack(side=TOP, fill=X)
        self.lf2et5 = EntryFloatDark(self.lf2)
        self.lf2et5.pack(side=TOP, fill=X)
        #lb3
        noteList = ("蓝键 Tap", "黄健 Drag", "长条 Hold", "红键 Flick")
        self.lf3rb1 = LiToolboxY(self.lf3)
        self.lf3rb1.build(0, 0, 100, 100, noteList)
        self.lf3cb1 = LiCheckbox(self.lf3)
        self.lf3cb1.build(100, 0, 100, 25, text="自动吸附", value=self.adsorption, command=self.set_adsorption)

        self.bt1 = ButtonDark(self.fr1, text="确认并编译", height=2, command=self.compile)
        self.bt1.pack(side=BOTTOM, fill=X, expand=False)

        # 确认最大时间
        self.t1 = max(self.line.noteList, key=lambda note: note.time_+note.holdTime)
        self.t1 = self.t1.time_ + self.t1.holdTime

        self.top.bind("<Configure>", self.changeSizeEvent)
        self.scroller.bind("<ButtonRelease-1>", self.scrollerBt1Event2)
        self.canvas.bind("<Control-Button-1>", self.mouseEventCtrl)
        self.scroller.bind("<Button-1>", self.scrollerBt1Event0)
        self.scroller.bind("<MouseWheel>", self.wheelEvent)
        self.canvas.bind("<MouseWheel>", self.wheelEvent)
        self.top.bind("<BackSpace>", self.deleteEvent)
        self.top.bind("<Delete>", self.deleteEvent)
        self.lf2et1.bind("<KeyRelease>", self.NoteInfoEvent)
        self.lf2et2.bind("<KeyRelease>", self.NoteInfoEvent)
        self.lf2et3.bind("<KeyRelease>", self.NoteInfoEvent)
        self.lf2et4.bind("<KeyRelease>", self.NoteInfoEvent)
        self.lf2et5.bind("<KeyRelease>", self.NoteInfoEvent)

        self.top.bind("<KeyPress-Alt_L>", self.createAltFrame)
        self.top.bind("<KeyRelease-Alt_L>", self.destroyAltFrame)
        self.canvas.bind("<Button-1>", self.mouseEvent)
        self.canvas.bind("<Motion>", self.motionEvent)

        self.update()

    def createAltFrame(self, *args):
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
            this.place(x=20, y=20*i)
            self.alfFrameLabelList.append(this)
        for i in range(len(self.alfFrameLabelList)):
            if i == self.lineIndex:
                self.alfFrameLabelList[i].config(bg="#777")
            else:
                self.alfFrameLabelList[i].config(bg="#222")
        self.top.update()
        self.altFrame.bind("<MouseWheel>", self.changeLine)

    def destroyAltFrame(self, args):
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
        self.line = chart.lineList[self.lineIndex]
        self.update()

    def rendFrame(self):
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
            text=f"{self.t0/32:.2f}",
            fill="#ddd"
        )
        for t in Arange(self.t0//4*4, self.t0//4*4+self.dt, 4):
            y = (1 - (t - self.t0) / self.dt) * self.h0
            if t % 32 == 0:
                self.canvas.create_line(
                    0, y, self.w0, y,
                    fill="#555"
                )
                self.canvas.create_text(
                    5, y, anchor=NW,
                    text=str(t),
                    fill="#ddd"
                )
                self.canvas.create_text(
                    self.w0-5, y, anchor=NE,
                    text=str(t//32),
                    fill="#ddd"
                )
            else:
                self.canvas.create_line(
                    50, y, self.w0-50, y,
                    fill="#444"
                )

        if self.adsorption:
            X = 0.06525 * self.w0
            for record in self.Xrecord:
                x = record * X + 0.5 * self.w0
                self.canvas.create_line(
                    x, 0, x, self.h0,
                    fill="#444"
                )

    def calcNoteHandleToRender(self, noteMode: bool):
        X = 0.06525 * self.w0
        b1 = self.t0
        b2 = self.t0 + self.dt

        # 记录 note 的 x 值，方便吸附
        self.Xrecord = set()

        for note in self.line.noteList:
            a1 = note.time_
            a2 = note.time_ + note.holdTime
            if max(a1, b1) > min(a2, b2):
                continue

            y0 = (1 - (note.time_ - self.t0) / self.dt) * self.h0
            y1 = (1 - (note.time_ + note.holdTime - self.t0) / self.dt) * self.h0
            y0 = min(y0, self.h0)
            y1 = max(y1, 0)
            x = note.posX * X + 0.5 * self.w0
            # self.Xrecord.add(note.posX)

            if noteMode:
                if note.type_ == 1:
                    handle = NoteHandle(note, x, y0, TAP_COLOR, 4)
                elif note.type_ == 2:
                    handle = NoteHandle(note, x, y0, DRAG_COLOR, 2)
                elif note.type_ == 4:
                    handle = NoteHandle(note, x, y0, FLICK_COLOR, 4)
                elif note.type_ == 3:
                    handle = HoldHandle(note, x, y0, y1, HOLD_COLOR)
                else:
                    continue
            else:
                if note.type_ == 1:
                    handle = NoteHandle(note, x, y0, TAP_COLOR_DARK, 4)
                elif note.type_ == 2:
                    handle = NoteHandle(note, x, y0, DRAG_COLOR_DARK, 2)
                elif note.type_ == 4:
                    handle = NoteHandle(note, x, y0, FLICK_COLOR_DARK, 4)
                elif note.type_ == 3:
                    handle = HoldHandle(note, x, y0, y1, HOLD_COLOR_DARK)
                else:
                    continue
            self.handles.append(handle)

    def calcEventHandleToRender(self, lineTimer: LineTimer, minValue: float, maxValue: float, color: str, screenMode: ScreenMode):

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
            x1 = ((startValue - minValue) / (maxValue - minValue) + 0.1) * self.w0/1.2
            x2 = ((endValue - minValue) / (maxValue - minValue) + 0.1) * self.w0/1.2
            y1 = (1 - (startTimeT - self.t0) / self.dt) * self.h0
            y2 = (1 - (endTimeT - self.t0) / self.dt) * self.h0
            handle = EventHandle(lineTimer, i, screenMode, x1, x2, y1, y2, color)
            self.handles.append(handle)

    def renderHandle(self):

        NS = 0.05 * self.w0

        for handle in self.handles:
            if isinstance(handle, EventHandle):
                if abs(handle.y2 - handle.y1) < 20:
                    handleSize = 3
                else:
                    handleSize = 5

                if handle in self.selected:

                    self.canvas.create_line(
                        handle.x1, handle.y1 - handleSize - 4,
                        handle.x2, handle.y2 + handleSize + 4,
                        fill=handle.color,
                        width=6,
                    )

                    self.canvas.create_rectangle(
                        handle.x1 - handleSize - 4, handle.y1 - handleSize - 4,
                        handle.x1 + handleSize + 4, handle.y1 + 4,
                        outline="#ddd",
                        width=4,
                    )

                    self.canvas.create_rectangle(
                        handle.x2 - handleSize - 4, handle.y2 - 4,
                        handle.x2 + handleSize + 4, handle.y2 + handleSize + 4,
                        outline="#ddd",
                        width=4,
                    )


                self.canvas.create_line(
                    handle.x1, handle.y1,
                    handle.x2, handle.y2,
                    fill=handle.color,
                    width=1,
                )

                self.canvas.create_rectangle(
                    handle.x1 - handleSize, handle.y1 - handleSize,
                    handle.x1 + handleSize, handle.y1 + 0,
                    outline=handle.color,
                    fill=handle.color,
                    width=1,
                )

                self.canvas.create_rectangle(
                    handle.x2 - handleSize, handle.y2 - 0,
                    handle.x2 + handleSize, handle.y2 + handleSize,
                    outline=handle.color,
                    width=1,
                )

            elif isinstance(handle, NoteHandle):
                self.canvas.create_line(
                    handle.x - NS, handle.y,
                    handle.x + NS, handle.y,
                    fill=handle.color,
                    width=handle.width,
                )
                if handle in self.selected:
                    self.canvas.create_rectangle(
                        handle.x - 6 - NS, handle.y - 8,
                        handle.x + 6 + NS, handle.y + 8,
                        outline="#ddd",
                        width=4,
                    )

            elif isinstance(handle, HoldHandle):
                self.canvas.create_polygon(
                    handle.x - NS, handle.y1,
                    handle.x + NS, handle.y2,
                    fill=handle.color,
                )

                if handle in self.selected:
                    self.canvas.create_rectangle(
                        handle.x - 6 - NS, handle.y1 - 6,
                        handle.x + 6 + NS, handle.y2 + 6,
                        outline="#ddd",
                        width=4,
                    )


    def set_adsorption(self, value=None):
        if value is None:
            self.adsorption = not self.adsorption
        else:
            self.adsorption = value
        self.update()

    def rendScroll(self):
        y0 = self.h0 * (1 - (self.t0 / self.t1))
        y1 = self.h0 * (1 - ((self.t0 + self.dt) / self.t1))
        self.scroller.delete("all")
        self.scroller.create_rectangle(
            0, y0, 20, y1,
            fill="#666",
            width=0
        )
        self.scroller.create_line(
            0, y0, 20, y0,
            fill="#ddd",
            width=3,
        )

        self.lf0et1.config(text=f"{self.t0:.2f}")
        self.lf0et2.config(text=f"{self.t0/self.line.bpm*1.875:.2f}")
        self.lf0et3.config(text=f"{self.t0/32:.2f}")

    def updateNoteInfo(self):
        self.lf2et1.delete("0", END) 
        self.lf2et2.delete("0", END)
        self.lf2et3.delete("0", END)
        self.lf2et4.delete("0", END)
        self.lf2et5.delete("0", END)

        if not len(self.selected) == 1:
            return
        note = self.selected[0]

        self.lf2et1.insert("0", note.type_)
        self.lf2et2.insert("0", note.time_)
        self.lf2et3.insert("0", note.posX)
        self.lf2et4.insert("0", note.holdTime)
        self.lf2et5.insert("0", note.speed)

    def NoteInfoEvent(self, event):
        try:
            type_ = self.lf2et1.getInt()
            for note in self.selected:
                note.type_ = type_
        except ValueError:
            pass
        try:
            time_ = self.lf2et2.getFloat()
            for note in self.selected:
                note.time_ = time_
        except ValueError:
            pass
        try:
            posX = self.lf2et3.getFloat()
            for note in self.selected:
                note.posX = posX
        except ValueError:
            pass
        try:
            holdTime = self.lf2et4.getFloat()
            for note in self.selected:
                note.holdTime = holdTime
        except ValueError:
            pass
        try:
            speed = self.lf2et5.getFloat()
            for note in self.selected:
                note.speed = speed
        except ValueError:
            pass

        for note in self.selected:
            if note.holdTime > 0:
                note.type_ = 3
                self.lf2et1.delete("0", END)
                self.lf2et1.insert("0", 3)


    def calcHandle(self):

        self.handles: list[Handle] = []

        if self.screenMode is not ScreenMode.ALPHA:
            self.calcEventHandleToRender(self.line.alpha, minValue=0, maxValue=1, color=ALPHA_COLOR_DARK, screenMode=ScreenMode.ALPHA)
        if self.screenMode is not ScreenMode.ROTATE:
            self.calcEventHandleToRender(self.line.rotate, minValue=-360, maxValue=360, color=ROTATE_COLOR_DARK, screenMode=ScreenMode.ROTATE)
        if self.screenMode is not ScreenMode.MOVE1:
            self.calcEventHandleToRender(self.line.move1, minValue=0, maxValue=1, color=MOVE1_COLOR_DARK, screenMode=ScreenMode.MOVE1)
        if self.screenMode is not ScreenMode.MOVE2:
            self.calcEventHandleToRender(self.line.move2, minValue=0, maxValue=1, color=MOVE2_COLOR_DARK, screenMode=ScreenMode.MOVE2)
        if self.screenMode is not ScreenMode.SPEED:
            self.calcEventHandleToRender(self.line.speed, minValue=0, maxValue=10, color=SPEED_COLOR_DARK, screenMode=ScreenMode.SPEED)
        if self.screenMode is not ScreenMode.NOTE:
            self.calcNoteHandleToRender(False)

        if self.screenMode is ScreenMode.ALPHA:
            self.calcEventHandleToRender(self.line.alpha, minValue=0, maxValue=1, color=ALPHA_COLOR, screenMode=ScreenMode.ALPHA)
        elif self.screenMode is ScreenMode.ROTATE:
            self.calcEventHandleToRender(self.line.rotate, minValue=-360, maxValue=360, color=ROTATE_COLOR, screenMode=ScreenMode.ROTATE)
        elif self.screenMode is ScreenMode.MOVE1:
            self.calcEventHandleToRender(self.line.move1, minValue=0, maxValue=1, color=MOVE1_COLOR, screenMode=ScreenMode.MOVE1)
        elif self.screenMode is ScreenMode.MOVE2:
            self.calcEventHandleToRender(self.line.move2, minValue=0, maxValue=1, color=MOVE2_COLOR, screenMode=ScreenMode.MOVE2)
        elif self.screenMode is ScreenMode.SPEED:
            self.calcEventHandleToRender(self.line.speed, minValue=0, maxValue=10, color=SPEED_COLOR, screenMode=ScreenMode.SPEED)
        elif self.screenMode is ScreenMode.NOTE:
            self.calcNoteHandleToRender(True)

    def update(self):

        self.canvas.delete("all")
        self.rendFrame()
        self.rendScroll()
        self.renderHandle()

    def mouseMatch(self, event):
        print("mouseMatch")
        minDistance: float = 20
        matchedObj: Handle|None = None
        NS = 0.05 * self.w0

        for handle in self.handles:
            if isinstance(handle, NoteHandle):
                d = math.sqrt((event.x - handle.x) ** 2 + (event.y - handle.y) ** 2)
                d -= 5 if self.screenMode is ScreenMode.NOTE else 0
            if isinstance(handle, HoldHandle):
                if abs(handle.x - event.x) < NS and handle.y1 < event.y < handle.y2:
                    d = 0
                else:
                    d = float('inf')
                if self.screenMode is ScreenMode.NOTE:
                    d -= 5
            if isinstance(handle, EventHandle):
                if not handle.y2 < event.y < handle.y1:
                    d = float('inf')
                else:
                    xp = (event.y - handle.y1) / (handle.y2 - handle.y1) * (handle.x2 - handle.x1) + handle.x1
                    d = abs(event.x - xp)
            if d < minDistance:
                minDistance = d
                matchedObj = handle
        return matchedObj

    def mouseCast(self, event):
        # 将鼠标位置转换为时间和位置数据

        X = 0.06525 * self.w0
        posX = (event.x - 0.5* self.w0) / X
        time_ = self.dt + self.t0 - self.dt*event.y/self.h0

        if self.adsorption:
            minDistance = 1000
            matched = None
            for record in self.Xrecord:
                if abs(posX - record) < minDistance:
                    minDistance = abs(posX - record)
                    matched = record
            if minDistance < 1:
                posX = matched
            else:
                posX = round(posX)
            time_ = (time_ + 2) // 4 * 4

        return (posX, time_)

    def mouseEvent(self, event):
        matched = self.mouseMatch(event)
        if matched is not None:
            if isinstance(matched, (HoldHandle, NoteHandle)):
                i = self.changeScreenMode(ScreenMode.NOTE)
            elif isinstance(matched, EventHandle):
                i = self.changeScreenMode(matched.type_)
            self.selected = [matched] if not i else []
        else:
            self.selected = []
        self.motionEvent(event)
        self.update()
        return

    def changeScreenMode(self, screenMode):
        if screenMode is not self.screenMode:
            self.screenMode = screenMode
            self.calcHandle()
            return True
        else:
            return False

    def deleteEvent(self, event):
        for handle in self.selected:
            try:
                if isinstance(handle, (NoteHandle, HoldHandle)):
                    self.line.noteList.remove(handle.note)
                elif isinstance(handle, EventHandle):
                    handle.lineTimer.popPeriod(handle.index)
            except ValueError:
                pass
        self.selected = []
        self.motionEvent(event)
        self.calcHandle()
        self.update()

    def mouseEventCtrl(self, event):
        matched = self.mouseMatch(event)
        if matched is None:
            return
        if isinstance(matched, (HoldHandle, NoteHandle)):
            if self.changeScreenMode(ScreenMode.NOTE):
                self.selected = [matched]
                self.update()
                return
        elif isinstance(matched, EventHandle):
            if self.changeScreenMode(matched.type_):
                self.selected = [matched]
                self.update()
                return
        self.selected.append(matched)
        self.motionEvent(event)
        self.update()

    def motionEvent(self, event):

        NS = 0.05 * self.w0
        print(self.selected)

        for handle in self.selected:
            if (isinstance(handle, NoteHandle)
                and handle.x - NS < event.x < handle.x + NS
                and handle.y - 10 < event.y < handle.y + 10):
                self.canvas.config(cursor="fleur")
                return
            elif isinstance(handle, EventHandle):
                xp = (event.y - handle.y1) / (handle.y2 - handle.y1) * (handle.x2 - handle.x1) + handle.x1
                if (abs(event.x - handle.x1) + abs(event.y - handle.y1) < 20
                    or abs(event.y - handle.y2) + abs(event.x - handle.x2)) < 20:
                    self.canvas.config(cursor="sb_h_double_arrow")
                    return
                if abs(event.x - xp) < 10:
                    self.canvas.config(cursor="fleur")
                    return
        for handle in self.handles:
            if (isinstance(handle, NoteHandle)
                and handle.x - NS < event.x < handle.x + NS
                and handle.y - 10 < event.y < handle.y + 10):
                self.canvas.config(cursor="hand2")
                return
            elif isinstance(handle, EventHandle):
                xp = (event.y - handle.y1) / (handle.y2 - handle.y1) * (handle.x2 - handle.x1) + handle.x1
                if (abs(event.x - handle.x1) + abs(event.y - handle.y1) < 20
                    or abs(event.y - handle.y2) + abs(event.x - handle.x2)) < 20:
                    self.canvas.config(cursor="hand2")
                    return
                if abs(event.x - xp) < 10:
                    self.canvas.config(cursor="hand2")
                    return
        self.canvas.config(cursor="arrow")


    def set_to(self, t0):
        t0 = max(t0, 0)
        t0 = min(self.t1, t0)
        self.t0 = t0
        self.calcHandle()
        self.update()

    def scrollerBt1Event0(self, event):
        self.scroller.bind("<Motion>", self.scrollerBt1Event1)

    def scrollerBt1Event1(self, event):
        t = self.t1 * (1 - (event.y / self.h0))
        self.set_to(t)

    def scrollerBt1Event2(self, event):
        self.scroller.unbind("<Motion>")
        self.scrollerBt1Event1(event)

    def wheelEvent(self, event):
        self.set_to(event.delta/10 + self.t0)

    def changeSizeEvent(self, event):
        self.h0 = self.canvas.winfo_height()
        self.calcHandle()
        self.update()

    def compile(self):
        self.line.noteList = sorted(self.line.noteList, key=lambda x: x.time_)

        # 开始计算 floorPosition
        f0 = 0
        speedEventIndex = 0
        for note in self.line.noteList:
            while note.time_ > self.line.speed.endTimeList[speedEventIndex]:
                st = self.line.speed.startTimeList[speedEventIndex]
                et = self.line.speed.endTimeList[speedEventIndex]
                speed = self.line.speed.endValueList[speedEventIndex]
                speedEventIndex += 1
                f0 += (et - st) * 1.875 / self.line.bpm * speed

            st = self.line.speed.startTimeList[speedEventIndex]
            speed = self.line.speed.endValueList[speedEventIndex]
            floorPos = f0 + (note.time_ - st) * 1.875 / self.line.bpm * speed
            note.floorPos = floorPos

        f = open("output.json", "w", encoding="utf-8")
        f.write(self.chart.toJson())
        f.close()
        self.top.destroy()


if __name__ == '__main__':
    import analyzer
    chart = analyzer.analyzeJson(r"D:\Projects\PygamePhiChart\charts\rr\Chart_AT #4757")

    top = Tk()
    top.geometry("50x50+0+0")
    te1 = TimelineEditor(top, chart, 0)

    mainloop()