from script.player import Player
from libs.autoMatch import Matcher
from libs.vec3D import *
from libs.chart import *


matched = Matcher(r"D:\Projects\PygamePhiChart\charts\愚人节\雪降SP")
player = Player(matcher=matched, w=1600, h=900, fps=90, debug=False)
# 设置副标题
player.name = "今年も「雪降り、メリクリ」目指して頑張ります！！"
player.level = "SP Lv.?"
player.subtitle = "AUTOPLAY"
player.halfScore = "#0    252000"


# 启用3D
player.enable3D = False
player.enableNewVision = False
player.displacementY = 1.0
player.enableMapping = False
player.autoplay = True
# 设置摄像机位置，推荐处于中间偏上的位置
player.cmrY = player.height * 0.1
player.cmrX = player.width * 0.5
player.lineLength = 3 * player.width

# 设置键出现的位置，推荐值为3倍屏幕高度
player.boundary = 4.0 * player.height
# 设置流速，推荐为3倍速
player.speed3D = 4.0

# 设置键大小和特效大小，由于透视，建议调大一点
player.noteSize = player.width / 8
player.hitEffectSize = player.width / 6

# 初始化并进入消息循环
player.initPlayer()
player.startTimeS = player.waveDurationS // 2 - 20
player.mainloop()