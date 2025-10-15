import copy


class LineTimer:
    def __init__(self, bpm, defaultValue: float = 0):
        self.bpm = bpm
        self.peroidCount = 0
        self.endTimeList: list[float] = []
        self.endValueList: list[float] = []
        self.startTimeList: list[float] = []
        self.startValueList: list[float] = []
        self.defaultValue = defaultValue

    def __call__(self, time_: float):
        return self.value_2(time_)

    @property
    def periodCount(self):
        return len(self.endTimeList)

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls(self.bpm, self.defaultValue)
        memo[id(self)] = result
        result.endTimeList = copy.deepcopy(self.endTimeList, memo)
        result.endValueList = copy.deepcopy(self.endValueList, memo)
        result.startTimeList = copy.deepcopy(self.startTimeList, memo)
        result.startValueList = copy.deepcopy(self.startValueList, memo)
        return result

    def second(self, time_, baseBPM=None):
        if baseBPM is None:
            return time_ / self.bpm * 1.875
        else:
            return time_ / baseBPM * 1.875

    def latestTimeT(self):
        if len(self.endTimeList) > 0:
            return self.endTimeList[-1]
        else:
            return 0

    def latestValue(self):
        if len(self.endValueList) > 0:
            return self.endValueList[-1]
        else:
            return self.defaultValue

    def addPeriod(self, startTime, endTime, startValue, endValue):
        if startTime > endTime:
            raise ValueError(f"EndTime must be later than startTime. {startTime} vs {endTime}")
        self.endTimeList.append(endTime)
        self.endValueList.append(endValue)
        self.startTimeList.append(startTime)
        self.startValueList.append(startValue)
        return self

    def addEvent(self, endTime, endValue):
        self.endTimeList.append(endTime)
        self.endValueList.append(endValue)
        self.startTimeList.append(self.latestTimeT())
        self.startValueList.append(self.latestValue())

    def popPeriod(self, index: int):
        self.endTimeList.pop(index)
        self.endValueList.pop(index)
        self.startTimeList.pop(index)
        self.startValueList.pop(index)

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

    def value_2(self, time: float) -> float:
        """根据时间获取值：区间内线性插值，区间外按规则返回"""
        if not self.startTimeList:
            return self.defaultValue  # 无区间时返回默认值

        # 二分查找时间所在区间
        left, right = 0, len(self.startTimeList) - 1
        found_index = -1

        while left <= right:
            mid = (left + right) // 2
            # 检查是否在当前区间内
            if self.startTimeList[mid] <= time <= self.endTimeList[mid]:
                found_index = mid
                break
            # 时间在当前区间之前，搜索左半部分
            elif time < self.startTimeList[mid]:
                right = mid - 1
            # 时间在当前区间之后，搜索右半部分
            else:
                left = mid + 1

        if found_index != -1:
            # 区间内线性插值
            start_t = self.startTimeList[found_index]
            end_t = self.endTimeList[found_index]
            start_v = self.startValueList[found_index]
            end_v = self.endValueList[found_index]

            if start_t == end_t:
                return start_v  # 处理零长度区间
            ratio = (time - start_t) / (end_t - start_t)
            return start_v + ratio * (end_v - start_v)
        else:
            # 区间外处理：第一个区间前返回默认值，其他返回上一个区间的末值
            if left == 0:
                return self.defaultValue  # 在第一个区间之前
            else:
                return self.endValueList[left - 1]  # 在区间之间或最后一个区间之后

    def value_1(self, time_):

        if len(self.endTimeList) == 0:
            return self.defaultValue

        if time_ > self.endTimeList[-1]:
            return self.endValueList[-1]

        left = 0
        right = len(self.startValueList)
        while left <= right:
            mid = (left + right) // 2
            start, end = self.startTimeList[mid], self.endTimeList[mid]
            if start <= time_ < end:  # 检查 target 是否在当前中间区间内
                d = (time_ - start) / (end - start)
                a = self.startValueList[mid]
                b = self.endValueList[mid]
                return (b - a) * d + a
            elif time_ == end:
                return self.endValueList[mid]
            elif time_ < start:  # target 小于当前区间起始，更新右边界
                right = mid - 1
            else:  # target 大于当前区间结束，更新左边界
                left = mid + 1
        return self.defaultValue

    def getValue(self, time_):
        if time_ > self.endTimeList[-1]:
            return self.defaultValue
        else:
            return self.__call__(time_)

