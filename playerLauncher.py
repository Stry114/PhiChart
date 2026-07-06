import traceback
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox

import pygame

from tk.pullbar import *

import libs.autoMatch
import libs.vec3D
import zipfile
import shutil
import os


def clear_directory(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir, exist_ok=True)
        return

    for item in os.listdir(target_dir):
        item_path = os.path.join(target_dir, item)
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
        except OSError as e:
            raise OSError(f"清空目录失败：{item_path} -> {e}")


def open_dir(*args):
    d = filedialog.askdirectory(initialdir="charts")
    if d == "":
        return

    matcher = libs.autoMatch.Matcher(d)
    if matcher.illuFile is None:
        messagebox.showerror("Error", "未找到曲绘文件。\n支持的格式有：*.png *.jpg")
        return
    if matcher.audioFile is None:
        messagebox.showerror("Error", "未找到音频文件。\n支持的格式有：*.wav *.mp3")
        return
    if matcher.chartFile is None:
        messagebox.showerror("Error", "未找到谱面文件。\n支持的格式有：*.json")
        return

    lf2et0.setValue(matcher.chartFile.replace("/", "\\"))
    lf2et1.setValue(matcher.audioFile.replace("/", "\\"))
    lf2et2.setValue(matcher.illuFile.replace("/", "\\"))


def open_zip(*args):
    d = filedialog.askopenfilename(initialdir="charts", filetypes=(("zip压缩文件", "*.zip"), ("pez包", "*.pez"), ("所有类型", "*.*")))
    if d == "":
        return

    print(d)
    clear_directory("./temp")
    try:
        with zipfile.ZipFile(d, 'r') as zip_ref:
            zip_ref.extractall("./temp")
    except FileNotFoundError:
        messagebox.showerror("Error", "找不到文件\n"+d)
    except PermissionError:
        messagebox.showerror("Error", f"打开压缩包时发生错误：\n无写入权限。无法提取压缩包内文件。")
    except Exception as e:
        messagebox.showerror("Error", f"打开压缩包时发生错误：\n{e}")

    matcher = libs.autoMatch.Matcher("./temp")
    if matcher.illuFile is None:
        messagebox.showerror("Error", "未找到曲绘文件。\n支持的格式有：*.png *.jpg")
        return
    if matcher.audioFile is None:
        messagebox.showerror("Error", "未找到音频文件。\n支持的格式有：*.wav *.mp3")
        return
    if matcher.chartFile is None:
        messagebox.showerror("Error", "未找到谱面文件。\n支持的格式有：*.json")
        return

    lf2et0.setValue(matcher.chartFile.replace("/", "\\"))
    lf2et1.setValue(matcher.audioFile.replace("/", "\\"))
    lf2et2.setValue(matcher.illuFile.replace("/", "\\"))


def start_up(*a):

    # 加载播放器
    if lf5tb1.get() == 0:
        import player as pl
    else:
        import player3D as pl

    # 初始化播放器
    try:
        f = lf1et0.getValue()
        w = lf1et1.getValue()
        h = lf1et2.getValue()
        ns = lf1et3.getValue()
        es = lf1et4.getValue()
        ll = lf1et5.getValue()
    except ValueError as e:
        messagebox.showerror("Error", f"参数错误出现在：图形选项。\n{e}")
        return
    sw = top.winfo_screenwidth()
    sh = top.winfo_screenheight()
    if h > sh or w > sw:
        if messagebox.askyesno("图形选项", f"您设置的播放器窗口分辨率超过了当前屏幕的尺寸。是否缩小播放器窗口分辨率？"):
            h = min(h, sh)
            w = min(w, sw)
    player = pl.Player(w=w, h=h, fps=f)
    player.noteSize = ns
    player.hitEffectSize = es
    player.lineLength = ll

    try:
        f1 = lf2et0.get()
        f2 = lf2et1.get()
        f3 = lf2et2.get()
    except Exception as e:
        messagebox.showerror("Error", f"未知类型的错误出现在：谱面文件。\n{e}")
        return
    player.chartFile = f1
    player.audioFile = f2
    player.illuFile = f3

    try:
        subt = lf3et0.get()
        name = lf3et1.get()
        diff = lf3et2.get()
        displayUI = lf3ck1.get()
        displayDB = lf3ck2.get()
        doubleHit = lf3ck3.get()
    except Exception as e:
        messagebox.showerror("Error", f"未知类型的错误出现在：UI选项。\n{e}")
        return
    player.subtitle = subt
    player.name = name
    player.level = diff
    player.displayUI = displayUI
    player.displayDebug = displayDB
    player.doubleHitEffect = doubleHit

    try:
        delay = lf4et0.getValue()
        speed = lf4et1.getValue()
        speed3D = lf4et2.getValue()
        startTime = lf4et3.getValue()
    except ValueError as e:
        messagebox.showerror("Error", f"参数错误出现在：播放设置。\n{e}")
        return
    player.chartDelay = delay
    player.speed = speed
    player.speed3D = speed3D
    player.startTime = startTime

    try:
        enable3D = lf5ck1.get()
        enableCp = lf5ck2.get()
        enableNV = lf5ck3.get()
        cmrX = lf5et1.getValue() * w
        cmrY = lf5et2.getValue() * h
        cmrZ = lf5et3.getValue() * h
        print(cmrX, cmrY, cmrZ)
    except Exception as e:
        messagebox.showerror("Error", f"参数错误出现在：3D设置。\n{e}")
        return
    player.enable3D = enable3D
    player.enableCompiler = enableCp
    player.enableNewVision = enableNV
    player.cmrX = cmrX
    player.cmrY = cmrY
    player.cmrPos = libs.vec3D.V3d(cmrX, cmrY, cmrZ)

    if player.enableNewVision:
        player.displacementY = 0.75
    else:
        player.displacementY = 1.00

    try:
        player.autoplay = True
        player.initPlayer()
        top.destroy()
        player.mainloop()
    except pygame.error as e:
        messagebox.showerror("Error", f"播放器遇到错误：文件路径无效或文件路径为空：\n{e}")
        traceback.print_exc()
    except Exception as e:
        messagebox.showerror("Error", f"播放器遇到未知类型的错误：\n{e}")
        traceback.print_exc()
    finally:
        pygame.quit()


