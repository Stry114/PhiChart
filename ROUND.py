import math
import random

from chart import *
from player import *
from autoMatch import Matcher


player: Player = Player(Matcher(r"charts/Trojan"), 1440, 1080, fps=120)
player.name = "Trojan"
player.level = "SP Lv.?"
player.lineLength = 10000

player.noteSize = player.width / 10
player.enable3D = False
player.initPlayer()


chart: Chart = player.chart
roundLineList: list[Line] = []
# 结束时间
END_TIME: float = 9999999
# 键速度
SPEED = 1.6
# 尺寸分母
sizeIndex = 3
# 分键数量
LINE_NUMBER = 8
LINE_NUM_HALF = 4
DELTA_ANGLE = 22.5
# 拉伸映射
X_SCALE = 2.0
Y_SCALE = 1.0
# 事件事件单位
EVENT_TIME_UNIT = 16
EVENT_TIME_UNIT_HALF = 8
# 位移系数
X_MOVE_SCALE = 0
Y_MOVE_SCALE = 0


for i in range(LINE_NUMBER):
    theta = math.pi / LINE_NUM_HALF * i + (DELTA_ANGLE/180*math.pi)
    rotate = 360 / LINE_NUMBER * i + 90 + (DELTA_ANGLE)
    move1 = 0.5 + math.cos(theta) / sizeIndex
    move2 = 0.5 + math.sin(theta) / sizeIndex * (player.width / player.height)

    line: Line = Line(chart.bpm)
    line.rotate.addPeriod(-1000, -128, rotate, rotate)
    line.move1.addPeriod(-1000, -128, move1, move1)
    line.move2.addPeriod(-1000, -128, move2, move2)
    line.alpha.addPeriod(0, END_TIME, 0, 0)
    line.speed.addPeriod(0, END_TIME, SPEED, SPEED)

    noteTag0 = Note(4, END_TIME, 0, 0, 0)
    noteTag0.doubleHit = True
    noteTag1 = Note(2, END_TIME, 1.7, 0, 0)
    noteTag1.doubleHit = True
    noteTag2 = Note(2, END_TIME, -1.7, 0, 0)
    noteTag2.doubleHit = True
    line.noteList.append(noteTag1)
    line.noteList.append(noteTag2)
    line.noteList.append(noteTag0)
    roundLineList.append(line)


noteCount = 0
for i in range(len(chart.lineList)):
    line = chart.lineList[i]
    for note in line.noteList:
        noteCount += 1
        x, y = player.getNoteHitPos(line, note)
        hx = (x / player.width - 0.5) * X_SCALE
        hy = (y / player.height - 0.5) * Y_SCALE

        theta = math.atan2(hy, hx) - (DELTA_ANGLE/180*math.pi)
        if hx == 0 and hy == 0:
            theta = line.rotate(note.time_ - 64) / 180 * math.pi - (DELTA_ANGLE/180*math.pi)
        index = round(theta / math.pi * LINE_NUM_HALF) % LINE_NUMBER
        lineToAdd = roundLineList[index]

        newNote: Note = Note(
            type_=note.type_,
            time_=note.time_,
            posX=0,
            holdTime=note.holdTime,
            floorPos=lineToAdd.pos(note.time_)
        )

        newNote.hx = hx
        newNote.hy = hy
        if newNote.type_ == 3:
            newNote.speed = SPEED
            newNote.floorPosT = lineToAdd.pos(note.time_ + note.holdTime)
            newNote.visibleTime = max(0.5 - newNote.holdTime / 0.5, 0.28)
        else:
            newNote.visibleTime = 0.5
            pass

        lineToAdd.addNote(newNote)


# 合并曲谱
for line in chart.lineList[4:]:
    line.noteList = []
    roundLineList.append(line)
    for i in range(len(line.alpha.startValueList)):
        line.alpha.startValueList[i] *= 0.6
        line.alpha.endValueList[i] *= 0.6
chart.lineList = roundLineList
chart.noteList = []
for line in chart.lineList:
    chart.noteList += line.noteList

for t in range(1):
    dx = random.uniform(-0.1, 0.1)
    dy = random.uniform(-0.1, 0.1)
    st = t*EVENT_TIME_UNIT
    et = (t+1)*EVENT_TIME_UNIT

    # 计算区段内键平均位置
    count = 0
    sum_x = 0
    sum_y = 0
    notesInPeriod: list[Note] = []

    for line in chart.lineList:
        for note in chart.noteList:
            if not st < note.time_ < et:
                continue
            sum_x += note.hx
            sum_y += note.hy
            count += 1
    if count == 0:
        ave_x = 0
        ave_y = 0
    else:
        ave_x = -sum_x / count * X_MOVE_SCALE
        ave_y = -sum_y / count * Y_MOVE_SCALE
        print(ave_x, ave_y)

    if t % 2 == 0:
        ave_x = 0
    elif t % 4 == 1:
        ave_x = -0.2
    elif t % 4 == 3:
        ave_x = 0.2
    # 添加随机位移
    for i in range(LINE_NUMBER):
        theta = math.pi / LINE_NUM_HALF * i + (DELTA_ANGLE / 180 * math.pi)
        rotate = 360 / LINE_NUMBER * i + 90 + (DELTA_ANGLE)
        move1 = 0.5 + ave_x + math.cos(theta) / sizeIndex
        move2 = 0.5 + ave_y + math.sin(theta) / sizeIndex * (player.width / player.height)

        line = roundLineList[i]
        line.move1.addPeriod(st-EVENT_TIME_UNIT_HALF, et-EVENT_TIME_UNIT_HALF, line.move1.latestValue(), move1)
        line.move2.addPeriod(st-EVENT_TIME_UNIT_HALF, et-EVENT_TIME_UNIT_HALF, line.move2.latestValue(), move2)
        line.rotate.addPeriod(st-EVENT_TIME_UNIT_HALF, et-EVENT_TIME_UNIT_HALF, line.rotate.latestValue(), rotate)



# 计算双押
key = lambda note: note.time_
chart.noteList.sort(key=key)
for i in range(len(chart.noteList)-1):
    if chart.noteList[i].time_ == chart.noteList[i+1].time_:
        chart.noteList[i].doubleHit = True
        chart.noteList[i+1].doubleHit = True


import toml

f = open("output.toml", "w", encoding="utf-8")
toml.dump(chart.toRPEJson(), f)
f.close()

player.mainloop()