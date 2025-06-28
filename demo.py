from player import Player
from autoMatch import Matcher

player = Player(Matcher("charts/2085 AT"), w=1000, h=800, fps=120)

# 设置副标题
player.name = "PRAGMATISM -RESURRECTION-"
player.level = "高视角 AT Lv.16"

# 启用3D
player.enable3D = True
player.enableCompiler = False

# 设置摄像机位置，推荐处于中间偏上的位置
player.cmrY = player.height*0.5
player.cmrX = player.width*0.5

# 设置键出现的位置，推荐值为3倍屏幕高度
player.boundary = 3.6 * player.height
# 设置流速，推荐为3倍速
player.speed = 3.6

# 设置键大小和特效大小，由于透视，建议调大一点
player.noteSize = player.width / 8
player.hitEffectSize = player.width / 6

# 初始化并进入消息循环
player.initPlayer()
player.mainloop()