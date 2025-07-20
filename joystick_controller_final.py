#!/usr/bin/env python3
"""
JoystickShield PC Controller - Final Game Version
Optimized for gaming, ensures proper key recognition
"""

import serial
import serial.tools.list_ports
import time
import threading
import sys
import ctypes
from collections import defaultdict

# Import input libraries
try:
    import win32api
    import win32con
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False

class GameJoystickController:
    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.key_states = defaultdict(bool)
        self.last_position = {"x": 0, "y": 0}

        # Long press functionality
        self.button_press_times = {}  # Record button press times
        self.button_states = {}  # Record button states
        self.long_press_threshold = 0.2  # Long press threshold (seconds) - 200ms
        self.long_press_triggered = {}  # Record if long press has been triggered
        self.short_press_executed = {}  # Record if short press has been executed

        # Button auto-release functionality (Arduino only sends press events)
        self.button_last_seen = {}  # Record last time button was detected
        self.button_timeout = 0.15  # Button timeout (seconds) - if no signal received for this time, consider button released

        # Direction key auto-release functionality
        self.last_direction_time = {}  # Record last direction key trigger time
        self.direction_timeout = 0.15  # Direction key timeout (seconds) - quick release when joystick stops

        # Use most compatible input method
        self.use_win32 = WIN32_AVAILABLE
        
        # Windows virtual key code mapping
        self.vk_codes = {
            'w': 0x57, 'a': 0x41, 's': 0x53, 'd': 0x44,
            'v': 0x56, 'space': 0x20, 'e': 0x45, 'f': 0x46,
            'up': 0x26, 'down': 0x28, 'left': 0x25, 'right': 0x27,
            'o': 0x4F, 'j': 0x4A, 'i': 0x49, 'k': 0x4B,  # Basic keys
            'shift': 0x10, 'ctrl': 0x11, 'alt': 0x12  # Modifier keys
        }
        
        # Key mapping configuration
        self.key_mapping = {
            # Joystick directions -> Keyboard keys (consistent with button mapping)
            "Joystick Up": "w",           # Corresponds to up button
            "Joystick Down": "s",         # Corresponds to down button
            "Joystick Left": "a",         # Corresponds to left button
            "Joystick Right": "d",        # Corresponds to right button
            "Joystick LeftUp": ["a", "w"],     # Up + Left
            "Joystick RightUp": ["d", "w"],    # Up + Right
            "Joystick LeftDown": ["a", "s"],   # Down + Left
            "Joystick RightDown": ["d", "s"],  # Down + Right

            # Buttons -> Keyboard keys (short press)
            "Joystick Button Clicked": "f",
            "Up Button Clicked": "o",
            "Down Button Clicked": "j",
            "Left Button Clicked": "i",
            "Right Button Clicked": "k",
            "E Button Clicked": "e",
            "F Button Clicked": "v",

            # Special functions
            "Joystick NotCenter": None,  # No key mapping
        }

        # Long press mapping configuration
        self.long_press_mapping = {
            "Joystick Button": "space",   # Long press joystick button -> Space
            "Up Button": "up",            # Long press up button -> Up arrow key
            "Down Button": "down",        # Long press down button -> Down arrow key
            "Left Button": "left",        # Long press left button -> Left arrow key
            "Right Button": "right",      # Long press right button -> Right arrow key
            "E Button": "shift",          # Long press E button -> Shift
            "F Button": "ctrl",           # Long press F button -> Ctrl
        }
    
    def get_foreground_window_title(self):
        """Get current active window title"""
        if not WIN32_AVAILABLE:
            return "Unknown"
        try:
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetWindowText(hwnd)
        except:
            return "Unknown"

    def ensure_game_focus(self):
        """Ensure game window has focus"""
        window_title = self.get_foreground_window_title()
        if "python" in window_title.lower() or "cmd" in window_title.lower():
            print(f"⚠️  Current active window: {window_title}")
            print("Please switch to game window!")
            return False
        return True
    
    def press_key_win32(self, key):
        """Press key using Win32 API"""
        if not self.use_win32 or key not in self.vk_codes:
            return False

        try:
            # Ensure game window is active
            if not self.ensure_game_focus():
                return False

            vk_code = self.vk_codes[key]
            win32api.keybd_event(vk_code, 0, 0, 0)
            return True
        except Exception as e:
            print(f"❌ Win32 key press failed {key}: {e}")
            return False

    def release_key_win32(self, key):
        """Release key using Win32 API"""
        if not self.use_win32 or key not in self.vk_codes:
            return False

        try:
            vk_code = self.vk_codes[key]
            win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            print(f"❌ Win32 key release failed {key}: {e}")
            return False
    
    def press_key_keyboard(self, key):
        """Press key using keyboard library"""
        if not KEYBOARD_AVAILABLE:
            return False
        try:
            keyboard.press(key)
            return True
        except Exception as e:
            print(f"❌ keyboard key press failed {key}: {e}")
            return False

    def release_key_keyboard(self, key):
        """Release key using keyboard library"""
        if not KEYBOARD_AVAILABLE:
            return False
        try:
            keyboard.release(key)
            return True
        except Exception as e:
            print(f"❌ keyboard key release failed {key}: {e}")
            return False
    
    def press_keys_continuous(self, keys):
        """Press keys (continuous state)"""
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            if not self.key_states[key]:
                success = False

                # Prefer Win32 API
                if self.use_win32:
                    success = self.press_key_win32(key)
                    method = "Win32"
                else:
                    success = self.press_key_keyboard(key)
                    method = "keyboard"

                # If preferred method fails, try backup method
                if not success:
                    if self.use_win32 and KEYBOARD_AVAILABLE:
                        success = self.press_key_keyboard(key)
                        method = "keyboard(backup)"
                    elif not self.use_win32 and WIN32_AVAILABLE:
                        success = self.press_key_win32(key)
                        method = "Win32(backup)"

                if success:
                    self.key_states[key] = True
                    print(f"🔽 Press: {key} ({method})")
                else:
                    print(f"❌ Unable to press key: {key}")
    
    def press_keys(self, keys):
        """Press keys (button event)"""
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            success_press = False
            success_release = False
            method = ""

            # Press
            if self.use_win32:
                success_press = self.press_key_win32(key)
                method = "Win32"
            else:
                success_press = self.press_key_keyboard(key)
                method = "keyboard"

            if success_press:
                print(f"🔽 Press: {key} ({method})")
                time.sleep(0.05)  # Brief delay

                # Release
                if self.use_win32:
                    success_release = self.release_key_win32(key)
                else:
                    success_release = self.release_key_keyboard(key)

                if success_release:
                    print(f"🔼 Release: {key} ({method})")
                else:
                    print(f"❌ Unable to release key: {key}")
            else:
                print(f"❌ Unable to press key: {key}")
    
    def release_keys(self, keys):
        """Release keys"""
        if isinstance(keys, str):
            keys = [keys]

        for key in keys:
            if self.key_states[key]:
                success = False
                method = ""

                if self.use_win32:
                    success = self.release_key_win32(key)
                    method = "Win32"
                else:
                    success = self.release_key_keyboard(key)
                    method = "keyboard"

                if success:
                    self.key_states[key] = False
                    print(f"🔼 Release: {key} ({method})")
                else:
                    print(f"❌ Unable to release key: {key}")

    def release_all_keys(self):
        """Release all keys"""
        for key, pressed in self.key_states.items():
            if pressed:
                if self.use_win32:
                    self.release_key_win32(key)
                else:
                    self.release_key_keyboard(key)
                self.key_states[key] = False

    def handle_button_press(self, button_name):
        """Handle button press event"""
        current_time = time.time()

        # Update last time button was detected
        self.button_last_seen[button_name] = current_time

        # If button was not pressed before, this is a new press event
        if not self.button_states.get(button_name, False):
            # Record press time
            self.button_press_times[button_name] = current_time
            self.button_states[button_name] = True
            self.long_press_triggered[button_name] = False
            self.short_press_executed[button_name] = False
            print(f"🔽 Button pressed: {button_name} (waiting to determine short/long press)")
        # If button is already in pressed state, only update last detection time, don't process repeatedly

    def handle_button_release(self, button_name):
        """Handle button release event"""
        if button_name not in self.button_states or not self.button_states[button_name]:
            return

        current_time = time.time()
        press_time = self.button_press_times.get(button_name, current_time)
        hold_duration = current_time - press_time

        self.button_states[button_name] = False

        # Determine if it's a long press or short press based on duration
        if hold_duration >= self.long_press_threshold:
            # Long press: execute long press action
            long_press_key = self.long_press_mapping.get(button_name)
            if long_press_key:
                self.press_keys([long_press_key])  # Execute long press as a key press event
                print(f"� Long press: {button_name} -> {long_press_key} (duration {hold_duration:.2f}s)")
        else:
            # Short press: execute short press action
            short_press_action = f"{button_name} Clicked"
            if short_press_action in self.key_mapping:
                keys = self.key_mapping[short_press_action]
                if keys:
                    self.press_keys(keys)
                    print(f"👆 Short press: {button_name} -> {keys} (duration {hold_duration:.2f}s)")

    def check_long_press(self):
        """Check if any key has reached long press condition - now disabled, using release-time detection"""
        # This function is now disabled since we determine long/short press on button release
        pass

    def press_single_key_continuous(self, key):
        """Press single key (continuous state)"""
        if not self.key_states[key]:
            success = False
            method = ""

            if self.use_win32:
                success = self.press_key_win32(key)
                method = "Win32"
            else:
                success = self.press_key_keyboard(key)
                method = "keyboard"

            if success:
                self.key_states[key] = True
                print(f"🔽 Press: {key} ({method})")

    def release_single_key(self, key):
        """Release single key"""
        if self.key_states[key]:
            success = False
            method = ""

            if self.use_win32:
                success = self.release_key_win32(key)
                method = "Win32"
            else:
                success = self.release_key_keyboard(key)
                method = "keyboard"

            if success:
                self.key_states[key] = False
                print(f"🔼 Release: {key} ({method})")

    def press_direction_keys(self, keys, direction_data):
        """处理方向键按下（短按模式）"""
        if isinstance(keys, str):
            keys = [keys]

        current_time = time.time()

        # 记录方向键触发时间
        for key in keys:
            self.last_direction_time[key] = current_time

        # 执行短按
        self.press_keys(keys)
        print(f"🎮 方向短按: {direction_data} -> {'+'.join(keys)}")

    def release_all_direction_keys(self):
        """Release all direction keys"""
        direction_keys = ["w", "a", "s", "d"]
        released_keys = []

        for key in direction_keys:
            if self.key_states[key]:
                self.release_single_key(key)
                released_keys.append(key)

        if released_keys:
            print(f"🎯 Joystick centered, releasing direction keys: {'+'.join(released_keys)}")

    def check_direction_timeout(self):
        """Check if direction keys have timed out, release if so"""
        current_time = time.time()
        direction_keys = ["w", "a", "s", "d"]
        keys_to_release = []

        for key in direction_keys:
            if key in self.last_direction_time:
                time_since_last = current_time - self.last_direction_time[key]
                if time_since_last > self.direction_timeout:
                    # Timeout, release key
                    keys_to_release.append(key)
            elif self.key_states.get(key, False):
                # Key is pressed but no timestamp recorded, release it
                keys_to_release.append(key)

        # Release all timed out keys
        for key in keys_to_release:
            if self.key_states.get(key, False):
                self.release_single_key(key)
                print(f"⏰ Direction key timeout release: {key}")
            # Clear record
            if key in self.last_direction_time:
                del self.last_direction_time[key]

    def check_button_timeout(self):
        """Check if buttons have timed out, auto-release if so"""
        current_time = time.time()
        buttons_to_release = []

        for button_name, last_seen_time in self.button_last_seen.items():
            if self.button_states.get(button_name, False):
                time_since_last = current_time - last_seen_time
                if time_since_last > self.button_timeout:
                    # Button timeout, auto-release
                    buttons_to_release.append(button_name)

        # Release timed out buttons
        for button_name in buttons_to_release:
            print(f"⏰ Button timeout auto-release: {button_name}")
            self.handle_button_release(button_name)
            # Clear record
            if button_name in self.button_last_seen:
                del self.button_last_seen[button_name]
    
    def connect_serial(self, baudrate=115200):
        """Connect to serial port - auto-find available port"""
        return self.auto_find_port(baudrate)

    def auto_find_port(self, baudrate=115200):
        """Auto-find Arduino port"""
        print("🔍 Auto-searching for Arduino port...")
        ports = serial.tools.list_ports.comports()

        if not ports:
            print("❌ No serial port devices found")
            return False

        print(f"Found {len(ports)} serial port devices:")
        for i, port in enumerate(ports, 1):
            print(f"  {i}. {port.device} - {port.description}")

        # Prioritize ports containing Arduino keywords
        arduino_ports = []
        other_ports = []

        for port in ports:
            description = port.description.lower()
            if any(keyword in description for keyword in ['arduino', 'ch340', 'cp210', 'ftdi']):
                arduino_ports.append(port)
            else:
                other_ports.append(port)

        # Try Arduino-related ports first, then other ports
        all_ports = arduino_ports + other_ports

        for port in all_ports:
            try:
                print(f"🔌 Attempting connection: {port.device} ({port.description})")
                self.serial_port = serial.Serial(port.device, baudrate, timeout=1)
                print(f"✅ Successfully connected to: {port.device}")
                time.sleep(2)  # Wait for Arduino restart
                return True
            except Exception as e:
                print(f"   ❌ Connection failed: {e}")
                continue

        print("❌ All ports failed to connect")
        return False
    
    def process_joystick_data(self, data):
        """Process joystick data"""
        data = data.strip()

        # Parse timestamped data
        if " > " in data:
            _, actual_data = data.split(" > ", 1)
            data = actual_data.strip()

        # Ignore system information
        ignore_patterns = ["Calibrating", "JoystickShield", "Starting", "=", "complete", "Complete"]
        if any(pattern in data for pattern in ignore_patterns):
            return

        # Handle position data
        if "Joystick Position" in data or ("X:" in data and "Y:" in data):
            self.handle_position_data(data)
            return

        print(f"📡 Received: {data}")

        # Handle joystick center events
        if "Joystick NotCenter" in data:
            # Don't release keys for NotCenter, let timeout handle it
            return

        if "Joystick Center" in data:
            # Joystick returned to center - immediately release all direction keys
            self.release_all_direction_keys()
            print(f"🎯 Joystick returned to center - releasing all WASD keys")
            return

        # If we haven't received any joystick direction data for a while, release direction keys
        # This handles the case where Arduino stops sending direction data when joystick is centered
        current_time = time.time()
        if self.last_direction_time:
            oldest_direction_time = min(self.last_direction_time.values())
            if current_time - oldest_direction_time > self.direction_timeout:
                self.release_all_direction_keys()
                self.last_direction_time.clear()

        # Check key mapping (priority processing)
        if data in self.key_mapping:
            keys = self.key_mapping[data]
            if keys:
                # Joystick directions use continuous keys (hold)
                if "Joystick " in data and data != "Joystick Button Clicked":
                    self.press_keys_continuous(keys)  # Hold direction keys
                    # Update direction key timestamps
                    current_time = time.time()
                    if isinstance(keys, list):
                        for key in keys:
                            self.last_direction_time[key] = current_time
                    else:
                        self.last_direction_time[keys] = current_time
                    print(f"🎮 Joystick direction: {data} -> Hold {'+'.join(keys) if isinstance(keys, list) else keys}")
                elif "Clicked" in data:
                    # Button press event: support long press functionality, don't execute short press immediately
                    button_name = data.replace(" Clicked", "").strip()
                    self.handle_button_press(button_name)
                    # No longer execute short press immediately, wait to determine short/long press
                else:
                    self.press_keys_continuous(keys)  # Other events
            return

        # Handle button release events (not used since Arduino doesn't send release events)
        if "Released" in data:
            button_name = data.replace(" Released", "").strip()
            self.handle_button_release(button_name)
            return
    
    def handle_position_data(self, data):
        """Handle position data"""
        try:
            if "X:" in data and "Y:" in data:
                x_start = data.find("X:") + 2
                comma_pos = data.find(",", x_start)
                y_start = data.find("Y:") + 2

                if comma_pos == -1:
                    return

                x_str = data[x_start:comma_pos].strip()
                y_str = data[y_start:].strip()

                x_pos = int(x_str)
                y_pos = int(y_str)

                # Dead zone detection - increased for better center detection
                dead_zone = 15
                if abs(x_pos) <= dead_zone and abs(y_pos) <= dead_zone:
                    # Release all direction keys immediately when centered
                    self.release_all_direction_keys()
                    print(f"🎯 Joystick centered: X={x_pos}, Y={y_pos}")
                else:
                    # Handle directional movement
                    self.handle_movement(x_pos, y_pos, dead_zone)

        except Exception as e:
            print(f"⚠️  Position data parsing error: {e}")
    
    def handle_movement(self, x_pos, y_pos, dead_zone):
        """Handle movement"""
        # First release all direction keys
        direction_keys = ["w", "a", "s", "d"]
        for key in direction_keys:
            if self.key_states[key]:
                self.release_keys(key)

        # Determine which keys need to be pressed
        keys_to_press = []

        if y_pos > dead_zone:  # Up (positive Y-axis means up)
            keys_to_press.append("w")
        elif y_pos < -dead_zone:  # Down (negative Y-axis means down)
            keys_to_press.append("s")

        if x_pos < -dead_zone:  # Left
            keys_to_press.append("a")
        elif x_pos > dead_zone:  # Right
            keys_to_press.append("d")

        # Press corresponding keys
        if keys_to_press:
            self.press_keys_continuous(keys_to_press)
            print(f"🎮 Movement: {'+'.join(keys_to_press)} (X={x_pos}, Y={y_pos})")
    
    def serial_listener(self):
        """Serial port listening thread"""
        print("🎮 Starting joystick data monitoring...")

        while self.is_running:
            try:
                # Process serial port data
                if self.serial_port and self.serial_port.is_open and self.serial_port.in_waiting:
                    data = self.serial_port.readline().decode('utf-8', errors='ignore')
                    if data:
                        self.process_joystick_data(data)

                # Check long press status
                self.check_long_press()

                # Check direction key timeout
                self.check_direction_timeout()

                # Check button timeout
                self.check_button_timeout()

            except Exception as e:
                print(f"❌ Serial port read error: {e}")
                break

            time.sleep(0.01)
    
    def start(self):
        """Start controller"""
        print("=" * 60)
        print("🎮 JoystickController - Final Game Version")
        print("=" * 60)

        # Display input method
        method = "Win32 API" if self.use_win32 else "keyboard library"
        print(f"🎯 Input method: {method}")

        # Check permissions
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin:
                print("✅ Running as administrator")
            else:
                print("⚠️  Not running as administrator, may affect game compatibility")
        except:
            pass

        # Connect to serial port
        if not self.connect_serial():
            print("❌ Unable to connect to serial port, program exiting")
            return
        
        # Display key mappings
        print("\n🎯 Joystick Direction Mapping:")
        direction_actions = [k for k in self.key_mapping.keys() if "Joystick " in k and "Button" not in k]
        for action in direction_actions:
            keys = self.key_mapping[action]
            if keys:
                if isinstance(keys, list):
                    keys_str = " + ".join(keys)
                else:
                    keys_str = keys
                print(f"  {action} -> {keys_str}")

        print("\n🎯 Button Short Press Mapping:")
        button_actions = [k for k in self.key_mapping.keys() if "Clicked" in k]
        for action in button_actions:
            keys = self.key_mapping[action]
            if keys:
                if isinstance(keys, list):
                    keys_str = " + ".join(keys)
                else:
                    keys_str = keys
                print(f"  {action} -> {keys_str}")

        print(f"\n🎯 Button Long Press Mapping (hold ≥ {self.long_press_threshold}s):")
        for button_name, long_key in self.long_press_mapping.items():
            print(f"  {button_name} Long Press -> {long_key}")

        print(f"\n⚠️  Important Notes:")
        print("1. Please ensure game window is active")
        print("2. Recommend setting game to windowed mode")
        print("3. Supports button short press and long press functionality")
        print("4. If still no response, check game input settings")
        print("\n⌨️  Press Ctrl+C to exit")
        print("-" * 60)
        
        # Start listening thread
        self.is_running = True
        listener_thread = threading.Thread(target=self.serial_listener)
        listener_thread.daemon = True
        listener_thread.start()

        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n🛑 Exiting...")
            self.stop()

    def stop(self):
        """Stop controller"""
        self.is_running = False
        self.release_all_keys()

        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            print("✅ Serial port closed")

        print("✅ Controller stopped")

def main():
    print("🔍 Checking dependencies...")

    if not WIN32_AVAILABLE and not KEYBOARD_AVAILABLE:
        print("❌ Missing input libraries, please install:")
        print("pip install pywin32 keyboard")
        sys.exit(1)

    if WIN32_AVAILABLE:
        print("✅ Win32 API available")
    if KEYBOARD_AVAILABLE:
        print("✅ keyboard library available")

    controller = GameJoystickController()
    controller.start()

if __name__ == "__main__":
    main()
