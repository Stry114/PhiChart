import time

from chart import *
import math


class ChartException:
    time: float
    line: Line
    name: str = "异常"

    def __str__(self):
        return type(self).__name__


class NoteConflictException(ChartException):
    name: str = "Note重叠"
    def __init__(self, chart, line, note1, note2):
        self.chart: Chart = chart
        self.note1: Note = note1
        self.note2: Note = note2
        self.time = note1.time_
        self.line: Line = line

    def __str__(self):
        return f"Note conflict at time={self.note1.time_}."

class NoteOutOfRangeException(ChartException):
    name: str = "Note超界"
    def __init__(self, chart, line, note):
        self.chart: Chart = chart
        self.note: Note = note
        self.time = note.time_
        self.line: Line = line

    def __str__(self):
        return f"Notes go beyond the boundary at time={self.note.time_}."

class SpeedEventNotHookedException(ChartException):
    name: str = "速度事件未钩定"
    def __init__(self, chart, line, lineTimer, index):
        self.chart: Chart = chart
        self.line: Line = line
        self.lineTimer: LineTimer = lineTimer
        self.index = index
        self.time = lineTimer.startTimeList[index]

    def __str__(self):
        return f"The start and end values of the speed event are inconsistent at time={self.time}."


class EventOverlapException(ChartException):
    name = "事件重叠"
    def __init__(self, chart, line, lineTimer, index):
        self.chart: Chart = chart
        self.line: Line = line
        self.lineTimer: LineTimer = lineTimer
        self.index = index
        self.time = lineTimer.startTimeList[index]

    def __str__(self):
        return f"The time of the events overlaps at time={self.time}."


class EventDiscontinuityException(ChartException):
    name = "事件不连续"
    def __init__(self, chart, line, lineTimer, index):
        self.chart: Chart = chart
        self.line: Line = line
        self.lineTimer: LineTimer = lineTimer
        self.index = index
        self.time = lineTimer.startTimeList[index]

    def __str__(self):
        return f"Adjacent events must be consecutive. At time={self.time}."


class EmptyArrayException(ChartException):
    name = "空数组异常"
    def __init__(self, chart, line, lineTimer):
        self.chart: Chart = chart
        self.line: Line = line
        self.lineTimer: LineTimer = lineTimer
        self.time = 0

    def __str__(self):
        return f"At least one event should be populated."


class LastEventPrematureException(ChartException):
    name = "末事件过早结束"
    def __init__(self, chart, line, lineTimer, index):
        self.chart: Chart = chart
        self.line: Line = line
        self.lineTimer: LineTimer = lineTimer
        self.index = index
        self.time = lineTimer.startTimeList[index]

    def __str__(self):
        return f"The final event must be end no earlier than 99999."


class FirstEventTooLateException(ChartException):
    name = "首事件起始时间不为0"
    def __init__(self, chart, line, lineTimer, index):
        self.chart: Chart = chart
        self.line: Line = line
        self.lineTimer: LineTimer = lineTimer
        self.index = index
        self.time = lineTimer.startTimeList[index]

    def __str__(self):
        return f"The first event began too late at time={self.time}."


def sorted(chart: Chart):
    for line in chart.lineList:
        line.noteList.sort(key=lambda note: note.time_)
        optimized_insertion_sort(line.alpha)
        optimized_insertion_sort(line.move1)
        optimized_insertion_sort(line.move2)
        optimized_insertion_sort(line.theta)
        optimized_insertion_sort(line.speed)
        optimized_insertion_sort(line.rotate)

def printLineTimer(lineTimer: LineTimer):
    print(time.time())
    print(lineTimer.startTimeList)
    for i in range(len(lineTimer.startTimeList)):
        print(f"i ~\t{lineTimer.startTimeList[i]}({lineTimer.startValueList[i]}) ~\t{lineTimer.endTimeList[i]}({lineTimer.endValueList[i]})")

def optimized_insertion_sort(lineTimer: LineTimer):
    """
    针对只有少量无序元素的长列表优化的插入排序

    思路：
    1. 遍历列表找出无序元素的位置
    2. 只对这些无序元素执行插入操作
    3. 避免对已有序部分进行不必要的比较
    """
    n = len(lineTimer.startTimeList)

    for i in range(1, n):
        current = lineTimer.startTimeList[i]
        startValue = lineTimer.startValueList[i]
        startTime = lineTimer.startTimeList[i]
        endValue = lineTimer.endValueList[i]
        endTime = lineTimer.endTimeList[i]
        j = i - 1

        # 只有当前元素小于前一个元素时才需要移动（说明无序）
        if current < lineTimer.startTimeList[j]:
            # 将大于current的元素后移
            while j >= 0 and current < lineTimer.startTimeList[j]:
                lineTimer.startValueList[j + 1] = lineTimer.startValueList[j]
                lineTimer.startTimeList[j + 1] = lineTimer.startTimeList[j]
                lineTimer.endValueList[j + 1] = lineTimer.endValueList[j]
                lineTimer.endTimeList[j + 1] = lineTimer.endTimeList[j]
                j -= 1

            lineTimer.startValueList[j + 1] = startValue
            lineTimer.startTimeList[j + 1] = startTime
            lineTimer.endValueList[j + 1] = endValue
            lineTimer.endTimeList[j + 1] = endTime





def check(chart: Chart):

    # 先整理排序
    sorted(chart)

    for line in chart.lineList:

        for i in range(len(line.noteList)):
            n1 = line.noteList[i]

            # 检查键冲突
            if i < len(line.noteList) - 1:
                n2 = line.noteList[i + 1]
                if n1.time_ == n2.time_ and abs(n1.posX - n2.posX) <= 1:
                    yield NoteConflictException(chart, line, n1, n2)

            # 检查键超界
            if not -10 < n1.posX < 10:
                yield NoteOutOfRangeException(chart, line, n1)

        for i in range(len(line.speed.startTimeList)):
            # 检查速度事件前后值钩定
            if line.speed.startValueList[i] != line.speed.endValueList[i]:
                yield SpeedEventNotHookedException(chart, line, line.speed, i)


        lineTimerList = (line.move1, line.move2, line.speed, line.alpha, line.rotate)
        for lineTimer in lineTimerList:
            for i in range(len(lineTimer.startTimeList)-1):
                if lineTimer.endTimeList[i] > lineTimer.startTimeList[i+1]:
                    yield EventOverlapException(chart, line, lineTimer, i+1)

                if lineTimer.endTimeList[i] < lineTimer.startTimeList[i+1]:
                    yield EventDiscontinuityException(chart, line, lineTimer, i+1)

        for lineTimer in lineTimerList:
            if len(lineTimer.startTimeList) == 0:
                yield EmptyArrayException(chart, line, lineTimer)
            if lineTimer.startTimeList[0] > 0:
                yield FirstEventTooLateException(chart, line, lineTimer, 0)
        for lineTimer in lineTimerList:
            if len(lineTimer.startTimeList) > 0 and lineTimer.endTimeList[-1] < 99999:
                # yield LastEventPrematureException(chart, line, lineTimer, -1)
                break
