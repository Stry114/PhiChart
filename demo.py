from player3D import Player
from libs.autoMatch import Matcher

matched = Matcher(r"D:\Projects\PygamePhiChart\charts\轻涟")
player = Player(matcher=matched, w=1000, h=800, fps=120)
# 设置副标题
player.name = "PhiChart Project Preview"
player.level = "IN Lv.?"
player.subtitle = "ELEVATED"


# 启用3D
player.displayDebug = True
player.enable3D = False
player.enableNewVision = False
player.displacementY = 1.0
player.enableMapping = False
# 设置摄像机位置，推荐处于中间偏上的位置
player.cmrY = player.height * 0.1
player.cmrX = player.width * 0.5
player.lineLength = 3000

# 设置键出现的位置，推荐值为3倍屏幕高度
player.boundary = 4.0 * player.height
# 设置流速，推荐为3倍速
player.speed3D = 4.0

# 设置键大小和特效大小，由于透视，建议调大一点
player.noteSize = player.width / 8
player.hitEffectSize = player.width / 6

# 初始化并进入消息循环
player.initPlayer()
player.startTimeS = 0

# line = player.chart.lineList[0]
# line.theta.addPeriod(0, 512, 90, 90)
# line.theta.addPeriod(512, 768, 90, 0)
player.mainloop()