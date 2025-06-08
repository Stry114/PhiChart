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
from analyzer import analyzeJson
from autoMatch import Matcher

top = Tk()
top.title("PhiChart Launcher v0.1 by Stry")
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

            if lb4et1.state() == NORMAL and lb4et1.get() != "":
                centerX = int(lb4et1.get())
            else:
                centerX = int(player.width / 2)
            if lb4et1.state() == NORMAL and lb4et2.get() != "":
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

        if lb5int1.get() == 1:
            player.enable3D = True
            if lb5et1.get() != "":
                player.speed = float(lb5et1.get())
            if lb5et2.get() != "":
                player.boundary = float(lb5et2.get())
            if lb5et3.get() != "":
                player.cmrX = float(lb5et3.get())
            if lb5et4.get() != "":
                player.cmrY = float(lb5et4.get())
            if lb5et5.get() != "":
                player.b = float(lb5et5.get())

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
    setEntry(lb3et1, "60")
    setEntry(lb3et2, "")
    setEntry(lb3et3, "")
    setEntry(lb3et4, "")
    lb3int1.set(0)
    lb3int2.set(0)
    lb4int1.set(0)
    lb5int1.set(0)

def selectLines(*args):
    chart = analyzeJson(lb1et1.get())

    root = Toplevel()
    root.config(padx=20, pady=20)
    root.geometry("800x600")
    intVarList = []
    checkboxList = []

    for i in range(len(chart.lineList)):
        line = chart.lineList[i]
        noteNum = len(line.noteList)
        moveNum = len(line.move1.startTimeList)
        speedNum = len(line.speed.startTimeList)
        alphaNum = len(line.alpha.startTimeList)
        rotationNum = len(line.rotate.startTimeList)

        intVar = IntVar(value=0)
        intVarList.append(intVar)
        checkBox = ttk.Checkbutton(root, text=f"Line{i}\t{noteNum} notes    "
                                              f"\t{speedNum} speed events"
                                              f"\t{moveNum} move events"
                                              f"\t{alphaNum} alpha events"
                                              f"\t{rotationNum} rotate events.", variable=intVar)
        checkBox.pack(side=TOP, anchor=W, fill=X)
        checkboxList.append(checkBox)

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
lb5int2 = IntVar()
lb5ck1 = ttk.Checkbutton(lb5, variable=lb5int1, text="启用立体谱面")
lb5ck1.grid(row=0, column=0, sticky=EW, padx=5, pady=5, columnspan=2)
lb5ck2 = ttk.Checkbutton(lb5, variable=lb5int2, text="仅对部分判定线生效")
lb5ck2.grid(row=6, column=0, sticky=EW, padx=5, pady=5, columnspan=2)
Label(lb5, text="流速（下落倍速）").grid(row=1, column=0)
Label(lb5, text="Note出现的位置").grid(row=2, column=0)
Label(lb5, text="摄像机水平位置").grid(row=3, column=0)
Label(lb5, text="摄像机垂直位置").grid(row=4, column=0)
Label(lb5, text="摄像机前后位置").grid(row=5, column=0)
lb5et1 = ttk.Entry(lb5)
lb5et1.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
lb5et2 = ttk.Entry(lb5)
lb5et2.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
lb5et3 = ttk.Entry(lb5)
lb5et3.grid(row=3, column=1, sticky=EW, padx=5, pady=5)
lb5et4 = ttk.Entry(lb5)
lb5et4.grid(row=4, column=1, sticky=EW, padx=5, pady=5)
lb5et5 = ttk.Entry(lb5)
lb5et5.grid(row=5, column=1, sticky=EW, padx=5, pady=5)
lb5bt1 = ttk.Button(lb5ck2, text="选取", command=selectLines)
lb5bt1.pack(side=RIGHT, fill=Y)

lb6.columnconfigure(index=0, weight=1)
lb6.columnconfigure(index=1, weight=1)
lb6bt1 = ttk.Button(lb6, text="打开文件夹", command=openDir)
lb6bt1.grid(row=0, column=0, sticky=EW, padx=5, pady=5, ipady=5)
lb6bt2 = ttk.Button(lb6, text="默认参数", command=defaultArgs)
lb6bt2.grid(row=0, column=1, sticky=EW, padx=5, pady=5, ipady=5)
lb6bt3 = ttk.Button(lb6, text="开始", command=launch)
lb6bt3.grid(row=1, column=0, sticky=EW, padx=5, pady=5, ipady=10, columnspan=2)

