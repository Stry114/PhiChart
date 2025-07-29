from tkinter import *
from mytk import *
from pygame import mixer


# 暂停
doPause = False


class marker:
    def __init__(self, master):

        self.top = Toplevel(master)
        self.top.geometry('600x200')
        self.top.resizable(False, False)
        self.top.configure(bg='#222')

        self.pic_pause = PhotoImage(file='assets/pause.png')
        self.pic_space = PhotoImage(file='../assets/space.png')
        self.pic_play = PhotoImage(file='assets/play.png')

        self.bt1 = Label(self.top, bd=0, image=self.pic_play, bg="#333")
        self.bt1.place(x=20, y=20, width=40, height=40)
        self.bt1.bind("<Button-1>", self.pause)

        self.bt2 = Label(self.top, bd=0, image=self.pic_space, bg="#333")
        self.bt2.place(x=70, y=20, width=100, height=40)
        self.bt2.bind("<Button-1>", self.mark)

        self.doPause = False

    def pause(self, *event, value=None):
        print(value)
        if value is None:
            self.doPause = not self.doPause
        else:
            self.doPause = value
        if self.doPause:
            self.bt1.configure(image=self.pic_pause)
        else:
            self.bt1.configure(image=self.pic_play)


    def mark(self, *event):
        pass


if __name__ == '__main__':

    root = Tk()
    root.geometry('100x100+800+800')
    a = marker(root, )

    mainloop()