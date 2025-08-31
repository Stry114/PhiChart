import math
import numpy as np


def insert_mid_points(x, y):
    """在每个原始区间插入3个中间点（线性插值）"""
    x_extended = []
    y_extended = []
    n = len(x)

    for i in range(n - 1):
        x0, x1 = x[i], x[i + 1]
        y0, y1 = y[i], y[i + 1]
        dx = x1 - x0
        dy = y1 - y0

        # 添加原始起点
        x_extended.append(x0)
        y_extended.append(y0)

        # 插入3个中间点（线性插值）
        for j in range(1, 4):
            t = j / 4  # 1/4, 2/4, 3/4 位置
            x_extended.append(x0 + t * dx)
            y_extended.append(y0 + t * dy)

    # 添加最后一个原始点
    x_extended.append(x[-1])
    y_extended.append(y[-1])

    return x_extended, y_extended


class CubicSpline:
    """三次样条插值类（接受单个x值）"""
    # 保持原有实现不变
    def __init__(self, x, y, insertPoint=False):
        self.x = list(x)
        self.y = list(y)
        self.n = len(x)
        self.h = [self.x[i + 1] - self.x[i] for i in range(self.n - 1)]
        self.coeffs = self._compute_coefficients()

    def _compute_coefficients(self):
        n = self.n
        h = self.h
        y = self.y

        A = [[0.0] * n for _ in range(n)]
        B = [0.0] * n

        A[0][0] = 1.0
        A[-1][-1] = 1.0

        for i in range(1, n - 1):
            A[i][i - 1] = h[i - 1]
            A[i][i] = 2 * (h[i - 1] + h[i])
            A[i][i + 1] = h[i]
            B[i] = 3 * ((y[i + 1] - y[i]) / h[i] - (y[i] - y[i - 1]) / h[i - 1])

        c = self._gauss_elimination(A, B)

        coeffs = []
        for i in range(n - 1):
            a = y[i]
            b = (y[i + 1] - y[i]) / h[i] - h[i] * (c[i + 1] + 2 * c[i]) / 3
            d = (c[i + 1] - c[i]) / (3 * h[i])
            coeffs.append((a, b, c[i], d))

        return coeffs

    def _gauss_elimination(self, A, B):
        n = len(B)
        for i in range(n):
            max_row = i
            for j in range(i, n):
                if abs(A[j][i]) > abs(A[max_row][i]):
                    max_row = j

            A[i], A[max_row] = A[max_row], A[i]
            B[i], B[max_row] = B[max_row], B[i]

            pivot = A[i][i]
            if abs(pivot) < 1e-10:
                raise ValueError("矩阵奇异，无法求解")

            for j in range(i + 1, n):
                factor = A[j][i] / pivot
                B[j] -= factor * B[i]
                for k in range(i, n):
                    A[j][k] -= factor * A[i][k]

        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            sum_val = B[i]
            for j in range(i + 1, n):
                sum_val -= A[i][j] * x[j]
            x[i] = sum_val / A[i][i]

        return x

    def __call__(self, x):
        segment = 0
        while segment < self.n - 2 and x > self.x[segment + 1]:
            segment += 1

        a, b, c, d = self.coeffs[segment]
        dx = x - self.x[segment]
        return a + b * dx + c * dx **2 + d * dx** 3


