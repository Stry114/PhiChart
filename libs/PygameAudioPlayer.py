import pygame
import time
import os
import wave
import threading
from pygame import mixer
from threading import Event


class NonBlockingAudioPlayer:
    def __init__(self, file_path):
        """初始化非阻塞音频播放器"""
        # 初始化Pygame音频系统
        pygame.init()
        mixer.init()

        # 音频文件信息
        self.file_path = file_path
        self.file_type = self._get_file_type()

        # 音频参数
        self.sample_rate = 44100
        self.channels = 2
        self.sample_width = 2
        self.total_frames = 0
        self.duration = 0.0
        self.audio_data = None

        # 播放控制事件（非阻塞核心）
        self.play_event = Event()  # 播放事件
        self.pause_event = Event()  # 暂停事件
        self.stop_event = Event()  # 停止事件
        self.seek_event = Event()  # 跳转事件
        self.speed_event = Event()  # 变速事件

        # 播放状态变量
        self.current_speed = 1.0
        self.current_frame = 0
        self.target_seek = 0.0  # 目标跳转位置
        self.target_speed = 1.0  # 目标速度
        self.is_playing = False
        self.is_paused = False

        # 线程安全锁
        self.state_lock = threading.Lock()

        # 加载音频
        self._load_audio()

        # 播放线程
        self.play_thread = None
        self._start_play_thread()

    def _get_file_type(self):
        ext = os.path.splitext(self.file_path)[1].lower()
        if ext in ('.wav', '.wave'):
            return 'wav'
        elif ext == '.mp3':
            return 'mp3'
        else:
            raise ValueError(f"不支持的格式: {ext}")

    def _load_audio(self):
        if self.file_type == 'wav':
            self._load_wav()
        else:
            self._load_mp3()
        self.duration = self.total_frames / self.sample_rate

    def _load_wav(self):
        with wave.open(self.file_path, 'rb') as wf:
            self.sample_rate = wf.getframerate()
            self.channels = wf.getnchannels()
            self.sample_width = wf.getsampwidth()
            self.total_frames = wf.getnframes()
            self.audio_data = wf.readframes(self.total_frames)

    def _load_mp3(self):
        try:
            sound = pygame.mixer.Sound(self.file_path)
            self.audio_data = sound.get_raw()
            self.total_frames = len(self.audio_data) // (self.sample_width * self.channels)
        except pygame.error as e:
            raise RuntimeError(f"MP3加载失败: {str(e)}")

    def _start_play_thread(self):
        """启动播放控制线程（非阻塞）"""
        self.play_thread = threading.Thread(target=self._play_loop)
        self.play_thread.daemon = True  # 守护线程，主进程退出时自动结束
        self.play_thread.start()

    def _play_loop(self):
        """播放控制循环（在独立线程中运行）"""
        channel = None
        sound = None
        current_rate = self.sample_rate

        while True:
            # 等待播放事件
            self.play_event.wait()

            # 检查是否需要停止
            if self.stop_event.is_set():
                self._reset_events()
                if channel:
                    channel.stop()
                channel = None
                sound = None
                continue

            # 检查是否需要暂停
            if self.pause_event.is_set():
                if channel:
                    channel.pause()
                # 等待暂停结束或停止信号
                while self.pause_event.is_set() and not self.stop_event.is_set():
                    time.sleep(0.05)

                if self.stop_event.is_set():
                    self._reset_events()
                    if channel:
                        channel.stop()
                    channel = None
                    sound = None
                    continue
                else:
                    # 恢复播放
                    if channel:
                        channel.unpause()

            # 检查是否需要变速
            if self.speed_event.is_set():
                with self.state_lock:
                    self.current_speed = self.target_speed
                self.speed_event.clear()

                # 重新初始化音频系统以应用新速度
                new_rate = int(self.sample_rate * self.current_speed)
                if new_rate != current_rate:
                    current_rate = new_rate
                    mixer.quit()
                    mixer.init(frequency=current_rate, size=-16,
                               channels=self.channels, buffer=1024)

                    # 重新创建声音对象
                    if sound:
                        channel.stop()
                    sound = pygame.mixer.Sound(self.audio_data)
                    channel = sound.play(loops=0)

            # 检查是否需要跳转
            if self.seek_event.is_set():
                with self.state_lock:
                    target_frame = int(self.target_seek * self.sample_rate)
                    self.current_frame = target_frame

                self.seek_event.clear()

                # 实现跳转
                if sound:
                    channel.stop()
                sound = pygame.mixer.Sound(self.audio_data)
                # 计算跳转的起始位置（秒）
                start_pos = self.current_frame / (self.sample_rate * self.current_speed)
                channel = sound.play(loops=0)

            # 初始化声音对象（如果需要）
            if not sound and not self.stop_event.is_set():
                sound = pygame.mixer.Sound(self.audio_data)
                start_pos = self.current_frame / (self.sample_rate * self.current_speed)
                channel = sound.play(loops=0)

            # 更新当前播放位置
            if channel and channel.get_busy() and not self.pause_event.is_set():
                with self.state_lock:
                    # 计算当前帧位置
                    elapsed = channel.get_pos() / 1000.0 * self.current_speed
                    self.current_frame = min(
                        int(self.current_frame + elapsed * self.sample_rate),
                        self.total_frames
                    )
            elif not self.pause_event.is_set() and not self.stop_event.is_set():
                # 播放结束
                self.stop()

            # 短暂休眠，避免CPU占用过高
            time.sleep(0.05)

    def _reset_events(self):
        """重置所有事件状态"""
        self.play_event.clear()
        self.pause_event.clear()
        self.stop_event.clear()
        self.seek_event.clear()
        self.speed_event.clear()

    def play(self, speed=0.5):
        """开始播放"""
        with self.state_lock:
            self.is_playing = True
            self.is_paused = False
            self.current_speed = speed
            self.target_speed = speed

        self._reset_events()
        self.speed_event.set()  # 触发速度设置
        self.play_event.set()  # 触发播放

    def pause(self):
        """暂停播放（非阻塞）"""
        with self.state_lock:
            if self.is_playing and not self.is_paused:
                self.is_paused = True
                self.pause_event.set()

    def resume(self):
        """恢复播放（非阻塞）"""
        with self.state_lock:
            if self.is_playing and self.is_paused:
                self.is_paused = False
                self.pause_event.clear()

    def stop(self):
        """停止播放（非阻塞）"""
        with self.state_lock:
            self.is_playing = False
            self.is_paused = False
            self.current_frame = 0

        self.stop_event.set()

    def seek(self, seconds):
        """跳转到指定时间（非阻塞）"""
        if seconds < 0:
            seconds = 0
        if seconds > self.duration:
            seconds = self.duration

        with self.state_lock:
            self.target_seek = seconds

        self.seek_event.set()  # 触发跳转事件

    def set_speed(self, speed):
        """设置播放速度（非阻塞）"""
        if speed <= 0:
            raise ValueError("速度必须为正数")

        with self.state_lock:
            self.target_speed = speed

        self.speed_event.set()  # 触发速度事件

    def get_current_time(self):
        """获取当前播放时间"""
        with self.state_lock:
            return self.current_frame / self.sample_rate

    def is_active(self):
        """检查是否正在播放或暂停中"""
        with self.state_lock:
            return self.is_playing

    def __del__(self):
        """清理资源"""
        self.stop()
        mixer.quit()
        pygame.quit()


