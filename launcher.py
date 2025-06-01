from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import threading
import traceback

import pygame

import player
from libs.toolTip import ToolTip
from player import Player
from autoMatch import Matcher

top = Tk()
top.title("PhiChart Launcher")
top.minsize(width=400, height=500)
top.config(padx=20, pady=20)

def setEntry(entry: ttk.Entry, string: str):
    entry.delete(0, END)
    entry.insert(0, string)

def openDir(*args):
    directory = filedialog.askdirectory(initialdir="charts/", title="打开目录")
    if directory == "" or directory is None:
        return

    matcher = Matcher(directory)
    setEntry(lb1et1, matcher.chartFile)
    setEntry(lb1et2, matcher.audioFile)
    setEntry(lb1et3, matcher.illuFile)


def runningThread():

    try:
        assert lb2et1.get() != "", "未填写窗口分辨。"
        assert lb2et2.get() != "", "未填写窗口分辨。"
        player = Player(w=int(lb2et1.get()), h=int(lb2et2.get()))

        assert lb1et1.get() != "", "未填写谱面文件。"
        assert lb1et2.get() != "", "未填写音频文件。"
        assert lb1et3.get() != "", "未填写曲绘文件。"
        player.chartFile = lb1et1.get()
        player.audioFile = lb1et2.get()
        player.illuFile = lb1et3.get()

        assert lb1et4.get() != "", "未填写副标题。"
        assert lb1et5.get() != "", "未填写曲名。"
        assert lb1et6.get() != "", "未填写难度。"
        player.subtitle = lb1et4.get()
        player.name = lb1et5.get()
        player.level = lb1et6.get()

        if lb2et3.get() != "":
            player.noteSize = int(lb2et3.get())
        if lb2et4.get() != "":
            player.hitEffectSize = int(lb2et4.get())
        if lb3et1.get() != "":
            player.fps = int(lb3et1.get())
        if lb3et2.get() != "":
            player.chartDelay = float(lb3et2.get())
        if lb3et3.get() != "":
            player.background_brightness = float(lb3et3.get())
        if lb3et4.get() != "":
            player.background_blurRadius = int(lb3et4.get())
        if lb3int1.get() == 1:
            player.displayUI = False
        if lb3int2.get() == 1:
            player.displayDebug = True

        if lb4int1.get() == 1:
            player.enableMapping = True

            if lb4et1.get() != "":
                centerX = int(lb4et1.get())
            else:
                centerX = int(player.width / 2)
            if lb4et2.get() != "":
                centerY = int(lb4et2.get())
            else:
                centerY = int(player.height / 2)
            if lb4et3.get() != "":
                scale = float(lb4et3.get())
            else:
                scale = 0.2
            x1 = round(centerX - player.width * scale * 0.5)
            x2 = round(centerX + player.width * scale * 0.5)
            y1 = round(centerY - player.height * scale * 0.5)
            y2 = round(centerY + player.height * scale * 0.5)
            player.targetRectOfMapping = (x1, y1, x2, y2)




        player.initPlayer()
        player.mainloop()

    except AssertionError as e:
        messagebox.showerror("PhiChart", str(e))
        return
    except ValueError as e:
        messagebox.showerror("PhiChart", "参数不合法。\n"+traceback.format_exc())
        return
    except Exception as e:
        messagebox.showerror("PhiChart", traceback.format_exc())
        return
    finally:
        pygame.quit()

def launch(*args):
    if player.running:
        messagebox.showerror("PhiChart", "存在其他运行中的实例，请勿重复启动。")
        return
    t1 = threading.Thread(daemon=True, target=runningThread)
    t1.start()

def defaultArgs(*args):
    print("???")
    setEntry(lb1et4, "PHICHART")
    setEntry(lb1et5, "Unknown")
    setEntry(lb1et6, "UN Lv.?")
    setEntry(lb2et1, "800")
    setEntry(lb2et2, "600")
    setEntry(lb2et3, "")
    setEntry(lb2et4, "")
    setEntry(lb3et1, "90")
    setEntry(lb3et2, "")
    setEntry(lb3et3, "")
    setEntry(lb3et4, "")
    lb3int1.set(0)
    lb3int2.set(0)
    lb4int1.set(0)
    lb5int1.set(0)