class BezierCurve:
    """贝塞尔曲线类（接受单个x值）"""
    # 保持原有实现不变
    def __init__(self, x, y):
        points = sorted(zip(x, y), key=lambda p: p[0])
        self.x = [p[0] for p in points]
        self.y = [p[1] for p in points]
        self.n = len(self.x)
        self.controls = list(zip(self.x, self.y))

        self.t_values = [i / 1000 for i in range(1001)]
        self.curve_points = [self._bezier_point(t) for t in self.t_values]
        self.curve_x = [p[0] for p in self.curve_points]
        self.curve_y = [p[1] for p in self.curve_points]

    def _combination(self, n, k):
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        k = min(k, n - k)
        result = 1
        for i in range(k):
            result = result * (n - i) // (i + 1)
        return result

    def _bezier_point(self, t):
        n = self.n - 1
        x, y = 0.0, 0.0
        for i in range(self.n):
            comb_val = self._combination(n, i)
            bernstein = comb_val * (t ** i) * ((1 - t) ** (n - i))
            x += bernstein * self.controls[i][0]
            y += bernstein * self.controls[i][1]
        return (x, y)

    def __call__(self, x):
        if x <= self.curve_x[0]:
            return self.curve_y[0]
        if x >= self.curve_x[-1]:
            return self.curve_y[-1]

        left, right = 0, len(self.curve_x) - 1
        while right - left > 1:
            mid = (left + right) // 2
            if self.curve_x[mid] < x:
                left = mid
            else:
                right = mid

        t = (x - self.curve_x[left]) / (self.curve_x[right] - self.curve_x[left])
        return self.curve_y[left] + t * (self.curve_y[right] - self.curve_y[left])


class QuadraticSpline:
    """二次样条插值类（平滑力度介于线性和三次样条之间）"""
    def __init__(self, x, y):
        # 确保x单调并去重
        points = sorted(zip(x, y), key=lambda p: p[0])
        self.x = [p[0] for p in points]
        self.y = [p[1] for p in points]
        self.n = len(self.x)
        if self.n < 2:
            raise ValueError("至少需要2个数据点")
        self.h = [self.x[i+1] - self.x[i] for i in range(self.n-1)]
        self.coeffs = self._compute_coefficients()

    def _compute_coefficients(self):
        """计算二次样条系数（每段为二次函数：a + b*(x-x0) + c*(x-x0)^2）"""
        n = self.n
        h = self.h
        y = self.y

        # 构建方程求解导数（假设首段导数为0，可调整）
        A = [[0.0]*(n-1) for _ in range(n-1)]
        B = [0.0]*(n-1)

        # 第一个方程：假设首段二阶导数为0（简化条件）
        A[0][0] = 1.0
        B[0] = 0.0

        # 中间方程：保证一阶导数连续
        for i in range(1, n-2):
            A[i][i-1] = h[i-1]
            A[i][i] = 2*(h[i-1] + h[i])
            A[i][i+1] = h[i]
            B[i] = 3*((y[i+1] - y[i])/h[i] - (y[i] - y[i-1])/h[i-1])

        # 最后一个方程：假设末段二阶导数为0
        A[-1][-1] = 1.0
        B[-1] = 0.0

        # 求解二阶导数
        c = self._gauss_elimination(A, B)

        # 计算每段的系数
        coeffs = []
        for i in range(n-1):
            a = y[i]
            b = (y[i+1] - y[i])/h[i] - h[i]*(2*c[i] + c[i+1])/3 if i < n-2 else (y[i+1] - y[i])/h[i]
            coeffs.append((a, b, c[i]))
        return coeffs

    def _gauss_elimination(self, A, B):
        """高斯消元法求解线性方程组"""
        n = len(B)
        for i in range(n):
            max_row = i
            for j in range(i, n):
                if abs(A[j][i]) > abs(A[max_row][i]):
                    max_row = j
            A[i], A[max_row] = A[max_row], A[i]
            B[i], B[max_row] = B[max_row], B[i]

            pivot = A[i][i]
            if abs(pivot) < 1e-10:
                raise ValueError("矩阵奇异，无法求解二次样条")

            for j in range(i+1, n):
                factor = A[j][i] / pivot
                B[j] -= factor * B[i]
                for k in range(i, n):
                    A[j][k] -= factor * A[i][k]

        x = [0.0]*n
        for i in range(n-1, -1, -1):
            sum_val = B[i]
            for j in range(i+1, n):
                sum_val -= A[i][j] * x[j]
            x[i] = sum_val / A[i][i]
        return x

    def __call__(self, x):
        """获取单个x值对应的插值结果"""
        # 查找x所在区间
        segment = 0
        while segment < self.n - 2 and x > self.x[segment + 1]:
            segment += 1

        a, b, c = self.coeffs[segment]
        dx = x - self.x[segment]
        return a + b * dx + c * dx** 2