str1 = "设置屏幕的宽度，单位：像素。\n过大的尺寸可能导致帧数受限/UI过小。\n手机1080P: 1920x1080（16：9）\n平板1080P: 1440x1080（4：3）"
str2 = "设置屏幕的高度，单位：像素。\n过大的尺寸可能导致帧数受限/UI过小。\n手机1080P: 1920x1080（16：9）\n平板1080P: 1440x1080（4：3）"
ToolTip(lb2et1, str1)
ToolTip(lb2et2, str1)

str3 = "设置键的大小，单位：像素。\n推荐设置为屏幕宽度的1/10~1/8。"
str4 = "设置击中特效的大小，单位：像素。\n推荐设置为屏幕宽度的1/8~1/6。"
ToolTip(lb2et3, str3)
ToolTip(lb2et4, str4)

str5 = "显示在连击数下方的文字。\n常设置为“AUTOPLAY”。"
str6 = "显示在左下角的文字。\n常设置为曲名。"
str7 = "显示在右下角的文字。\n常设置为难度。"
ToolTip(lb1et4, str5)
ToolTip(lb1et5, str6)
ToolTip(lb1et6, str7)

str8 = "此功能尚不稳定，谨慎开启！"
str9 = "键下落的流速，不会影响BPM。\n开启立体模式后，由于视野内note的数量增加，\n若不提高流速就会出现“读谱不能”的现象。\n默认值为 2.5（倍速）。"
str10 = "键出现的位置（对应2D谱中距离判定线的位置）。\n单位：像素\n推荐值介于2~4倍窗口高度之间。"
str11 = "摄像机的水平位置。单位：像素。\n坐标原点位于屏幕左下角，向右为水平正方向。\n此值应介于0~屏幕宽度之间，推荐将摄像机放在屏幕中间偏上的位置。"
str12 = "摄像机的垂直位置。单位：像素。\n坐标原点位于屏幕左下角，向上为垂直正方向。\n此值应介于0~屏幕高度之间，推荐将摄像机放在屏幕中间偏上的位置。"
str27 = "摄像机的到屏幕的距离（垂直屏幕向外）。单位：Y。\n默认值为1.0，不建议修改此值。\n摄像机距离屏幕越远，视角越低。"
str26 = "启动器暂未适配此版本"
ToolTip(lb5ck1, str8)
ToolTip(lb5et1, str9)
ToolTip(lb5et2, str10)
ToolTip(lb5et3, str11)
ToolTip(lb5et4, str12)
ToolTip(lb5et5, str27)
ToolTip(lb5ck2, str26)

str13 = "此功能尚不稳定，谨慎开启！"
str14 = "此功能暂时受限，不允许修改。"
str15 = "此功能暂时受限，不允许修改。"
str16 = "此值应当介于0~1（不含端点）之间。\n默认值为 0.2"
ToolTip(lb4ck1, str13)
ToolTip(lb4et1, str14)
ToolTip(lb4et2, str15)
ToolTip(lb4et3, str16)

str17 = "默认值为 60。\n此值不应过小，推荐值为60~90。\n*请注意，击中特效是固定的42帧。\n*在B站投稿时请确保分辨率不低于1080P，以免帧数受限。"
str18 = "音乐与谱面之间的时差。单位：秒\n当此值为正时，谱面会延后开始，此值可正可负。"
str19 = "背景图面的亮度。\n此值为0时，画面最暗；\n此值为1时，画面最暗；\n此值超出0~1范围时，程序崩溃。"
str20 = "对曲绘进行高斯模糊，此值为模糊半径。请勿调整。"
ToolTip(lb3et1, str17)
ToolTip(lb3et2, str18)
ToolTip(lb3et3, str19)
ToolTip(lb3et4, str20)

str21 = "隐藏所有文字、进度条。"
str22 = "输出调试信息。\n可能导致帧数下降。"
ToolTip(lb3ck1, str21)
ToolTip(lb3ck2, str22)

str23 = "json\n仅支持官谱！\n请点击右下方“打开文件夹”。"
str24 = "wav/mp3"
str25 = "jpg/png"
ToolTip(lb1et1, str23)
ToolTip(lb1et2, str24)
ToolTip(lb1et3, str25)

setEntry(lb4et1, "DISABLED")
setEntry(lb4et2, "DISABLED")
lb4et1.config(state=DISABLED)
lb4et2.config(state=DISABLED)


if __name__ == '__main__':
    defaultArgs()
    mainloop()