from tkinter import *
from tk.mytk import *
from tkinter import font
import time
import tk.color255 as c255

theme_color = "#fff"
basic_color = "#333"
front_color = "#444"
basic_font_color = "black"
active_font_color = "white"

themeColorObj = c255.Color(theme_color)
basicColorObj = c255.Color(basic_color)
frontColorObj = c255.Color(front_color)


def Nothing(*arg): return ...


def TestFunc(*arg): print(time.time())


class LiButton(Button):
    def build(self, x, y, w=80, h=20, command=Nothing):
        self.config(bd=0)
        self.config(command=command)
        self.config(activeforeground=active_font_color)
        self.config(activebackground=theme_color)
        self.place(x=x, y=y, width=w, height=h)
        self.bind("<Enter>", self.Enter_function)
        self.bind("<Leave>", self.Leave_function)
        self.command = command
        self.Leave_function()
        return self

    def Enter_function(self, *args):
        self.config(bg=front_color)

    def Leave_function(self, *args):
        self.config(bg=basic_color)


class LiLabel(Label):
    def build(self, x, y, text, anchor="w", fg="black"):
        self.place(x=x, y=y)
        self.config(fg=fg)
        self.config(text=text)
        self.config(anchor=anchor)
        return self

    def text(self, text):
        self.config(text=str(text))


class LiEntry(Entry):
    def build(self, x, y, w=80, h=20, value=""):
        self.config(bd=0)
        self.setvalue(value)
        self.Leave_function()
        self.place(x=x, y=y, width=w, height=h)
        self.bind("<Enter>", self.Enter_function)
        self.bind("<Leave>", self.Leave_function)
        return self

    def Enter_function(self, *args):
        self.config(bg=front_color)

    def Leave_function(self, *args):
        self.config(bg=basic_color)

    def setvalue(self, value):
        self.delete("0", "end")
        self.insert("0", str(value))


