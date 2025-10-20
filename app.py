import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time

BAUD_RATE = 9600  # Change to 38400 if your HC-05 uses that baud rate

class GestureVisualizer(tk.Canvas):
    """Visual feedback for gestures with animated hand"""
    def __init__(self, parent):
        super().__init__(parent, height=250, bg='#1A1A2E', highlightthickness=0)
        self.center_x = 300
        self.center_y = 125
        
        # Create hand emoji that will move
        self.hand_id = self.create_text(
            self.center_x, self.center_y, text="✋", font=("Arial", 100), fill="#FFFFFF"
        )
        
        # Gesture text below
        self.gesture_text = self.create_text(
            self.center_x, self.center_y + 90, text="Waiting for gesture...", 
            font=("Arial", 18, "bold"), fill="#AAAAAA"
        )
        
        # Position indicators
        self.left_indicator = self.create_oval(30, 110, 60, 140, fill="#2196F3", outline="", state='hidden')
        self.center_indicator = self.create_oval(285, 110, 315, 140, fill="#4CAF50", outline="", state='hidden')
        self.right_indicator = self.create_oval(540, 110, 570, 140, fill="#FF6B9D", outline="", state='hidden')
        
        self.current_position = "CENTER"
        self.animation_in_progress = False
    
    def show_gesture(self, gesture):
        """Animate hand to gesture position"""
        if self.animation_in_progress:
            return
        
        gesture_config = {
            "LEFT": {
                "x": 100,
                "emoji": "👈",
                "color": "#2196F3",
                "text": "◀️ LEFT DETECTED",
                "indicator": self.left_indicator
            },
            "CENTER": {
                "x": self.center_x,
                "emoji": "✋",
                "color": "#4CAF50",
                "text": "✋ CENTER DETECTED",
                "indicator": self.center_indicator
            },
            "RIGHT": {
                "x": 500,
                "emoji": "👉",
                "color": "#FF6B9D",
                "text": "▶️ RIGHT DETECTED",
                "indicator": self.right_indicator
            },
            "NONE": {
                "x": self.center_x,
                "emoji": "🚫",
                "color": "#9E9E9E",
                "text": "⭕ NO GESTURE",
                "indicator": self.center_indicator
            }
        }
        
        if gesture not in gesture_config:
            return
        
        config = gesture_config[gesture]
        
        # Hide all indicators
        self.itemconfig(self.left_indicator, state='hidden')
        self.itemconfig(self.center_indicator, state='hidden')
        self.itemconfig(self.right_indicator, state='hidden')
        
        # Show target indicator
        self.itemconfig(config["indicator"], state='normal')
        
        # Animate hand movement
        self.animate_to_position(config["x"], config["emoji"], config["color"], config["text"])
        self.current_position = gesture
    
    def animate_to_position(self, target_x, emoji, color, text):
        """Smooth animation to target position"""
        self.animation_in_progress = True
        current_coords = self.coords(self.hand_id)
        current_x = current_coords[0]
        
        print(f"Animating from {current_x} to {target_x}")  # Debug
        
        # Calculate steps for smooth animation
        steps = 20
        dx = (target_x - current_x) / steps
        
        def move_step(step):
            if step < steps:
                self.move(self.hand_id, dx, 0)
                self.after(15, lambda: move_step(step + 1))
            else:
                # Final position adjustment and update
                self.coords(self.hand_id, target_x, self.center_y)
                self.itemconfig(self.hand_id, text=emoji, fill=color)
                self.itemconfig(self.gesture_text, text=text, fill=color)
                
                # Pulse effect
                self.scale(self.hand_id, target_x, self.center_y, 1.2, 1.2)
                self.after(150, lambda: self.scale(self.hand_id, target_x, self.center_y, 0.833, 0.833))
                self.after(300, lambda: setattr(self, 'animation_in_progress', False))
        
        move_step(0)

