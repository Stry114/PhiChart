from player import Player
from autoMatch import Matcher


player = Player(Matcher("D:/Projects/PygamePhiChart/charts/圣夜赞歌"), w=1200, h=800, fps=120)
player.enable3D = True
player.initPlayer()
player.mainloop()