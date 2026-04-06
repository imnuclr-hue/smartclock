import os
os.environ["KIVY_WINDOW"] = "sdl2"
os.environ["KIVY_GL_BACKEND"] = "sdl2"

from datetime import datetime, timedelta

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.slider import Slider

from sensors.bh1750_sensor import BH1750Sensor
from sensors.bme280_sensor import BME280
from utils.settings import load_settings, save_settings
from utils.logger import log_error

light_sens = 150.0


class ButtonLabel(ButtonBehavior, Label):
    def on_press(self):
        self.color = (0.7, 0.7, 0.7, 1)

    def on_release(self):
        self.color = (1, 1, 1, 1)


class MinimalClock(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=dp(40), spacing=dp(10), **kwargs)

        with self.canvas.before:
            Color(0.05, 0.05, 0.05, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_bg, pos=self._update_bg)

        self.time_label = Label(font_size="140sp", halign="center", valign="middle", bold=True, color=(1, 1, 1, 1), markup=True)
        self.add_widget(self.time_label)

        self.secondary_label = Label(font_size="40sp", halign="center", valign="middle", color=(0.8, 0.8, 0.8, 1))
        self.add_widget(self.secondary_label)

        self.env_label = Label(font_size="28sp", halign="center", valign="middle", color=(0.6, 0.8, 1, 1))
        self.add_widget(self.env_label)

    def _update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos


class ClockScreen(Screen):
    pass


class SettingsScreen(Screen):
    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings

        layout = BoxLayout(orientation="vertical", padding=dp(40), spacing=dp(20))

        with layout.canvas.before:
            Color(0.07, 0.07, 0.07, 1)
            self.bg = Rectangle(size=layout.size, pos=layout.pos)

        layout.bind(size=self._update_bg, pos=self._update_bg)

        layout.add_widget(Label(text="Settings", font_size="60sp", color=(1, 1, 1, 1)))

        layout.add_widget(Label(text="Brightness Min", font_size="32sp"))
        self.slider_min = Slider(min=0.0, max=1.0, value=self.settings.get("brightness_min", 0.25))
        layout.add_widget(self.slider_min)

        layout.add_widget(Label(text="Brightness Max", font_size="32sp"))
        self.slider_max = Slider(min=0.0, max=1.0, value=self.settings.get("brightness_max", 1.0))
        layout.add_widget(self.slider_max)

        self.slider_min.bind(value=self.save_settings)
        self.slider_max.bind(value=self.save_settings)

        self.time_format_label = ButtonLabel(
            text="24-Hour" if self.settings.get("time_format_24h", True) else "12-Hour",
            font_size="48sp"
        )
        self.time_format_label.bind(on_release=self.toggle_time_format)
        layout.add_widget(self.time_format_label)

        self.add_widget(layout)

    def save_settings(self, *args):
        self.settings["brightness_min"] = self.slider_min.value
        self.settings["brightness_max"] = self.slider_max.value
        save_settings(self.settings)

    def toggle_time_format(self, *args):
        val = not self.settings.get("time_format_24h", True)
        self.settings["time_format_24h"] = val
        save_settings(self.settings)
        self.time_format_label.text = "24-Hour" if val else "12-Hour"

    def _update_bg(self, *args):
        self.bg.size = self.children[0].size
        self.bg.pos = self.children[0].pos


class CountdownScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical", padding=dp(40), spacing=dp(20))

        self.mode = "duration"

        self.preview_label = Label(text="00:00", font_size="90sp")
        layout.add_widget(self.preview_label)

        self.mode_label = ButtonLabel(text="Mode: Duration", font_size="32sp")
        self.mode_label.bind(on_release=self.toggle_mode)
        layout.add_widget(self.mode_label)

        self.hours = 0
        self.minutes = 0
        self.seconds = 0

        def make_row(name, func):
            row = BoxLayout()
            row.add_widget(Label(text=name))

            minus = ButtonLabel(text="-", font_size="60sp")
            plus = ButtonLabel(text="+", font_size="60sp")

            minus.bind(on_release=lambda *a: func(-1))
            plus.bind(on_release=lambda *a: func(1))

            row.add_widget(minus)
            row.add_widget(plus)
            return row

        layout.add_widget(make_row("Hours", self.adjust_hours))
        layout.add_widget(make_row("Minutes", self.adjust_minutes))
        layout.add_widget(make_row("Seconds", self.adjust_seconds))

        start = ButtonLabel(text="START", font_size="50sp", color=(0.3, 1, 0.3, 1))
        stop = ButtonLabel(text="STOP", font_size="50sp", color=(1, 0.3, 0.3, 1))

        start.bind(on_release=self.start_countdown)
        stop.bind(on_release=self.stop_countdown)

        layout.add_widget(start)
        layout.add_widget(stop)

        self.add_widget(layout)

    def toggle_mode(self, *args):
        if self.mode == "duration":
            self.mode = "target_time"
            self.mode_label.text = "Mode: Target Time"
        else:
            self.mode = "duration"
            self.mode_label.text = "Mode: Duration"

        self.update_preview()

    def adjust_hours(self, d):
        self.hours = max(0, min(23, self.hours + d))
        self.update_preview()

    def adjust_minutes(self, d):
        self.minutes = max(0, min(59, self.minutes + d))
        self.update_preview()

    def adjust_seconds(self, d):
        self.seconds = max(0, min(59, self.seconds + d))
        self.update_preview()

    def update_preview(self):
        # ALWAYS show hours now
        self.preview_label.text = f"{self.hours:02d}:{self.minutes:02d}:{self.seconds:02d}"
    
    def get_total_seconds(self):
        return self.hours * 3600 + self.minutes * 60 + self.seconds

    def start_countdown(self, *args):
        app = App.get_running_app()

        if self.mode == "duration":
            total = self.get_total_seconds()
        else:
            now = datetime.now()
            target = now.replace(hour=self.hours, minute=self.minutes, second=self.seconds, microsecond=0)
            if target <= now:
                target += timedelta(days=1)
            total = int((target - now).total_seconds())

        app.enter_countdown_mode(total)
        self.manager.current = "clock"

    def stop_countdown(self, *args):
        app = App.get_running_app()
        app.countdown_active = False
        app.countdown_remaining = 0


class SmartClockApp(App):
    def build(self):
        self.settings = load_settings()
        self.light_sensor = BH1750Sensor()
        self.bme = BME280()

        self.countdown_active = False
        self.countdown_remaining = 0

        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))

        self.clock_layout = MinimalClock()
        self.clock_screen = ClockScreen(name="clock")
        self.clock_screen.add_widget(self.clock_layout)

        self.sm.add_widget(self.clock_screen)
        self.sm.add_widget(SettingsScreen(self.settings, name="settings"))
        self.sm.add_widget(CountdownScreen(name="countdown"))

        Clock.schedule_interval(self.update_time, 1)
        Clock.schedule_interval(self.update_brightness, 1)
        Clock.schedule_interval(self.update_environment, 2)

        Window.bind(on_touch_up=self.on_touch_down)
        Window.fullscreen = True

        return self.sm

    def on_touch_down(self, window, touch):
        if touch.grab_current:
            return

        if touch.x < 100:
            self.sm.current = "clock"
        elif touch.x > Window.width - 100:
            self.sm.current = "settings"
        elif touch.y < 100:
            self.sm.current = "countdown"

    def enter_countdown_mode(self, total):
        self.countdown_remaining = total
        self.countdown_active = total > 0

    def update_time(self, dt):
        try:
            now = datetime.now()

            # 12h / 24h formatting
            if self.settings.get("time_format_24h", True):
                time_str = now.strftime("%H:%M:%S")
                suffix = ""
            else:
                time_str = now.strftime("%I:%M:%S")
                suffix = now.strftime("%p")

            if self.countdown_active:
                if self.countdown_remaining <= 0:
                    self.countdown_active = False
                    self.clock_layout.time_label.text = "Time's up"
                    self.clock_layout.secondary_label.text = f"{time_str} {suffix}".strip()
                    return

                self.countdown_remaining -= 1
                t = self.countdown_remaining

                hrs = t // 3600
                mins = (t % 3600) // 60
                secs = t % 60

                # ✅ Restore minus sign
                self.clock_layout.time_label.text = f"-{hrs:02d}:{mins:02d}:{secs:02d}"

                # ✅ Restore small time display
                self.clock_layout.secondary_label.text = f"{time_str} {suffix}".strip()

            else:
                if suffix:
                    self.clock_layout.time_label.text = f"{time_str} [size=48]{suffix}[/size]"
                else:
                    self.clock_layout.time_label.text = time_str

                self.clock_layout.secondary_label.text = ""

        except Exception as e:
            log_error("Time error", e)

    def update_brightness(self, dt):
        lux = self.light_sensor.read_lux()
        if lux is None:
            return

        t = max(0, min(lux, 1000)) / light_sens
        bmin = self.settings.get("brightness_min", 0.25)
        bmax = self.settings.get("brightness_max", 1.0)
        b = bmin + t * (bmax - bmin)

        self.clock_layout.time_label.color = (b, b, b, 1)

    def update_environment(self, dt):
        try:
            data = self.bme.read()
            print("BME:", data)

            if data:
                temp, pressure, humidity = data
                self.clock_layout.env_label.text = f"{temp:.1f}°C  {humidity:.0f}%  {pressure:.0f}hPa"

        except Exception as e:
            log_error("BME280 error", e)

def start_display():
    SmartClockApp().run()