class ColorLineTimer(LineTimer):
    def __init__(self, bpm, defaultValue: list[int] = None):
        defaultValue = defaultValue if defaultValue is not None else [254, 255, 169]
        self.bpm = bpm
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
        return self

    @property
    def peroidCount(self):
        return len(self.endTimeList)

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
            if start <= time_ < end:  # 检查 target 是否在当前中间区间内
                d = (time_ - start) / (end - start)
                v1 = self.startValueList[mid]
                v2 = self.endValueList[mid]
                r = (v2[0] - v1[0]) * d + v1[0]
                g = (v2[1] - v1[1]) * d + v1[1]
                b = (v2[2] - v1[2]) * d + v1[2]
                return [r, g, b]
            elif time_ == end:
                return self.endValueList[mid]
            elif time_ < start:  # target 小于当前区间起始，更新右边界
                right = mid - 1
            else:  # target 大于当前区间结束，更新左边界
                left = mid + 1
        return self.defaultValue

# class SpeedEvent:
#     def __init__(self, bpm):
#         self.bpm = bpm
#         self.peroidCount = 0
#
#         self.ValueList = []
#         self.endTimeList = []
#         self.startTimeList = []


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

        # 键尺寸
        self.size = 1.0
        # 键透明度
        self.alpha = 255
        # 可视时间
        self.visibleTime = 999999.0
        # 是否假键
        self.isFake = False
        # 是否启用3D
        # 0 跟随播放器 1 强制禁用
        self.ban3D = 0

        self.hit = False
        self.begin = False
        self.doubleHit = False

        # 转谱时的临时线
        self.tempLine: Line|None = None

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls(
            copy.deepcopy(self.type_, memo),
            copy.deepcopy(self.time_, memo),
            copy.deepcopy(self.posX, memo),
            copy.deepcopy(self.floorPos, memo),
            copy.deepcopy(self.speed, memo),
            copy.deepcopy(self.holdTime, memo),
            copy.deepcopy(self.above, memo)
        )
        memo[id(self)] = result
        result.size = copy.deepcopy(self.size, memo)
        result.alpha = copy.deepcopy(self.alpha, memo)
        result.visibleTime = copy.deepcopy(self.visibleTime, memo)
        result.isFake = copy.deepcopy(self.isFake, memo)
        result.hit = copy.deepcopy(self.hit, memo)
        result.begin = copy.deepcopy(self.begin, memo)
        result.doubleHit = copy.deepcopy(self.doubleHit, memo)
        result.floorPosT = copy.deepcopy(self.floorPosT, memo)
        result.tempLine = copy.deepcopy(self.tempLine, memo)
        return result

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

class Period:
    def __init__(self, length: int, name="Period"):
        self.name = name
        self.length = length
        self.colorIndex = 3
        self.notes: list[Note] = []

        self.move1 = LineTimer(0)
        self.move2 = LineTimer(0)
        self.theta = LineTimer(0)
        self.speed = LineTimer(0, 1.0)
        self.alpha = LineTimer(0, 1.0)
        self.rotate = LineTimer(0, 0.0)

    def toJsonDic(self):
        dic = {
            "name": self.name,
            "length": self.length,
            "colorIndex": self.colorIndex,
            "move1": [
                self.move1.startTimeList, self.move1.endTimeList,
                self.move1.startValueList, self.move1.endValueList
            ],
            "move2": [
                self.move2.startTimeList, self.move2.endTimeList,
                self.move2.startValueList, self.move2.endValueList
            ],
            "alpha": [
                self.alpha.startTimeList, self.alpha.endTimeList,
                self.alpha.startValueList, self.alpha.endValueList
            ],
            "rotate": [
                self.rotate.startTimeList, self.rotate.endTimeList,
                self.rotate.startValueList, self.rotate.endValueList
            ]
        }
        return dic