# 使用示例 - 演示非阻塞特性
if __name__ == "__main__":
    try:
        # 替换为你的音频文件
        audio_file = "test.wav"  # 或 "test.mp3"

        print("创建播放器实例（非阻塞）")
        player = NonBlockingAudioPlayer(audio_file)
        print(f"音频时长: {player.duration:.2f}秒")

        print("开始0.5倍速播放（非阻塞）")
        player.play(speed=0.5)

        # 主进程可以继续执行其他任务
        for i in range(5):
            print(f"主进程正在执行任务... {i + 1}/5")
            time.sleep(1)  # 模拟主进程工作

        print(f"暂停播放（当前位置: {player.get_current_time():.2f}秒）")
        player.pause()

        # 主进程继续工作
        print("主进程继续处理其他事务...")
        time.sleep(2)

        print("恢复播放")
        player.resume()

        # 主进程继续工作
        for i in range(3):
            print(f"主进程继续执行任务... {i + 1}/3")
            time.sleep(1)

        print(f"跳转到10秒位置（当前位置: {player.get_current_time():.2f}秒）")
        player.seek(10)

        # 主进程继续工作
        for i in range(4):
            print(f"主进程继续执行任务... {i + 1}/4")
            time.sleep(1)

        print("设置为0.8倍速播放")
        player.set_speed(0.8)

        # 主进程继续工作
        for i in range(3):
            print(f"主进程继续执行任务... {i + 1}/3")
            time.sleep(1)

        print("停止播放")
        player.stop()
        print("程序结束")

    except Exception as e:
        print(f"发生错误: {e}")
