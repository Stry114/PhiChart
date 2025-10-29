from libs.chart import *
from libs.analyzer import *
from libs.autoMatch import Matcher

from player import Player
import math


matcher = Matcher("charts/波塞冬AT")
player = Player(matcher, w=1080, h=800, fps=120, debug=True)
player.noteSize = player.width / 12
player.initPlayer()


r = 0.36
numOfLines = 90
newLines: list[Line] = []
for i in range(numOfLines):
    line = Line(player.chart.bpm)
    newLines.append(line)

    rotate = 360 / numOfLines * i
    x = 0.5 + r * math.cos(rotate/180*math.pi + math.pi/2)
    y = 0.5 + r * math.sin(rotate/180*math.pi + math.pi/2) * (player.width / player.height)
    line.rotate.addPeriod(0, 999999, rotate, rotate)
    line.alpha.addPeriod(0, 999999, 1.0, 1.0)
    line.speed.addPeriod(0, 999999, 1.6, 1.6)
    line.move1.addPeriod(0, 999999, x, x)
    line.move2.addPeriod(0, 999999, y, y)


for line in player.chart.lineList:
    for note in line.noteList:
        angle = ((-note.posX / 40) * 360 + 270) % 360
        index = round((angle - 90) / (360 / numOfLines))
        print(note.posX, angle, index)

        note.posX = 0
        note.visibleTime = 0.5
        note.above = False
        line.noteList.remove(note)
        newLines[index%numOfLines].addNote(note)


player.chart.lineList = newLines
player.chart.fastCalcFloorPos()
player.startTimeS = 60
player.mainloop()
