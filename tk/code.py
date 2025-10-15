import tkinter as tk
from tkinter import font, ttk
import re

from tk.pullbar import *


class SimpleCodeEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("简单代码编辑器")
        self.root.geometry("800x600")

        # 设置字体
        self.font = font.Font(family="Consolas", size=12)

        # 创建行号区域和文本编辑区域的框架
        self.frame = Frame(root, bg="#333")
        self.frame.pack(fill=tk.BOTH, expand=True)

        # 行号文本框
        self.line_numbers = Text(self.frame, font=self.font, width=4, padx=5, takefocus=0, borderwidth=0, background="#222", state=tk.DISABLED, highlightthickness=0, fg="#777")
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=1)

        # 主文本编辑区域
        self.text = Text(self.frame, font=self.font, wrap=tk.NONE, undo=True, borderwidth=0, background="#222", highlightthickness=0, fg="#ddd", insertbackground="#fff",)
        self.text.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 创建滚动条
        self.scrollbar = ttk.Scrollbar(self.text, command=self.on_scroll)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 绑定事件
        self.text.bind("<KeyRelease>", self.update_line_numbers)
        self.text.bind("<MouseWheel>", self.update_line_numbers)
        self.text.bind("<ButtonRelease-1>", self.update_line_numbers)
        self.text.bind("<Configure>", self.update_line_numbers)

        # 设置快捷键
        self.set_shortcuts()

        # 配置标签用于语法高亮
        self.configure_tags()

        # 初始更新行号
        self.update_line_numbers()

        # 绑定文本变化事件用于高亮
        self.text.bind("<KeyRelease>", self.highlight_syntax, add=True)

        # 初始高亮
        self.highlight_syntax()

    def set_shortcuts(self):
        """设置基本快捷键"""
        # Ctrl+C 复制
        self.text.bind("<Control-c>", self.copy_text)
        # Ctrl+V 粘贴
        self.text.bind("<Control-v>", self.paste_text)
        # Ctrl+X 剪切
        self.text.bind("<Control-x>", self.cut_text)
        # Ctrl+Z 撤销
        self.text.bind("<Control-z>", self.undo)
        # Ctrl+Y 重做
        self.text.bind("<Control-y>", self.redo)
        # Ctrl+A 全选
        self.text.bind("<Control-a>", self.select_all)
    def configure_tags(self):
        """配置用于语法高亮的标签"""
        # 关键字高亮
        self.text.tag_configure("keyword", foreground="#FF6B6B")
        # 数字高亮
        self.text.tag_configure("number", foreground="#6BFFB2")
        # 注释高亮
        self.text.tag_configure("type", foreground="#FFE06B")

    def update_line_numbers(self, event=None):
        """更新行号显示"""
        # 获取文本内容的行数
        lines = self.text.get("1.0", tk.END).count("\n") + 1

        # 更新行号文本框
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert(tk.END, "\n".join(str(i) for i in range(1, lines + 1)))
        self.line_numbers.config(state=tk.DISABLED)

        # 保持行号与文本区域滚动同步
        self.line_numbers.yview_moveto(self.text.yview()[0])

    def on_scroll(self, *args):
        """处理滚动事件，保持行号与文本同步滚动"""
        self.text.yview(*args)
        self.line_numbers.yview(*args)

    def highlight_syntax(self, event=None):
        """简单的语法高亮实现"""
        # 先移除所有现有标签
        for tag in self.text.tag_names():
            self.text.tag_remove(tag, "1.0", tk.END)

        # 定义要高亮的关键字（Python关键字示例）
        keywords = [
            "new",  # 放置事件
            "set",  # 放置事件
            "del",  # 放置事件
            "var",  # 放置事件
            "for",  # 放置事件
            "return",  # 放置事件
            "input",  # 放置事件
            "line",  # 放置事件
        ]

        # 高亮关键字（修正版）
        # 使用Tcl兼容的正则表达式，避免使用复杂的lookbehind/lookahead
        pattern = r'\m(' + '|'.join(keywords) + r')\M'  # \m和\M是Tcl的单词边界
        start_pos = "1.0"
        while True:
            start_pos = self.text.search(pattern, start_pos, stopindex=tk.END, regexp=True)
            if not start_pos:
                break
            # 计算单词结束位置
            word_end = self.text.index(f"{start_pos} wordend")
            self.text.tag_add("keyword", start_pos, word_end)
            start_pos = word_end

        # 定义要高亮的关键字（Python关键字示例）
        keywords = [
            "index",  # 放置事件
            "on",  # 放置事件
            "in",  # 放置事件

            "alpha",  # 放置事件
            "moveX",  # 放置事件
            "moveY",  # 放置事件
            "moveZ",  # 放置事件
            "speed",  # 放置事件
            "rotate",  # 放置事件
            "theta",  # 放置事件

            "tap",  # 放置事件
            "drag",  # 放置事件
            "flick",  # 放置事件
            "hold",  # 放置事件
        ]

        # 高亮关键字（修正版）
        # 使用Tcl兼容的正则表达式，避免使用复杂的lookbehind/lookahead
        pattern = r'\m(' + '|'.join(keywords) + r')\M'  # \m和\M是Tcl的单词边界
        start_pos = "1.0"
        while True:
            start_pos = self.text.search(pattern, start_pos, stopindex=tk.END, regexp=True)
            if not start_pos:
                break
            # 计算单词结束位置
            word_end = self.text.index(f"{start_pos} wordend")
            self.text.tag_add("type", start_pos, word_end)
            start_pos = word_end

        # 定义要高亮的关键字（Python关键字示例）
        keywords = [
            "sin",  # 放置事件
            "cos",  # 放置事件
            "tan",  # 放置事件
            "ln",  # 放置事件
            "log",  # 放置事件
            "sqrt",  # 放置事件
        ]

        # 高亮关键字（修正版）
        # 使用Tcl兼容的正则表达式，避免使用复杂的lookbehind/lookahead
        pattern = r'\m(' + '|'.join(keywords) + r')\M'  # \m和\M是Tcl的单词边界
        start_pos = "1.0"
        while True:
            start_pos = self.text.search(pattern, start_pos, stopindex=tk.END, regexp=True)
            if not start_pos:
                break
            # 计算单词结束位置
            word_end = self.text.index(f"{start_pos} wordend")
            self.text.tag_add("function", start_pos, word_end)
            start_pos = word_end

        # 高亮数字（修正版 - 使用更简单的模式）
        # 简化正则表达式以适应Tcl的语法要求
        pattern = r'\m(0x[0-9a-fA-F]+|0b[01]+|\d+(\.\d*)?([eE][+-]?\d+)?)\M'
        start_pos = "1.0"
        while True:
            start_pos = self.text.search(pattern, start_pos, stopindex=tk.END, regexp=True)
            if not start_pos:
                break
            # 计算数字结束位置
            line = start_pos.split('.')[0]
            line_end = f"{line}.end"
            line_text = self.text.get(start_pos, line_end)

            # 使用Python的re模块查找完整匹配
            match = re.match(r'(0x[0-9a-fA-F]+|0b[01]+|\d+(\.\d*)?([eE][+-]?\d+)?)', line_text)
            if match:
                end_col = int(start_pos.split('.')[1]) + len(match.group(0))
                end_pos = f"{line}.{end_col}"
                self.text.tag_add("number", start_pos, end_pos)
                start_pos = end_pos
            else:
                start_pos = self.text.index(f"{start_pos}+1c")

    def find_matching_quote(self, start_pos, quote):
        """查找与起始引号匹配的结束引号"""
        current_pos = self.text.index(f"{start_pos}+1c")
        line = start_pos.split('.')[0]
        end_of_line = f"{line}.end"

        while current_pos <= end_of_line:
            char = self.text.get(current_pos, f"{current_pos}+1c")
            if char == quote:
                # 检查是否是转义的引号
                prev_char = self.text.get(f"{current_pos}-1c", current_pos)
                if prev_char != '\\':
                    return current_pos
            current_pos = self.text.index(f"{current_pos}+1c")
        return None

    # 快捷键功能实现
    def copy_text(self, event=None):
        self.text.event_generate("<<Copy>>")
        return "break"

    def paste_text(self, event=None):
        self.text.event_generate("<<Paste>>")
        return "break"

    def cut_text(self, event=None):
        self.text.event_generate("<<Cut>>")
        return "break"

    def undo(self, event=None):
        try:
            self.text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def redo(self, event=None):
        try:
            self.text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    def select_all(self, event=None):
        self.text.tag_add("sel", "1.0", tk.END)
        return "break"


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleCodeEditor(root)
    root.mainloop()


"""
input t1
input t2
input x
input y
input lineIndex

line lineIndex+0
new moveX t0 t1 x-0.1 x
new moveY t0 t1 y y
new drag t1 0

line lineIndex+1
new moveX t0 t1 x+0.1 x
new moveY t0 t1 y y
new drag t1 0

line lineIndex+2
new moveX t0 t1 x x
new moveY t0 t1 y-0.1 y
new drag t1 0

line lineIndex+3
new moveX t0 t1 x x
new moveY t0 t1 y y+0.1
new drag t1 0
"""