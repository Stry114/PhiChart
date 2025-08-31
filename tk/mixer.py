from tkinter import *
from tkinter import font

import analyzer
from tk.chartException import sorted
from tk.pullbar import *
from tk.color255 import Color
from pygame import mixer
from chart import *
import time
import json
import os

BG_COLOR = Color("#333")
COLOR1 = Color("#FF6B6B")
COLOR2 = Color("#FFB26B")
COLOR3 = Color("#FFE06B")
COLOR4 = Color("#6BFFB2")
COLOR5 = Color("#6BD5FF")
COLOR6 = Color("#6B85FF")
COLOR7 = Color("#A36BFF")
COLOR1_DARK = COLOR1.mix(BG_COLOR, 0.2)
COLOR2_DARK = COLOR2.mix(BG_COLOR, 0.2)
COLOR3_DARK = COLOR3.mix(BG_COLOR, 0.2)
COLOR4_DARK = COLOR4.mix(BG_COLOR, 0.2)
COLOR5_DARK = COLOR5.mix(BG_COLOR, 0.2)
COLOR6_DARK = COLOR6.mix(BG_COLOR, 0.2)
COLOR7_DARK = COLOR7.mix(BG_COLOR, 0.2)

COLOR_LIST = [COLOR1, COLOR2, COLOR3, COLOR4, COLOR5, COLOR6, COLOR7]
COLOR_DARK_LIST = [COLOR1_DARK, COLOR2_DARK, COLOR3_DARK, COLOR4_DARK, COLOR5_DARK, COLOR6_DARK, COLOR7_DARK]

BG_COLOR = Color("#333")
MOVE1_COLOR_obj = Color("#999999")
MOVE2_COLOR_obj = Color("#ffd700")
SPEED_COLOR_obj = Color("#1e90ff")
ALPHA_COLOR_obj = Color("#00FA9A")
THETA_COLOR_obj = Color("#7A67EE")
ROTATE_COLOR_obj = Color("#FF1493")
MOVE1_COLOR = MOVE1_COLOR_obj.toRRGGBB()
MOVE2_COLOR = MOVE2_COLOR_obj.toRRGGBB()
SPEED_COLOR = SPEED_COLOR_obj.toRRGGBB()
ALPHA_COLOR = ALPHA_COLOR_obj.toRRGGBB()
THETA_COLOR = THETA_COLOR_obj.toRRGGBB()
ROTATE_COLOR = ROTATE_COLOR_obj.toRRGGBB()
MOVE1_COLOR_DARK = MOVE1_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
MOVE2_COLOR_DARK = MOVE2_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
SPEED_COLOR_DARK = SPEED_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
ALPHA_COLOR_DARK = ALPHA_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
THETA_COLOR_DARK = THETA_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()
ROTATE_COLOR_DARK = ROTATE_COLOR_obj.mix(BG_COLOR, 0.2).toRRGGBB()

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


def appendLineTimer(lineTimer: LineTimer, lineTimer2: LineTimer, dt):
    for i in lineTimer2.startTimeList:
        print("粘贴一个事件", i + dt, end="\n")
        lineTimer.startTimeList.append(i + dt)
    for i in lineTimer2.endTimeList:
        lineTimer.endTimeList.append(i + dt)
        print("到", i + dt)
    for i in lineTimer2.startValueList:
        lineTimer.startValueList.append(i)
    for i in lineTimer2.endValueList:
        lineTimer.endValueList.append(i)


