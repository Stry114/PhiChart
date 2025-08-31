import os
import toml
from chart import *


def lineTimer2tml(lineTimer: LineTimer):
    # 根据 chart.py 中的 LineTimer 类，将 lineTimer 对象转换为 TOML 格式的字符串
    return {
        "bpm": lineTimer.bpm,
        "peroidCount": lineTimer.peroidCount,
        "endTimeList": lineTimer.endTimeList,
        "endValueList": lineTimer.endValueList,
        "startTimeList": lineTimer.startTimeList,
        "startValueList": lineTimer.startValueList,
        "defaultValue": lineTimer.defaultValue
    }


def note2toml(note: Note):
    # 根据 chart.py 中的 Note 类，将 note 对象转换为 TOML 格式的字符串
    return {
        "type": note.type_,
        "time": note.time_,
        "posX": note.posX,
        "floorPos": note.floorPos,
        "speed": note.speed,
        "holdTime": note.holdTime,
        "above": note.above,
        "size": note.size,
        "alpha": note.alpha,
        "visibleTime": note.visibleTime,
        "isFake": note.isFake,
        "hit": note.hit,
        "begin": note.begin,
        "doubleHit": note.doubleHit
    }


def line2toml(line: Line):
    # 根据 chart.py 中的 Line 类，将 line 对象转换为 TOML 格式的字符串
    return {
        "bpm": line.bpm,
        "move1": lineTimer2tml(line.move1),
        "move2": lineTimer2tml(line.move2),
        "speed": lineTimer2tml(line.speed),
        "alpha": lineTimer2tml(line.alpha),
        "rotate": lineTimer2tml(line.rotate),
        "theta": lineTimer2tml(line.theta),
        "noteList": [note2toml(note) for note in line.noteList],
        "scaleX": lineTimer2tml(line.scaleX),
        "scaleY": lineTimer2tml(line.scaleY),
        "texture": line.texture,
        "cmrH": line.cmrH
    }


def chart2toml(chart: Chart):
    # 根据 chart.py 中的 Chart 类，将 chart 对象转换为 TOML 格式的字符串
    return {

        "bpm": chart.bpm,
        "RPE_Chart": chart.RPE_Chart,
        
        "RPE_level": chart.RPE_level,
        "charter": chart.charter,
        "composer": chart.composer,
        "illustration": chart.illustration,
        "name": chart.name,
        "level": chart.level,
        "id": chart.id, 
        "song": chart.song,
        "bg": chart.bg,
        "duration": chart.duration,
        "chartTime": chart.chartTime,

        "lineList" : [ line2toml(line) for line in chart.lineList ],
    }

def toml2note(dic: dict):
    # 创建一个 Note 对象，参数随便填
    note: Note = Note(0, 0, 0, 0, 0, 0, False)
    # 将字典中的键值对赋值给 Note 对象的属性
    note.type_ = dic["type"]
    note.time_ = dic["time"]
    note.posX = dic["posX"]
    note.floorPos = dic["floorPos"]
    note.speed = dic["speed"]
    note.holdTime = dic["holdTime"]
    note.above = dic["above"]
    note.size = dic["size"]
    note.alpha = dic["alpha"]
    note.visibleTime = dic["visibleTime"]
    note.isFake = dic["isFake"]
    note.hit = dic["hit"]
    note.begin = dic["begin"]
    note.doubleHit = dic["doubleHit"]
    return note

def toml2linetimer(dic: dict):
    # 创建一个 LineTimer 对象，参数随便填
    lineTimer: LineTimer = LineTimer(0, 0.0)
    # 将字典中的键值对赋值给 LineTimer 对象的属性
    lineTimer.bpm = dic["bpm"]
    lineTimer.peroidCount = int(dic["peroidCount"])
    lineTimer.endTimeList = dic["endTimeList"]
    lineTimer.endValueList = dic["endValueList"]
    lineTimer.startTimeList = dic["startTimeList"]
    lineTimer.startValueList = dic["startValueList"]
    lineTimer.defaultValue = dic["defaultValue"]
    return lineTimer

def toml2line(dic: dict):
    # 创建一个 Line 对象，参数随便填
    line: Line = Line(0)
    # 将字典中的键值对赋值给 Line 对象的属性
    line.bpm = dic["bpm"]
    line.move1 = toml2linetimer(dic["move1"])
    line.move2 = toml2linetimer(dic["move2"])
    line.speed = toml2linetimer(dic["speed"])
    line.alpha = toml2linetimer(dic["alpha"])
    line.rotate = toml2linetimer(dic["rotate"])
    line.theta = toml2linetimer(dic["theta"])
    line.noteList = [toml2note(note) for note in dic["noteList"]]
    line.scaleX = toml2linetimer(dic["scaleX"])
    line.scaleY = toml2linetimer(dic["scaleY"])
    line.texture = dic["texture"]
    return line

def toml2chart(dic: dict):
    # 创建一个 Chart 对象，参数随便填
    chart: Chart = Chart(False)
    # 将字典中的键值对赋值给 Chart 对象的属性
    chart.bpm = dic["bpm"]
    chart.RPE_Chart = dic["RPE_Chart"]
    chart.RPE_level = dic["RPE_level"]
    chart.charter = dic["charter"]
    chart.composer = dic["composer"]
    chart.illustration = dic["illustration"]
    chart.name = dic["name"]
    chart.level = dic["level"]
    chart.id = dic["id"]
    chart.song = dic["song"]
    chart.bg = dic["bg"]
    chart.duration = dic["duration"]
    chart.chartTime = dic["chartTime"]
    
    chart.lineList = [toml2line(line) for line in dic["lineList"]]
    
    return chart