class HC05App:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 HC-05 Gesture Receiver")
        self.root.geometry("600x780")
        self.root.resizable(False, False)
        self.root.configure(bg='#0F3460')
        
        self.ser = None
        self.is_connected = False
        self.gesture_count = {"LEFT": 0, "CENTER": 0, "RIGHT": 0, "NONE": 0}
        self.total_gestures = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.root, bg='#0F3460', padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        title = tk.Label(main_frame, text="🎯 Gesture Detection System", font=("Arial", 24, "bold"),
                         bg='#0F3460', fg='#FFFFFF')
        title.pack(pady=(0, 5))
        
        subtitle = tk.Label(main_frame, text="Ultrasonic HC-05 Controller", 
                           font=("Arial", 12), bg='#0F3460', fg='#AAAAAA')
        subtitle.pack(pady=(0, 20))
        
        # --- CONNECTION ---
        connection_frame = tk.Frame(main_frame, bg='#16213E', relief=tk.FLAT)
        connection_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Status
        status_container = tk.Frame(connection_frame, bg='#16213E', pady=15)
        status_container.pack(fill=tk.X)
        self.status_dot = tk.Canvas(status_container, width=20, height=20, bg='#16213E', highlightthickness=0)
        self.status_dot.pack(side=tk.LEFT, padx=(20,10))
        self.dot_id = self.status_dot.create_oval(2,2,18,18, fill='#F44336', outline='')
        self.status_label = tk.Label(status_container, text="Not Connected", font=("Arial",14,"bold"),
                                     bg='#16213E', fg='#F44336')
        self.status_label.pack(side=tk.LEFT)
        
        # Port selection
        port_frame = tk.Frame(connection_frame, bg='#16213E', pady=10)
        port_frame.pack(fill=tk.X, padx=20)
        tk.Label(port_frame, text="COM Port:", font=("Arial", 12), bg='#16213E', fg='#AAAAAA').pack(side=tk.LEFT, padx=(0,10))
        ports = serial.tools.list_ports.comports()
        self.com_var = tk.StringVar()
        self.com_box = ttk.Combobox(port_frame, values=[p.device for p in ports], textvariable=self.com_var,
                                    state="readonly", width=15, font=("Arial",11))
        self.com_box.pack(side=tk.LEFT)
        if ports: self.com_box.current(0)
        tk.Button(port_frame, text="🔄", command=self.refresh_ports, bg='#2196F3', fg='white',
                  font=("Arial",12), relief=tk.FLAT, padx=10, cursor='hand2').pack(side=tk.LEFT, padx=5)
        
        # Connect/Disconnect
        btn_frame = tk.Frame(connection_frame, bg='#16213E', pady=15)
        btn_frame.pack()
        self.connect_btn = tk.Button(btn_frame, text="🔌 Connect", command=self.connect_hc05,
                                     bg='#4CAF50', fg='white', font=("Arial",12,"bold"), relief=tk.FLAT, padx=20, pady=10,
                                     cursor='hand2')
        self.connect_btn.pack(side=tk.LEFT, padx=5)
        self.disconnect_btn = tk.Button(btn_frame, text="⏸️ Disconnect", command=self.disconnect_hc05,
                                        bg='#F44336', fg='white', font=("Arial",12,"bold"), relief=tk.FLAT, padx=20, pady=10,
                                        state=tk.DISABLED, cursor='hand2')
        self.disconnect_btn.pack(side=tk.LEFT, padx=5)
        
        # --- GESTURE VISUALIZER ---
        viz_label = tk.Label(main_frame, text="📡 Live Hand Tracking", font=("Arial",16,"bold"), 
                            bg='#0F3460', fg='#FFFFFF')
        viz_label.pack(pady=(10,5))
        self.visualizer = GestureVisualizer(main_frame)
        self.visualizer.pack(fill=tk.X, pady=(0,15))
        
        # --- STATISTICS ---
        stats_frame = tk.Frame(main_frame, bg='#16213E', pady=20)
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(15,0))
        
        tk.Label(stats_frame, text="📊 Detection Statistics", font=("Arial",14,"bold"), 
                bg='#16213E', fg='#FFFFFF').pack(pady=(0,15))
        
        # Gesture counts in grid
        count_grid = tk.Frame(stats_frame, bg='#16213E')
        count_grid.pack(pady=10)
        
        gestures = [
            ("LEFT", "👈", "#2196F3"),
            ("RIGHT", "👉", "#FF6B9D"),
            ("CENTER", "✋", "#4CAF50"),
            ("NONE", "🚫", "#9E9E9E")
        ]
        
        self.count_labels = {}
        for i, (name, emoji, color) in enumerate(gestures):
            frame = tk.Frame(count_grid, bg='#1A1A2E', relief=tk.FLAT, padx=15, pady=10)
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky='ew')
            
            tk.Label(frame, text=emoji, font=("Arial", 24), bg='#1A1A2E', fg='#FFFFFF').pack()
            tk.Label(frame, text=name, font=("Arial", 10, "bold"), bg='#1A1A2E', fg='#AAAAAA').pack()
            count_label = tk.Label(frame, text="0", font=("Arial", 20, "bold"), bg='#1A1A2E', fg=color)
            count_label.pack()
            self.count_labels[name] = count_label
        
        # Total counter
        total_frame = tk.Frame(stats_frame, bg='#0F3460', pady=15, relief=tk.FLAT)
        total_frame.pack(fill=tk.X, padx=20, pady=(15,10))
        tk.Label(total_frame, text="Total Gestures Detected:", font=("Arial", 12), 
                bg='#0F3460', fg='#AAAAAA').pack()
        self.total_label = tk.Label(total_frame, text="0", font=("Arial", 28, "bold"), 
                                    bg='#0F3460', fg='#4CAF50')
        self.total_label.pack()
        
        # Last received
        self.received_label = tk.Label(stats_frame, text="Waiting for data...", font=("Arial",11),
                                       bg='#16213E', fg='#999999')
        self.received_label.pack(pady=(10,0))
        
        # Reset button
        reset_btn = tk.Button(stats_frame, text="🔄 Reset Statistics", command=self.reset_stats,
                             bg='#FF9800', fg='white', font=("Arial",11,"bold"), relief=tk.FLAT, 
                             padx=20, pady=8, cursor='hand2')
        reset_btn.pack(pady=(10,0))
    
    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.com_box['values'] = [p.device for p in ports]
        if ports: self.com_box.current(0)
        messagebox.showinfo("Ports Refreshed", f"Found {len(ports)} port(s)")
    
    def connect_hc05(self):
        com = self.com_var.get()
        if not com:
            messagebox.showwarning("Select COM", "Please select a COM port")
            return
        try:
            # Try different baud rates
            baud_rates = [9600, 38400, 115200]
            connected = False
            
            for baud in baud_rates:
                try:
                    print(f"Trying to connect at {baud} baud...")
                    self.ser = serial.Serial(
                        port=com, 
                        baudrate=baud, 
                        timeout=2,
                        bytesize=serial.EIGHTBITS,
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_ONE
                    )
                    time.sleep(2)
                    self.ser.reset_input_buffer()
                    self.ser.reset_output_buffer()
                    print(f"Connected successfully at {baud} baud!")
                    connected = True
                    break
                except:
                    if self.ser and self.ser.is_open:
                        self.ser.close()
                    continue
            
            if not connected:
                raise Exception("Could not connect at any baud rate (tried 9600, 38400, 115200)")
            
            self.is_connected = True
            self.status_dot.itemconfig(self.dot_id, fill='#4CAF50')
            self.status_label.config(text=f"Connected to {com}", fg='#4CAF50')
            self.connect_btn.config(state=tk.DISABLED)
            self.disconnect_btn.config(state=tk.NORMAL)
            self.com_box.config(state=tk.DISABLED)
            self.received_label.config(text="✅ Connected! Listening for gestures...")
            threading.Thread(target=self.read_from_hc05, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect:\n{str(e)}")
    
    def disconnect_hc05(self):
        self.is_connected = False
        if self.ser and self.ser.is_open:
            try: self.ser.close()
            except: pass
        self.status_dot.itemconfig(self.dot_id, fill='#F44336')
        self.status_label.config(text="Not Connected", fg='#F44336')
        self.connect_btn.config(state=tk.NORMAL)
        self.disconnect_btn.config(state=tk.DISABLED)
        self.com_box.config(state='readonly')
        self.received_label.config(text="Waiting for data...")
    
    def reset_stats(self):
        self.gesture_count = {"LEFT": 0, "CENTER": 0, "RIGHT": 0, "NONE": 0}
        self.total_gestures = 0
        self.update_stats()
        messagebox.showinfo("Reset", "Statistics have been reset!")
    
    def update_stats(self):
        for gesture, count in self.gesture_count.items():
            self.count_labels[gesture].config(text=str(count))
        self.total_label.config(text=str(self.total_gestures))
    
    def read_from_hc05(self):
        print("Starting to read from HC-05...")
        while self.is_connected:
            try:
                if self.ser and self.ser.is_open and self.ser.in_waiting > 0:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    print(f"Received: '{line}'")  # Debug print
                    
                    if line:
                        # Extract gesture from [BT: GESTURE] format
                        gesture = None
                        if "[BT:" in line:
                            # Extract text between [BT: and ]
                            start = line.find("[BT:") + 4
                            end = line.find("]", start)
                            if start > 3 and end > start:
                                gesture = line[start:end].strip().upper()
                                print(f"Extracted gesture: '{gesture}'")
                        else:
                            # Try direct gesture name
                            gesture = line.upper()
                        
                        # Update received label with timestamp
                        timestamp = time.strftime("%H:%M:%S")
                        self.root.after(0, lambda l=line: self.received_label.config(
                            text=f"📨 {l[:30]}... at {timestamp}" if len(l) > 30 else f"📨 {l} at {timestamp}"
                        ))
                        
                        # Check if it's a valid gesture
                        if gesture in ["LEFT", "CENTER", "RIGHT", "NONE"]:
                            print(f"✅ Valid gesture: {gesture} - Moving hand!")
                            # Update visualizer - ANIMATE THE HAND!
                            self.root.after(0, lambda g=gesture: self.visualizer.show_gesture(g))
                            
                            # Update statistics
                            self.gesture_count[gesture] += 1
                            self.total_gestures += 1
                            self.root.after(0, self.update_stats)
                        else:
                            print(f"❌ Invalid gesture: {gesture}")
            except Exception as e:
                print(f"Read error: {e}")
            time.sleep(0.05)  # Fast polling for responsive detection

def main():
    root = tk.Tk()
    app = HC05App(root)
    root.mainloop()

if __name__ == "__main__":
    main()