class Line:
    def __init__(self, bpm):
        self.bpm = bpm
        self.move1 = LineTimer(bpm)
        self.move2 = LineTimer(bpm)
        self.speed = LineTimer(bpm, 1.0)
        self.alpha = LineTimer(bpm, 0.0)
        self.rotate = LineTimer(bpm, 0.0)

        # 3D事件
        # 下落面仰角
        self.theta = LineTimer(bpm, 0.0)
        # z轴事件
        self.move3 = LineTimer(bpm, 0.0)
        # 线高度角
        self.noteList: list[Note] = []

        # RPE 扩展线条属性
        self.scaleX = LineTimer(bpm, 1.0)
        self.scaleY = LineTimer(bpm, 1.0)
        self.color = ColorLineTimer(bpm)
        self.texture = "line.png"
        self.attachUI = None

        # 运行时变量
        self.cmrH: float = 1.0

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls(self.bpm)
        memo[id(self)] = result
        result.move1 = copy.deepcopy(self.move1, memo)
        result.move2 = copy.deepcopy(self.move2, memo)
        result.speed = copy.deepcopy(self.speed, memo)
        result.alpha = copy.deepcopy(self.alpha, memo)
        result.rotate = copy.deepcopy(self.rotate, memo)
        result.theta = copy.deepcopy(self.theta, memo)
        result.noteList = copy.deepcopy(self.noteList, memo)
        result.scaleX = copy.deepcopy(self.scaleX, memo)
        result.scaleY = copy.deepcopy(self.scaleY, memo)
        result.color = copy.deepcopy(self.color, memo)
        result.texture = copy.deepcopy(self.texture, memo)
        result.cmrH = copy.deepcopy(self.cmrH, memo)
        return result

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
        for i in range(len(self.speed.startTimeList)):
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

    def fastCalcFloorPos(self):
        j = 0
        floorBase = 0
        for i in range(len(self.speed.startTimeList)):
            st = self.speed.startTimeList[i]
            et = self.speed.startTimeList[i+1] if i < len(self.speed.startTimeList)-1 else 9999999
            s = self.speed.startValueList[i]
            e = self.speed.endValueList[i]
            for k in range(j, len(self.noteList)):
                note = self.noteList[k]
                if note.time_ >= et:
                    floorBase += (et - st) * s * 1.875 / self.bpm
                    break
                else:
                    note.floorPos = floorBase + (note.time_ - st) * s * 1.875 / self.bpm
                    if note.type_ == 3:
                        note.floorPosT = note.floorPos + note.holdTime * s * 1.875 / self.bpm
                    j += 1

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
                "alpha": int(note.alpha),
                "endTime": self.timeTtoBeat(note.time_+note.holdTime),
                "isFake": 1 if note.isFake else 0,
                "positionX": note.posX * 75.951,
                "size": 1.0,
                "speed": note.speed,
                "startTime": self.timeTtoBeat(note.time_),
                "type": self.de_convertType(note.type_),
                "visibleTime": note.visibleTime,
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
                "end": int(lineTimer.endValueList[i]*255),
                "endTime": self.timeTtoBeat(lineTimer.endTimeList[i]),
                "linkgroup": 0,
                "start": int(lineTimer.startValueList[i]*255),
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
    def __init__(self, bpm):
        self.bpm = bpm
        # 线高度角
        self.noteList: list[Note] = []
        # RPE 扩展线条属性
        self.texture = "line.png"
        # 运行时变量
        self.cmrH: float = 1.0
        # 事件层
        self.eventLayers: list[EventLayer] = []
        # 非事件层的事件
        self.color = ColorLineTimer(bpm)
        self.move3 = LineTimer(bpm, 0.0)
        self.theta = LineTimer(bpm, 0.0)
        self.scaleX = LineTimer(bpm, 1.0)
        self.scaleY = LineTimer(bpm, 1.0)
        # 附着到UI上
        self.attachUI = None

        # pos函数优化缓存
        self.lastTime: float = 0.0
        self.lastPos: float = 0.0

    def move1(self, timeT: float) -> float:
        return sum([layer.move1(timeT) - 0.5 for layer in self.eventLayers]) + 0.5

    def move2(self, timeT: float) -> float:
        return sum([layer.move2(timeT) - 0.5 for layer in self.eventLayers]) + 0.5

    def speed(self, timeT: float) -> float:
        return sum([layer.speed(timeT) for layer in self.eventLayers])

    def alpha(self, timeT: float) -> float:
        return sum([layer.alpha(timeT) for layer in self.eventLayers])

    def rotate(self, timeT: float) -> float:
        return sum([layer.rotate(timeT) for layer in self.eventLayers])

    def pos(self, timeT: float) -> float:
        if timeT > self.lastTime:
            pos = self.lastPos
            t = self.lastTime
        else:
            pos = 0
            t = 0
        while t < timeT:
            t += 1
            if t < timeT:
                pos += self.speed(t) * 1.875 / self.bpm
                self.lastPos = pos
                self.lastTime = t
            else:
                return pos + (timeT%1) * self.speed(t) * 1.875 / self.bpm


