class LineTimer:
    def __init__(self, bpm, defaultValue: float = 0):
        self.bpm = bpm
        self.peroidCount = 0
        self.endTimeList = []
        self.endValueList = []
        self.startTimeList = []
        self.startValueList = []
        self.defaultValue = defaultValue

    def second(self, time_, baseBPM=None):
        if baseBPM is None:
            return time_ / self.bpm * 1.875
        else:
            return time_ / baseBPM * 1.875

    def latestTimeT(self):
        return self.endTimeList[-1]

    def latestValue(self):
        return self.endValueList[-1]

    def addPeriod(self, startTime, endTime, startValue, endValue):
        if startTime > endTime:
            raise ValueError(f"EndTime must be later than startTime. {startTime} vs {endTime}")
        self.endTimeList.append(endTime)
        self.endValueList.append(endValue)
        self.startTimeList.append(startTime)
        self.startValueList.append(startValue)
        self.peroidCount += 1
        return self

    def popPeriod(self, index: int):
        self.endTimeList.pop(index)
        self.endValueList.pop(index)
        self.startTimeList.pop(index)
        self.startValueList.pop(index)
        self.peroidCount -= 1

    def max(self):
        m1 = max(self.startValueList)
        m2 = max(self.endValueList)
        return max(m1, m2)

    def min(self):
        m1 = min(self.startValueList)
        m2 = min(self.endValueList)
        return min(m1, m2)

    def value_0(self, time_):
        for i in range(self.peroidCount):
            s = self.startTimeList[i]
            e = self.endTimeList[i]
            if not s <= time_ < e:
                continue
            d = (time_ - s) / (e - s)
            a = self.startValueList[i]
            b = self.endValueList[i]
            return (b - a) * d + a
        raise IndexError("Time index out of defineded range of timer.")

    def __call__(self, time_):

        if len(self.endTimeList) == 0:
            return self.defaultValue

        if time_ > self.endTimeList[-1]:
            return self.endValueList[-1]

        left = 0
        right = self.peroidCount
        while left <= right:
            mid = (left + right) // 2
            start, end = self.startTimeList[mid], self.endTimeList[mid]
            if start <= time_ <= end:  # 检查 target 是否在当前中间区间内
                d = (time_ - start) / (end - start)
                a = self.startValueList[mid]
                b = self.endValueList[mid]
                return (b - a) * d + a
            elif time_ < start:  # target 小于当前区间起始，更新右边界
                right = mid - 1
            else:  # target 大于当前区间结束，更新左边界
                left = mid + 1
        return self.defaultValue


class ColorLineTimer(LineTimer):
    def __init__(self, bpm, defaultValue: list[int] = None):
        defaultValue = defaultValue if defaultValue is not None else [254, 255, 169]
        self.bpm = bpm
        self.peroidCount = 0
        self.endTimeList = []
        self.endValueList = []
        self.startTimeList = []
        self.startValueList = []
        self.defaultValue: list[int] = defaultValue

    def addPeriod(self, startTime, endTime, startValue, endValue):
        print("add new period", startValue, endValue)
        if startTime > endTime:
            raise ValueError(f"EndTime must be later than startTime. {startTime} vs {endTime}")
        self.endTimeList.append(endTime)
        self.endValueList.append(endValue)
        self.startTimeList.append(startTime)
        self.startValueList.append(startValue)
        self.peroidCount += 1
        return self

    def __call__(self, time_):

        if len(self.endTimeList) == 0:
            return self.defaultValue

        if time_ > self.endTimeList[-1]:
            return self.endValueList[-1]

        left = 0
        right = self.peroidCount
        while left <= right:
            mid = (left + right) // 2
            start, end = self.startTimeList[mid], self.endTimeList[mid]
            if start <= time_ <= end:  # 检查 target 是否在当前中间区间内
                d = (time_ - start) / (end - start)
                v1 = self.startValueList[mid]
                v2 = self.endValueList[mid]
                r = (v2[0] - v1[0]) * d + v1[0]
                g = (v2[1] - v1[1]) * d + v1[1]
                b = (v2[2] - v1[2]) * d + v1[2]
                return [r, g, b]
            elif time_ < start:  # target 小于当前区间起始，更新右边界
                right = mid - 1
            else:  # target 大于当前区间结束，更新左边界
                left = mid + 1
        raise IndexError("Time index out of defineded range of timer.")


class SpeedEvent:
    def __init__(self, bpm):
        self.bpm = bpm
        self.peroidCount = 0

        self.ValueList = []
        self.endTimeList = []
        self.startTimeList = []