class LiFloatEntry(Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.obj0 = LiEntry(self)
        self.obj1 = LiButton(self, text="◀")
        self.obj2 = LiButton(self, text="▶")

    def build(self, x, y, w=120, h=20, value=0., step=1):
        w = max(60, w)
        self.step = step
        self.height = min(25, h)
        self.place(x=x, y=y, width=w, height=h)
        self.obj0.build(0, 0, w - 2 * self.height, h)
        self.obj1.build(w - 2 * self.height, 0, self.height, h, self.left_function)
        self.obj2.build(w - 1 * self.height, 0, self.height,
                        h, self.right_function)
        self.setvalue(value)
        return self

    def right_function(self, *args):
        try:
            value = float(self.obj0.get())
            value = round(value + self.step, 10)
            self.setvalue(value)
        except:
            self.setvalue(0)

    def left_function(self, *args):
        try:
            value = float(self.obj0.get())
            value = round(value - self.step, 10)
            self.setvalue(value)
        except:
            self.setvalue(0)

    def setvalue(self, value: float):
        self.obj0.delete("0", "end")
        self.obj0.insert("0", value)

    def get(self):
        return eval(self.obj0.get())


class LiCheckbox(FrameDark):
    def __init__(self, *args):
        super().__init__(*args)
        self.obj0 = ButtonDark(self, bg=basic_color, bd=0)
        self.obj1 = Button(self, anchor="w", bd=0, bg="#222", fg="#ddd")

    def build(self, x, y, w=100, h=20, text="LiCheckbox", value=False, command=Nothing):
        w = max(60, w)
        self.value = value
        self.command = command
        self.obj1.config(text=text)
        self.place(x=x, y=y, width=w, height=h)
        self.obj0.place(x=0, y=6, width=12, height=12)
        self.obj1.place(x=12, y=0)
        self.obj0.config(command=self.Button1_function)
        self.obj1.config(command=self.Button1_function)
        self.obj0.bind("<Enter>", self.Enter_function)
        self.obj0.bind("<Leave>", self.Leave_function)
        self.obj1.bind("<Enter>", self.Enter_function)
        self.obj1.bind("<Leave>", self.Leave_function)
        self.Leave_function()
        return self

    def Enter_function(self, *args):
        if self.value:
            self.obj0.config(bg=theme_color)
        else:
            self.obj0.config(bg=front_color)

    def Leave_function(self, *args):
        if self.value:
            self.obj0.config(bg=theme_color)
        else:
            self.obj0.config(bg=basic_color)

    def Button1_function(self, *args):
        self.command()
        self.setvalue(not self.value)

    def setvalue(self, value: bool):
        self.value = value
        if self.value:
            self.obj0.config(bg=theme_color)
        else:
            self.obj0.config(bg=front_color)

    def get(self):
        return self.value


class LiRadiobox(FrameDark):
    def __init__(self, *args):
        super().__init__(*args)
        self.objs: list[LiCheckbox] = []
        self.command = Nothing

    def build(self, x, y, w, h, objs=("LiRadiobox",), value=0, command=Nothing):
        index = 0
        h = max(18 * len(objs), h)
        height = h / len(objs)
        for obj in objs:
            this = LiCheckbox(self)
            this.build(0, index * height, w, height, obj, False, self.func)
            self.objs.append(this)
            index += 1
        self.place(x=x, y=y, width=w, height=h)
        self.objs[value].setvalue(True)
        self.command = command
        return self

    def func(self):
        for i in self.objs:
            i.setvalue(False)
            i.Leave_function()
        self.command(self.get())

    def get(self):
        index = 0
        for i in self.objs:
            if i.value:
                return index
            index += 1

    def set(self, value):
        self.objs[value].Button1_function()


class LiToolBotton(Frame):
    def __init__(self, master, text, value, command=Nothing, fg=None, *args):
        super().__init__(master, *args)
        self.obj0 = ButtonDark(self, bg=basic_color, bd=0, text=text, cursor="hand2")
        self.obj0.pack(side=TOP, fill=BOTH, expand=True)
        self.obj0.config(command=self.Button1_function)
        self.value = value
        self.command = command

        if fg is not None:
            self.active_fg = fg
            self.default_fg = fg
        else:
            self.active_fg = front_color
            self.default_fg = theme_color

        self.obj0.bind("<Enter>", self.Enter_function)
        self.obj0.bind("<Leave>", self.Leave_function)
        self.setvalue(value)

    def Enter_function(self, *args):
        if self.value:
            self.obj0.config(bg=theme_color)
        else:
            self.obj0.config(bg=front_color)

    def Leave_function(self, *args):
        if self.value:
            self.obj0.config(bg=theme_color)
        else:
            self.obj0.config(bg=basic_color)

    def Button1_function(self, *args):
        self.setvalue(not self.value)
        self.command()

    def setvalue(self, *args, value: bool = None):
        self.value = value if value else not self.value
        if self.value:
            self.obj0.config(bg=theme_color)
            self.obj0.config(fg=self.active_fg)
        else:
            self.obj0.config(bg=front_color)
            self.obj0.config(fg=self.default_fg)

    def get(self):
        return self.value


class LiToolBox(FrameDark):
    class LiToolBoxButton(Label):
        def __init__(self, master: "LiToolBox", index: int, text: str, activeColor=theme_color, *args):
            super().__init__(master, text=text, anchor="center", *args)
            self.index = index
            self.master: "LiToolBox" = master

            activeColor = activeColor if activeColor is not None else theme_color
            self.activeFG = c255.Color(activeColor)
            self.activeBG = self.activeFG.mix(frontColorObj, 1, 1.5)
            self.normalBG = self.activeFG.mix(basicColorObj, 1, 1.5)

            self.config(fg=self.activeFG.toRRGGBB())
            self.bind("<Enter>", self.enterEvent)
            self.bind("<Leave>", self.leaveEvent)
            self.bind("<Button-1>", self.clickedEvent)

        def enterEvent(self, *e):
            if self.master.index == self.index:
                self.config(bg=self.activeBG.toRRGGBB())
            else:
                self.config(bg=front_color)

        def leaveEvent(self, *e):
            if self.master.index == self.index:
                self.config(bg=self.normalBG.toRRGGBB())
            else:
                self.config(bg=basic_color)

        def clickedEvent(self, *e):
            self.master.set(self.index)

    def __init__(self, master, texts: tuple, colors: tuple, command=Nothing, *args):
        super().__init__(master, *args)
        self.objs = []
        self.index = 0
        self.master = master
        self.command = command

        self.texts = texts
        self.colors = colors

        # 动画条
        self.begin = 0
        self.scrollIndex = 0

    def build(self, x, y, w, h):
        self.w = w
        buttomWidth = w / len(self.texts)
        for i in range(len(self.texts)):
            this = self.LiToolBoxButton(self, i, text=self.texts[i], activeColor=self.colors[i])
            this.place(x=i * buttomWidth, y=0, width=buttomWidth, height=h)
            this.leaveEvent()
            self.objs.append(this)

        self.scroll = Frame(self)
        self.scroll.place(x=0, y=h - 3, height=3, width=buttomWidth)
        self.place(x=x, y=y, width=w, height=h)
        self.scrollLoop()

        return self

    def get(self):
        return self.index

    def set(self, value):
        self.begin = self.index
        self.index = value
        for obj in self.objs:
            obj.leaveEvent()
        self.command(value)

        self.scrollIndex = 0
        self.scrollLoop()

    def scrollLoop(self):
        if self.scrollIndex < 16:
            self.scrollIndex += 1
            self.after(10, self.scrollLoop)

        i = self.scrollIndex / 16
        buttomWidth = self.w / len(self.texts)
        color = self.objs[self.begin].activeFG.mix(self.objs[self.index].activeFG, 1 - i, i)
        x = (i * (self.index - self.begin) + self.begin) * buttomWidth
        self.scroll.place(x=x)
        self.scroll.config(bg=color.toRRGGBB())


class LiPullbar(Frame):
    def __init__(self, *args):
        super().__init__(*args)
        self.obj0 = Label(self, anchor="w", bg=basic_color)
        self.obj1 = Label(self, anchor="w", bg=theme_color)

    def build(self, x, y, w=100, h=20, value=0.3, command=Nothing):
        self.state = True
        self.total_width = w
        self.value_width = 0
        self.command = command
        self.place(x=x, y=y, width=w, height=h)
        self.obj0.place(x=0, y=0, width=self.total_width, height=h)
        self.obj1.place(x=0, y=0, width=self.value_width, height=h)
        self.obj0.bind("<ButtonRelease-1>", self.Release_function)
        self.obj1.bind("<ButtonRelease-1>", self.Release_function)
        self.obj0.bind("<Button-1>", self.Button1_function)
        self.obj1.bind("<Button-1>", self.Button1_function)
        self.obj0.bind("<Enter>", self.Enter_function)
        self.obj1.bind("<Enter>", self.Enter_function)
        self.obj0.bind("<Leave>", self.Leave_function)
        self.obj1.bind("<Leave>", self.Leave_function)
        self.setvalue(value)
        return self

    def setvalue(self, value):
        self.value = value
        self.value_width = max(self.total_width * self.value - 1, 0)
        self.obj1.place(width=self.value_width)

    def Button1_function(self, event):
        self.obj0.bind("<Motion>", self.Motion_function)
        self.obj1.bind("<Motion>", self.Motion_function)
        self.Motion_function(event)

    def Release_function(self, event):
        self.obj0.bind("<Motion>", Nothing)
        self.obj1.bind("<Motion>", Nothing)
        self.Motion_function(event)
        self.command()

    def Enter_function(self, *args):
        self.obj0.config(bg=front_color)

    def Leave_function(self, *args):
        self.obj0.config(bg=basic_color)

    def Motion_function(self, event):
        self.value_width = event.x - 1
        self.obj1.place(width=self.value_width)
        self.value = self.value_width / self.total_width
        self.Enter_function()


class Tooltip:
    def __init__(self, father: Widget, text="Tooltip"):
        self.father = father
        self.master = father.master
        self.mas_geo = father.winfo_geometry()
        self.mas_geo = self.mas_geo.replace("x", "+")
        self.mas_geo = self.mas_geo.split("+")

        self.x, self.y = float(self.mas_geo[2]), float(self.mas_geo[3])
        self.w, self.h = float(self.mas_geo[0]), float(self.mas_geo[1])
        self.text = text
        self.father.bind("<Enter>", self.enter_function)
        self.father.bind("<Leave>", self.leave_function)

    def enter_function(self, *args):
        print(self.h, self.y)
        self.this = Label(self.master, text=self.text, justify='left')
        self.this.place(x=self.x, y=self.y)

    def leave_function(self, *args):
        self.this.destroy()


class LiButtonDark(Frame):
    def __init__(self, master, text, command, height=1, var=0, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.textLabel = Label(self, anchor="center", text=text, height=height)
        self.textLabel.pack(fill=BOTH, expand=True)
        self.command = command
        self.text = text
        self.var = var

        self.scrollIndex = 0
        self.scrollTarget = 0
        self.scroll = Frame(self)

        self.textLabel.bind("<Enter>", self.enterEvent)
        self.textLabel.bind("<Leave>", self.leaveEvent)
        self.textLabel.bind("<Button-1>", self.clickEvent)
        self.textLabel.bind("<ButtonRelease-1>", self.enterEvent)
        self.leaveEvent(0)

    def clickEvent(self, event):
        self.command(self.var)
        self.textLabel.config(bg=theme_color)
        self.textLabel.config(fg=basic_color)

    def enterEvent(self, event):
        self.textLabel.config(bg=front_color)
        self.textLabel.config(fg=theme_color)
        self.startScrollLoop(10)

    def leaveEvent(self, event):
        self.textLabel.config(bg=basic_color)
        self.textLabel.config(fg=theme_color)
        self.startScrollLoop(0)

    def scrollLoop(self, *args):
        if self.scrollIndex == self.scrollTarget:
            pass
        else:
            self.scrollIndex += (self.scrollTarget - self.scrollIndex) / abs(self.scrollTarget - self.scrollIndex)
            self.after(10, self.scrollLoop)

        w = self.winfo_width()
        h = self.winfo_height()
        if self.scrollIndex == 0:
            self.scroll.place(x=-w)
        else:
            xn = (10 - self.scrollIndex) / 20 * w
            wn = int(self.scrollIndex / 10 * w)
            self.scroll.place(x=xn, y=h - 3, width=wn, height=h)

    def startScrollLoop(self, target):
        if self.scrollIndex == self.scrollTarget:
            self.after(10, self.scrollLoop)
        self.scrollTarget = target

    def destroy(self):
        self.scroll.destroy()
        self.textLabel.destroy()
        super().destroy()


def validate_integer(action, value_if_allowed):
    # action 1 表示插入，0 表示删除，-1 表示其他操作
    if action == '1':  # 插入操作
        # 允许空值
        if value_if_allowed == "":
            return True

        # 允许单独的负号
        if value_if_allowed == "-":
            return True

        # 检查是否为有效的整数格式（负号开头且后面跟数字）
        if value_if_allowed.startswith("-"):
            # 去掉负号后检查剩余部分是否为数字
            return value_if_allowed[1:].isdigit()
        else:
            # 纯数字检查
            return value_if_allowed.isdigit()

    return True  # 其他操作（如删除）都允许


class LiIntEntryDark(FrameDark):
    def __init__(self, master, defaultValue=0, step=1, command=Nothing, height=1, var=0, min=float("-inf"), max=float("inf"), *args, **kwargs):

        vcmd = master.register(validate_integer)

        super().__init__(master, *args, **kwargs)
        self.et1 = Entry(self, bg="#333", bd="0", validate="key", validatecommand=(vcmd, '%d', '%P'), width=5)
        self.et1.pack(side=LEFT, fill=BOTH, expand=True)
        self.bt2 = ButtonDark(self, text=">", command=self.add, width=2, height=height)
        self.bt2.pack(side=RIGHT, fill=Y)
        self.bt1 = ButtonDark(self, text="<", command=self.min, width=2, height=height)
        self.bt1.pack(side=RIGHT, fill=Y)
        self.et1.insert(END, str(defaultValue))
        self.defaultValue = defaultValue
        self.command = command
        self.step = step
        self.var = var
        self.minValue = min
        self.maxValue = max

        self.et1.config(insertbackground="#fff", fg="#ddd")
        self.et1.bind("<Enter>", self.Enter_function)
        self.et1.bind("<Leave>", self.Leave_function)
        self.et1.bind("<KeyRelease>", self.callback)
        self.et1.bind("<MouseWheel>", self.on_WheelEvent)
        self.et1.bind("<Return>", self.on_enter_press)

    def on_enter_press(self, event):
        self.master.focus_set()
        # 返回"break"阻止事件继续传播
        return "break"

    def setValue(self, value: int):
        self.et1.delete(0, END)
        self.et1.insert(0, str(value))
        self.callback()

    def callback(self, *args):
        self.command(self.var)

    def min(self, *args):
        if self.et1.get() != "":
            value = int(float(self.et1.get()))
        else:
            value = self.defaultValue
        value -= self.step
        value = round(min(self.maxValue, max(self.minValue, value)))
        self.setValue(value)

    def add(self, *args):
        if self.et1.get() != "":
            value = int(float(self.et1.get()))
        else:
            value = self.defaultValue
        value += self.step
        value = round(min(self.maxValue, max(self.minValue, value)))
        self.setValue(value)

    def Enter_function(self, *args):
        self.et1.config(bg="#444")

    def Leave_function(self, *args):
        self.et1.config(bg="#333")

    def on_WheelEvent(self, event):
        if event.delta > 0:
            self.add()
        else:
            self.min()

    def get(self):
        return self.et1.get()

    def getValue(self):
        if self.et1.get() != "":
            value = int(float(self.et1.get()))
            value = round(min(self.maxValue, max(self.minValue, value)))
        else:
            value = self.defaultValue
        return value

def validate_float(action, value_if_allowed):
    # 允许删除操作
    if action != '1':  # 不是插入操作
        return True

    # 允许空值
    if value_if_allowed == "":
        return True

    # 允许单独的负号
    if value_if_allowed == "-":
        return True

    # 允许单独的小数点
    if value_if_allowed == ".":
        return True

    # 检查是否为有效的浮点数格式
    try:
        # 尝试将输入转换为浮点数
        float(value_if_allowed)
        # 检查是否有多个小数点
        if value_if_allowed.count('.') > 1:
            return False
        # 检查是否有多个负号或负号不在开头
        if value_if_allowed.count('-') > 1 or (
                value_if_allowed.count('-') == 1 and not value_if_allowed.startswith('-')):
            return False
        return True
    except ValueError:
        return False


class LiFloatEntryDark(LiIntEntryDark):
    def __init__(self, master, defaultValue: float = 0.0, step=1, command=Nothing, height=1, var=0, *args, **kwargs):
        super().__init__(master, command=command, height=height, var=var, *args, **kwargs)
        vcmd = master.register(validate_float)
        self.et1.config(validate="key", validatecommand=(vcmd, '%d', '%P'))

        self.defaultValue = defaultValue
        self.et1.insert(END, str(defaultValue))
        self.step = step

    def setValue(self, value: float):
        self.et1.delete(0, END)
        self.et1.insert(0, str(value))
        self.callback()

    def callback(self, *args):
        self.command(self.var)

    def min(self, *args):
        if self.et1.get() != "":
            value = int(float(self.et1.get()))
        else:
            value = self.defaultValue
        value -= self.step
        value = float(min(self.maxValue, max(self.minValue, value)))
        self.setValue(value)

    def add(self, *args):
        if self.et1.get() != "":
            value = int(float(self.et1.get()))
        else:
            value = self.defaultValue
        value += self.step
        value = float(min(self.maxValue, max(self.minValue, value)))
        self.setValue(value)

    def getValue(self):
        if self.et1.get() != "":
            value = int(float(self.et1.get()))
            value = float(min(self.maxValue, max(self.minValue, value)))
        else:
            value = self.defaultValue
        return value


class LiIntLabelEntryDark(FrameDark):
    def __init__(self, master, text, defaultValue=0, step=1, command=Nothing, height=1, var=0, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.lb1 = LabelDark(self, text=text, anchor=W)
        self.lb1.pack(side=TOP, fill=X)
        self.et1 = LiIntEntryDark(self, defaultValue=defaultValue, step=step, command=command, height=height, var=var,
                                  *args, **kwargs)
        self.et1.pack(side=BOTTOM, fill=BOTH, expand=True)


class LiFloatLabelEntryDark(FrameDark):
    def __init__(self, master, text, defaultValue=0.0, step=1, command=Nothing, height=1, var=0, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.lb1 = LabelDark(self, text=text, anchor=W)
        self.lb1.pack(side=TOP, fill=X)
        self.et1 = LiFloatEntryDark(self, defaultValue=defaultValue, step=step, command=command, height=height, var=var,
                                    *args, **kwargs)
        self.et1.pack(side=BOTTOM, fill=BOTH, expand=True)


if __name__ == "__main__":
    top = Tk()
    a1 = LiFloatEntryDark(top, command=print)
    a1.pack(side=TOP, fill=BOTH, expand=True)
    mainloop()
