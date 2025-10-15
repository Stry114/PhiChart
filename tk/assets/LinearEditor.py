from tk.mytk import *
from libs.chart import *


class LinearEditor(Frame):
    def __init__(self, master, chart: Chart, lineIndex:int):
        self.lineIndex = lineIndex
        self.chart = chart
        self.line = chart.lineList[lineIndex]

        # 当前底部时间
        self.t0 = 1600
        # 最大时间
        self.t1 = 0
        # 底部到顶部的时间差
        self.dt = 160
        # canvas 高度
        self.h0 = 720
        self.w0 = 600

        self.master = master
        self.top = Toplevel(master)
        self.top.title("线性编辑器")
        self.top.geometry("1000x600")
        self.top.minsize(1000, 800)
        self.top.config(padx=40, pady=40)
        self.top.config(bg="#222")

        self.fr1 = Frame(self.top)
        self.fr1.pack(side=TOP, fill=BOTH, expand=True)
        self.fr2 = Frame(self.top, height=30)
        self.fr2.pack(side=TOP, fill=X, expand=False)