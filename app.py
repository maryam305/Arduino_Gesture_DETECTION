# main.py
from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.utils import platform

# Threading & parsing
import threading
import time

# Optional desktop serial support
try:
    import serial
    import serial.tools.list_ports
    HAS_PYSERIAL = True
except Exception:
    HAS_PYSERIAL = False

# Optional Android Bluetooth via pyjnius
ANDROID_BLUETOOTH_AVAILABLE = False
if platform == "android":
    try:
        from jnius import autoclass, cast
        ANDROID_BLUETOOTH_AVAILABLE = True
    except Exception:
        ANDROID_BLUETOOTH_AVAILABLE = False

# --- KV UI ---
KV = """
<MainRoot>:
    orientation: "vertical"
    padding: dp(10)
    spacing: dp(8)
    canvas.before:
        Color:
            rgba: (0.06,0.13,0.38,1)  # dark blue background
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        size_hint_y: None
        height: dp(72)
        spacing: dp(8)
        Label:
            text: "🎯 Gesture Detection System"
            font_size: '22sp'
            bold: True
            color: (1,1,1,1)
        Label:
            text: root.conn_status
            size_hint_x: None
            width: dp(220)
            color: root.conn_color

    BoxLayout:
        size_hint_y: None
        height: dp(56)
        spacing: dp(8)
        Spinner:
            id: port_spinner
            text: root.port_text
            values: root.port_list
            size_hint_x: .6
        Button:
            text: "🔄 Refresh"
            size_hint_x: .2
            on_release: root.refresh_ports()
        Button:
            id: connect_btn
            text: root.connect_text
            size_hint_x: .2
            on_release: root.toggle_connect()

    FloatLayout:
        size_hint_y: None
        height: dp(300)
        canvas.before:
            Color:
                rgba: (0.1,0.1,0.12,1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            id: hand_label
            text: root.hand_emoji
            font_size: '120sp'
            center_x: self.parent.center_x
            center_y: self.parent.center_y + dp(20)
            color: root.hand_color
        Label:
            id: gesture_text
            text: root.gesture_text
            font_size: '18sp'
            size_hint: None, None
            size: self.texture_size
            center_x: self.parent.center_x
            y: dp(10)
            color: root.hand_color

        # position indicators (left/center/right)
        Label:
            text: "◀"
            font_size: '36sp'
            center_x: self.parent.x + dp(60)
            center_y: self.parent.center_y + dp(-40)
            opacity: 1 if root.ind_left else .15
        Label:
            text: "●"
            font_size: '28sp'
            center_x: self.parent.center_x
            center_y: self.parent.center_y + dp(-40)
            color: (0.3,1,0.4,1) if root.ind_center else (1,1,1,0.15)
        Label:
            text: "▶"
            font_size: '36sp'
            center_x: self.parent.right - dp(60)
            center_y: self.parent.center_y + dp(-40)
            opacity: 1 if root.ind_right else .15

    GridLayout:
        cols: 2
        row_default_height: dp(100)
        row_force_default: True
        spacing: dp(8)
        BoxLayout:
            orientation: "vertical"
            canvas.before:
                Color:
                    rgba: (0.1,0.1,0.12,1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "👈 LEFT"
                font_size: '20sp'
            Label:
                text: str(root.count_left)
                font_size: '28sp'
                color: (0.2,0.6,1,1)
        BoxLayout:
            orientation: "vertical"
            canvas.before:
                Color:
                    rgba: (0.1,0.1,0.12,1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "👉 RIGHT"
                font_size: '20sp'
            Label:
                text: str(root.count_right)
                font_size: '28sp'
                color: (1,0.4,0.6,1)
        BoxLayout:
            orientation: "vertical"
            canvas.before:
                Color:
                    rgba: (0.1,0.1,0.12,1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "✋ CENTER"
                font_size: '20sp'
            Label:
                text: str(root.count_center)
                font_size: '28sp'
                color: (0.2,1,0.4,1)
        BoxLayout:
            orientation: "vertical"
            canvas.before:
                Color:
                    rgba: (0.1,0.1,0.12,1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "🚫 NONE"
                font_size: '20sp'
            Label:
                text: str(root.count_none)
                font_size: '28sp'
                color: (0.6,0.6,0.6,1)

    BoxLayout:
        size_hint_y: None
        height: dp(48)
        spacing: dp(8)
        Button:
            text: "🔄 Reset Stats"
            on_release: root.reset_stats()
        Label:
            text: "Last:"
            size_hint_x: None
            width: dp(50)
            color: (1,1,1,0.7)
        Label:
            text: root.last_received
            color: (1,1,1,0.9)

    BoxLayout:
        size_hint_y: None
        height: dp(36)
        spacing: dp(8)
        Label:
            text: "Mode:"
            size_hint_x: None
            width: dp(60)
            color: (1,1,1,0.7)
        Label:
            text: root.mode_text
            color: (1,1,1,0.9)
"""

