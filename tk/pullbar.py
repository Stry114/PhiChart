from tkinter import *
from tk.mytk import *
import time


theme_color = "#fff"
basic_color = "#333"
front_color = "#444"
basic_font_color = "black"
active_font_color = "white"


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
        self.obj0.build(0, 0, w-2*self.height, h)
        self.obj1.build(w-2*self.height, 0, self.height, h, self.left_function)
        self.obj2.build(w-1*self.height, 0, self.height,
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
        self.objs = []

    def build(self, x, y, w, h, objs=("LiRadiobox",), value=0):
        index = 0
        h = max(18*len(objs), h)
        height = h/len(objs)
        for obj in objs:
            this = LiCheckbox(self)
            this.build(0, index*height, w, height, obj, False, self.func)
            self.objs.append(this)
            index += 1
        self.place(x=x, y=y, width=w, height=h)
        self.objs[value].setvalue(True)
        return self

    def func(self):
        for i in self.objs:
            i.setvalue(False)
            i.Leave_function()

    def get(self):
        index = 0
        for i in self.objs:
            if i.value:
                return index
            index += 1


class LiToolBotton(Frame):
    def __init__(self, *args, fg=None):
        super().__init__(*args)
        self.obj0 = ButtonDark(self, bg=basic_color, bd=0)
        # self.obj1 = Button(self, anchor="w", bd=0, bg="#222", fg="#ddd")

        if fg is not None:
            self.active_fg = fg
            self.default_fg = fg
        else:
            self.active_fg = front_color
            self.default_fg = theme_color

    def build(self, x, y, w=100, h=20, text="LiCheckbox", value=False, command=Nothing, fg=None):

        w = max(20, w)
        self.value = value
        self.command = command
        self.obj0.config(text=text)
        self.place(x=x, y=y, width=w, height=h)
        self.obj0.place(x=0, y=0, width=w, height=h)
        self.obj0.config(command=self.Button1_function)
        self.obj0.bind("<Enter>", self.Enter_function)
        self.obj0.bind("<Leave>", self.Leave_function)
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
            self.obj0.config(fg=self.active_fg)
        else:
            self.obj0.config(bg=front_color)
            self.obj0.config(fg=self.default_fg)

    def get(self):
        return self.value

class LiToolbox(LiRadiobox):
    def __init__(self, *args):
        super().__init__(*args)
        self.objs = []

    def build(self, x, y, w, h, objs=("LiToolbox",), colors=None, value=0):
        index = 0
        w = max(18*len(objs), w)
        width = int(w/len(objs))
        for obj in objs:
            color = colors[index] if colors is not None else None
            this = LiToolBotton(self, fg=color)
            this.build(index*width, 0, width, h, obj, False, self.func)
            self.objs.append(this)
            index += 1
        self.place(x=x, y=y, width=w, height=h)
        self.objs[value].setvalue(True)
        return self

class LiToolboxY(LiRadiobox):
    def __init__(self, *args):
        super().__init__(*args)
        self.objs = []

    def build(self, x, y, w, h, objs=("LiToolbox",), value=0):
        index = 0
        h = max(18*len(objs), h)
        height = h/len(objs)
        for obj in objs:
            this = LiToolBotton(self)
            this.build(0, index*height, w, height, obj, False, self.func)
            self.objs.append(this)
            index += 1
        self.place(x=x, y=y, width=w, height=h)
        self.objs[value].setvalue(True)
        return self

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
    def __init__(self, father: Label, text="Tooltip"):
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
        self.this = Label(self.master, text=self.text)
        self.this.place(x=self.x, y=self.y)

    def leave_function(self, *args):
        self.this.destroy()


if __name__ == "__main__":
    top = Tk()
    a1 = LiButton(top).build(20, 20)
    mainloop()
