from player import Player
from autoMatch import Matcher



player = Player(Matcher("D:/Projects/PygamePhiChart/charts/反命题 AT"), w=1200, h=800, fps=120, debug=True)
# player.targetRectOfMapping = (640, 400,960,600)
player.displayUI = False
player.chartDelay = -60
player.initPlayer()
player.mainloop()