# --- Backend Implementations ---
class BluetoothBackendBase:
    """Base interface - must implement connect(port), disconnect(), is_connected(), read_loop(callback)"""
    def connect(self, port):
        raise NotImplementedError()
    def disconnect(self):
        raise NotImplementedError()
    def is_connected(self):
        return False
    def read_loop(self, callback):
        """Start background read thread and call callback(line) on each received line."""
        raise NotImplementedError()

class SerialBackend(BluetoothBackendBase):
    def __init__(self):
        self.ser = None
        self._stop = threading.Event()
        self._thread = None

    def connect(self, port, baud=9600):
        if not HAS_PYSERIAL:
            raise RuntimeError("pyserial not available")
        self.ser = serial.Serial(port=port, baudrate=baud, timeout=1)
        time.sleep(1.2)
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        return True

    def disconnect(self):
        self._stop.set()
        if self.ser and self.ser.is_open:
            try:
                self.ser.close()
            except Exception:
                pass

    def is_connected(self):
        return self.ser is not None and self.ser.is_open

    def read_loop(self, callback):
        self._stop.clear()
        def _read():
            while not self._stop.is_set() and self.is_connected():
                try:
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                        if line:
                            callback(line)
                    else:
                        time.sleep(0.02)
                except Exception as e:
                    print("Serial read error:", e)
                    time.sleep(0.1)
        self._thread = threading.Thread(target=_read, daemon=True)
        self._thread.start()

if ANDROID_BLUETOOTH_AVAILABLE:
    # Android classic Bluetooth SPP backend
    from jnius import autoclass, cast
    UUID = autoclass('java.util.UUID')

    class AndroidBluetoothBackend(BluetoothBackendBase):
        def __init__(self):
            self.adapter = autoclass('android.bluetooth.BluetoothAdapter').getDefaultAdapter()
            self.socket = None
            self._stop = threading.Event()
            self._thread = None

        def connect(self, mac_address, uuid_str="00001101-0000-1000-8000-00805F9B34FB"):
            if not self.adapter:
                raise RuntimeError("No Bluetooth adapter")
            remote = self.adapter.getRemoteDevice(mac_address)
            uuid = UUID.fromString(uuid_str)
            # createRfcommSocketToServiceRecord
            try:
                self.socket = remote.createRfcommSocketToServiceRecord(uuid)
                activity = autoclass('org.kivy.android.PythonActivity').mActivity
                self.socket.connect()
                # getInputStream
                self.input_stream = self.socket.getInputStream()
            except Exception as e:
                raise RuntimeError(f"Android Bluetooth connect failed: {e}")
            return True

        def disconnect(self):
            self._stop.set()
            try:
                if self.socket:
                    self.socket.close()
            except Exception:
                pass

        def is_connected(self):
            return self.socket is not None

        def read_loop(self, callback):
            self._stop.clear()
            def _read():
                buf = bytearray()
                while not self._stop.is_set() and self.is_connected():
                    try:
                        # read available bytes (blocking small read)
                        if self.input_stream.available() > 0:
                            b = self.input_stream.read()
                            if b == -1:
                                time.sleep(0.05)
                                continue
                            if b == 10 or b == 13:
                                if buf:
                                    line = bytes(buf).decode('utf-8', errors='ignore').strip()
                                    buf.clear()
                                    if line:
                                        callback(line)
                            else:
                                buf.append(b)
                        else:
                            time.sleep(0.02)
                    except Exception as e:
                        print("Android read error:", e)
                        time.sleep(0.1)
            self._thread = threading.Thread(target=_read, daemon=True)
            self._thread.start()

