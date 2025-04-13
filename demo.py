from player import Player
from autoMatch import Matcher


player = Player(Matcher("charts/rr/"))
player.initPlayer()
player.mainloop()