class EventLayer:
    def __init__(self, bpm):
        self.bpm = bpm
        self.move1 = LineTimer(bpm, 0.5)
        self.move2 = LineTimer(bpm, 0.5)
        self.speed = LineTimer(bpm, 1.0)
        self.alpha = LineTimer(bpm, 0.0)
        self.rotate = LineTimer(bpm, 0.0)


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

        # 打点器打的点
        self.beats = []
        # 铺面延迟
        self.offset = 0.0

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls(self.RPE_Chart)
        memo[id(self)] = result
        result.bpm = copy.deepcopy(self.bpm, memo)
        result.noteCount = copy.deepcopy(self.noteCount, memo)
        result.lineList = copy.deepcopy(self.lineList, memo)
        result.noteList = copy.deepcopy(self.noteList, memo)
        result.RPE_level = copy.deepcopy(self.RPE_level, memo)
        result.charter = copy.deepcopy(self.charter, memo)
        result.composer = copy.deepcopy(self.composer, memo)
        result.illustration = copy.deepcopy(self.illustration, memo)
        result.name = copy.deepcopy(self.name, memo)
        result.level = copy.deepcopy(self.level, memo)
        result.id = copy.deepcopy(self.id, memo)
        result.song = copy.deepcopy(self.song, memo)
        result.bg = copy.deepcopy(self.bg, memo)
        result.duration = copy.deepcopy(self.duration, memo)
        result.chartTime = copy.deepcopy(self.chartTime, memo)
        result.beats = copy.deepcopy(self.beats, memo)
        return result

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

    def fastCalcFloorPos(self):
        self.noteCount = 0
        for line in self.lineList:
            line.fastCalcFloorPos()
            self.noteCount += len(line.noteList)

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

    def __deepcopy__(self, memo):
        # 创建新实例
        cls = self.__class__
        result = cls(self.RPE_Chart)
        memo[id(self)] = result

        # 复制基本属性
        result.bpm = copy.deepcopy(self.bpm, memo)
        result.noteCount = copy.deepcopy(self.noteCount, memo)
        result.RPE_level = copy.deepcopy(self.RPE_level, memo)
        result.charter = copy.deepcopy(self.charter, memo)
        result.composer = copy.deepcopy(self.composer, memo)
        result.illustration = copy.deepcopy(self.illustration, memo)
        result.name = copy.deepcopy(self.name, memo)
        result.level = copy.deepcopy(self.level, memo)
        result.id = copy.deepcopy(self.id, memo)
        result.song = copy.deepcopy(self.song, memo)
        result.bg = copy.deepcopy(self.bg, memo)
        result.duration = copy.deepcopy(self.duration, memo)
        result.chartTime = copy.deepcopy(self.chartTime, memo)
        result.beats = copy.deepcopy(self.beats, memo)

        # 深度复制 lineList 和 noteList
        result.lineList = copy.deepcopy(self.lineList, memo)
        result.noteList = copy.deepcopy(self.noteList, memo)

        return result


