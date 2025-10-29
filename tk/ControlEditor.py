from tkinter import *
from pullbar import *
from tkinter import messagebox, ttk, font
from libs.chart import *


class ControlEditor(Canvas):
    def __init__(self, master, control: LineTimer=None):
        super().__init__(master)
        self.control = control
        self.config(highlightthickness=0, bg="#272727")
        self.pack(fill=BOTH, expand=1)

        # 横轴左侧值
        self.t0 = 0
        # 横轴左右差值
        self.dt = 1000
        # 纵轴上下差值
        self.dv = 2.5
        # 绘制区域大小
        self.w = 0
        self.h = 0
        # 绘制边距
        self.w0 = 0
        self.h0 = 0

        # 鼠标靠近是显示阴影的节点的索引
        self.candidate: int|None = None
        self.selecting: int|None = None

        if control is None:
            self.control = LineTimer(0, 1.0)
        if control.periodCount == 0:
            self.control.addPeriod(0.0, 99999999, 1.0, 1.0)

        self.bind("<Motion>", self.onMotion)
        self.bind("<Button-1>", self.onPress)
        self.bind("<MouseWheel>", self.onWheel)
        self.bind("<ButtonRelease-1>", self.onRelease)
        self.bind("<Control-MouseWheel>", self.onScaleValue)
        self.bind("<Control-Alt-MouseWheel>", self.onScaleTime)
        self.after(200, self.update)

    def update(self):
        self.w = self.winfo_width()
        self.h = self.winfo_height() - 20

        self.delete("all")

        for t in range(int(self.t0//10*10), int(self.t0+self.dt//10*10), 10):
            x = (t - self.t0) / self.dt * self.w + self.w0
            if t % 100 == 0:
                text = str(t)+" px" if t==0 else str(t)
                self.create_line(x, self.h0, x, self.h0+self.h + 20, width=1, fill="#444")
                self.create_text(x+5, self.h0+self.h+2, text=text, anchor=NW, fill="#ddd")
            else:
                self.create_line(x, self.h0, x, self.h0+self.h, width=1, fill="#333")

        for v in range(int(self.dv)+1):
            y = (1 - v/self.dv) * self.h + self.h0
            color = "#777" if v == 0 else "#444"
            self.create_line(self.w0, y, self.w0+self.w, y, width=1, fill=color)
            self.create_text(self.w0+5, y-1, text=str(float(v))+"x", anchor=SW, fill="#ddd")

        for i in range(self.control.periodCount):
            t1 = self.control.startTimeList[i]
            t2 = self.control.endTimeList[i]
            v1 = self.control.startValueList[i]
            v2 = self.control.endValueList[i]

            x1 = (t1 - self.t0) / self.dt * self.w + self.w0
            x2 = (t2 - self.t0) / self.dt * self.w + self.w0
            y1 = (1 - v1/self.dv) * self.h + self.h0
            y2 = (1 - v2/self.dv) * self.h + self.h0

            if i == self.control.periodCount - 1:
                x2 = self.w0+self.w
                y2 = y1

            nodeColor = "#777" if i == self.candidate else "#222"
            nodeColor = "#ccc" if i == self.selecting else nodeColor
            self.create_line(x1, y1, x2, y2, width=3, fill="#ddd")
            self.create_oval(x1-8, y1-8, x1+8, y1+8, fill=nodeColor, outline="#ddd", width=2)

    def onWheel(self, event):
        self.t0 -= event.delta / abs(event.delta) * self.dt / 12
        self.t0 = max(self.t0, 0)
        self.update()

    def onScaleValue(self, event):
        self.dv -= event.delta / abs(event.delta) * 0.5
        self.dv = min(10.0, max(self.dv, 2))
        self.update()

    def onScaleTime(self, event):
        self.dt -= event.delta / abs(event.delta) * 200
        self.dt = min(2000, max(self.dt, 200))
        self.update()

    def screenToIndex(self, event):
        w0 = 0
        self.w = self.winfo_width()
        for i in range(self.control.periodCount):
            t1 = self.control.startTimeList[i]
            x1 = (t1 - self.t0) / self.dt * self.w + w0

            if abs(x1 - event.x) < 8:
                return i, "pullNode"
            elif event.x < x1 - 8:
                return i, "addNewNode"
        return self.control.periodCount, "addNewNode"

    def onPress(self, event):
        self.bind("<Motion>", self.onDrag)

        res = self.screenToIndex(event)
        self.selecting = res[0]
        if res[1] == "addNewNode":
            t = (event.x - self.w0) / self.w * self.dt + self.t0
            self.control.startTimeList.insert(res[0], t)
            self.control.endTimeList.insert(res[0], self.control.endTimeList[res[0]-1])
            self.control.startValueList.insert(res[0], 0)
            self.control.endValueList.insert(res[0], self.control.endValueList[res[0]-1])
            self.control.easingTypeList.insert(res[0], 1)
            self.control.endTimeList[res[0] - 1] = t
        self.onDrag(event)

    def onRelease(self, event):
        self.bind("<Motion>", self.onMotion)
        self.onDrag(event)

    def onDrag(self, event):
        v = (1 - (event.y - self.h0) / self.h) * self.dv
        t = round(((event.x - self.w0) / self.w * self.dt + self.t0) / 20) * 20
        if self.selecting != 0:
            self.control.endValueList[self.selecting-1] = v
            self.control.endTimeList[self.selecting-1] = t
        self.control.startValueList[self.selecting] = v
        self.control.startTimeList[self.selecting] = t
        self.update()

    def onMotion(self, event):
        res = self.screenToIndex(event)
        self.candidate = res[0] if res[1] == "pullNode" else None
        self.update()


if __name__ == '__main__':
    root = Tk()
    root.title('Control Editor')
    root.geometry("800x200")
    root.config(bg='#222')
    root.config(padx=20, pady=20)

    lineTimer = (LineTimer(100, 0)
                 .addPeriod(0, 200, 0.5, 1.0)
                 .addPeriod(200, 400, 1.0, 0.5)
                 .addPeriod(400, 600, 0.5, 0.5)
                 .addPeriod(600, 800, 0.5, 0.0)
                 .addPeriod(800, 1000, 0.0, 0.0)
                 )
    controlEditor = ControlEditor(root, lineTimer)
    controlEditor.pack(fill=BOTH, expand=1)

    root.mainloop()