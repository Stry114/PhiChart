from tkinter import *
from tkinter import ttk, font
from tkinter import messagebox
from tkinter import filedialog
import threading
import traceback

import pygame

from libs.toolTip import ToolTip
from player3D import Player
from libs.analyzer import analyzeJson
from libs.autoMatch import Matcher

top = Tk()
top.title("PhiChart Launcher v0.4 by Stry")
top.minsize(width=1000, height=700)
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
            if lb5int2.get() == 1:
                player.enableNewVision = True

        if lb7int1.get() == 1:
            player.enableCompiler = True

        # 先读取铺面并初始化
        player.initPlayer()

        if lb7int1.get() == 1:
            player.enableCompiler = True
            if lb7et2.get() != "":
                player.chart.RPE_level = int(lb7et2.get())
            if lb7et3.get() != "":
                player.chart.charter = lb7et3.get()
            if lb7et4.get() != "":
                player.chart.composer = lb7et4.get()
            if lb7et5.get() != "":
                player.chart.illustration = lb7et5.get()
            if lb7et6.get() != "":
                player.chart.id = lb7et6.get()

        # 进入消息循环
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
    setEntry(lb2et1, "1200")
    setEntry(lb2et2, "800")
    setEntry(lb2et3, "")
    setEntry(lb2et4, "")
    setEntry(lb3et1, "60")
    setEntry(lb3et2, "")
    setEntry(lb3et3, "")
    setEntry(lb3et4, "")
    setEntry(lb7et2, "160")
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
        speedNum = len(line.speed3D.startTimeList)
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

def adjustCmr():

    def cnvMousePressed(event):
        cnvW = canvas.winfo_width()
        cnvH = canvas.winfo_height()
        cmrX = event.x / cnvW
        cmrY = event.y / cnvH
        updateAdjCmr(cmrX, cmrY)

    def updateAdjCmr(cmrX=0.5, cmrY=0.5):
        canvas.delete("all")
        cnvW = canvas.winfo_width()
        cnvH = canvas.winfo_height()
        x1, x3 = cnvW*0.15, cnvW*0.95
        x7, x9 = cnvW*0.15, cnvW*0.95
        y7, y1 = cnvH*0.15, cnvH*0.95
        y9, y3 = cnvH*0.15, cnvH*0.95
        x5, y5 = cmrX*cnvW, cmrY*cnvH
        x4 = x1 * 0.7 + x5 * 0.3
        x6 = x9 * 0.7 + x5 * 0.3
        y2 = y1 * 0.7 + y5 * 0.3
        y8 = y9 * 0.7 + y5 * 0.3
        x4i = x1 * 0.2 + x5 * 0.8
        x6i = x9 * 0.2 + x5 * 0.8
        y2i = y1 * 0.2 + y5 * 0.8
        y8i = y9 * 0.2 + y5 * 0.8

        canvas.create_rectangle(x1, y1, x9, y9, outline="black", fill="white", width=3)
        canvas.create_line(x7, y7, x5, y5)
        canvas.create_line(x9, y9, x5, y5)
        canvas.create_line(x3, y3, x5, y5)
        canvas.create_line(x1, y1, x5, y5)
        canvas.create_rectangle(x4i, y8i, x6i, y2i, fill="white", width=0)
        canvas.create_line(x4, y2, x6, y2)
        canvas.create_line(x4, y8, x6, y8)
        canvas.create_line(x4, y8, x4, y2)
        canvas.create_line(x6, y8, x6, y2)

        canvas.create_line(x1, y7-10, x1, y7-30, fill="black", width=3)
        canvas.create_line(x3, y7-10, x3, y7-30, fill="black", width=3)
        canvas.create_line(x1-10, y1, x1-30, y1, fill="black", width=3)
        canvas.create_line(x1-10, y7, x1-30, y7, fill="black", width=3)

    root = Toplevel()
    root.config(padx=40, pady=40)
    root.title("调整摄像机位置")
    root.geometry("400x400")

    canvas = Canvas(root, bg="SystemButtonFace")
    canvas.pack(fill=BOTH, expand=True)
    adjCmrLb1 = Label(root, anchor=W)
    adjCmrLb1.pack(side=TOP, fill=X)
    adjCmrLb2 = Label(root, anchor=W)
    adjCmrLb2.pack(side=TOP, fill=X)
    adjCmrLb3 = Label(root, anchor=W)
    adjCmrLb3.pack(side=TOP, fill=X)

    root.bind("<Button-1>", cnvMousePressed)
    root.after(500, updateAdjCmr)