fr1 = Frame(top)
fr1.pack(side=LEFT, fill=BOTH, expand=True)
fr3 = Frame(top)
fr3.pack(side=RIGHT, fill=BOTH, expand=True)
fr2 = Frame(top)
fr2.pack(side=RIGHT, fill=BOTH, expand=True)

lb1 = LabelFrame(fr1, text="谱面信息", padx=5, pady=5)
lb1.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb2 = LabelFrame(fr1, text="画面设置", padx=5, pady=5)
lb2.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb3 = LabelFrame(fr2, text="高级设置", padx=5, pady=5)
lb3.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb4 = LabelFrame(fr2, text="谱面揭秘（映射）", padx=5, pady=5)
lb4.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb5 = LabelFrame(fr3, text="立体谱面", padx=5, pady=5)
lb5.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb6 = Frame(fr3)
lb6.pack(side=TOP, fill=X, padx=5, pady=5)

lb1.columnconfigure(index=1, weight=1)
Label(lb1, text="谱面文件").grid(row=0, column=0)
Label(lb1, text="音频文件").grid(row=1, column=0)
Label(lb1, text="曲绘文件").grid(row=2, column=0)
Label(lb1, text="副标题").grid(row=3, column=0)
Label(lb1, text="曲名").grid(row=4, column=0)
Label(lb1, text="难度").grid(row=5, column=0)
lb1et1 = ttk.Entry(lb1)
lb1et1.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
lb1et2 = ttk.Entry(lb1)
lb1et2.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
lb1et3 = ttk.Entry(lb1)
lb1et3.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
lb1et4 = ttk.Entry(lb1)
lb1et4.grid(row=3, column=1, sticky=EW, padx=5, pady=5)
lb1et5 = ttk.Entry(lb1)
lb1et5.grid(row=4, column=1, sticky=EW, padx=5, pady=5)
lb1et6 = ttk.Entry(lb1)
lb1et6.grid(row=5, column=1, sticky=EW, padx=5, pady=5)
# lb1bt1 = ttk.Button(lb1, text="打开文件夹")
# lb1bt1.grid(row=6, column=0, sticky=EW, padx=5, pady=5, ipady=5, columnspan=2)

lb2.columnconfigure(index=1, weight=1)
Label(lb2, text="窗口宽度").grid(row=0, column=0)
Label(lb2, text="窗口高度").grid(row=1, column=0)
Label(lb2, text="键宽度").grid(row=2, column=0)
Label(lb2, text="特效尺寸").grid(row=3, column=0)
lb2et1 = ttk.Entry(lb2)
lb2et1.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
lb2et2 = ttk.Entry(lb2)
lb2et2.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
lb2et3 = ttk.Entry(lb2)
lb2et3.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
lb2et4 = ttk.Entry(lb2)
lb2et4.grid(row=3, column=1, sticky=EW, padx=5, pady=5)

lb3.columnconfigure(index=1, weight=1)
Label(lb3, text="最大帧率").grid(row=0, column=0)
Label(lb3, text="谱面延迟").grid(row=1, column=0)
Label(lb3, text="背景亮度").grid(row=2, column=0)
Label(lb3, text="模糊半径").grid(row=3, column=0)
lb3et1 = ttk.Entry(lb3)
lb3et1.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
lb3et2 = ttk.Entry(lb3)
lb3et2.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
lb3et3 = ttk.Entry(lb3)
lb3et3.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
lb3et4 = ttk.Entry(lb3)
lb3et4.grid(row=3, column=1, sticky=EW, padx=5, pady=5)

