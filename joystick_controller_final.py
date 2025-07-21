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
from ctypes import wintypes
from collections import defaultdict

# Import input method manager
from input_method_manager import InputMethodManager

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
    # Direction keys constant
    DIRECTION_KEYS = ["w", "a", "s", "d"]

    def __init__(self):
        self.serial_port = None
        self.is_running = False
        self.key_states = defaultdict(bool)

        # Direction key auto-release functionality
        self.last_direction_time = {}  # Record last direction key trigger time
        self.direction_timeout = 0.15  # Direction key timeout (seconds) - quick release when joystick stops

        # Initialize input method manager
        self.input_method_manager = InputMethodManager()

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
            # Joystick directions
            "Joystick Up": "w",
            "Joystick Down": "s",
            "Joystick Left": "a",
            "Joystick Right": "d",
            "Joystick LeftUp": ["a", "w"],
            "Joystick RightUp": ["d", "w"],
            "Joystick LeftDown": ["a", "s"],
            "Joystick RightDown": ["d", "s"],

            # Button clicks
            "Joystick Button Clicked": "f",
            "Up Button Clicked": "o",
            "Down Button Clicked": "j",
            "Left Button Clicked": "i",
            "Right Button Clicked": "k",
            "E Button Clicked": "e",
            "F Button Clicked": "v",

            # Special functions
            "Joystick NotCenter": None,
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

    # Input method functions moved to input_method_manager.py

    def switch_to_english_input(self):
        """Switch to English input method using input method manager"""
        return self.input_method_manager.switch_to_english_input()

    def ensure_game_focus(self):
        """Ensure game window has focus"""
        window_title = self.get_foreground_window_title()
        if "python" in window_title.lower() or "cmd" in window_title.lower():
            print(f"⚠️  Current active window: {window_title}")
            print("Please switch to game window!")
            return False
        return True

    def _get_input_method_name(self):
        """Get current input method name"""
        return "Win32" if self.use_win32 else "keyboard"
    
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
        """Handle button press event - immediate short press only"""
        # Execute short press action immediately
        short_press_action = f"{button_name} Clicked"
        if short_press_action in self.key_mapping:
            keys = self.key_mapping[short_press_action]
            if keys:
                self.press_keys(keys)
                print(f"� Button press: {button_name} -> {'+'.join(keys) if isinstance(keys, list) else keys}")


    def handle_joystick_direction_press(self, direction_name):
        """Handle joystick direction press event - immediate response"""
        # Execute WASD keys immediately
        if direction_name in self.key_mapping:
            keys = self.key_mapping[direction_name]
            if keys:
                self.press_keys_continuous(keys)
                keys_str = '+'.join(keys) if isinstance(keys, list) else keys
                print(f"🕹️ Joystick direction pressed: {direction_name} -> {keys_str}")

    def handle_joystick_direction_release(self, direction_name):
        """Handle joystick direction release event"""
        # Release WASD keys immediately
        if direction_name in self.key_mapping:
            keys = self.key_mapping[direction_name]
            if keys:
                self.release_keys(keys)
                keys_str = '+'.join(keys) if isinstance(keys, list) else keys
                print(f"🔼 Joystick direction released: {direction_name} -> {keys_str}")


    def press_single_key_continuous(self, key):
        """Press single key (continuous state)"""
        if not self.key_states[key]:
            success = self.press_key_win32(key) if self.use_win32 else self.press_key_keyboard(key)
            if success:
                self.key_states[key] = True
                print(f"🔽 Press: {key} ({self._get_input_method_name()})")

    def release_single_key(self, key):
        """Release single key"""
        if self.key_states[key]:
            success = self.release_key_win32(key) if self.use_win32 else self.release_key_keyboard(key)
            if success:
                self.key_states[key] = False
                print(f"🔼 Release: {key} ({self._get_input_method_name()})")

    def release_all_direction_keys(self):
        """Release all direction keys"""
        released_keys = []

        for key in self.DIRECTION_KEYS:
            if self.key_states[key]:
                self.release_single_key(key)
                released_keys.append(key)

        if released_keys:
            print(f"🎯 Joystick centered, releasing direction keys: {'+'.join(released_keys)}")

    def check_direction_timeout(self):
        """Check if direction keys have timed out, release if so"""
        current_time = time.time()
        keys_to_release = []

        for key in self.DIRECTION_KEYS:
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



        print(f"📡 Received: {data}")

        # Handle joystick center events
        if "Joystick NotCenter" in data:
            # Don't release keys for NotCenter, let timeout handle it
            return

        if "Joystick Center" in data:
            # Joystick returned to center - release all direction keys
            self.release_all_direction_keys()
            print(f"🎯 Joystick returned to center")
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
                # Joystick directions with immediate response
                if "Joystick " in data and data != "Joystick Button Clicked":
                    # Handle joystick direction press (immediate response)
                    self.handle_joystick_direction_press(data)
                    # Update direction key timestamps for timeout mechanism
                    current_time = time.time()
                    if isinstance(keys, list):
                        for key in keys:
                            self.last_direction_time[key] = current_time
                    else:
                        self.last_direction_time[keys] = current_time
                elif "Clicked" in data:
                    # Button press event
                    button_name = data.replace(" Clicked", "").strip()
                    self.handle_button_press(button_name)
                else:
                    self.press_keys_continuous(keys)
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

                dead_zone = 15
                self.handle_movement(x_pos, y_pos, dead_zone)

        except Exception as e:
            print(f"⚠️  Position data parsing error: {e}")
    
    def handle_movement(self, x_pos, y_pos, dead_zone):
        """Handle movement"""
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

        # Get currently pressed direction keys
        currently_pressed = [key for key in self.DIRECTION_KEYS if self.key_states.get(key, False)]

        # Only change keys if the direction actually changed
        if set(keys_to_press) != set(currently_pressed):
            # Release keys that are no longer needed
            for key in currently_pressed:
                if key not in keys_to_press:
                    self.release_keys(key)

            # Press new keys that weren't pressed before
            for key in keys_to_press:
                if key not in currently_pressed:
                    self.press_keys_continuous([key])

            if keys_to_press:
                print(f"🎮 Movement changed: {'+'.join(keys_to_press)} (X={x_pos}, Y={y_pos})")
            else:
                print(f"🎮 Movement stopped (X={x_pos}, Y={y_pos})")
    
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
                # Check direction key timeout
                self.check_direction_timeout()

            except Exception as e:
                print(f"❌ Serial port read error: {e}")
                break

            time.sleep(0.01)
    
    def start(self):
        """Start controller"""
        print("=" * 60)
        print("🎮 JoystickController - Final Game Version")
        print("=" * 60)

        # Switch to English input method
        self.switch_to_english_input()

        # Display input method
        method_name = "Win32 API" if self.use_win32 else "keyboard library"
        print(f"🎯 Input method: {method_name}")

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

        print(f"\n🕹️ Joystick Direction Control:")
        for direction_name, keys in self.key_mapping.items():
            if "Joystick " in direction_name and direction_name != "Joystick Button Clicked" and keys is not None:
                keys_str = '+'.join(keys) if isinstance(keys, list) else keys
                print(f"  {direction_name} -> {keys_str}")

        print(f"\n⚠️  Important Notes:")
        print("1. Please ensure game window is active")
        print("2. Recommend setting game to windowed mode")
        print("3. Supports button short press functionality only")
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