class MovingAverage:
    """移动平均平滑（小窗口，平滑力度弱）"""
    def __init__(self, x, y, window_size=3):
        # 确保x单调
        points = sorted(zip(x, y), key=lambda p: p[0])
        self.x = [p[0] for p in points]
        self.y = [p[1] for p in points]
        self.n = len(self.x)
        self.window_size = max(1, min(window_size, self.n))  # 窗口大小限制在有效范围内
        self.smoothed_y = self._compute_smoothed()

    def _compute_smoothed(self):
        """计算平滑后的y值"""
        smoothed = []
        half_window = self.window_size // 2
        for i in range(self.n):
            # 计算窗口范围（避免越界）
            start = max(0, i - half_window)
            end = min(self.n, i + half_window + 1)
            # 窗口内平均值
            window_mean = sum(self.y[start:end]) / (end - start)
            smoothed.append(window_mean)
        return smoothed

    def __call__(self, x):
        """获取单个x值对应的平滑结果（通过线性插值实现）"""
        # 边界处理
        if x <= self.x[0]:
            return self.smoothed_y[0]
        if x >= self.x[-1]:
            return self.smoothed_y[-1]

        # 查找x所在区间
        left, right = 0, self.n - 1
        while right - left > 1:
            mid = (left + right) // 2
            if self.x[mid] < x:
                left = mid
            else:
                right = mid

        # 线性插值
        t = (x - self.x[left]) / (self.x[right] - self.x[left])
        return self.smoothed_y[left] + t * (self.smoothed_y[right] - self.smoothed_y[left])


class LocalSmoothing:
    """局部平滑类（通过参数r控制平滑范围）"""

    def __init__(self, x, y, r=0.3):
        # 确保x单调并去重
        points = sorted(zip(x, y), key=lambda p: p[0])
        self.x = [p[0] for p in points]
        self.y = [p[1] for p in points]
        self.n = len(self.x)
        if self.n < 2:
            raise ValueError("至少需要2个数据点")
        if not (0 <= r <= 1):
            raise ValueError("参数r必须在0到1之间")

        self.r = r  # 平滑范围控制参数（0~1）
        self.cubic_spline = CubicSpline(self.x, self.y)  # 使用三次样条作为平滑算法

    def __call__(self, x):
        """获取x值对应的结果：数据点附近平滑，其他区域线性插值"""
        # 边界处理：超出范围保持边界值
        if x <= self.x[0]:
            return self.y[0]
        if x >= self.x[-1]:
            return self.y[-1]

        # 查找x所在区间
        i = 0
        while i < self.n - 2 and x > self.x[i + 1]:
            i += 1

        # 首末区间不平滑处理（使用线性插值）
        if i == 0 or i == self.n - 2:
            return self._linear_interpolation(x, i)

        # 计算当前区间长度
        h = self.x[i + 1] - self.x[i]
        if h == 0:  # 避免除零错误
            return self.y[i]

        # 计算到两端点的距离与区间长度的比值
        dx_left = x - self.x[i]
        dx_right = self.x[i + 1] - x
        ratio_left = dx_left / h
        ratio_right = dx_right / h

        # 判断是否在平滑区域（靠近左端点或右端点）
        if ratio_left < self.r or ratio_right < self.r:
            # 数据点附近使用三次样条平滑
            return self.cubic_spline(x)
        else:
            # 远离数据点区域使用线性插值
            return self._linear_interpolation(x, i)

    def _linear_interpolation(self, x, i):
        """在指定区间i上进行线性插值"""
        x0, x1 = self.x[i], self.x[i + 1]
        y0, y1 = self.y[i], self.y[i + 1]
        t = (x - x0) / (x1 - x0)
        return y0 + t * (y1 - y0)