lb3int1 = IntVar()
lb3ck1 = ttk.Checkbutton(lb3, variable=lb3int1, text="隐藏UI")
lb3ck1.grid(row=4, column=0, sticky=EW, padx=5, pady=5, columnspan=2)
lb3int2 = IntVar()
lb3ck2 = ttk.Checkbutton(lb3, variable=lb3int2, text="调试信息")
lb3ck2.grid(row=5, column=0, sticky=EW, padx=5, pady=5, columnspan=2)

lb4.columnconfigure(index=1, weight=1)
lb4int1 = IntVar()
lb4ck1 = ttk.Checkbutton(lb4, variable=lb4int1, text="启用谱面揭秘")
lb4ck1.grid(row=0, column=0, sticky=EW, padx=5, pady=5, columnspan=2)
Label(lb4, text="中心水平位置").grid(row=1, column=0)
Label(lb4, text="中心垂直位置").grid(row=2, column=0)
Label(lb4, text="缩放比例").grid(row=3, column=0)
lb4et1 = ttk.Entry(lb4)
lb4et1.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
lb4et2 = ttk.Entry(lb4)
lb4et2.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
lb4et3 = ttk.Entry(lb4)
lb4et3.grid(row=3, column=1, sticky=EW, padx=5, pady=5)

lb5.columnconfigure(index=1, weight=1)
lb5int1 = IntVar()
lb5ck1 = ttk.Checkbutton(lb5, variable=lb5int1, text="启用立体谱面")
lb5ck1.grid(row=0, column=0, sticky=EW, padx=5, pady=5, columnspan=2)
Label(lb5, text="流速（下落倍速）").grid(row=1, column=0)
Label(lb5, text="Note出现的位置").grid(row=2, column=0)
Label(lb5, text="摄像机水平位置").grid(row=3, column=0)
Label(lb5, text="摄像机垂直位置").grid(row=4, column=0)
lb5et1 = ttk.Entry(lb5)
lb5et1.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
lb5et2 = ttk.Entry(lb5)
lb5et2.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
lb5et2 = ttk.Entry(lb5)
lb5et2.grid(row=3, column=1, sticky=EW, padx=5, pady=5)
lb5et2 = ttk.Entry(lb5)
lb5et2.grid(row=4, column=1, sticky=EW, padx=5, pady=5)

lb6.columnconfigure(index=0, weight=1)
lb6.columnconfigure(index=1, weight=1)
lb6bt1 = ttk.Button(lb6, text="打开文件夹", command=openDir)
lb6bt1.grid(row=0, column=0, sticky=EW, padx=5, pady=5, ipady=5)
lb6bt2 = ttk.Button(lb6, text="默认参数", command=defaultArgs)
lb6bt2.grid(row=0, column=1, sticky=EW, padx=5, pady=5, ipady=5)
lb6bt3 = ttk.Button(lb6, text="开始", command=launch)
lb6bt3.grid(row=1, column=0, sticky=EW, padx=5, pady=5, ipady=10, columnspan=2)

str1 = "设置屏幕的宽度，单位像素。\n过大的尺寸可能导致帧数受限/UI过小。\n手机1080P: 1920x1080（16：9）\n平板1080P: 1440x1080（4：3）"
str2 = "设置屏幕的高度，单位像素。\n过大的尺寸可能导致帧数受限/UI过小。\n手机1080P: 1920x1080（16：9）\n平板1080P: 1440x1080（4：3）"
ToolTip(lb2et1, str1)
ToolTip(lb2et2, str1)

str3 = "设置键的大小，单位像素。\n推荐设置为屏幕宽度的1/10~1/8。"
str4 = "设置击中特效的大小，单位像素。\n推荐设置为屏幕宽度的1/8~1/6。"
ToolTip(lb2et3, str3)
ToolTip(lb2et4, str4)

str5 = "显示在连击数下方的文字。\n常设置为“AUTOPLAY”。"
str6 = "显示在左下角的文字。\n常设置为曲名。"
str7 = "显示在右下角的文字。\n常设置为难度。"
ToolTip(lb1et4, str5)
ToolTip(lb1et5, str6)
ToolTip(lb1et6, str7)

if __name__ == '__main__':
    defaultArgs()
    mainloop()