else:
    AndroidBluetoothBackend = None

# --- GUI Root ---
class MainRoot(BoxLayout):
    # UI state properties
    conn_status = StringProperty("Not Connected")
    conn_color = (1, 0.27, 0.27, 1)
    connect_text = StringProperty("🔌 Connect")
    port_list = []
    port_text = StringProperty("Select port")
    hand_emoji = StringProperty("✋")
    hand_color = (0.8,0.8,0.8,1)
    gesture_text = StringProperty("Waiting for gesture...")
    ind_left = BooleanProperty(False)
    ind_center = BooleanProperty(True)
    ind_right = BooleanProperty(False)
    count_left = NumericProperty(0)
    count_right = NumericProperty(0)
    count_center = NumericProperty(0)
    count_none = NumericProperty(0)
    last_received = StringProperty("No data yet")
    mode_text = StringProperty("Auto / Mock")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backend = None
        self.reading = False
        self.total = 0
        self._detect_mode()  # sets mode_text and backend availability
        Clock.schedule_once(lambda dt: self.refresh_ports(), 0.2)

    def _detect_mode(self):
        if platform == "android" and ANDROID_BLUETOOTH_AVAILABLE:
            self.mode_text = "Android Bluetooth (pyjnius)"
        elif HAS_PYSERIAL:
            self.mode_text = "Desktop Serial (pyserial)"
        else:
            self.mode_text = "Mock (no Bluetooth available)"

    def refresh_ports(self):
        if HAS_PYSERIAL:
            ports = list(serial.tools.list_ports.comports())
            self.port_list = [p.device for p in ports]
            self.port_text = self.port_list[0] if self.port_list else "No ports"
        else:
            self.port_list = []
            self.port_text = "No serial"

    def toggle_connect(self):
        if self.reading:
            self.disconnect()
        else:
            self.connect()

    def connect(self):
        # Decide backend based on environment
        try:
            if platform == "android" and ANDROID_BLUETOOTH_AVAILABLE:
                # On Android we expect user to provide MAC in spinner or use a known address
                backend = AndroidBluetoothBackend()
                # For ease, spinner holds MAC or we fallback to mock
                mac = self.port_text if self.port_text and ":" in self.port_text else None
                if not mac:
                    # If no mac provided, enter mock mode
                    self._start_mock_reader()
                    return
                backend.connect(mac)
                self.backend = backend
            elif HAS_PYSERIAL:
                backend = SerialBackend()
                port = self.port_text if self.port_text and self.port_text != "No ports" else None
                if not port:
                    self._start_mock_reader()
                    return
                # try common baud rates as in original
                for baud in (9600, 38400, 115200):
                    try:
                        backend.connect(port, baud=baud)
                        break
                    except Exception:
                        continue
                if not backend.is_connected():
                    raise RuntimeError("Could not open serial")
                self.backend = backend
            else:
                # no bluetooth/serial available -> mock
                self._start_mock_reader()
                return

            # success - update UI
            self.conn_status = f"Connected to {self.port_text}"
            self.conn_color = (0.24,0.69,0.33,1)
            self.connect_text = "⏸️ Disconnect"
            self.reading = True
            # start read loop
            self.backend.read_loop(self._on_line_received)
        except Exception as e:
            self.conn_status = f"Error: {e}"
            self.conn_color = (1,0.27,0.27,1)
            print("Connect error:", e)

    def disconnect(self):
        try:
            if self.backend:
                self.backend.disconnect()
            self.reading = False
            self.backend = None
        except Exception as e:
            print("Disconnect error:", e)
        self.conn_status = "Not Connected"
        self.conn_color = (1,0.27,0.27,1)
        self.connect_text = "🔌 Connect"

    def _start_mock_reader(self):
        # Useful for testing UI on desktop without hardware
        self.conn_status = "Mock mode (no physical device)"
        self.conn_color = (0.9,0.6,0.2,1)
        self.connect_text = "⏸️ Stop Mock"
        self.reading = True
        def mock_loop():
            choices = ["[BT: LEFT]", "[BT: RIGHT]", "[BT: CENTER]", "[BT: NONE]"]
            while self.reading:
                line = choices[int(time.time()) % 4]
                self._on_line_received(line)
                time.sleep(1.0)
        t = threading.Thread(target=mock_loop, daemon=True)
        t.start()

    def reset_stats(self):
        self.count_left = self.count_right = self.count_center = self.count_none = 0
        self.total = 0

    @mainthread
    def _update_last(self, line):
        now = time.strftime("%H:%M:%S")
        short = (line[:30] + '...') if len(line) > 30 else line
        self.last_received = f"{short} at {now}"

    def _on_line_received(self, line):
        # Called from background thread
        print("Received:", line)
        # parse like original: [BT: GESTURE]
        gesture = None
        if "[BT:" in line:
            start = line.find("[BT:") + 4
            end = line.find("]", start)
            if start > 3 and end > start:
                gesture = line[start:end].strip().upper()
        else:
            gesture = line.strip().upper()

        # update last label
        Clock.schedule_once(lambda dt, l=line: self._update_last(l), 0)

        if gesture in ("LEFT", "RIGHT", "CENTER", "NONE"):
            # schedule UI animation
            Clock.schedule_once(lambda dt, g=gesture: self.show_gesture(g), 0)
            # update counts
            if gesture == "LEFT":
                self.count_left += 1
            elif gesture == "RIGHT":
                self.count_right += 1
            elif gesture == "CENTER":
                self.count_center += 1
            elif gesture == "NONE":
                self.count_none += 1
            self.total += 1
        else:
            print("Invalid gesture:", gesture)

    def show_gesture(self, gesture):
        # animations for hand label: move to left/center/right and change emoji/color/text
        hand = self.ids.get('hand_label')
        gt = self.ids.get('gesture_text')
        if not hand or not gt:
            return

        w = self.width
        center_x = self.width / 2
        y = hand.center_y

        config = {
            "LEFT": {"x": self.x + 100, "emoji": "👈", "color": (0.2,0.6,1,1), "text": "◀️ LEFT DETECTED"},
            "CENTER": {"x": center_x, "emoji": "✋", "color": (0.2,1,0.4,1), "text": "✋ CENTER DETECTED"},
            "RIGHT": {"x": self.right - 100, "emoji": "👉", "color": (1,0.4,0.6,1), "text": "▶️ RIGHT DETECTED"},
            "NONE": {"x": center_x, "emoji": "🚫", "color": (0.6,0.6,0.6,1), "text": "⭕ NO GESTURE"}
        }

        c = config.get(gesture, config["NONE"])

        # update indicator booleans
        self.ind_left = (gesture == "LEFT")
        self.ind_center = (gesture == "CENTER" or gesture == "NONE")
        self.ind_right = (gesture == "RIGHT")

        # animate position & pulse
        Animation.cancel_all(hand)
        anim = Animation(center_x=c["x"], d=0.25, t='out_quad')
        anim &= Animation(font_size='140sp' if gesture != "NONE" else '120sp', d=0.12)
        anim.start(hand)

        # pulse effect after move
        def pulse(*args):
            Animation.cancel_all(hand)
            a = Animation(font_size='160sp', d=0.12) + Animation(font_size='120sp', d=0.12)
            a.start(hand)
        Clock.schedule_once(pulse, 0.28)

        # set emoji & colors & text
        self.hand_emoji = c["emoji"]
        self.hand_color = c["color"]
        self.gesture_text = c["text"]

class GestureApp(App):
    def build(self):
        Window.clearcolor = (0.06,0.13,0.38,1)
        Builder.load_string(KV)
        return MainRoot()

if __name__ == "__main__":
    GestureApp().run()