class Interpolation:
    """插值算法类，支持线性插值、拉格朗日插值和埃尔米特插值"""

    def __init__(self, x, y, dy=None, method='linear'):
        """
        初始化插值器

        参数:
            x: 节点x坐标列表
            y: 节点y坐标列表
            dy: 节点导数值列表（仅埃尔米特插值需要）
            method: 插值方法，可选'linear'（线性）、'lagrange'（拉格朗日）、'hermite'（埃尔米特）
        """
        # 验证输入
        if len(x) != len(y):
            raise ValueError("x和y的长度必须相同")

        if method == 'hermite' and (dy is None or len(dy) != len(x)):
            raise ValueError("使用埃尔米特插值时必须提供与x长度相同的dy")

        # 转换为numpy数组以便计算
        self.x = np.array(x, dtype=np.float64)
        self.y = np.array(y, dtype=np.float64)
        self.dy = np.array(dy, dtype=np.float64) if dy is not None else None

        # 检查节点是否排序，如未排序则进行排序
        if not np.all(np.diff(self.x) > 0):
            indices = np.argsort(self.x)
            self.x = self.x[indices]
            self.y = self.y[indices]
            if self.dy is not None:
                self.dy = self.dy[indices]

        self.method = method

    def __call__(self, x):
        """
        计算插值结果

        参数:
            x: 单个数值或数组

        返回:
            插值结果
        """
        # 如果输入是数组，逐个计算
        if isinstance(x, (list, np.ndarray)):
            return np.array([self._interpolate_single(val) for val in x])
        else:
            return self._interpolate_single(x)

    def _interpolate_single(self, x):
        """对单个点进行插值计算"""
        if self.method == 'linear':
            return self._linear_interpolation(x)
        elif self.method == 'lagrange':
            return self._lagrange_interpolation(x)
        elif self.method == 'hermite':
            return self._hermite_interpolation(x)
        else:
            raise ValueError(f"不支持的插值方法: {self.method}")

    def _linear_interpolation(self, x):
        """线性插值"""
        # 找到x所在的区间
        n = len(self.x)

        # 处理边界情况
        if x <= self.x[0]:
            return self.y[0]
        if x >= self.x[-1]:
            return self.y[-1]

        # 找到x所在的区间
        i = np.searchsorted(self.x, x) - 1

        # 线性插值公式
        x0, y0 = self.x[i], self.y[i]
        x1, y1 = self.x[i + 1], self.y[i + 1]

        return y0 + (y1 - y0) * (x - x0) / (x1 - x0)

    def _lagrange_interpolation(self, x):
        """拉格朗日插值"""
        n = len(self.x)
        result = 0.0

        for i in range(n):
            # 计算拉格朗日基函数
            l_i = 1.0
            for j in range(n):
                if i != j:
                    l_i *= (x - self.x[j]) / (self.x[i] - self.x[j])
            result += self.y[i] * l_i

        return result

    def _hermite_interpolation(self, x):
        """埃尔米特插值（带一阶导数约束）"""
        n = len(self.x)
        result = 0.0

        for i in range(n):
            # 计算函数值基函数alpha_i(x)
            alpha = 1.0
            beta_sum = 0.0

            for j in range(n):
                if j != i:
                    factor = (x - self.x[j]) / (self.x[i] - self.x[j])
                    alpha *= factor
                    beta_sum += 1 / (self.x[i] - self.x[j])

            alpha = alpha ** 2 * (1 - 2 * beta_sum * (x - self.x[i]))

            # 计算导数值基函数beta_i(x)
            li = 1.0
            for j in range(n):
                if j != i:
                    li *= (x - self.x[j]) / (self.x[i] - self.x[j])
            beta = (x - self.x[i]) * (li ** 2)

            # 累加结果
            result += alpha * self.y[i] + beta * self.dy[i]

        return result


# 示例用法
if __name__ == "__main__":
    x_points = [0, 2, 4, 6, 8, 10]
    y_points = [math.sin(x) for x in x_points]

    # 初始化各平滑器
    cubic = CubicSpline(x_points, y_points)
    bezier = BezierCurve(x_points, y_points)
    quadratic = QuadraticSpline(x_points, y_points)
    moving_avg = MovingAverage(x_points, y_points, window_size=3)  # 小窗口（3个点）

    # 测试单个值
    x_test = 3.5
    print(f"x={x_test}处的各方法结果：")
    print(f"三次样条: {cubic(x_test)}")
    print(f"贝塞尔曲线: {bezier(x_test)}")
    print(f"二次样条: {quadratic(x_test)}")
    print(f"移动平均(窗口3): {moving_avg(x_test)}")