top = Tk()
top.config(bg="#222")
top.minsize(width=648, height=600)
top.iconbitmap("assets/logo.ico")
top.title("PhiChart Player Launcher")
top.config(padx=40, pady=40)


lf2 = LabelFrameDark(top, text="谱面文件", padx=10, pady=10)
lf1 = LabelFrameDark(top, text="图形选项", padx=10, pady=10)
lf3 = LabelFrameDark(top, text="UI选项", padx=10, pady=10)
lf4 = LabelFrameDark(top, text="播放设置", padx=10, pady=10)
lf5 = LabelFrameDark(top, text="3D设置", padx=10, pady=10)
lf2.columnconfigure(index=1, weight=1)


LabelDark(lf2, text="谱面文件 (Json)").grid(row=0, column=0, sticky=W, padx=5)
LabelDark(lf2, text="音频文件 (mp3/wav)").grid(row=1, column=0, sticky=W, padx=5)
LabelDark(lf2, text="曲绘文件 (png/jpg)").grid(row=2, column=0, sticky=W, padx=5)
lf2et0 = EntryDark(lf2)
lf2et0.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
lf2et1 = EntryDark(lf2)
lf2et1.grid(row=1, column=1, sticky=EW, padx=5, pady=5)
lf2et2 = EntryDark(lf2)
lf2et2.grid(row=2, column=1, sticky=EW, padx=5, pady=5)
lf2bt1 = ButtonDark(lf2, text="打开文件夹...", command=open_dir, height=2)
lf2bt1.grid(row=3, column=0, sticky=EW, padx=5, pady=5, columnspan=2)
lf2bt1 = ButtonDark(lf2, text="打开压缩包（zip/pez）", command=open_zip, height=2)
lf2bt1.grid(row=4, column=0, sticky=EW, padx=5, pady=5, columnspan=2)


