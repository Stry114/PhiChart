import tkinter as tk
from tkinter import ttk, messagebox
import math
import time  # 用于获取时间戳


class BezierEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("贝塞尔曲线编辑器")

        # 深色主题颜色配置
        self.colors = {
            "bg_main": "#222222",  # 主背景色
            "bg_secondary": "#333333",  # 次要背景色
            "text": "#ffffff",  # 文本颜色
            "border": "#444444",  # 边框颜色
            "highlight": "#555555",  # 高亮颜色
            "notebook_active": "#555555",  # 激活的标签页颜色
            "bezier_curve": "#4a90e2",  # 贝塞尔曲线颜色
            "control_line": "#777777",  # 控制线颜色
            "control_point": "#ffffff",  # 控制点颜色
            "selected_point": "#ff4757",  # 选中点颜色
            "trail_line": "#ff6b81",  # 轨迹线颜色
            "start_point": "#2ecc71",  # 起点颜色
            "end_point": "#e74c3c",  # 终点颜色
            "boundary": "#666666",  # 边界线颜色
        }

        # 目标画布尺寸（4:3比例）
        self.canvas_width, self.canvas_height = 800, 600

        # 设置全局主题
        self.setup_dark_theme()

        # 创建标签页控件 - 使用自定义深色样式
        self.notebook = ttk.Notebook(root, style="Dark.TNotebook")
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 创建贝塞尔曲线编辑标签页
        self.bezier_frame = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.bezier_frame, text="贝塞尔曲线")

        # 创建轨迹绘制标签页
        self.trail_frame = ttk.Frame(self.notebook, style="Dark.TFrame")
        self.notebook.add(self.trail_frame, text="轨迹绘制")

        # 缩放相关变量（贝塞尔曲线页）
        self.scale_factor = 1.0  # 缩放因子，1.0为原始大小，0.5为缩小
        self.offset_x = 0  # 水平偏移量
        self.offset_y = 0  # 垂直偏移量

        # 贝塞尔曲线控制点（存储在世界坐标系中）
        self.control_points = []
        self.selected_point = None
        self.dragging = False

        # 轨迹绘制相关变量
        self.trail_points = []  # 存储轨迹点，格式: (x, y, timestamp)
        self.drawing_trail = False  # 是否正在绘制轨迹
        self.trail_start_time = 0  # 轨迹开始时间
        self.trail_duration = 0  # 轨迹总时长（秒）

        # 创建两个标签页的UI
        self.create_bezier_widgets()
        self.create_trail_widgets()

        # 绑定事件
        self.bind_bezier_events()
        self.bind_trail_events()

        # 计算并设置窗口大小，确保画布达到目标尺寸
        self.root.update_idletasks()  # 确保所有控件都已计算尺寸
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        self.root.geometry(f"{window_width}x{window_height}")
        self.root.resizable(False, False)  # 禁止调整窗口大小

    def setup_dark_theme(self):
        """设置完整的深色主题样式，修复Notebook和边框问题"""
        # 设置根窗口背景
        self.root.configure(bg=self.colors["bg_main"])

        # 创建自定义样式
        self.style = ttk.Style()

        # 修复Notebook样式
        self.style.configure("Dark.TNotebook",
                             background=self.colors["bg_main"],
                             foreground=self.colors["text"],
                             bordercolor=self.colors["border"],
                             darkcolor=self.colors["border"],
                             lightcolor=self.colors["border"])

        # 修复Notebook标签样式
        self.style.configure("Dark.TNotebook.Tab",
                             background=self.colors["bg_secondary"],
                             foreground=self.colors["text"],
                             padding=[12, 4],
                             font=("SimHei", 10))

        # 修复选中标签的样式
        self.style.map("Dark.TNotebook.Tab",
                       background=[("selected", self.colors["notebook_active"])],
                       foreground=[("selected", self.colors["text"])])

        # 框架样式 - 消除白边
        self.style.configure("Dark.TFrame",
                             background=self.colors["bg_main"],
                             bordercolor=self.colors["border"],
                             relief=tk.SUNKEN)

        # 按钮样式
        self.style.configure("Dark.TButton",
                             background=self.colors["bg_secondary"],
                             foreground=self.colors["text"],
                             bordercolor=self.colors["border"],
                             padding=5,
                             font=("SimHei", 10),
                             focusthickness=1,
                             focuscolor=self.colors["highlight"])
        self.style.map("Dark.TButton",
                       background=[("active", "#444444")])

        # 标签样式
        self.style.configure("Dark.TLabel",
                             background=self.colors["bg_main"],
                             foreground=self.colors["text"],
                             font=("SimHei", 10))

        # 状态栏样式
        self.style.configure("Status.TLabel",
                             background=self.colors["bg_secondary"],
                             foreground=self.colors["text"],
                             font=("SimHei", 10))

    # ------------------------------
    # 贝塞尔曲线标签页相关功能
    # ------------------------------
    def create_bezier_widgets(self):
        # 控制面板
        control_frame = ttk.Frame(self.bezier_frame, padding="5", style="Dark.TFrame")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(control_frame, text="贝塞尔曲线编辑器:", style="Dark.TLabel").pack(side=tk.LEFT, padx=5)

        ttk.Button(control_frame, text="添加点", command=self.add_point, style="Dark.TButton").pack(side=tk.LEFT,
                                                                                                    padx=5)
        ttk.Button(control_frame, text="删除选中点", command=self.delete_selected, style="Dark.TButton").pack(
            side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="清空所有点", command=self.clear_all, style="Dark.TButton").pack(side=tk.LEFT,
                                                                                                        padx=5)
        ttk.Button(control_frame, text="缩放 (1x/0.5x)", command=self.toggle_zoom, style="Dark.TButton").pack(
            side=tk.LEFT, padx=5)

        # 画布框架 - 消除白边
        self.bezier_canvas_frame = ttk.Frame(
            self.bezier_frame,
            padding="5",
            relief=tk.SUNKEN,
            borderwidth=1,
            style="Dark.TFrame"
        )
        self.bezier_canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 创建指定尺寸的画布
        self.bezier_canvas = tk.Canvas(
            self.bezier_canvas_frame,
            bg=self.colors["bg_secondary"],
            width=self.canvas_width,
            height=self.canvas_height,
            highlightbackground=self.colors["border"],  # 画布边框颜色
            highlightthickness=1  # 边框厚度
        )
        self.bezier_canvas.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        self.bezier_status_var = tk.StringVar()
        self.bezier_status_var.set("点击画布添加控制点，拖动控制点调整曲线 | 缩放: 1x")
        status_bar = ttk.Label(
            self.bezier_frame,
            textvariable=self.bezier_status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            style="Status.TLabel"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定画布尺寸变化事件
        self.bezier_canvas.bind("<Configure>", self.on_bezier_canvas_configure)
        self.actual_width = self.canvas_width
        self.actual_height = self.canvas_height

    def bind_bezier_events(self):
        self.bezier_canvas.bind("<Button-1>", self.on_bezier_canvas_click)
        self.bezier_canvas.bind("<B1-Motion>", self.on_bezier_drag)
        self.bezier_canvas.bind("<ButtonRelease-1>", self.on_bezier_release)
        self.bezier_canvas.bind("<Motion>", self.on_bezier_mouse_move)

    def on_bezier_canvas_configure(self, event):
        """当画布尺寸变化时更新实际尺寸"""
        self.actual_width = event.width
        self.actual_height = event.height
        self.redraw_bezier()

    def toggle_zoom(self):
        """切换缩放状态（1x <-> 0.5x）"""
        # 获取屏幕中心坐标（使用实际画布尺寸）
        screen_center_x = self.actual_width // 2
        screen_center_y = self.actual_height // 2

        # 计算屏幕中心在世界坐标系中的位置
        world_center_x, world_center_y = self.screen_to_world(screen_center_x, screen_center_y)

        # 切换缩放因子
        new_scale = 0.5 if self.scale_factor == 1.0 else 1.0

        # 计算新的偏移量，确保世界中心在屏幕中心保持不变
        self.offset_x = screen_center_x - world_center_x * new_scale
        self.offset_y = screen_center_y - world_center_y * new_scale

        # 更新缩放因子
        self.scale_factor = new_scale

        self.redraw_bezier()
        self.update_bezier_status()

    def screen_to_world(self, x, y):
        """将屏幕坐标转换为世界坐标"""
        world_x = (x - self.offset_x) / self.scale_factor
        world_y = (y - self.offset_y) / self.scale_factor
        return world_x, world_y

    def world_to_screen(self, x, y):
        """将世界坐标转换为屏幕坐标"""
        screen_x = x * self.scale_factor + self.offset_x
        screen_y = y * self.scale_factor + self.offset_y
        return screen_x, screen_y

    def add_point(self, x=None, y=None):
        """添加控制点，如果没有指定坐标，则在中心添加"""
        if x is None or y is None:
            # 转换屏幕中心到世界坐标
            x, y = self.screen_to_world(self.actual_width // 2, self.actual_height // 2)

        self.control_points.append((x, y))
        self.selected_point = len(self.control_points) - 1
        self.redraw_bezier()

    def delete_selected(self):
        """删除选中的控制点"""
        if self.selected_point is not None and 0 <= self.selected_point < len(self.control_points):
            del self.control_points[self.selected_point]
            self.selected_point = None
            self.redraw_bezier()

    def clear_all(self):
        """清空所有控制点"""
        if messagebox.askyesno("确认", "确定要清空所有控制点吗?"):
            self.control_points = []
            self.selected_point = None
            self.redraw_bezier()

    def on_bezier_canvas_click(self, event):
        """处理画布点击事件"""
        world_x, world_y = self.screen_to_world(event.x, event.y)

        # 检查是否点击了已有点（使用屏幕坐标进行距离判断）
        for i, (x, y) in enumerate(self.control_points):
            screen_x, screen_y = self.world_to_screen(x, y)
            if math.hypot(screen_x - event.x, screen_y - event.y) <= 10:  # 10像素范围内视为点击点
                self.selected_point = i
                self.dragging = True
                self.redraw_bezier()
                return

        # 否则添加新点
        self.add_point(world_x, world_y)

    def on_bezier_drag(self, event):
        """处理拖动事件"""
        if self.dragging and self.selected_point is not None:
            # 更新选中点的坐标（世界坐标）
            world_x, world_y = self.screen_to_world(event.x, event.y)
            self.control_points[self.selected_point] = (world_x, world_y)
            self.redraw_bezier()

    def on_bezier_release(self, event):
        """处理鼠标释放事件"""
        self.dragging = False

    def on_bezier_mouse_move(self, event):
        """处理鼠标移动事件，更新状态栏"""
        world_x, world_y = self.screen_to_world(event.x, event.y)
        self.bezier_status_var.set(
            f"屏幕坐标: ({event.x}, {event.y}) | 世界坐标: ({int(world_x)}, {int(world_y)}) "
            f"| 控制点数量: {len(self.control_points)} | 缩放: {self.scale_factor}x "
            f"| 画布尺寸: {self.actual_width}x{self.actual_height}"
        )

    def update_bezier_status(self):
        """更新状态栏信息"""
        # 获取当前鼠标在画布上的位置
        x = self.bezier_canvas.winfo_pointerx() - self.bezier_canvas.winfo_rootx()
        y = self.bezier_canvas.winfo_pointery() - self.bezier_canvas.winfo_rooty()

        # 创建一个简单的对象来模拟Event
        class MockEvent:
            def __init__(self, x, y):
                self.x = x
                self.y = y

        # 使用模拟的Event对象调用on_mouse_move
        self.on_bezier_mouse_move(MockEvent(x, y))

    def get_bezier_point(self, t):
        """根据参数t获取贝塞尔曲线上的点"""
        if len(self.control_points) < 2:
            return None

        n = len(self.control_points) - 1
        x, y = 0, 0

        for i in range(n + 1):
            # 贝塞尔曲线公式
            binom = math.comb(n, i)
            term = binom * (t ** i) * ((1 - t) ** (n - i))
            x += term * self.control_points[i][0]
            y += term * self.control_points[i][1]

        return (x, y)

    def bezier_curve(self, num_points=100):
        """计算贝塞尔曲线上的点"""
        curve_points = []
        for t in [i / num_points for i in range(num_points + 1)]:
            point = self.get_bezier_point(t)
            if point:
                curve_points.append(point)
        return curve_points

    def draw_1x_bounds(self):
        """在0.5x缩放时绘制1x范围的标记框"""
        if self.scale_factor == 0.5:
            # 计算1x范围在世界坐标系中的边界
            world_left, world_top = self.screen_to_world(0, 0)
            world_right, world_bottom = self.screen_to_world(self.actual_width, self.actual_height)

            # 转换回屏幕坐标
            screen_left, screen_top = self.world_to_screen(world_left, world_top)
            screen_right, screen_bottom = self.world_to_screen(world_right, world_bottom)

            # 绘制标记框
            self.bezier_canvas.create_rectangle(
                screen_left, screen_top, screen_right, screen_bottom,
                outline=self.colors["boundary"], dash=(2, 4), width=2
            )
            # 添加标记文本
            self.bezier_canvas.create_text(
                screen_left + 5, screen_top + 15,
                text="1x 范围",
                fill=self.colors["boundary"],
                font=("SimHei", 9)
            )

    def redraw_bezier(self):
        """重绘画布"""
        self.bezier_canvas.delete("all")

        # 当缩放为0.5x时，绘制1x范围的标记框
        self.draw_1x_bounds()

        # 绘制贝塞尔曲线
        if len(self.control_points) >= 2:
            curve_points = self.bezier_curve()
            if curve_points:
                # 转换世界坐标到屏幕坐标
                screen_curve = [self.world_to_screen(x, y) for x, y in curve_points]
                self.bezier_canvas.create_line(screen_curve, fill=self.colors["bezier_curve"], width=2)

        # 绘制控制点之间的连线
        if len(self.control_points) >= 2:
            screen_points = [self.world_to_screen(x, y) for x, y in self.control_points]
            self.bezier_canvas.create_line(screen_points, fill=self.colors["control_line"], dash=(4, 2))

        # 绘制控制点
        for i, (x, y) in enumerate(self.control_points):
            screen_x, screen_y = self.world_to_screen(x, y)
            color = self.colors["selected_point"] if i == self.selected_point else self.colors["control_point"]
            # 控制点用圆形表示
            self.bezier_canvas.create_oval(
                screen_x - 8, screen_y - 8, screen_x + 8, screen_y + 8,
                fill=color,
                outline=self.colors["border"]
            )
            # 显示点的序号
            self.bezier_canvas.create_text(
                screen_x + 12, screen_y - 12,
                text=str(i),
                fill=self.colors["text"]
            )

    # ------------------------------
    # 轨迹绘制标签页相关功能
    # ------------------------------
    def create_trail_widgets(self):
        # 控制面板
        control_frame = ttk.Frame(self.trail_frame, padding="5", style="Dark.TFrame")
        control_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(control_frame, text="轨迹绘制:", style="Dark.TLabel").pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="清除轨迹", command=self.clear_trail, style="Dark.TButton").pack(side=tk.LEFT,
                                                                                                        padx=5)

        # 画布框架 - 消除白边
        self.trail_canvas_frame = ttk.Frame(
            self.trail_frame,
            padding="5",
            relief=tk.SUNKEN,
            borderwidth=1,
            style="Dark.TFrame"
        )
        self.trail_canvas_frame.pack(fill=tk.BOTH, expand=True)

        # 创建画布
        self.trail_canvas = tk.Canvas(
            self.trail_canvas_frame,
            bg=self.colors["bg_secondary"],
            width=self.canvas_width,
            height=self.canvas_height,
            highlightbackground=self.colors["border"],  # 画布边框颜色
            highlightthickness=1  # 边框厚度
        )
        self.trail_canvas.pack(fill=tk.BOTH, expand=True)

        # 状态栏
        self.trail_status_var = tk.StringVar()
        self.trail_status_var.set("按住鼠标左键拖动绘制轨迹")
        status_bar = ttk.Label(
            self.trail_frame,
            textvariable=self.trail_status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            style="Status.TLabel"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 绑定画布尺寸变化事件
        self.trail_canvas.bind("<Configure>", self.on_trail_canvas_configure)
        self.trail_actual_width = self.canvas_width
        self.trail_actual_height = self.canvas_height

    def bind_trail_events(self):
        self.trail_canvas.bind("<Button-1>", self.on_trail_mouse_down)
        self.trail_canvas.bind("<B1-Motion>", self.on_trail_mouse_drag)
        self.trail_canvas.bind("<ButtonRelease-1>", self.on_trail_mouse_up)
        self.trail_canvas.bind("<Motion>", self.on_trail_mouse_move)

    def on_trail_canvas_configure(self, event):
        """当画布尺寸变化时更新实际尺寸"""
        self.trail_actual_width = event.width
        self.trail_actual_height = event.height

    def on_trail_mouse_down(self, event):
        """鼠标按下开始绘制轨迹，记录开始时间"""
        self.drawing_trail = True
        self.trail_start_time = time.time()  # 记录开始时间戳
        # 记录起始点，包含时间戳（相对时间，单位：秒）
        self.trail_points = [(event.x, event.y, 0.0)]
        self.redraw_trail()

    def on_trail_mouse_drag(self, event):
        """鼠标拖动时记录轨迹点和时间戳"""
        if self.drawing_trail:
            # 计算相对开始时间的时间戳（秒）
            current_time = time.time() - self.trail_start_time
            # 直接记录所有经过的点，不做平滑处理
            self.trail_points.append((event.x, event.y, current_time))
            self.redraw_trail()

    def on_trail_mouse_up(self, event):
        """鼠标释放结束绘制，更新总时长"""
        self.drawing_trail = False
        # 记录最后一个点
        if self.trail_points:
            current_time = time.time() - self.trail_start_time
            if current_time != self.trail_points[-1][2]:
                self.trail_points.append((event.x, event.y, current_time))
                self.trail_duration = current_time  # 更新总时长
                self.redraw_trail()

    def on_trail_mouse_move(self, event):
        """更新轨迹绘制页的状态栏"""
        duration_text = f"总时长: {self.trail_duration:.2f}s | " if self.trail_duration > 0 else ""
        self.trail_status_var.set(
            f"{duration_text}坐标: ({event.x}, {event.y}) | 轨迹点数量: {len(self.trail_points)} | 按住鼠标左键拖动绘制轨迹"
        )

    def clear_trail(self):
        """清除当前轨迹"""
        self.trail_points = []
        self.trail_duration = 0
        self.redraw_trail()

    def redraw_trail(self):
        """重绘轨迹"""
        self.trail_canvas.delete("all")

        # 绘制轨迹
        if len(self.trail_points) >= 2:
            # 提取x,y坐标用于绘制线条
            line_points = [(p[0], p[1]) for p in self.trail_points]
            self.trail_canvas.create_line(line_points, fill=self.colors["trail_line"], width=2)

        # 绘制轨迹起点
        if self.trail_points:
            start_x, start_y, _ = self.trail_points[0]
            self.trail_canvas.create_oval(
                start_x - 5, start_y - 5, start_x + 5, start_y + 5,
                fill=self.colors["start_point"],
                outline=self.colors["border"]
            )
            self.trail_canvas.create_text(
                start_x + 10, start_y - 10,
                text="起点",
                fill=self.colors["start_point"]
            )

            # 绘制轨迹终点
            end_x, end_y, _ = self.trail_points[-1]
            self.trail_canvas.create_oval(
                end_x - 5, end_y - 5, end_x + 5, end_y + 5,
                fill=self.colors["end_point"],
                outline=self.colors["border"]
            )
            self.trail_canvas.create_text(
                end_x + 10, end_y - 10,
                text="终点",
                fill=self.colors["end_point"]
            )

    def get_trail_point(self, t):
        """轨迹绘制的参数方程接口，根据参数t获取对应点的坐标"""
        if not self.trail_points or len(self.trail_points) < 2 or self.trail_duration <= 0:
            return None

        # 计算目标时间
        target_time = t * self.trail_duration

        # 找到目标时间所在的区间
        for i in range(len(self.trail_points) - 1):
            x1, y1, t1 = self.trail_points[i]
            x2, y2, t2 = self.trail_points[i + 1]

            if t1 <= target_time <= t2:
                # 计算时间比例
                if t2 - t1 == 0:
                    ratio = 0
                else:
                    ratio = (target_time - t1) / (t2 - t1)

                # 线性插值计算坐标
                x = x1 + ratio * (x2 - x1)
                y = y1 + ratio * (y2 - y1)
                return (x, y)

        # 如果t超过1，返回终点
        if t >= 1.0:
            return (self.trail_points[-1][0], self.trail_points[-1][1])

        # 如果t小于0，返回起点
        return (self.trail_points[0][0], self.trail_points[0][1])


if __name__ == "__main__":
    root = tk.Tk()
    app = BezierEditor(root)
    root.mainloop()
