from player3D import Player
from libs.autoMatch import Matcher

player = Player(Matcher(r"/charts/白复生 IN"), w=1200, h=800, fps=60)

# 设置副标题
player.name = "白复生"
player.level = "IN Lv.?"
player.subtitle = "PYGAME PHICHART"

# 启用3D
player.enable3D = True
player.enableNewVision = True
player.enableCompiler = True

# 设置摄像机位置，推荐处于中间偏上的位置
player.cmrY = player.height*0.1
player.cmrX = player.width*0.5
player.cmrB = 2

# 设置键出现的位置，推荐值为3倍屏幕高度
player.boundary = 7.2 * player.height
# 设置流速，推荐为3倍速
player.speed = 7.2

# 设置键大小和特效大小，由于透视，建议调大一点
player.noteSize = player.width / 8
player.hitEffectSize = player.width / 6

# 初始化并进入消息循环
player.startTimeS = 0
player.initPlayer()


player.chart.charter = "官谱改编"

player.mainloop()