LabelDark(lf1, text="最大帧率 (FPS)").grid(row=0, column=0, sticky=W, padx=5)
LabelDark(lf1, text="窗口宽度 (px)").grid(row=0, column=1, sticky=W, padx=5)
LabelDark(lf1, text="窗口高度 (px)").grid(row=0, column=2, sticky=W, padx=5)
LabelDark(lf1, text="键宽度 (px)").grid(row=2, column=0, sticky=W, padx=5)
LabelDark(lf1, text="特效宽度 (px)").grid(row=2, column=1, sticky=W, padx=5)
LabelDark(lf1, text="判定线长度 (px)").grid(row=2, column=2, sticky=W, padx=5)
lf1et0 = LiIntEntryDark(lf1, width=12, min=5).setValue(120)
lf1et0.grid(row=1, column=0, sticky=W, padx=5)
lf1et1 = LiIntEntryDark(lf1, width=12, min=100).setValue(1920)
lf1et1.grid(row=1, column=1, sticky=W, padx=5)
lf1et2 = LiIntEntryDark(lf1, width=12, min=100).setValue(1080)
lf1et2.grid(row=1, column=2, sticky=W, padx=5)
lf1et3 = LiIntEntryDark(lf1, width=12, min=10).setValue(1920//8)
lf1et3.grid(row=3, column=0, sticky=W, padx=5)
lf1et4 = LiIntEntryDark(lf1, width=12, min=10).setValue(1920//6)
lf1et4.grid(row=3, column=1, sticky=W, padx=5)
lf1et5 = LiIntEntryDark(lf1, width=12, min=10).setValue(1920*3)
lf1et5.grid(row=3, column=2, sticky=W, padx=5)


LabelDark(lf3, text="副标题").grid(row=0, column=0, sticky=W, padx=5)
LabelDark(lf3, text="曲名").grid(row=0, column=1, sticky=W, padx=5)
LabelDark(lf3, text="难度").grid(row=0, column=2, sticky=W, padx=5)
lf3et0 = EntryDark(lf3, width=24).setValue("AUTOPLAY")
lf3et0.grid(row=1, column=0, sticky=W, padx=5)
lf3et1 = EntryDark(lf3, width=24).setValue("Unknown")
lf3et1.grid(row=1, column=1, sticky=W, padx=5)
lf3et2 = EntryDark(lf3, width=24).setValue("UN Lv.?")
lf3et2.grid(row=1, column=2, sticky=W, padx=5)
LabelDark(lf3, text=" ",).grid(row=2, column=0, sticky=W, pady=3)
lf3ck1 = LiCheckbox(lf3,)
lf3ck1.build(x=8, y=50, text="显示UI", value=True)
lf3ck2 = LiCheckbox(lf3,)
lf3ck2.build(x=80, y=50, text="显示调试信息", value=False)
lf3ck3 = LiCheckbox(lf3,)
lf3ck3.build(x=190, y=50, text="双押提示", value=True)


LabelDark(lf4, text="谱面延迟 (s)").grid(row=0, column=0, sticky=W, padx=5)
LabelDark(lf4, text="倍速").grid(row=0, column=1, sticky=W, padx=5)
LabelDark(lf4, text="3D流速").grid(row=0, column=2, sticky=W, padx=5)
LabelDark(lf4, text="起始时间 (s)").grid(row=0, column=3, sticky=W, padx=5)
lf4et0 = LiFloatEntryDark(lf4, width=12, step=0.01).setValue(0.0)
lf4et0.grid(row=1, column=0, sticky=W, padx=5)
lf4et1 = LiFloatEntryDark(lf4, width=12, step=0.1, min=0.0).setValue(1.0)
lf4et1.grid(row=1, column=1, sticky=W, padx=5)
lf4et2 = LiFloatEntryDark(lf4, width=12, step=0.1, min=0.0).setValue(4.0)
lf4et2.grid(row=1, column=2, sticky=W, padx=5)
lf4et3 = LiFloatEntryDark(lf4, width=12, step=1.0, min=0.0).setValue(0.0)
lf4et3.grid(row=1, column=3, sticky=W, padx=5)


LabelDark(lf5, text=" ",).grid(row=0, column=0, sticky=W, pady=3)
LabelDark(lf5, text="渲染器",).grid(row=1, column=0, sticky=W, pady=5)
lf5ck1 = LiCheckbox(lf5,)
lf5ck1.build(x=8, y=0, text="启用3D", value=False)
lf5ck2 = LiCheckbox(lf5,)
lf5ck2.build(x=100, y=0, text="启用3D转谱", value=False)
lf5ck3 = LiCheckbox(lf5,)
lf5ck3.build(x=200, y=0, text="下压铺面", value=False)
lf5tb1 = LiToolBox(lf5, ("PhiChart Player (伪3D)", "PhiChart Player 3D (新渲染器)"), ("#ddd", "#ddd"))
lf5tb1.build(80, 30, 451, 25)
LabelDark(lf5, text="摄像机位置 (px)\t",).grid(row=2, column=0, sticky=W, pady=5)
LabelDark(lf5, text=" X",).grid(row=2, column=1, sticky=W, pady=5)
LabelDark(lf5, text=" Y",).grid(row=2, column=3, sticky=W, pady=5)
LabelDark(lf5, text=" Z",).grid(row=2, column=5, sticky=W, pady=5)
lf5et1 = LiFloatEntryDark(lf5, width=10, step=0.1).setValue(0.5)
lf5et1.grid(row=2, column=2, sticky=W, padx=5)
lf5et2 = LiFloatEntryDark(lf5, width=10, step=0.1).setValue(0.5)
lf5et2.grid(row=2, column=4, sticky=W, padx=5)
lf5et3 = LiFloatEntryDark(lf5, width=10, step=0.1, max=0.0).setValue(-1)
lf5et3.grid(row=2, column=6, sticky=W, padx=5)

bt1 = ButtonDark(top, text="启动", command=start_up, height=2)
bt1.pack(side=BOTTOM, fill=X, pady=10)


def basic_page(*args):
    lf2.pack(side=TOP, fill=X)
    lf3.pack(side=TOP, fill=X, pady=10)
    lf1.pack_forget()
    lf4.pack_forget()
    lf5.pack_forget()
    bt3.config(state=DISABLED)
    bt4.config(state=NORMAL)

def advanced_page(*args):
    lf1.pack(side=TOP, fill=X)
    lf4.pack(side=TOP, fill=X, pady=10)
    lf5.pack(side=TOP, fill=X, pady=10)
    lf2.pack_forget()
    lf3.pack_forget()
    bt4.config(state=DISABLED)
    bt3.config(state=NORMAL)


btfr = FrameDark(top,)
btfr.pack(side=BOTTOM, fill=X)
bt3 = ButtonDark(btfr, text="基础设置", command=basic_page, height=2)
bt3.pack(side=LEFT, fill=BOTH, expand=True)
LabelDark(btfr, text="  ").pack(side=LEFT)
bt4 = ButtonDark(btfr, text="高级设置", command=advanced_page, height=2)
bt4.pack(side=LEFT, fill=BOTH, expand=True)

basic_page()
mainloop()
