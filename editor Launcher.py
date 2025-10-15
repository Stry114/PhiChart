from libs.autoMatch import *
from tk.timelineEditor import *
import multiprocessing
import tk.tomlIO as tomlIO
import toml
import os
import re


def fix_homogeneous_array(content):
    """
    预处理 TOML 文本，将数组中的整数转为浮点数（解决非同质数组问题）
    例如：[1, 2.0, 3] → [1.0, 2.0, 3.0]
    """
    # 正则匹配数组中的整数（不匹配小数）
    # 匹配规则：数组内的正负整数，且前后不是小数点（避免误改小数）
    pattern = r"(?<=\[|\s|,)-?\d+(?=\s|,|\])"
    fixed_content = re.sub(pattern, lambda m: f"{m.group()}.0", content)
    return fixed_content


def newDir():
    def submit():
        if et1.get() == "":
            messagebox.showinfo("Error", "曲名为空。")
            return
        elif et2.get() == "":
            messagebox.showinfo("Error", "未选择曲绘。")
            return
        elif et3.get() == "":
            messagebox.showinfo("Error", "未选择音频。")
            return
        elif et4.get() == "":
            messagebox.showinfo("Error", "难度为空。")
            return
        elif et5.get() == "":
            messagebox.showinfo("Error", "ID为空。")
            return
        elif et9.get() == "":
            # 检验数字格式
            messagebox.showinfo("Error", "BPM为空。")
            return
        if not et9.get().replace('.', '', 1).isdigit():
            messagebox.showinfo("Error", "BPM格式错误。")
            return
        if not et10.get().isdigit():
            messagebox.showinfo("Error", "线数格式错误。")
            return

        # 校验数据是否处于推荐值范围内
        try:
            assert 1 <= int(et10.get()) <= 24, "线数超出推荐范围（1~24）。"
            assert 1 <= int(et9.get()) <= 1000, "BPM超出推荐范围（1~1000）。"
        except AssertionError as e:
            i = messagebox.askokcancel("警告",
                                       str(e) + "\n不合理的设置可能会导致程序运行不稳定，并意外的bug。\n是否继续？")
            if not i:
                return

        dir = os.path.join("./tk/projects/", et1.get())

        # 检查文件夹是否存在，不存在就创建
        if not os.path.exists(dir):
            os.mkdir(dir)
        else:
            messagebox.showinfo("Error", f"名为：\n{dir}\n的项目文件夹已存在。")
            return

        # 复制文件到新文件夹
        import shutil
        # 复制曲绘
        shutil.copy(et2.get(), os.path.join(dir, os.path.basename(et2.get())))
        # 复制音频
        shutil.copy(et3.get(), os.path.join(dir, os.path.basename(et3.get())))
        # 创建空谱面对象
        chart: Chart = newDefaultChart(
            bpm=float(et9.get()),
            numOfLine=int(et10.get()),
        )

        # 填入meta数据
        chart.name = et1.get()
        chart.bg = os.path.basename(et2.get())
        chart.song = os.path.basename(et3.get())
        chart.level = et4.get()
        chart.id = et5.get()
        chart.composer = et6.get()
        chart.charter = et7.get()
        chart.illustration = et8.get()
        chart.bpm = float(et9.get())
        # 尝试导出
        f = open(os.path.join(dir, "PCdata.toml"), "w", encoding="utf-8")
        f.write(toml.dumps(tomlIO.chart2toml(chart)))
        f.close()

        # 打开编辑器
        top.destroy()
        openDir(dir)

    def selectImage():
        file = filedialog.askopenfilename(initialdir="charts/", title="选择曲绘", filetypes=(
        ("PNG文件", "*.png"), ("JPG文件", "*.jpg;*.jpeg"), ("所有文件", "*.*")))
        if file:
            if not (file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg")):
                messagebox.showerror("文件类型", "曲绘文件：使用了不受支持的文件类型。")
                return
            et2.delete(0, END)
            et2.insert(0, file)

    def selectAudio():
        file = filedialog.askopenfilename(initialdir="charts/", title="选择音频",
                                          filetypes=(("WAV文件", "*.wav"), ("MP3文件", "*.mp3"), ("所有文件", "*.*")))
        if file:
            if not (file.endswith(".wav") or file.endswith(".mp3")):
                messagebox.showerror("文件类型", "音频文件：使用了不受支持的文件类型。")
                return
            et3.delete(0, END)
            et3.insert(0, file)

    def randomID():
        import random
        id = str(random.randint(10 ^ 12, 10 ^ 13 - 1))
        et5.delete(0, END)
        et5.insert(0, id)

    root.destroy()
    top = Tk()
    top.geometry('720x720')
    top.config(bg="#222", padx=30, pady=30)
    top.title('PhiChart Editor Launcher')
    top.minsize(600, 600)

    lf1 = LabelFrameDark(top, text="META（元数据）", padx=10, pady=10)
    lf1.pack(side=TOP, fill=X)

    lf1.columnconfigure(1, weight=1)

    LabelDark(lf1, anchor=W, text="曲名").grid(row=0, column=0, padx=5, pady=5)
    et1 = EntryDark(lf1)
    et1.grid(row=0, column=1, padx=5, pady=5, sticky=NSEW, columnspan=2)

    LabelDark(lf1, anchor=W, text="曲绘").grid(row=1, column=0, padx=5, pady=5)
    et2 = EntryDark(lf1)
    et2.grid(row=1, column=1, padx=5, pady=5, sticky=NSEW)

    LabelDark(lf1, anchor=W, text="音频").grid(row=2, column=0, padx=5, pady=5)
    et3 = EntryDark(lf1)
    et3.grid(row=2, column=1, padx=5, pady=5, sticky=NSEW)

    LabelDark(lf1, anchor=W, text="难度").grid(row=3, column=0, padx=5, pady=5)
    et4 = EntryDark(lf1)
    et4.grid(row=3, column=1, padx=5, pady=5, sticky=NSEW, columnspan=2)

    LabelDark(lf1, anchor=W, text="ID").grid(row=4, column=0, padx=5, pady=5)
    et5 = EntryDark(lf1)
    et5.grid(row=4, column=1, padx=5, pady=5, sticky=NSEW)

    LabelDark(lf1, anchor=W, text="曲师").grid(row=5, column=0, padx=5, pady=5)
    et6 = EntryDark(lf1)
    et6.grid(row=5, column=1, padx=5, pady=5, sticky=NSEW, columnspan=2)

    LabelDark(lf1, anchor=W, text="谱师").grid(row=6, column=0, padx=5, pady=5)
    et7 = EntryDark(lf1)
    et7.grid(row=6, column=1, padx=5, pady=5, sticky=NSEW, columnspan=2)

    LabelDark(lf1, anchor=W, text="画师").grid(row=7, column=0, padx=5, pady=5)
    et8 = EntryDark(lf1)
    et8.grid(row=7, column=1, padx=5, pady=5, sticky=NSEW, columnspan=2)

    LabelDark(lf1, anchor=W, text="BPM").grid(row=8, column=0, padx=5, pady=5)
    et9 = EntryDark(lf1)
    et9.grid(row=8, column=1, padx=5, pady=5, sticky=NSEW, columnspan=2)

    LabelDark(lf1, anchor=W, text="线数").grid(row=9, column=0, padx=5, pady=5)
    et10 = EntryDark(lf1)
    et10.grid(row=9, column=1, padx=5, pady=5, sticky=NSEW, columnspan=2)

    et1.insert(END, "123123")
    et2.insert(END, r"D:\Projects\PygamePhiChart\tk\assets\base.png")
    et3.insert(END, r"D:\Projects\PygamePhiChart\charts\db doll\dbdoll.wav")
    et4.insert(END, "123123")
    et5.insert(END, "123123")
    et9.insert(END, "123")
    et10.insert(END, "24")

    bt1 = ButtonDark(top, text="创建", height=2, command=submit)
    bt1.pack(side=BOTTOM, fill=X)
    bt2 = ButtonDark(lf1, text="选定", width=8, command=selectImage)
    bt2.grid(row=1, column=2, padx=5, pady=5, sticky=EW)
    bt2 = ButtonDark(lf1, text="选定", width=8, command=selectAudio)
    bt2.grid(row=2, column=2, padx=5, pady=5, sticky=EW)
    bt2 = ButtonDark(lf1, text="随机", width=8, command=randomID)
    bt2.grid(row=4, column=2, padx=5, pady=5, sticky=EW)


class FileButton(ButtonDark):
    def __init__(self, master, file, func):
        super().__init__(master, text="    " + file, command=self.command, anchor="w")
        self.file = file
        self.func = func

    def command(self):
        self.func(self.file)


def askOpenDir():
    file = filedialog.askdirectory(initialdir="./tk/projects/")
    if file:
        openDir(file)


def openDir(dir: str):
    try:
        matcher = TomlMatcher(dir)
        f = open(matcher.chartFile, "r", encoding="utf-8")
        chart = tomlIO.toml2chart(toml.loads(fix_homogeneous_array(f.read())))
        f.close()
    except Exception as e:
        import traceback
        traceback.print_exc()
        messagebox.showinfo("Error", str(e))
        return

    try:
        root.destroy()
    except Exception:
        pass

    editor = TimelineEditor(
        chart,
        matcher.audioFile,
        matcher.illuFile,
        dir,
    )
    mainloop()


if __name__ == '__main__':

    multiprocessing.freeze_support()

    root = Tk()
    root.geometry('720x720')
    root.config(bg="#222", padx=30, pady=30)
    root.title('PhiChart Editor Launcher')
    root.minsize(600, 600)

    root.columnconfigure(1, weight=1)
    img1 = PhotoImage(file='assets/new.png')
    img2 = PhotoImage(file='assets/open.png')
    rbt1 = ButtonDark(root, image=img1, bd=0, bg="#222", cursor="hand2", command=newDir)
    rbt1.grid(row=0, column=0, pady=10)
    rbt2 = ButtonDark(root, image=img2, bd=0, bg="#222", cursor="hand2", command=askOpenDir)
    rbt2.grid(row=1, column=0, pady=10)
    LabelDark(root, anchor=W, text="新建项目文件夹").grid(row=0, column=1, padx=10, pady=10, sticky=NW)
    LabelDark(root, anchor=W, text="打开已有的项目文件夹").grid(row=1, column=1, padx=10, pady=10, sticky=NW)

    dirList = os.listdir('./tk/projects/')
    for i in range(min(10, len(dirList))):
        dir = os.path.join("./tk/projects/", dirList[i])
        this = FileButton(root, dir, openDir)
        this.grid(row=i + 2, column=0, padx=0, pady=2, sticky=EW, columnspan=2)

    root.mainloop()