class Note:
    def __init__(self, type_, time_, posX, floorPos, speed=1, holdTime=0, above=True):
        self.posX = posX
        self.time_ = time_
        self.type_ = type_
        self.speed = speed
        self.above = above
        self.holdTime = holdTime
        self.floorPos = floorPos
        self.floorPosT: float | None = None

        # 键透明度
        self.alpha = 255

        self.hit = False
        self.begin = False
        self.doubleHit = False

        # 转谱时的临时线
        self.tempLine: Line|None = None

    def toJson(self):
        return (
            "{"
            f'"type":{self.type_},'
            f'"time":{self.time_},'
            f'"positionX":{self.posX},'
            f'"holdTime":{self.holdTime},'
            f'"speed":{self.speed},'
            f'"floorPosition":{self.floorPos}'
            "}"
        )


class Line:
    def __init__(self, bpm):
        self.bpm = bpm
        self.move1 = LineTimer(bpm)
        self.move2 = LineTimer(bpm)
        self.speed = LineTimer(bpm, 1.0)
        self.alpha = LineTimer(bpm, 1.0)
        self.rotate = LineTimer(bpm, 0.0)

        self.noteList: list[Note] = []

        # RPE 扩展线条属性
        self.scaleX = LineTimer(bpm, 1.0)
        self.scaleY = LineTimer(bpm, 1.0)
        self.color = ColorLineTimer(bpm)
        self.texture = "line.png"


        # 运行时变量
        self.cmrH: float = 1.0

    def addNote(self, note: Note):
        self.noteList.append(note)

    def report(self, level=0, index=0):
        print(" " * 4 * level + "<line>", index)
        level += 1
        print(" " * 4 * level + f"bpm\t{self.bpm}")
        print(" " * 4 * level + f"move1\t{self.move1.peroidCount}\t[{self.move1.min()}, {self.move1.max()}]")
        print(" " * 4 * level + f"move2\t{self.move2.peroidCount}\t[{self.move2.min()}, {self.move2.max()}]")
        print(" " * 4 * level + f"alpha\t{self.alpha.peroidCount}\t[{self.alpha.min()}, {self.alpha.max()}]")
        print(" " * 4 * level + f"speed\t{self.speed.peroidCount}\t[{self.speed.min()}, {self.speed.max()}]")
        print(" " * 4 * level + f"rotate\t{self.rotate.peroidCount}\t[{self.rotate.min()}, {self.rotate.max()}]")

    def pos(self, time_):
        pos = 0
        for i in range(self.speed.peroidCount):
            s = self.speed.startTimeList[i]
            e = self.speed.endTimeList[i]
            if not s <= time_ < e and i != len(self.speed.startTimeList) - 1:
                pos += (e - s) * self.speed.startValueList[i] * 1.875 / self.bpm
            else:
                return (time_ - s) * self.speed.startValueList[i] * 1.875 / self.bpm + pos

    def toJson(self):
        noteBelow = []
        noteAbove = []
        for note in self.noteList:
            if note.above:
                noteAbove.append(note.toJson())
            else:
                noteBelow.append(note.toJson())

        speedEvents = []
        for i in range(self.speed.peroidCount):
            this = (
                "{"
                f'"startTime":{self.speed.startTimeList[i]},'
                f'"endTime":{self.speed.endTimeList[i]},'
                f'"value":{self.speed.startValueList[i]}'
                "}"
            )
            speedEvents.append(this)

        moveEvents = []
        for i in range(self.move1.peroidCount):
            this = (
                "{"
                f'"startTime":{self.move1.startTimeList[i]},'
                f'"endTime":{self.move1.endTimeList[i]},'
                f'"start":{self.move1.startValueList[i]},'
                f'"end":{self.move1.endValueList[i]},'
                f'"start2":{self.move2.startValueList[i]},'
                f'"end2":{self.move2.endValueList[i]}'
                "}"
            )
            moveEvents.append(this)

        rotateEvents = []
        for i in range(self.rotate.peroidCount):
            this = (
                "{"
                f'"startTime":{self.rotate.startTimeList[i]},'
                f'"endTime":{self.rotate.endTimeList[i]},'
                f'"start":{self.rotate.startValueList[i]},'
                f'"end":{self.rotate.endValueList[i]}'
                "}"
            )
            rotateEvents.append(this)

        alphaEvents = []
        for i in range(self.alpha.peroidCount):
            this = (
                "{"
                f'"startTime":{self.alpha.startTimeList[i]},'
                f'"endTime":{self.alpha.endTimeList[i]},'
                f'"start":{self.alpha.startValueList[i]},'
                f'"end":{self.alpha.endValueList[i]}'
                "}"
            )
            alphaEvents.append(this)

        return (
            "{"
            f'"bpm":{self.bpm},'
            f'"notesAbove":[{",".join(noteAbove)}],'
            f'"notesBelow":[{",".join(noteBelow)}],'
            f'"speedEvents":[{",".join(speedEvents)}],'
            f'"judgeLineMoveEvents":[{",".join(moveEvents)}],'
            f'"judgeLineRotateEvents":[{",".join(rotateEvents)}],'
            f'"judgeLineDisappearEvents":[{",".join(alphaEvents)}]'
            "}"
        )


    def timeTtoBeat(self, timeT) -> list[int]:
        if timeT % 32 == 0:
            return [int(timeT//32), 0, 1]
        if timeT % 16 == 0:
            return [int(timeT//32), 1, 2]
        if timeT % 8 == 0:
            return [int(timeT//32), int(timeT%32//8), 4]
        if timeT % 4 == 0:
            return [int(timeT//32), int(timeT%32//4), 8]
        if timeT % 2 == 0:
            return [int(timeT//32), int(timeT%32//2), 16]
        if timeT % 1 == 0:
            return [int(timeT//32), int(timeT%32//1), 32]
        else:
            return [int(timeT//32), int(timeT%32//(32/1024)), 1024]

    def de_convertType(self, Type: int) -> int:
        if Type == 3:
            return 2
        elif Type == 4:
            return 3
        elif Type == 2:
            return 4
        return 1

    def toRPEJson(self):
        lineDict = {
            "Group": 0,
            "Name": "Untitled",
            "Texture": self.texture,
            "alphaControl": [
                {
                    "alpha": 1.0,
                    "easing": 1,
                    "x": 0.0
                },
                {
                    "alpha": 1.0,
                    "easing": 1,
                    "x": 9999999.0
                }
            ],
            "anchor": [
                0.5,
                0.5
            ],
            "bpmfactor": 1.0,
            "eventLayers": [
                {
                    "alphaEvents": [],
                    "moveXEvents": [],
                    "moveYEvents": [],
                    "rotateEvents": [],
                    "speedEvents": []
                }
            ],
            "extended": {
                "scaleYEvents": [],
                "scaleXEvents": [],
                "colorEvents": []
            },
            "father": -1,
            "isCover": 1,
            "isGif": False,
            "notes": [],
            "numOfNotes": len(self.noteList),
            "posControl": [
                {
                    "easing": 1,
                    "pos": 1.0,
                    "x": 0.0
                },
                {
                    "easing": 1,
                    "pos": 1.0,
                    "x": 9999999.0
                }
            ],
            "sizeControl": [
                {
                    "easing": 1,
                    "size": 1.0,
                    "x": 0.0
                },
                {
                    "easing": 1,
                    "size": 1.0,
                    "x": 9999999.0
                }
            ],
            "skewControl": [
                {
                    "easing": 1,
                    "skew": 0.0,
                    "x": 0.0
                },
                {
                    "easing": 1,
                    "skew": 0.0,
                    "x": 9999999.0
                }
            ],
            "yControl": [
                {
                    "easing": 1,
                    "x": 0.0,
                    "y": 1.0
                },
                {
                    "easing": 1,
                    "x": 9999999.0,
                    "y": 1.0
                }
            ],
            "zOrder": 0
        }

        for note in self.noteList:
            noteDict = {
                "above": 1 if note.above else 2,
                "alpha": note.alpha,
                "endTime": self.timeTtoBeat(note.time_+note.holdTime),
                "isFake": 0,
                "positionX": note.posX * 75.951,
                "size": 1.0,
                "speed": note.speed,
                "startTime": self.timeTtoBeat(note.time_),
                "type": self.de_convertType(note.type_),
                "visibleTime": 999999.0,
                "yOffset": 0.0
            }
            lineDict["notes"].append(noteDict)

        lineTimer: LineTimer = self.speed
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": lineTimer.endValueList[i] * 9/2,
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": lineTimer.startValueList[i] * 9/2,
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            lineDict["eventLayers"][0]["speedEvents"].append(eventDict)

        lineTimer: LineTimer = self.move1
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": (lineTimer.endValueList[i]-0.5)*1350,
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": (lineTimer.startValueList[i]-0.5)*1350,
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            lineDict["eventLayers"][0]["moveXEvents"].append(eventDict)

        lineTimer: LineTimer = self.move2
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": (lineTimer.endValueList[i]-0.5)*900,
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": (lineTimer.startValueList[i]-0.5)*900,
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            lineDict["eventLayers"][0]["moveYEvents"].append(eventDict)

        lineTimer: LineTimer = self.alpha
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": lineTimer.endValueList[i]*255,
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": lineTimer.startValueList[i]*255,
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            lineDict["eventLayers"][0]["alphaEvents"].append(eventDict)

        lineTimer: LineTimer = self.scaleX
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": lineTimer.endValueList[i],
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": lineTimer.startValueList[i],
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            lineDict["extended"]["scaleXEvents"].append(eventDict)
        if len(lineTimer.endTimeList) == 0:
            lineDict["extended"].pop("scaleXEvents")

        lineTimer: LineTimer = self.scaleY
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": lineTimer.endValueList[i],
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": lineTimer.startValueList[i],
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            lineDict["extended"]["scaleYEvents"].append(eventDict)
        if len(lineTimer.endTimeList) == 0:
            lineDict["extended"].pop("scaleYEvents")

        lineTimer: LineTimer = self.color
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": lineTimer.endValueList[i],
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": lineTimer.startValueList[i],
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            print(lineTimer.endValueList[i])
            lineDict["extended"]["colorEvents"].append(eventDict)
        if len(lineTimer.endTimeList) == 0:
            lineDict["extended"].pop("colorEvents")

        lineTimer: LineTimer = self.rotate
        for i in range(len(lineTimer.endTimeList)):
            eventDict = {
                "bezier": 0,
                "bezierPoints": [0.0, 0.0, 0.0, 0.0],
                "easingLeft": 0.0,
                "easingRight": 1.0,
                "easingType": 1,
                "end": 360-lineTimer.endValueList[i],
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": 360-lineTimer.startValueList[i],
                "startTime": self.timeTtoBeat(lineTimer.startTimeList[i]),
            }
            lineDict["eventLayers"][0]["rotateEvents"].append(eventDict)

        return lineDict


class RPELine(Line):
    pass

class Chart:
    def __init__(self, RPE_Chart=False):
        self.bpm = None
        self.RPE_Chart = RPE_Chart
        self.noteCount = 0
        self.lineList: list[Line] = []
        self.noteList: list[Note] = []

        # RPE META 数据
        self.RPE_level = 160
        self.charter = ""
        self.composer = ""
        self.illustration = ""
        self.name = "Unknown"
        self.level = "Un Lv.?"
        self.id = "114514"
        self.song = "music.wav"
        self.bg = "illu.png"
        self.duration = 0
        self.chartTime = 0

    def addLine(self, line: Line):
        self.bpm = line.bpm
        self.lineList.append(line)
        self.noteCount += len(line.noteList)
        self.noteList.extend(line.noteList)

    def report(self, level=0):
        print(" " * 4 * level + "<chart>")
        print(" " * 4 * (level + 1) + f"line\t{len(self.lineList)}")
        for i in range(len(self.lineList)):
            self.lineList[i].report(level + 1, i)

    @property
    def fullCombo(self):
        count = 0
        for line in self.lineList:
            count += len(line.noteList)
        return count

    def toJson(self):
        lineList = []
        for line in self.lineList:
            lineList.append(line.toJson())

        return (
            "{"
            f'"formatVersion": 3,'
            f'"offset": 0.0,'
            f'"judgeLineList": [{",".join(lineList)}]'
            "}"
        )

    def toRPEJson(self):

        chartDict: dict = {
            "annotation": "This chart was created using PhiChart. For more information, please visit the Github repository.",
            "BPMList": [
                {
                    "bpm": self.bpm,
                    "startTime": [0,0,1]
                }
            ],
            "META": {
                "RPEVersion": self.RPE_level,
                "background": self.bg,
                "charter": self.charter,
                "composer": self.composer,
                "duration": self.duration,
                "id": self.id,
                "illustration": self.illustration,
                "level": self.level,
                "name": self.name,
                "offset": 0,
                "song": self.song
            },
            "chartTime": self.chartTime,
            "judgeLineGroup": ["Default"],
            "judgeLineList": [line.toRPEJson() for line in self.lineList],
            "multiLineString": "0:10",
            "multiScale": 1.0
        }

        return chartDict
