import time


class FastBezierLookup:
    def __init__(self, p0, p1, p2, p3, num_samples=100):
        """
        初始化贝塞尔曲线预计算查找表（无numpy依赖）
        :param p0-p3: 四个控制点，格式为(x, y)元组
        :param num_samples: 预计算的采样点数量（默认2000）
        """
        self.p0 = p0
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.num_samples = num_samples

        # 预计算采样点
        self.x_samples, self.y_samples = self._precompute_samples()

        # 检查x是否严格单调
        if not self._is_strictly_monotonic(self.x_samples):
            raise ValueError("曲线x坐标必须严格单调（递增或递减）")

    def _precompute_samples(self):
        """预计算t∈[0,1]范围内的x和y采样点（纯Python实现）"""
        x_samples = []
        y_samples = []

        x0, y0 = self.p0
        x1, y1 = self.p1
        x2, y2 = self.p2
        x3, y3 = self.p3

        # 生成均匀分布的t值（0到1之间）
        for i in range(self.num_samples):
            t = i / (self.num_samples - 1)  # t ∈ [0, 1]
            mt = 1 - t  # 1-t

            # 计算贝塞尔曲线公式的各项
            mt3 = mt ** 3
            mt2_t = 3 * (mt ** 2) * t
            mt_t2 = 3 * mt * (t ** 2)
            t3 = t ** 3

            # 计算x和y坐标
            x = x0 * mt3 + x1 * mt2_t + x2 * mt_t2 + x3 * t3
            y = y0 * mt3 + y1 * mt2_t + y2 * mt_t2 + y3 * t3

            x_samples.append(x)
            y_samples.append(y)

        return x_samples, y_samples

    def _is_strictly_monotonic(self, arr):
        """检查数组是否严格单调（递增或递减）"""
        if len(arr) < 2:
            return True

        # 检查递增
        is_increasing = True
        for i in range(len(arr) - 1):
            if arr[i] >= arr[i + 1]:
                is_increasing = False
                break

        if is_increasing:
            return True

        # 检查递减
        is_decreasing = True
        for i in range(len(arr) - 1):
            if arr[i] <= arr[i + 1]:
                is_decreasing = False
                break

        return is_decreasing

    def get_y(self, target_x):
        """
        快速获取目标x对应的y值（二分查找+线性插值）
        """
        x = self.x_samples
        y = self.y_samples

        # 检查x是否在有效范围内
        if target_x < x[0] or target_x > x[-1]:
            raise ValueError(f"x值超出范围 [{x[0]:.2f}, {x[-1]:.2f}]")

        # 二分查找找到目标x所在的区间
        left, right = 0, len(x) - 1
        while right - left > 1:
            mid = (left + right) // 2
            if x[mid] < target_x:
                left = mid
            else:
                right = mid

        # 线性插值计算y值
        x0, y0 = x[left], y[left]
        x1, y1 = x[right], y[right]

        # 避免除零（严格单调情况下理论不会发生）
        if abs(x1 - x0) < 1e-12:
            return y0

        # 计算插值比例
        t = (target_x - x0) / (x1 - x0)
        return y0 + t * (y1 - y0)


# 测试与性能对比
if __name__ == "__main__":
    # 定义严格单调的控制点
    p0 = (0, 0)
    p1 = (2, 3)
    p2 = (5, 5)
    p3 = (8, 2)

    # 初始化快速查询器（2000个采样点）
    fast_bezier = FastBezierLookup(p0, p1, p2, p3, num_samples=2000)

    # 测试单个查询
    target_x = 4.0
    y_result = fast_bezier.get_y(target_x)
    print(f"目标x = {target_x} 对应的y值: {y_result:.6f}")

    # 性能测试：10万次查询
    num_queries = 100000
    # 生成测试用的x值列表（0到8之间均匀分布）
    x_min, x_max = fast_bezier.x_samples[0], fast_bezier.x_samples[-1]
    step = (x_max - x_min) / (num_queries - 1)
    x_values = [x_min + i * step for i in range(num_queries)]

    # 测试快速查询耗时
    start = time.time()
    for x in x_values:
        fast_bezier.get_y(x)
    fast_time = time.time() - start
    print(f"\n{num_queries}次查询耗时: {fast_time:.4f}秒")
    print(f"平均每次查询耗时: {fast_time / num_queries * 1e6:.2f}微秒")

    # 可视化（如果需要可取消注释，需安装matplotlib）
    # import matplotlib.pyplot as plt
    # plt.plot(fast_bezier.x_samples, fast_bezier.y_samples, label="贝塞尔曲线")
    # plt.scatter([p0[0], p1[0], p2[0], p3[0]],
    #             [p0[1], p1[1], p2[1], p3[1]], color='red', label="控制点")
    # plt.scatter(target_x, y_result, color='green', s=100, label=f"y={y_result:.2f}")
    # plt.xlabel("x")
    # plt.ylabel("y")
    # plt.legend()
    # plt.grid(True)
    # plt.show()