class Mixer(Toplevel):
    class Placing:
        def __init__(self, period: Period):
            self.period = period
            self.length = period.length
            self.time = 0
            self.index = 0

    def __init__(self, parent, chart: Chart, periodList: list[Period], callback, t0=0):
        Toplevel.__init__(self, parent)
        self.parent = parent
        self.title("Mixer（总览）")
        self.geometry("1000x800")
        self.config(bg="#222")
        self.config(padx=30, pady=30)

        # 起始点
        self.t0 = int(t0)
        # 效果列表
        self.periodList = periodList
        # 事件列表的y0值
        self.y0 = 0
        self.y1 = 999

        # 被选中的事件
        self.selectedIndex = -1
        self.selectingPlacing: Place | None = None
        self.placingList: list[Mixer.Placing] = []

        self.lines = chart.lineList
        self.chart = chart
        self.mousePos: tuple | None = None
        self.callback = callback

        self.rightFrame = Frame(self, bg='#222', highlightthickness=0, width=200)
        self.rightFrame.pack(side=RIGHT, fill=Y, padx=20)
        self.timeLine = Canvas(self, bg='#282828', highlightthickness=0, height=40)
        self.timeLine.pack(side=TOP, fill=X, pady=10)
        self.lineIndex = Canvas(self, bg='#333', highlightthickness=0, width=80)
        self.lineIndex.pack(side=LEFT, fill=Y)
        self.canvas = Canvas(self, bg='#222', highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=3)

        self.ft1 = font.Font(family='Microsoft yahei', size=12, weight='bold')
        LabelDark(self.rightFrame, anchor=W, text="预制事件列表", font=self.ft1).pack(side=TOP, fill=X)
        LabelDark(self.rightFrame, anchor=W, text="点击选择事件，放置到空闲轨道上。").pack(side=TOP, fill=X, pady=5)
        self.cp1 = Canvas(self.rightFrame, bg='#282828', highlightthickness=0, width=200)
        self.cp1.pack(side=TOP, fill=BOTH, expand=1, pady=10)
        self.bt1 = ButtonDark(self.rightFrame, text="从谱面中截取", command=self.exactPeriodTool, height=2)
        self.bt1.pack(side=TOP, fill=X, pady=10)
        self.bt2 = ButtonDark(self.rightFrame, text="Mix it", command=self.submit, height=2)
        self.bt2.pack(side=TOP, fill=X)

        self.canvas.bind("<Motion>", self.motionEvent)
        self.canvas.bind("<Leave>", self.mouseLeave)
        self.canvas.bind("<MouseWheel>", self.wheelEvent)
        self.canvas.bind("<Button-1>", self.mouseEvent)
        self.cp1.bind("<MouseWheel>", self.cp1WheelEvent)
        self.cp1.bind("<Button-1>", self.selectPeriod)

        self.loadPeriodFromJson()
        self.after(100, self.update)
        self.after(100, self.updateCp1)

    def loadPeriodFromJson(self):
        for file in os.listdir("tk/res/period"):
            if not file.endswith(".json"):
                continue
            try:
                f = open("tk/res/period/" + file, "r")
                dic = json.load(f)
                f.close()

                period = Period(dic["length"], dic["name"])
                period.colorIndex = dic["colorIndex"]

                key = ("alpha", "move1", "move2", "rotate")
                lts = (period.alpha, period.move1, period.move2, period.rotate)
                for j in range(len(lts)):
                    lineTimer = lts[j]
                    lineTimer.startTimeList = dic[key[j]][0]
                    lineTimer.endTimeList = dic[key[j]][1]
                    lineTimer.startValueList = dic[key[j]][2]
                    lineTimer.endValueList = dic[key[j]][3]
                self.periodList.append(period)
            except FileNotFoundError:
                pass

    def exactPeriodTool(self):

        def submit():
            try:
                line = self.lines[int(et2.get())]
                name = et1.get()
                st = float(et3.get()) * 32
                et = float(et4.get()) * 32
                ci = int(et5.get())
            except Exception as e:
                import traceback
                traceback.print_exc()
                return

            period = exactPeriodFromLine(line, st, et)
            period.name = name
            period.colorIndex = ci
            self.periodList.append(period)
            self.updateCp1()

            f = open("tk/res/period/" + name + ".json", "w")
            json.dump(period.toJsonDic(), f, indent=4)
            f.close()

        root = Toplevel(self)
        root.title("截取工具")
        root.minsize(400, 400)
        root.config(bg='#222', padx=30, pady=30)

        LabelDark(root, anchor=W, text="新事件名称").pack(side=TOP, fill=X)
        et1 = EntryDark(root)
        et1.pack(side=TOP, fill=X)
        LabelDark(root, anchor=W, text="线序号").pack(side=TOP, fill=X)
        et2 = EntryDark(root)
        et2.pack(side=TOP, fill=X)
        LabelDark(root, anchor=W, text="开始拍数").pack(side=TOP, fill=X)
        et3 = EntryDark(root)
        et3.pack(side=TOP, fill=X)
        LabelDark(root, anchor=W, text="结束拍数").pack(side=TOP, fill=X)
        et4 = EntryDark(root)
        et4.pack(side=TOP, fill=X)
        LabelDark(root, anchor=W, text="颜色标记").pack(side=TOP, fill=X)
        et5 = EntryDark(root)
        et5.pack(side=TOP, fill=X)
        et5.insert(END, "4")

        bt1 = ButtonDark(root, text="截取", command=submit, height=2)
        bt1.pack(side=BOTTOM, fill=X)

    def submit(self):
        for placing in self.placingList:
            appendLineTimer(self.lines[placing.index].alpha, placing.period.alpha, placing.time)
            appendLineTimer(self.lines[placing.index].move1, placing.period.move1, placing.time)
            appendLineTimer(self.lines[placing.index].move2, placing.period.move2, placing.time)
            appendLineTimer(self.lines[placing.index].rotate, placing.period.rotate, placing.time)
        sorted(self.chart)
        self.placingList = []
        self.destroy()
        self.callback()

    def updateCp1(self):
        self.cp1.delete("all")

        for i in range(len(self.periodList)):
            period = self.periodList[i]
            self.cp1.create_rectangle(
                0, i * 40 + 2 - self.y0, 200, i * 40 + 38 - self.y0,
                fill=COLOR_DARK_LIST[period.colorIndex % len(COLOR_LIST)].toRRGGBB(),
                width=0
            )
            self.cp1.create_rectangle(
                0, i * 40 + 2 - self.y0, 10, i * 40 + 38 - self.y0,
                fill=COLOR_LIST[period.colorIndex % len(COLOR_LIST)].toRRGGBB(),
                width=0
            )
            self.cp1.create_text(
                20, i * 40 + 10 - self.y0,
                anchor=NW, fill="#ddd",
                text=f"{period.name} ({period.length // 32:.2f} beats)"
            )
            if i == self.selectedIndex:
                self.cp1.create_rectangle(
                    3, i * 40 + 3 - self.y0, 197, i * 40 + 37 - self.y0,
                    outline="#fff",
                    width=6
                )

    def update(self):
        self.canvas.delete("all")
        self.timeLine.delete("all")
        self.lineIndex.delete("all")

        h0 = self.canvas.winfo_height()
        w0 = self.canvas.winfo_width()

        h1 = (h0 - 80) / len(self.lines)
        h2 = h0 / len(self.lines)
        hs = 0

        dur = 256
        div = 4

        placingList = self.placingList.copy()
        if self.selectingPlacing is not None and self.mousePos is not None:
            placingList.append(self.selectingPlacing)

        for t in range(self.t0, self.t0 + dur + div, 1):
            p = (t - self.t0) / dur * w0 + 80
            if t % 32 == 0:
                self.timeLine.create_line(p, 10, p, 40, fill="#999")
                self.timeLine.create_text(p + 5, 0, anchor=NW, fill="#ddd", text=str(int(t // 32)))
            elif t % 32 % 8 == 0:
                self.timeLine.create_line(p, 20, p, 40, fill="#999")
            elif t % 32 % 4 == 0:
                self.timeLine.create_line(p, 20, p, 40, fill="#555")
        if self.mousePos is not None:
            self.timeLine.create_line(self.mousePos[0] + 80, 0, self.mousePos[0] + 80, 40, fill="#ddd", width=4)

        for i in range(len(self.lines)):
            if self.mousePos is None:
                y1 = hs + 1
                y2 = hs + h2
                hs += h2

                y3 = y1 + (y2 - y1) * 0.0
                y4 = y1 + (y2 - y1) * 1.0
            else:
                if abs(self.mousePos[1] - h2 * i) < h2 / 2:
                    ht = h1 + 80
                    y1 = hs + 1
                    y2 = hs + ht
                    hs += ht
                    y3 = y1 + (y2 - y1) * 0.0
                    y4 = y1 + (y2 - y1) * 0.5
                else:
                    ht = h1
                    y1 = hs + 1
                    y2 = hs + ht
                    hs += ht
                    y3 = y1 + (y2 - y1) * 0.0
                    y4 = y1 + (y2 - y1) * 1.0
            colorDark = COLOR_DARK_LIST[i % len(COLOR_DARK_LIST)]
            color = COLOR_LIST[i % len(COLOR_DARK_LIST)]
            self.canvas.create_rectangle(0, y1, w0, y2, width=0, fill="#333")
            self.lineIndex.create_rectangle(60, y1, 80, y2, width=0, fill=color.toRRGGBB())
            self.lineIndex.create_text(10, y1, anchor=NW, fill="#ddd", text="Line " + str(i))

            start = None
            line = self.chart.lineList[i]
            for t in range(self.t0, self.t0 + dur + div, div):
                alpha = line.alpha.getValue(t + 0.1)
                if start is None and alpha > 0:
                    start = t
                elif start is not None and (alpha <= 0 or t == self.t0 + dur):
                    p1 = (start - self.t0) / dur * w0
                    p2 = (t - self.t0) / dur * w0
                    self.canvas.create_rectangle(p1, y3, p2, y4, width=0, fill=colorDark.toRRGGBB())
                    start = None

            for placing in placingList:
                if placing.index == i:
                    p1 = (placing.time - self.t0) / dur * w0
                    p2 = (placing.time + placing.length - self.t0) / dur * w0

                    self.canvas.create_rectangle(
                        p1, y3, p2, y4, width=0,
                        fill=COLOR_DARK_LIST[placing.period.colorIndex % len(COLOR_LIST)].toRRGGBB()
                    )

                    self.canvas.create_rectangle(
                        p1, y3, p1 + 10, y4, width=0,
                        fill=COLOR_LIST[placing.period.colorIndex % len(COLOR_LIST)].toRRGGBB()
                    )

                    self.canvas.create_text(
                        p1 + 15, y3 + 5, anchor=NW, fill="#ddd",
                        text=placing.period.name,
                    )

                    if placing is self.selectingPlacing:
                        self.canvas.create_rectangle(
                            p1 + 3, y3 + 3, p2 - 3, y4 - 3, width=6,
                            outline="#fff"
                        )

            for note in self.lines[i].noteList:
                if self.t0 <= note.time_ <= self.t0 + dur:
                    if note.type_ == 3:
                        color = HOLD_COLOR
                        p1 = (note.time_ - self.t0) / dur * w0
                        p2 = (note.time_ + note.holdTime - self.t0) / dur * w0
                        self.canvas.create_oval(
                            p1 + 2, y2 - 4, p1 - 2, y2 - 8,
                            fill=color, width=0
                        )
                        self.canvas.create_oval(
                            p2 + 2, y2 - 4, p2 - 2, y2 - 8,
                            fill=color, width=0
                        )
                        self.canvas.create_line(
                            p1, y2 - 6, p2, y2 - 6,
                            fill=color, width=5
                        )
            for note in self.lines[i].noteList:
                if self.t0 <= note.time_ <= self.t0 + dur:
                    p1 = (note.time_ - self.t0) / dur * w0
                    if note.type_ == 1:
                        color = TAP_COLOR
                    elif note.type_ == 2:
                        color = DRAG_COLOR
                    elif note.type_ == 4:
                        color = FLICK_COLOR
                    else:
                        continue
                    self.canvas.create_oval(
                        p1 + 2, y2 - 4, p1 - 2, y2 - 8,
                        fill=color, width=0
                    )


    def motionEvent(self, event):
        self.mousePos = (event.x, event.y)

        dur = 256
        h0 = self.canvas.winfo_height()
        w0 = self.canvas.winfo_width()
        h2 = h0 / len(self.lines)
        if self.selectingPlacing is not None:
            i = round(event.y / h2)
            t9 = self.mousePos[0] / w0 * dur + self.t0
            t9 = t9 // 8 * 8
            self.selectingPlacing.index = i
            self.selectingPlacing.time = t9

        self.update()

    def mouseEvent(self, event):
        if self.selectingPlacing is not None:
            self.placingList.append(self.selectingPlacing)
            self.selectingPlacing = None
        else:
            dur = 256
            h0 = self.canvas.winfo_height()
            w0 = self.canvas.winfo_width()
            h2 = h0 / len(self.lines)
            i = round(event.y / h2)
            for placing in self.placingList:
                p1 = (placing.time - self.t0) / dur * w0
                p2 = (placing.time + placing.length - self.t0) / dur * w0
                if i == placing.index and p1 < self.mousePos[0] < p2:
                    self.selectingPlacing = placing
                    self.placingList.remove(placing)
        self.update()

    def mouseLeave(self, event):
        self.mousePos = None
        self.update()

    def wheelEvent(self, event):
        if event.delta > 0:
            self.t0 -= 16
        else:
            self.t0 += 16
        self.t0 = max(self.t0, 0)
        self.update()

    def cp1WheelEvent(self, event):
        if event.delta > 0:
            self.y0 -= 16
        else:
            self.y0 += 16
        self.y0 = max(self.y0, 0)
        self.updateCp1()

    def selectPeriod(self, event):
        i = (event.y + self.y0) // 40
        if i < len(self.periodList):
            self.selectedIndex = i
            self.selectingPlacing = Mixer.Placing(self.periodList[i])
        else:
            self.selectedIndex = -1
            self.selectingPlacing = None
        self.updateCp1()


class Beater(Toplevel):
    def __init__(self, parent, chart: Chart, audioFile: str, callBackFunction):
        Toplevel.__init__(self, parent)
        self.parent = parent
        self.geometry("800x600")
        self.config(bg="#222")
        self.config(padx=30, pady=50)

        self.canvas1 = Canvas(self, bg='#333', height=80, highlightthickness=0)
        self.canvas1.pack(side=TOP, fill=X)
        self.canvas2 = Canvas(self, bg='#333', height=20, highlightthickness=0)
        self.canvas2.pack(side=TOP, fill=X, pady=10)

        self.fr1 = FrameDark(self)
        self.fr1.pack(side=TOP, fill=X)
        self.bt1 = ButtonDark(self.fr1, text="左移4拍（左箭头）", command=self.leftSwift, height=2)
        self.bt1.pack(side=LEFT, fill=X, expand=1)
        self.bt1 = ButtonDark(self.fr1, text="播放/暂停（Space）", command=self.play, height=2)
        self.bt1.pack(side=LEFT, fill=X, expand=1, padx=10, pady=10)
        self.bt1 = ButtonDark(self.fr1, text="移除所有点", command=self.deleteAll, height=2)
        self.bt1.pack(side=LEFT, fill=X, expand=1)
        self.bt1 = ButtonDark(self.fr1, text="回到开头（上箭头）", command=self.home, height=2)
        self.bt1.pack(side=LEFT, fill=X, expand=1, padx=10, pady=10)
        self.bt1 = ButtonDark(self.fr1, text="右移4拍（右箭头）", command=self.rightSwift, height=2)
        self.bt1.pack(side=LEFT, fill=X, expand=1)
        self.bt1 = ButtonDark(self, text="打点（任意字母键）", command=self.record, height=2)
        self.bt1.pack(side=TOP, fill=X)

        self.fr2 = LabelFrameDark(self, text="延迟补偿", padx=10, pady=10)
        self.fr2.pack(side=TOP, fill=X)
        self.et1 = EntryDark(self.fr2)
        self.et1.pack(side=TOP, fill=X, pady=5)
        self.et1.insert(0, "0")
        str1 = "因软件适配、硬件响应延迟缘故，可能导致音画不同步。若发现打点偏移，应当通过调整延迟补偿来抵消。"
        str2 = "此值为正时，打出的点将向后延迟一定的拍数。此值为负时，打出的点将向移动一定的拍数。输入完成后，请按回车。"
        LabelDark(self.fr2, text=str1, justify=LEFT).pack(side=TOP)
        LabelDark(self.fr2, text=str2, justify=LEFT).pack(side=TOP, pady=5)
        self.bt7 = ButtonDark(self.fr2, text="自动调整延迟", command=self.autoSetDelay, height=2)
        self.bt7.pack(side=TOP, fill=X, pady=5)
        str3 = "按照节拍，每拍敲击一次，然后按上面这个按钮，就会自动调整好延迟。"
        LabelDark(self.fr2, text=str3, justify=LEFT).pack(side=TOP)

        self.bt5 = ButtonDark(self, text="完成", command=self.submit, height=2)
        self.bt5.pack(side=BOTTOM, fill=X, pady=10)

        self.chart = chart
        self.beatList = chart.beats
        self.t0 = 0
        self.audioFile = audioFile
        self.fullLength = 9999
        self.delay = 0
        self.callBackFunction = callBackFunction

        self.playing = False
        self.lastFrameTime = time.time()

        self.after(500, self.update)
        self.et1.bind("<KeyRelease>", self.setDelta)
        self.et1.bind("<Return>", self.setFocus)
        self.bind("<Key>", self.record)
        self.bind("<space>", self.play)
        self.bind("<MouseWheel>", self.wheelEvent)
        self.bind("<Left>", self.leftSwift)
        self.bind("<Right>", self.rightSwift)
        self.bind("<Up>", self.home)

        mixer.init()
        mixer.music.load(self.audioFile)
        mixer.music.play()
        mixer.music.pause()
        self.fullLength = mixer.Sound(self.audioFile).get_length() / 1.875 * self.chart.bpm

    def update(self):
        self.canvas1.delete("all")
        self.canvas2.delete("all")

        w0 = self.canvas1.winfo_width()
        h0 = self.canvas1.winfo_height()

        for t in range(int(self.t0 - 256) // 4 * 4, int(self.t0 + 256) // 4 * 4 + 256, 4):
            pos = w0 * 0.5 + (t - self.t0) / 256 * w0
            if not 0 <= t < self.fullLength:
                continue
            if t % 32 == 0:
                self.canvas1.create_line(
                    pos, 0, pos, h0, width=3, fill="#444",
                )
                self.canvas1.create_text(
                    pos + 5, 0, text=str(int(t // 32)), fill="#ddd",
                    anchor=NW,
                )
            elif t % 32 % 8 == 0:
                self.canvas1.create_line(
                    pos, 0, pos, h0, width=1, fill="#444",
                )
            else:
                self.canvas1.create_line(
                    pos, 0, pos, h0, width=1, fill="#393939",
                )

        pos = self.t0 / self.fullLength * w0
        self.canvas2.create_line(
            pos, 0, pos, 20, width=4, fill="#ddd",
        )
        self.canvas1.create_line(
            w0 * 0.5, 0, w0 * 0.5, h0, width=1, fill="#ddd",
        )

        for beat in self.beatList:
            if self.t0 - 300 <= beat <= self.t0 + 300:
                pos = w0 * 0.5 + (beat - self.t0) / 256 * w0
                self.canvas1.create_oval(
                    pos - 5, h0 / 2 - 5,
                    pos + 5, h0 / 2 + 5,
                    outline="#ddd",
                    fill="",
                    width=2,
                )

    def play(self, *args):
        self.lastFrameTime = time.time()
        self.playing = not self.playing
        self.playLoop()

        if self.playing:
            mixer.music.unpause()
            mixer.music.set_pos(self.t0 * 1.875 / self.chart.bpm)
        else:
            mixer.music.pause()

    def playLoop(self):
        if self.playing:
            self.after(10, self.playLoop)

        current = time.time()
        delta = current - self.lastFrameTime
        self.t0 += delta / 1.875 * self.chart.bpm
        self.lastFrameTime = current
        self.update()

    def record(self, *event):
        if not self.playing:
            self.play()

        self.beatList.append(round((self.t0 + self.delay) / 4) * 4)
        self.update()

    def wheelEvent(self, event):
        if event.delta > 0:
            self.t0 -= 16
        else:
            self.t0 += 16
        self.update()

    def submit(self):
        self.chart.beats = self.beatList
        self.destroy()
        self.callBackFunction()
        mixer.quit()

    def leftSwift(self, *args):
        self.t0 -= 128
        self.update()

    def rightSwift(self, *args):
        self.t0 += 128
        self.update()

    def deleteAll(self, *args):
        self.beatList = []
        self.update()

    def setDelta(self, event):
        # if not self.et1.get().isdigit():
        #     self.fr1.focus_set()
        #     string = self.et1.get()
        #     self.et1.delete(0, END)
        #     self.et1.insert(0, string[:-1])
        try:
            self.delay = eval(self.et1.get()) * 32
        except ValueError:
            pass

    def setFocus(self, *args):
        self.fr1.focus_set()

    def home(self, *args):
        self.t0 = 0
        self.update()

    def autoSetDelay(self, *args):
        sum = 0
        for i in self.beatList:
            delta = (i / 32) - round(i / 32)
            sum += delta
        average = sum / len(self.beatList)
        for i in range(len(self.beatList)):
            self.beatList[i] -= average * 32
        self.delay = - average * 32
        self.et1.delete(0, END)
        self.et1.insert(0, str(average))
        self.update()


if __name__ == "__main__":
    lines = []

    top = Tk()
    top.geometry("10x10+10+10")

    # a = Beater(top, lines, newDefaultChart(174), r"D:\Projects\PygamePhiChart\charts\白复生 IN\music #1988.wav")
    # top.mainloop()
    # mixer.quit()

    chart: Chart = analyzer.analyzeJson(r"D:\Projects\PygamePhiChart\charts\ATRR IN\ATRR IN.json")
    # chart: Chart = newDefaultChart(174, 24)
    prList = []

    a = Mixer(top, chart, prList, print)
    top.mainloop()
