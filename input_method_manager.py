#!/usr/bin/env python3
"""
Input Method Manager
Handles automatic detection and switching of input methods
"""

import time
import ctypes

# Import Windows API libraries
try:
    import win32api
    import win32con
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False
    print("⚠️  win32api not available, using fallback methods")


class InputMethodManager:
    """Manages input method detection and switching"""
    
    def __init__(self):
        self.win32_available = WIN32_AVAILABLE
        
        # Language IDs for common input methods
        self.LANG_ENGLISH_US = 0x0409
        self.LANG_CHINESE_SIMPLIFIED = 0x0804
        self.LANG_CHINESE_TRADITIONAL = 0x0404
    
    def get_current_input_method(self):
        """Get current input method language"""
        try:
            if self.win32_available:
                # Get current thread ID
                thread_id = win32api.GetCurrentThreadId()
                
                # Get keyboard layout for current thread
                hkl = ctypes.windll.user32.GetKeyboardLayout(thread_id)
                
                # Extract language ID from keyboard layout
                # Lower 16 bits contain the language identifier
                lang_id = hkl & 0xFFFF
                
                # Identify language
                if lang_id == self.LANG_ENGLISH_US:
                    return "English"
                elif lang_id in [self.LANG_CHINESE_SIMPLIFIED, self.LANG_CHINESE_TRADITIONAL]:
                    return "Chinese"
                else:
                    return f"Other (ID: {lang_id:04X})"
                    
        except Exception as e:
            print(f"⚠️  Error detecting input method: {e}")
        
        return "Unknown"
    
    def is_chinese_input_method(self):
        """Check if current input method is Chinese"""
        current_method = self.get_current_input_method()
        return "Chinese" in current_method
    
    def is_english_input_method(self):
        """Check if current input method is English"""
        current_method = self.get_current_input_method()
        return "English" in current_method
    
    def try_shift_switch(self):
        """Try switching input method using Shift key"""
        try:
            if self.win32_available:
                # Press and release Shift key
                win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)  # Press
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release
            else:
                # Fallback using ctypes
                ctypes.windll.user32.keybd_event(0x10, 0, 0, 0)  # Press Shift (VK_SHIFT = 0x10)
                time.sleep(0.05)
                ctypes.windll.user32.keybd_event(0x10, 0, 2, 0)  # Release Shift (KEYEVENTF_KEYUP = 2)
            
            time.sleep(0.2)  # Wait for switch to take effect
            return True
            
        except Exception as e:
            print(f"⚠️  Error with Shift key switch: {e}")
            return False
    
    def try_ctrl_space_switch(self):
        """Try switching input method using Ctrl+Space"""
        try:
            if self.win32_available:
                # Press Ctrl+Space
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Press Ctrl
                win32api.keybd_event(win32con.VK_SPACE, 0, 0, 0)    # Press Space
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_SPACE, 0, win32con.KEYEVENTF_KEYUP, 0)    # Release Space
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Ctrl
            else:
                # Fallback using ctypes
                ctypes.windll.user32.keybd_event(0x11, 0, 0, 0)  # Press Ctrl (VK_CONTROL = 0x11)
                ctypes.windll.user32.keybd_event(0x20, 0, 0, 0)  # Press Space (VK_SPACE = 0x20)
                time.sleep(0.05)
                ctypes.windll.user32.keybd_event(0x20, 0, 2, 0)  # Release Space
                ctypes.windll.user32.keybd_event(0x11, 0, 2, 0)  # Release Ctrl
            
            time.sleep(0.2)  # Wait for switch to take effect
            return True
            
        except Exception as e:
            print(f"⚠️  Error with Ctrl+Space switch: {e}")
            return False
    
    def switch_to_english_input(self):
        """Switch to English input method if currently using Chinese"""
        try:
            # First check current input method
            current_method = self.get_current_input_method()
            print(f"🔍 Current input method: {current_method}")
            
            # Only switch if currently using Chinese input method
            if self.is_english_input_method():
                print("✅ Already using English input method, no switch needed")
                return True
            
            if not self.is_chinese_input_method():
                print(f"ℹ️  Using {current_method} input method, attempting switch anyway...")
            else:
                print("🔤 Chinese input detected, switching to English...")
            
            # Try Method 1: Shift key (most common for Chinese input methods)
            if self.try_shift_switch():
                new_method = self.get_current_input_method()
                if self.is_english_input_method():
                    print(f"✅ Successfully switched to: {new_method} (using Shift)")
                    return True
            
            # Try Method 2: Ctrl+Space (common alternative)
            if self.try_ctrl_space_switch():
                new_method = self.get_current_input_method()
                if self.is_english_input_method():
                    print(f"✅ Successfully switched to: {new_method} (using Ctrl+Space)")
                    return True
            
            # Final check
            final_method = self.get_current_input_method()
            if self.is_english_input_method():
                print(f"✅ Successfully switched to: {final_method}")
                return True
            else:
                print(f"⚠️  Still using: {final_method}")
                print("💡 Please manually switch to English input method for best compatibility")
                return False
                
        except Exception as e:
            print(f"⚠️  Error switching input method: {e}")
        
        return False
    
    def get_status_info(self):
        """Get current input method status information"""
        current_method = self.get_current_input_method()
        is_chinese = self.is_chinese_input_method()
        is_english = self.is_english_input_method()
        
        return {
            "current_method": current_method,
            "is_chinese": is_chinese,
            "is_english": is_english,
            "win32_available": self.win32_available
        }


# Convenience functions for easy import
def get_input_method_manager():
    """Get a new InputMethodManager instance"""
    return InputMethodManager()

def quick_switch_to_english():
    """Quick function to switch to English input method"""
    manager = InputMethodManager()
    return manager.switch_to_english_input()

def get_current_input_method():
    """Quick function to get current input method"""
    manager = InputMethodManager()
    return manager.get_current_input_method()


if __name__ == "__main__":
    # Test the input method manager
    print("🧪 Testing Input Method Manager")
    print("=" * 40)
    
    manager = InputMethodManager()
    
    # Show current status
    status = manager.get_status_info()
    print(f"Current method: {status['current_method']}")
    print(f"Is Chinese: {status['is_chinese']}")
    print(f"Is English: {status['is_english']}")
    print(f"Win32 available: {status['win32_available']}")
    
    print("\n🔄 Attempting to switch to English...")
    success = manager.switch_to_english_input()
    
    if success:
        print("✅ Switch operation completed successfully")
    else:
        print("❌ Switch operation failed")
