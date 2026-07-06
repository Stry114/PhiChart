from tkinter import *
from tkinter import ttk


class MyFrame(Frame):
    def __init__(self, master, spaceHeight, spaceWidth, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self._imageButtonU = PhotoImage(file="tk/assets/buttonU.png")
        self._imageButtonD = PhotoImage(file="tk/assets/buttonD.png")

        self.frame = FrameDark(self, height=spaceHeight, )
        self.frame.place(x=0, y=0, height=spaceHeight, width=spaceWidth)

        self.scrollerFrame = Frame(self)
        self.buttonU = Button(self.scrollerFrame, image=self._imageButtonU, bd=0, command=self.buttonU_Command)
        self.buttonD = Button(self.scrollerFrame, image=self._imageButtonD, bd=0, command=self.buttonD_Command)
        self.scroller = Label(self.scrollerFrame, bg="#aaa")

        # 滚动条宽度
        self.scrollerWidth = 20
        # 使用按钮操作的步长
        self.step = 20

        self.screenY1 = 0
        self.screenY2 = 0
        self.spaceHeight = spaceHeight
        self.spaceWidth = spaceWidth

        self.bind("<MouseWheel>", self.wheelEvent)
        self.frame.bind("<MouseWheel>", self.wheelEvent)
        self.bind("<Configure>", self.configureEvent)
        self.scroller.bind("<Enter>", self.scrollerEnter)
        self.scroller.bind("<Leave>", self.scrollerLeave)
        self.scroller.bind("<Button-1>", self.pullBegin)
        self.scroller.bind("<ButtonRelease-1>", self.pullEnd)

    def configureEvent(self, *args):
        frameH = self.winfo_height()
        frameW = self.winfo_width()
        scrollerH = frameH - 2 * self.scrollerWidth

        self.screenY2 = self.screenY1 + frameH
        if self.screenY2 * (scrollerH / self.spaceHeight) > scrollerH and frameH < self.spaceHeight:
            self.screenY1 = self.spaceHeight - frameH
            self.frame.place(x=0, y=-self.screenY1)
        if frameH < self.spaceHeight:
            y1 = self.screenY1 * (scrollerH / self.spaceHeight)
            y2 = self.screenY2 * (scrollerH / self.spaceHeight)
        else:
            self.scrollerFrame.place(x=frameW, y=0, width=self.scrollerWidth, height=frameH)
            return

        self.scrollerFrame.place(x=frameW-self.scrollerWidth, y=0, width=self.scrollerWidth, height=frameH)
        self.buttonU.place(x=0, y=0, width=self.scrollerWidth, height=self.scrollerWidth)
        self.buttonD.place(x=0, y=frameH-self.scrollerWidth, width=self.scrollerWidth, height=self.scrollerWidth)
        self.scroller.place(x=(self.scrollerWidth-8)/2, y=y1+self.scrollerWidth, width=8, height=(y2-y1))

    def scrollerEnter(self, *args):
        self.scroller.config(bg="#ccc")

    def scrollerLeave(self, *args):
        self.scroller.config(bg="#aaa")

    def setY(self, y):
        self.screenY1 = y
        self.frame.place(x=0, y=-self.screenY1)
        self.configureEvent()

    def buttonU_Command(self):
        self.screenY1 = max(self.screenY1 - self.step, 0)
        self.setY(self.screenY1)

    def buttonD_Command(self):
        frameH = self.winfo_height()
        self.screenY1 = min(self.spaceHeight - frameH, self.screenY1 + self.step)
        self.setY(self.screenY1)

    def pullBegin(self, event):
        self.pullBeginY = event.y
        self.scroller.bind("<Motion>", self.pullMotion)

    def pullMotion(self, event):
        frameH = self.winfo_height()
        scrollerH = frameH - 2 * self.scrollerWidth
        Y = self.screenY1 + (event.y-self.pullBeginY) / (scrollerH / self.spaceHeight)
        Y = max(0, Y)
        Y = min(Y, self.spaceHeight - frameH)
        self.setY(Y)

    def pullEnd(self, event):
        self.scroller.bind("<Motion>", self.nothing)

    def nothing(self, *args):
        return args

    def wheelEvent(self, event):
        frameH = self.winfo_height()
        Y = self.screenY1 - event.delta
        Y = max(0, Y)
        Y = min(Y, self.spaceHeight - frameH)
        self.setY(Y)

class MyFrameX(Frame):
    def __init__(self, master, spaceHeight, spaceWidth, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self._imageButtonL = PhotoImage(file="tk/assets/buttonL.png")
        self._imageButtonR = PhotoImage(file="tk/assets/buttonR.png")

        self.frame = FrameDark(self, height=spaceHeight, )
        self.frame.place(x=0, y=0, height=spaceHeight, width=spaceWidth)

        self.scrollerFrame = Frame(self)
        self.buttonR = Button(self.scrollerFrame, image=self._imageButtonL, bd=0, command=self.buttonL_Command)
        self.buttonL = Button(self.scrollerFrame, image=self._imageButtonR, bd=0, command=self.buttonR_Command)
        self.scroller = Label(self.scrollerFrame, bg="#aaa")

        # 滚动条宽度
        self.scrollerWidth = 20
        # 使用按钮操作的步长
        self.step = 20

        self.screenX1 = 0
        self.screenX2 = 0
        self.spaceHeight = spaceHeight
        self.spaceWidth = spaceWidth

        self.bind("<MouseWheel>", self.wheelEvent)
        self.frame.bind("<MouseWheel>", self.wheelEvent)
        self.bind("<Configure>", self.configureEvent)
        self.scroller.bind("<Enter>", self.scrollerEnter)
        self.scroller.bind("<Leave>", self.scrollerLeave)
        self.scroller.bind("<Button-1>", self.pullBegin)
        self.scroller.bind("<ButtonRelease-1>", self.pullEnd)

    def configureEvent(self, *args):
        frameH = self.winfo_height()
        frameW = self.winfo_width()
        scrollerW = frameW - 2 * self.scrollerWidth

        self.screenX2 = self.screenX1 + frameW
        if self.screenX2 * (scrollerW / self.spaceWidth) > scrollerW and frameW < self.spaceWidth:
            self.screenX1 = self.spaceWidth - frameW
            self.frame.place(x=-self.screenX1, y=0)
        if frameW < self.spaceWidth:
            x1 = self.screenX1 * (scrollerW / self.spaceWidth)
            x2 = self.screenX2 * (scrollerW / self.spaceWidth)
        else:
            self.scrollerFrame.place(x=0, y=frameH, width=frameW, height=self.scrollerWidth)
            return

        self.scrollerFrame.place(x=0, y=frameH-self.scrollerWidth, width=frameW, height=self.scrollerWidth)
        self.buttonR.place(x=0, y=0, width=self.scrollerWidth, height=self.scrollerWidth)
        self.buttonL.place(x=frameW-self.scrollerWidth, y=0, width=self.scrollerWidth, height=self.scrollerWidth)
        self.scroller.place(x=x1+self.scrollerWidth, y=(self.scrollerWidth-8)/2, width=(x2-x1), height=8)

    def scrollerEnter(self, *args):
        self.scroller.config(bg="#ccc")

    def scrollerLeave(self, *args):
        self.scroller.config(bg="#aaa")

    def setX(self, x):
        self.screenX1 = x
        self.frame.place(x=-self.screenX1, y=0)
        self.configureEvent()

    def buttonL_Command(self):
        self.screenX1 = max(self.screenX1 - self.step, 0)
        self.setX(self.screenX1)

    def buttonR_Command(self):
        frameW = self.winfo_width()
        self.screenX1 = min(self.spaceWidth - frameW, self.screenX1 + self.step)
        self.setX(self.screenX1)

    def pullBegin(self, event):
        self.pullBeginX = event.x
        self.scroller.bind("<Motion>", self.pullMotion)

    def pullMotion(self, event):
        frameW = self.winfo_width()
        scrollerW = frameW - 2 * self.scrollerWidth
        X = self.screenX1 + (event.x - self.pullBeginX) / (scrollerW / self.spaceWidth)
        X = max(0, X)
        X = min(X, self.spaceWidth - frameW)
        self.setX(X)

    def pullEnd(self, event):
        self.scroller.bind("<Motion>", self.nothing)

    def nothing(self, *args):
        return args

    def wheelEvent(self, event):
        frameW = self.winfo_height()
        X = self.screenX1 + event.delta
        X = max(0, X)
        X = min(X, self.spaceWidth - frameW)
        self.setX(X)

class MyFrameXY(Frame):
    def __init__(self, master, spaceHeight, spaceWidth, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self._imageButtonU = PhotoImage(file="tk/assets/buttonU.png")
        self._imageButtonD = PhotoImage(file="tk/assets/buttonD.png")
        self._imageButtonL = PhotoImage(file="tk/assets/buttonL.png")
        self._imageButtonR = PhotoImage(file="tk/assets/buttonR.png")
        self._imageSide = PhotoImage(file="tk/assets/side.png")

        self.frame = FrameDark(self, height=spaceHeight, )
        self.frame.place(x=0, y=0, height=spaceHeight, width=spaceWidth)

        self.scrollerFrameY = Frame(self)
        self.buttonU = Button(self.scrollerFrameY, image=self._imageButtonU, bd=0, command=self.buttonU_Command)
        self.buttonD = Button(self.scrollerFrameY, image=self._imageButtonD, bd=0, command=self.buttonD_Command)
        self.scrollerY = Label(self.scrollerFrameY, bg="#aaa")

        self.scrollerFrameX = Frame(self)
        self.buttonR = Button(self.scrollerFrameX, image=self._imageButtonL, bd=0, command=self.buttonR_Command)
        self.buttonL = Button(self.scrollerFrameX, image=self._imageButtonR, bd=0, command=self.buttonL_Command)
        self.scrollerX = Label(self.scrollerFrameX, bg="#aaa")

        self.sideRect = Label(self, image=self._imageSide)

        # 滚动条宽度
        self.scrollerWidth = 20
        # 使用按钮操作的步长
        self.step = 20

        self.screenY1 = 0
        self.screenY2 = 0
        self.screenX1 = 0
        self.screenX2 = 0
        self.spaceHeight = spaceHeight
        self.spaceWidth = spaceWidth

        self.bind("<MouseWheel>", self.wheelEvent)
        self.frame.bind("<MouseWheel>", self.wheelEvent)
        self.bind("<Configure>", self.configureEvent)
        self.scrollerY.bind("<Enter>", self.scrollerYEnter)
        self.scrollerY.bind("<Leave>", self.scrollerYLeave)
        self.scrollerY.bind("<Button-1>", self.pullYBegin)
        self.scrollerY.bind("<ButtonRelease-1>", self.pullYEnd)
        self.scrollerX.bind("<Enter>", self.scrollerXEnter)
        self.scrollerX.bind("<Leave>", self.scrollerXLeave)
        self.scrollerX.bind("<Button-1>", self.pullXBegin)
        self.scrollerX.bind("<ButtonRelease-1>", self.pullXEnd)

    def configureEvent(self, *args):
        frameH = self.winfo_height()
        frameW = self.winfo_width()
        scrollerH = frameH - 3 * self.scrollerWidth
        scrollerW = frameW - 3 * self.scrollerWidth

        self.screenY2 = self.screenY1 + frameH
        if self.screenY2 * (scrollerH / self.spaceHeight) > scrollerH and frameH < self.spaceHeight:
            self.screenY1 = self.spaceHeight - frameH
            self.frame.place(y=-self.screenY1)
        if frameH < self.spaceHeight:
            y1 = self.screenY1 * (scrollerH / self.spaceHeight)
            y2 = self.screenY2 * (scrollerH / self.spaceHeight)
            self.scrollerFrameY.place(x=frameW-self.scrollerWidth, y=0, width=self.scrollerWidth, height=frameH)    
            self.buttonU.place(x=0, y=0, width=self.scrollerWidth, height=self.scrollerWidth)
            self.buttonD.place(x=0, y=frameH-self.scrollerWidth*2, width=self.scrollerWidth, height=self.scrollerWidth)
            self.scrollerY.place(x=(self.scrollerWidth-8)/2, y=y1+self.scrollerWidth, width=8, height=(y2-y1))
        else:
            self.scrollerFrameY.place(x=frameW, y=0, width=self.scrollerWidth, height=frameH)
        
        self.screenX2 = self.screenX1 + frameW
        if self.screenX2 * (scrollerW / self.spaceWidth) > scrollerW and frameW < self.spaceWidth:
            self.screenX1 = self.spaceWidth - frameW
            self.frame.place(x=-self.screenX1)
        if frameW < self.spaceWidth:
            x1 = self.screenX1 * (scrollerW / self.spaceWidth)
            x2 = self.screenX2 * (scrollerW / self.spaceWidth)
            self.scrollerFrameX.place(x=0, y=frameH-self.scrollerWidth, width=frameW, height=self.scrollerWidth)
            self.buttonR.place(x=0, y=0, width=self.scrollerWidth, height=self.scrollerWidth)
            self.buttonL.place(x=frameW-self.scrollerWidth*2, y=0, width=self.scrollerWidth, height=self.scrollerWidth)
            self.scrollerX.place(x=x1+self.scrollerWidth, y=(self.scrollerWidth-8)/2, width=(x2-x1), height=8)
        else:
            self.scrollerFrameX.place(x=0, y=frameH, width=frameW, height=self.scrollerWidth)

        self.sideRect.place(x=frameW-self.scrollerWidth, y=frameH-self.scrollerWidth, width=self.scrollerWidth, height=self.scrollerWidth)

    def scrollerYEnter(self, *args):
        self.scrollerY.config(bg="#ccc")

    def scrollerYLeave(self, *args):
        self.scrollerY.config(bg="#aaa")

    def scrollerXEnter(self, *args):
        self.scrollerX.config(bg="#ccc")

    def scrollerXLeave(self, *args):
        self.scrollerX.config(bg="#aaa")

    def setY(self, y):
        self.screenY1 = y
        self.frame.place(y=-self.screenY1)
        self.configureEvent()

    def setX(self, x):
        self.screenX1 = x
        self.frame.place(x=-self.screenX1)
        self.configureEvent()

    def buttonU_Command(self):
        self.screenY1 = max(self.screenY1 - self.step, 0)
        self.setY(self.screenY1)

    def buttonD_Command(self):
        frameH = self.winfo_height()
        self.screenY1 = min(self.spaceHeight - frameH, self.screenY1 + self.step)
        self.setY(self.screenY1)

    def buttonL_Command(self):
        self.screenX1 = max(self.screenX1 - self.step, 0)
        self.setX(self.screenX1)

    def buttonR_Command(self):
        frameW = self.winfo_width()
        self.screenX1 = min(self.spaceWidth - frameW, self.screenX1 + self.step)
        self.setX(self.screenX1)

    def pullYBegin(self, event):
        self.pullBeginY = event.y
        self.scrollerY.bind("<Motion>", self.pullYMotion)

    def pullYMotion(self, event):
        frameH = self.winfo_height()
        scrollerH = frameH - 2 * self.scrollerWidth
        Y = self.screenY1 + (event.y-self.pullBeginY) / (scrollerH / self.spaceHeight)
        Y = max(0, Y)
        Y = min(Y, self.spaceHeight - frameH)
        self.setY(Y)

    def pullYEnd(self, event):
        self.scrollerY.bind("<Motion>", self.nothing)

    def pullXBegin(self, event):
        self.pullBeginX = event.x
        self.scrollerX.bind("<Motion>", self.pullXMotion)

    def pullXMotion(self, event):
        frameW = self.winfo_width()
        scrollerW = frameW - 2 * self.scrollerWidth
        X = self.screenX1 + (event.x - self.pullBeginX) / (scrollerW / self.spaceWidth)
        X = max(0, X)
        X = min(X, self.spaceWidth - frameW)
        self.setX(X)

    def pullXEnd(self, event):
        self.scrollerX.bind("<Motion>", self.nothing)

    def nothing(self, *args):
        return args

    def wheelEvent(self, event):
        frameH = self.winfo_height()
        Y = self.screenY1 - event.delta
        Y = max(0, Y)
        Y = min(Y, self.spaceHeight - frameH)
        self.setY(Y)

class LabelFramePlayer(LabelFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.bind("<Configure>", self.changeWidth)

    def changeWidth(self, event):
        self.after(100, self.callback)

    def callback(self):
        _height = self.winfo_height()
        _width = _height * 4 / 3
        self.config(width=_width)


class LabelFrameDark(LabelFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#222", fg="#ddd")

class FrameDark(Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#222")

class ButtonDark(Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#222", fg="#ddd")

class LabelDark(Label):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#222", fg="#ddd")

class CanvasDark(Canvas):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#222", bd=0)

class EntryDark(Entry):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#333", fg="#ddd", bd=0,)
        self.bind("<Enter>", self.enterEvent)
        self.bind("<Leave>", self.leaveEvent)

    def enterEvent(self, event):
        self.config(bg="#444", fg="#eee", bd=0,)

    def leaveEvent(self, event):
        self.config(bg="#333", fg="#ddd", bd=0,)

    def setValue(self, value):
        self.delete("0", END)
        self.insert(END, value)
        return self

class EntryFloatDark(EntryDark):
    def getFloat(self):
        return float(self.get())

class EntryIntDark(EntryDark):
    def getInt(self):
        return int(self.get())

class EntryStrDark(EntryDark):
    def getStr(self):
        return self.get()


class ButtonDark(Button):
    def __init__(self, master, state=False, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.config(bg="#333", fg="#ddd", bd=0,)
        self.bind("<Enter>", self.enterEvent)
        self.bind("<Leave>", self.leaveEvent)
        self.state = None
        self.setState(state)

    def setState(self, state=None):
        if state is None:
            self.state = not self.state
        else:
            self.state = state
        if self.state:
            self.config(bg="#fff", fg="#444")
        else:
            self.config(bg="#333", fg="#ddd")

    def enterEvent(self, event):
        if self.state:
            self.config(bg="#eee", fg="#333")
        else:
            self.config(bg="#444", fg="#eee")

    def leaveEvent(self, event):
        if self.state:
            self.config(bg="#fff", fg="#444")
        else:
            self.config(bg="#333", fg="#ddd")


if __name__ == '__main__':
    root = Tk()
    root.geometry("400x200")
    mf1 = MyFrameXY(root, 600, 1000)
    mf1.pack(expand=True, fill=BOTH)

    for y in range(0, 1000, 50):
        Label(mf1.frame, text=str(y)).place(x=y, y=0, width=60)
        Label(mf1.frame, text=str(y)).place(x=0, y=y, width=60)

    mainloop()