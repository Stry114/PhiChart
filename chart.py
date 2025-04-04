class LineTimer:
    def __init__(self, bpm):
        self.bpm = bpm
        self.peroidCount = 0
        self.endTimeList = []
        self.endValueList = []
        self.startTimeList = []
        self.startValueList = []
    
    def second(self, time_, baseBPM=None):
        if baseBPM is None:
            return time_ / self.bpm * 1.875
        else:
            return time_ / baseBPM * 1.875

    def addPeriod(self, startTime, endTime, startValue, endValue):
        if startTime > endTime:
            raise ValueError("EndTime must be later than startTime.")
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
            if not  s <= time_ < e:
                continue
            d = (time_ - s) / (e - s)
            a = self.startValueList[i]
            b = self.endValueList[i]
            return (b - a) * d + a
        raise IndexError("Time index out of defineded range of timer.")

    def __call__(self, time_):
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

        self.hit = False
        self.begin = False
        self.doubleHit = False

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
        self.speed = LineTimer(bpm)
        self.alpha = LineTimer(bpm)
        self.rotate = LineTimer(bpm)

        self.noteList: list[Note] = []

    def addNote(self, note: Note):
        self.noteList.append(note)

    def report(self, level=0, index=0):
        print(" "*4*level + "<line>", index)
        level += 1
        print(" "*4*level + f"bpm\t{self.bpm}")
        print(" "*4*level + f"move1\t{self.move1.peroidCount}\t[{self.move1.min()}, {self.move1.max()}]")
        print(" "*4*level + f"move2\t{self.move2.peroidCount}\t[{self.move2.min()}, {self.move2.max()}]")
        print(" "*4*level + f"alpha\t{self.alpha.peroidCount}\t[{self.alpha.min()}, {self.alpha.max()}]")
        print(" "*4*level + f"speed\t{self.speed.peroidCount}\t[{self.speed.min()}, {self.speed.max()}]")
        print(" "*4*level + f"rotate\t{self.rotate.peroidCount}\t[{self.rotate.min()}, {self.rotate.max()}]")

    def pos(self, time_):
        pos = 0
        for i in range(self.speed.peroidCount):
            s = self.speed.startTimeList[i]
            e = self.speed.endTimeList[i]
            if not s <= time_ < e:
                pos += (e - s) * self.speed.startValueList[i] * 1.875 / self.bpm
            else:
                return (time_ - s) * self.speed.startValueList[i] * 1.875 / self.bpm + pos
        print(time_, e)

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

class Chart:
    def __init__(self):
        self.bpm = None
        self.noteCount = 0
        self.lineList: list[Line] = []
        self.noteList: list[Note] = []

    def addLine(self, line: Line):
        self.bpm = line.bpm
        self.lineList.append(line)
        self.noteCount += len(line.noteList)
        self.noteList.extend(line.noteList)

    def report(self, level=0):
        print(" "*4*level + "<chart>")
        print(" "*4*(level+1) + f"line\t{len(self.lineList)}")
        for i in range(len(self.lineList)):
            self.lineList[i].report(level+1, i)

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