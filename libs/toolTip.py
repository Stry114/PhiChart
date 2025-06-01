import tkinter as tk


class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        self.id = None
        self.x = self.y = 0

        # 绑定鼠标事件
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)
        widget.bind("<Motion>", self.update_position)

    def show_tip(self, event=None):
        """显示提示框"""
        if self.tip_window:
            return

        # 计算提示框位置（控件下方居中）
        x = self.widget.winfo_rootx() + (self.widget.winfo_width() // 2)
        y = self.widget.winfo_rooty() + self.widget.winfo_height()

        # 创建顶层窗口
        self.tip_window = tk.Toplevel(self.widget)

        # 去除窗口装饰
        self.tip_window.wm_overrideredirect(True)

        # 设置位置（+10偏移使鼠标不遮挡提示）
        self.tip_window.wm_geometry(f"+{x}+{y + 10}")

        # 创建提示标签
        label = tk.Label(self.tip_window, text=self.text,
                        background="#fafafa", relief="solid", borderwidth=1,
                        font=("微软雅黑", 10),
                        justify = "left",  # 文字左对齐
                        anchor = "w",  # 内容左对齐
                        padx=8,          # 左右内边距
                        pady=4          # 上下内边距
        )
        label.pack()

    def hide_tip(self, event=None):
        """隐藏提示框"""
        if self.tip_window:
            self.tip_window.destroy()
            self.tip_window = None

    def update_position(self, event):
        """更新提示框位置（跟随鼠标移动）"""
        if self.tip_window:
            # 重新计算位置
            x = self.widget.winfo_rootx() + (event.x)
            y = self.widget.winfo_rooty() + event.y + 15
            self.tip_window.wm_geometry(f"+{x}+{y}")


# 示例使用
if __name__ == "__main__":
    root = tk.Tk()
    root.title("ToolTip 示例")
    root.geometry("300x200")

    # 创建几个带提示的按钮
    btn1 = tk.Button(root, text="保存", width=10)
    btn1.pack(pady=20)
    ToolTip(btn1, "将当前内容保存到文件")

    btn2 = tk.Button(root, text="打印", width=10)
    btn2.pack(pady=20)
    ToolTip(btn2, "打印文档内容")

    # 创建带提示的标签
    label = tk.Label(root, text="重要信息", relief="groove", width=15, padx=10, pady=5)
    label.pack(pady=20)
    ToolTip(label, "这是程序的敏感设置区域\n请谨慎操作！")

    root.mainloop()