def newDefaultChart(bpm, numOfLine=24) -> Chart:
    chart = Chart(True)
    for i in range(numOfLine):
        line = Line(bpm)
        line.move1.addPeriod(0, 64, 0.5, 0.5)
        line.move2.addPeriod(0, 64, 0.3, 0.3)
        line.move3.addPeriod(0, 64, 0.0, 0.0)
        line.alpha.addPeriod(0, 64, 0.0, 0.0)
        line.speed.addPeriod(0, 64, 1.0, 1.0)
        line.theta.addPeriod(0, 64, 0.0, 0.0)
        line.rotate.addPeriod(0,64, 0.0, 0.0)
        chart.addLine(line)

    return chart

def getEventIndexByTime(lineTimer: LineTimer, t: int):
    t = round(t)

    # 找到光标前最近的事件
    i = 0
    while i < len(lineTimer.startTimeList)-1:
        if lineTimer.startTimeList[i] < t <= lineTimer.startTimeList[i + 1]:
            break
        i += 1

    if len(lineTimer.startTimeList) == 0:
        lineTimer.startValueList.append(lineTimer.defaultValue)
        lineTimer.endValueList.append(lineTimer.defaultValue)
        lineTimer.startTimeList.append(0)
        lineTimer.endTimeList.append(t)
        return i
    if lineTimer.endTimeList[i] == t:
        print("set 1")
        return i
    if lineTimer.endTimeList[i] < t:
        print("set 2")
        st = lineTimer.endTimeList[i]
        sv = lineTimer.endValueList[i]
        lineTimer.startValueList.insert(i+1, sv)
        lineTimer.endValueList.insert(i+1, lineTimer.endValueList[i])
        lineTimer.startTimeList.insert(i+1, st)
        lineTimer.endTimeList.insert(i+1, t)
        return i+1
    if lineTimer.endTimeList[i] > t:
        print("set 3")
        sv = lineTimer.startValueList[i] + ((lineTimer.endValueList[i] - lineTimer.startValueList[i])
              * (t - lineTimer.startTimeList[i]) / (lineTimer.endTimeList[i] - lineTimer.startTimeList[i]))
        lineTimer.startValueList.insert(i+1, sv)
        lineTimer.endValueList.insert(i+1, lineTimer.endValueList[i])
        lineTimer.startTimeList.insert(i+1, t)
        lineTimer.endTimeList.insert(i+1, lineTimer.endTimeList[i])
        lineTimer.endTimeList[i] = t
        lineTimer.endValueList[i] = sv
        return i

def exactPeriodFromLine(line: Line, t1, t2) -> Period:
    period: Period = Period(t2-t1, "新的片段")

    lt1s = (line.alpha, line.move1, line.move2, line.rotate)
    lt2s = (period.alpha, period.move1, period.move2, period.rotate)

    for j in range(len(lt1s)):
        lineTimer1 = lt1s[j]
        lineTimer2 = lt2s[j]
        for t in range(int(t1), int(t2), 4):
            lineTimer2.addPeriod(t-int(t1), t+4-int(t1), lineTimer1(t+0.01), lineTimer1(t+4.01))
    return period