def loadTips():
    ToolTip(lb5ck1, lang.str8)
    ToolTip(lb5et1, lang.str9)
    ToolTip(lb5et2, lang.str10)
    ToolTip(lb5et3, lang.str11)
    ToolTip(lb5et4, lang.str12)
    ToolTip(lb5et5, lang.str27)
    ToolTip(lb5ck2, lang.str26)
    ToolTip(lb2et1, lang.str1)
    ToolTip(lb2et2, lang.str1)
    ToolTip(lb2et3, lang.str3)
    ToolTip(lb2et4, lang.str4)
    ToolTip(lb1et4, lang.str5)
    ToolTip(lb1et5, lang.str6)
    ToolTip(lb1et6, lang.str7)
    ToolTip(lb4ck1, lang.str13)
    ToolTip(lb4et1, lang.str14)
    ToolTip(lb4et2, lang.str15)
    ToolTip(lb4et3, lang.str16)
    ToolTip(lb3et1, lang.str17)
    ToolTip(lb3et2, lang.str18)
    ToolTip(lb3et3, lang.str19)
    ToolTip(lb3et4, lang.str20)
    ToolTip(lb3ck1, lang.str21)
    ToolTip(lb3ck2, lang.str22)
    ToolTip(lb1et1, lang.str23)
    ToolTip(lb1et2, lang.str24)
    ToolTip(lb1et3, lang.str25)
    ToolTip(lb7ck1, lang.str32)
    ToolTip(lb7et2, lang.str33)
    ToolTip(lb7et6, lang.str34)

def enableCompiler(*args):

    if lb7int1.get() != 1:
        return
    lb5int1.set(1)

    root = Toplevel(top)
    root.title("声明")
    root.geometry("400x360")
    root.config(padx=40, pady=40)
    root.attributes("-topmost", True)
    root.attributes("-toolwindow", True)

    ft1 = font.Font(size=24, weight="bold")
    Label(root, font=ft1, text="立体转谱器声明").pack(side=TOP, anchor=W, fill=X)
    Label(root, font=ft1, text="").pack(side=TOP, anchor=W, fill=X)
    Label(root, wraplength=320, justify="left", text=lang.str28).pack(side=TOP, anchor=W)
    Label(root, wraplength=320, justify="left", text=lang.str29).pack(side=TOP, anchor=W)
    Label(root, wraplength=320, justify="left", text=lang.str30).pack(side=TOP, anchor=W)
    Label(root, wraplength=320, justify="left", text=lang.str31).pack(side=TOP, anchor=W)

def ZH_CN():
    global lang
    loadTips()

def ZH_TW():
    global lang
    loadTips()


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
lb3 = LabelFrame(fr1, text="高级设置", padx=5, pady=5)
lb3.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb4 = LabelFrame(fr3, text="谱面揭秘（映射）", padx=5, pady=5)
lb4.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb5 = LabelFrame(fr2, text="立体谱面", padx=5, pady=5)
lb5.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
lb7 = LabelFrame(fr2, text="立体转谱与RPE选项", padx=5, pady=5)
lb7.pack(side=TOP, fill=BOTH, padx=5, pady=5, expand=True)
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
lb5ck2 = ttk.Checkbutton(lb5, variable=lb5int2, text="启用高视角")
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
lb5bt1 = ttk.Button(lb5ck2, text="调整视角", command=adjustCmr)
lb5bt1.pack(side=RIGHT, fill=Y)

lb6.columnconfigure(index=0, weight=1)
lb6.columnconfigure(index=1, weight=1)
lb6bt1 = ttk.Button(lb6, text="打开文件夹", command=openDir)
lb6bt1.grid(row=0, column=0, sticky=EW, padx=5, pady=5, ipady=5)
lb6bt2 = ttk.Button(lb6, text="默认参数", command=defaultArgs)
lb6bt2.grid(row=0, column=1, sticky=EW, padx=5, pady=5, ipady=5)
lb6bt3 = ttk.Button(lb6, text="开始", command=launch)
lb6bt3.grid(row=1, column=0, sticky=EW, padx=5, pady=5, ipady=10, columnspan=2)

lb7.columnconfigure(index=1, weight=1)
lb7int1 = IntVar()
lb7int2 = (IntVar())
lb7int2.set(1)
lb7ck1 = ttk.Checkbutton(lb7, variable=lb7int1, text="启用转谱", command=enableCompiler)
lb7ck1.grid(row=0, column=0, sticky=EW, padx=5, pady=5, columnspan=2)
Label(lb7, text="RPE版本").grid(row=3, column=0)
lb7et2 = ttk.Entry(lb7)
lb7et2.grid(row=3, column=1, sticky=EW, padx=5, pady=5)
Label(lb7, text="谱师").grid(row=4, column=0)
lb7et3 = ttk.Entry(lb7)
lb7et3.grid(row=4, column=1, sticky=EW, padx=5, pady=5)
Label(lb7, text="曲师").grid(row=5, column=0)
lb7et4 = ttk.Entry(lb7)
lb7et4.grid(row=5, column=1, sticky=EW, padx=5, pady=5)
Label(lb7, text="画师").grid(row=6, column=0)
lb7et5 = ttk.Entry(lb7)
lb7et5.grid(row=6, column=1, sticky=EW, padx=5, pady=5)
Label(lb7, text="ID").grid(row=7, column=0)
lb7et6 = ttk.Entry(lb7)
lb7et6.grid(row=7, column=1, sticky=EW, padx=5, pady=5)

setEntry(lb4et1, "DISABLED")
setEntry(lb4et2, "DISABLED")
lb4et1.config(state=DISABLED)
lb4et2.config(state=DISABLED)


if __name__ == '__main__':
    defaultArgs()
    ZH_CN()
    mainloop()