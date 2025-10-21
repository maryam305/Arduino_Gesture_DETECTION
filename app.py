from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, DictProperty, ListProperty
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.animation import Animation
import serial
import serial.tools.list_ports
import threading
import time

# ========= CONFIG =========
BAUD_RATES = [9600, 38400, 115200]
# ==========================


class GestureVisualizer(Widget):
    """Visualizer for gestures with live background color and animations"""
    gesture_text = StringProperty("Waiting for gesture...")
    emoji = StringProperty("✋")
    bg_color = ListProperty([0.15, 0.15, 0.2])  # Dark background

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.color_instr = Color(rgba=self.bg_color + [1])
            self.bg_rect = RoundedRectangle(
                radius=[20], pos=self.pos, size=self.size)

        # Add border
        with self.canvas.after:
            self.border_color = Color(rgba=[0.3, 0.3, 0.35, 1])
            self.border = Line(rounded_rectangle=(
                self.x, self.y, self.width, self.height, 20), width=2)

        self.bind(pos=self.update_rect, size=self.update_rect)
        self.bind(bg_color=self.update_color)

        self.label = Label(
            text=self.emoji,
            font_size="140sp",
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle'
        )
        self.add_widget(self.label)

    def update_rect(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.border.rounded_rectangle = (
            self.x, self.y, self.width, self.height, 20)

    def update_color(self, *args):
        """Updates the color in the Kivy canvas with animation"""
        self.color_instr.rgba = (*self.bg_color, 1)

    def on_emoji(self, instance, value):
        # Pulse animation when emoji changes
        self.label.text = value
        anim = Animation(font_size="160sp", duration=0.15) + \
            Animation(font_size="140sp", duration=0.15)
        anim.start(self.label)


class GestureAppUI(BoxLayout):
    connection_status = StringProperty("🔌 Not Connected")
    total_gestures = NumericProperty(0)
    gesture_count = DictProperty(
        {"LEFT": 0, "CENTER": 0, "RIGHT": 0, "NONE": 0})

    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=12, padding=20, **kwargs)
        self.ser = None
        self.is_connected = False

        # Set dark background
        with self.canvas.before:
            Color(0.1, 0.1, 0.12, 1)
            self.rect = RoundedRectangle(
                pos=self.pos, size=self.size, radius=[0])
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Title with gradient effect
        self.title = Label(
            text="🎯 Gesture Detection System",
            font_size="30sp",
            bold=True,
            color=(0.2, 0.9, 1, 1),  # Cyan
            size_hint=(1, 0.12)
        )

        # Port Spinner with better contrast
        self.port_spinner = Spinner(
            text="🔍 Scanning COM Ports...",
            size_hint=(1, 0.08),
            background_color=(0.2, 0.2, 0.25, 1),
            color=(1, 1, 1, 1),
            font_size="16sp"
        )
        Clock.schedule_interval(self.refresh_ports, 3)

        # Connect Button - Bright Green
        self.connect_btn = Button(
            text="✅ CONNECT",
            size_hint=(1, 0.08),
            background_color=(0, 0.8, 0.3, 1),  # Bright green
            color=(1, 1, 1, 1),
            bold=True,
            font_size="18sp",
            on_press=self.connect_hc05
        )

        # Disconnect Button - Bright Red
        self.disconnect_btn = Button(
            text="❌ DISCONNECT",
            size_hint=(1, 0.08),
            background_color=(1, 0.2, 0.2, 1),  # Bright red
            color=(1, 1, 1, 1),
            bold=True,
            font_size="18sp",
            on_press=self.disconnect_hc05,
            disabled=True
        )

        # Status with better visibility
        self.status_label = Label(
            text=self.connection_status,
            font_size="18sp",
            color=(1, 1, 0, 1),  # Yellow for high contrast
            size_hint=(1, 0.08),
            bold=True
        )

        # Visualizer
        self.visualizer = GestureVisualizer(size_hint=(1, 0.46))

        # Stats with better colors
        self.stats_label = Label(
            text="📊 LEFT: 0 | CENTER: 0 | RIGHT: 0 | NONE: 0",
            font_size="17sp",
            color=(0.9, 0.9, 0.9, 1),
            size_hint=(1, 0.1),
            bold=True
        )

        # Layout
        self.add_widget(self.title)
        self.add_widget(self.port_spinner)
        self.add_widget(self.connect_btn)
        self.add_widget(self.disconnect_btn)
        self.add_widget(self.status_label)
        self.add_widget(self.visualizer)
        self.add_widget(self.stats_label)

    def update_bg(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def refresh_ports(self, dt):
        """Scan for available COM ports"""
        ports = [p.device for p in serial.tools.list_ports.comports()]
        if ports:
            self.port_spinner.values = ports
            if self.port_spinner.text not in ports and "Scanning" in self.port_spinner.text:
                self.port_spinner.text = ports[0]
        else:
            self.port_spinner.values = ["No Ports Found"]
            self.port_spinner.text = "No Ports Found"

    def connect_hc05(self, instance):
        """Connect to HC-05 Bluetooth module"""
        com = self.port_spinner.text

        if "COM" not in com and "tty" not in com:  # Support Unix systems too
            self.status_label.text = "⚠️ Please select a valid COM port"
            self.status_label.color = (1, 0.5, 0, 1)
            return

        try:
            for baud in BAUD_RATES:
                try:
                    self.ser = serial.Serial(com, baudrate=baud, timeout=1)
                    time.sleep(2)  # Wait for connection
                    self.ser.reset_input_buffer()
                    self.ser.reset_output_buffer()
                    self.is_connected = True
                    print(f"✅ Connected at {baud} baud")
                    break
                except Exception as e:
                    print(f"Failed at {baud}: {e}")
                    continue

            if not self.is_connected:
                raise Exception("Failed to connect at any baud rate")

            self.status_label.text = f"✅ Connected to {com}"
            self.status_label.color = (0, 1, 0.5, 1)  # Bright green
            self.connect_btn.disabled = True
            self.disconnect_btn.disabled = False
            self.visualizer.bg_color = [0.15, 0.4, 0.25]  # Dark green

            # Start reading thread
            threading.Thread(target=self.read_serial, daemon=True).start()

        except Exception as e:
            self.status_label.text = f"❌ {str(e)}"
            self.status_label.color = (1, 0.3, 0.3, 1)

    def disconnect_hc05(self, instance):
        """Disconnect from HC-05"""
        self.is_connected = False
        try:
            if self.ser and self.ser.is_open:
                self.ser.close()
        except:
            pass

        self.connect_btn.disabled = False
        self.disconnect_btn.disabled = True
        self.status_label.text = "🔌 Disconnected"
        self.status_label.color = (1, 1, 0, 1)
        self.visualizer.bg_color = [0.15, 0.15, 0.2]
        self.visualizer.emoji = "✋"

    def update_ui(self, gesture):
        """Update UI based on detected gesture with high contrast colors"""
        colors = {
            "LEFT": [0.1, 0.3, 0.8],    # Deep blue
            "CENTER": [0.1, 0.7, 0.3],  # Bright green
            "RIGHT": [0.8, 0.1, 0.4],   # Deep pink/red
            "NONE": [0.3, 0.3, 0.35]    # Gray
        }

        emojis = {
            "LEFT": "👈",
            "CENTER": "👆",
            "RIGHT": "👉",
            "NONE": "✋"
        }

        self.visualizer.emoji = emojis.get(gesture, "✋")
        self.visualizer.bg_color = colors.get(gesture, [0.15, 0.15, 0.2])
        self.visualizer.gesture_text = f"{gesture} detected"

        # Update stats
        if gesture in self.gesture_count:
            self.gesture_count[gesture] += 1
            self.total_gestures += 1

        self.stats_label.text = (
            f"📊 LEFT: {self.gesture_count['LEFT']} | "
            f"CENTER: {self.gesture_count['CENTER']} | "
            f"RIGHT: {self.gesture_count['RIGHT']} | "
            f"NONE: {self.gesture_count['NONE']}"
        )

    def read_serial(self):
        """Read data from serial port in background thread"""
        print("🔄 Starting serial read thread...")

        while self.is_connected:
            try:
                if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
                    line = self.ser.readline().decode("utf-8", errors="ignore").strip()

                    if not line:
                        continue

                    print(f"📥 Received: {line}")

                    # Parse gesture from Arduino
                    if "[BT:" in line:
                        gesture = line.split(
                            "[BT:")[-1].split("]")[0].strip().upper()
                    else:
                        gesture = line.upper()

                    # Valid gestures
                    if gesture in ["LEFT", "CENTER", "RIGHT", "NONE"]:
                        Clock.schedule_once(lambda dt: self.update_ui(gesture))

            except Exception as e:
                print(f"❌ Serial error: {e}")
                Clock.schedule_once(
                    lambda dt: setattr(self.status_label,
                                       'text', f"⚠️ Error: {e}")
                )
                Clock.schedule_once(
                    lambda dt: setattr(self.status_label,
                                       'color', (1, 0.5, 0, 1))
                )

            time.sleep(0.05)  # Reduced delay for faster response


class GestureApp(App):
    def build(self):
        self.title = "HC-05 Gesture Detector"
        return GestureAppUI()


if __name__ == '__main__':
    GestureApp().run()
