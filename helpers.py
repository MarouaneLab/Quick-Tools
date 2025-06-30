# helpers.py
"""
This module contains various helper functions used across different parts
of the Quick Tools application.
"""
import pyperclip
import re
import colorsys

# Import constants (specifically for status messages)
from constants import WARNING_RED, SUCCESS_GREEN


def copy_to_clipboard_helper(app_instance, text_to_copy: str, success_message: str):
    """
    Copies the given text to the clipboard and updates the application's status.
    Uses pyperclip if available, falls back to tkinter's clipboard if not.

    Args:
        app_instance: The main application instance (needed for update_status and root access).
        text_to_copy (str): The string content to copy to the clipboard.
        success_message (str): The message to display in the status bar on success.
    """
    try:
        pyperclip.copy(text_to_copy)
        app_instance.update_status(success_message, SUCCESS_GREEN)
    except pyperclip.PyperclipException as e:
        # Fallback to tkinter's clipboard if pyperclip fails (e.g., no X server on Linux)
        try:
            app_instance.root.clipboard_clear()
            app_instance.root.clipboard_append(text_to_copy)
            app_instance.root.update() # Required for tkinter's clipboard to persist
            app_instance.update_status(f"{success_message} (fallback)", SUCCESS_GREEN)
        except Exception as tk_e:
            app_instance.update_status(f"Failed to copy: {tk_e}", WARNING_RED)
            print(f"Error copying to clipboard (pyperclip fallback): {tk_e}")
    except Exception as e:
        app_instance.update_status(f"Failed to copy: {e}", WARNING_RED)
        print(f"Unknown error copying to clipboard: {e}")

def hex_to_rgb(hex_code: str) -> tuple:
    """
    Converts a HEX color code (e.g., '#RRGGBB') to an RGB tuple (R, G, B).

    Args:
        hex_code (str): The HEX color string.

    Returns:
        tuple: An RGB tuple (0-255, 0-255, 0-255).
    """
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb_tuple: tuple) -> str:
    """
    Converts an RGB tuple (R, G, B) to a HEX color code (e.g., '#RRGGBB').

    Args:
        rgb_tuple (tuple): An RGB tuple (0-255, 0-255, 0-255).

    Returns:
        str: The HEX color string.
    """
    return '#{:02X}{:02X}{:02X}'.format(*rgb_tuple)

def hsv_to_hex(h: float, s: float, v: float) -> str:
    """
    Converts HSV (Hue, Saturation, Value) to a HEX color code.

    Args:
        h (float): Hue (0.0 to 1.0).
        s (float): Saturation (0.0 to 1.0).
        v (float): Value (0.0 to 1.0).

    Returns:
        str: The HEX color string.
    """
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return '#{:02X}{:02X}{:02X}'.format(int(r*255), int(g*255), int(b*255))

def is_valid_hex(hex_code: str) -> bool:
    """
    Checks if a string is a valid 7-character HEX color code (e.g., '#AABBCC').

    Args:
        hex_code (str): The string to validate.

    Returns:
        bool: True if valid, False otherwise.
    """
    return re.fullmatch(r'^#([0-9a-fA-F]{6})$', hex_code) is not None

