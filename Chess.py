#!/usr/bin/env python3
"""
Chess Piece Selector with GUI: All 12 pieces with numpad hotkeys.
Requires: pip install keyboard pyautogui opencv-python pillow
"""

import keyboard
import cv2
import numpy as np
import pyautogui
import time
from pathlib import Path
import tkinter as tk
from tkinter import scrolledtext
import threading

# Configuration - ALL 12 CHESS PIECES
CHESS_PIECES = {
    'white_pawn': {
        'hotkey': '1',
        'image_path': 'white_pawn.png',
    },
    'white_knight': {
        'hotkey': '2',
        'image_path': 'white_knight.png',
    },
    'white_light_bishop': {
        'hotkey': '3',
        'image_path': 'white_light_bishop.png',
    },
    'white_rook': {
        'hotkey': '4',
        'image_path': 'white_rook.png',
    },
    'white_queen': {
        'hotkey': '5',
        'image_path': 'white_queen.png',
    },
    'white_king': {
        'hotkey': '6',
        'image_path': 'white_king.png',
    },
    'black_pawn': {
        'hotkey': '7',
        'image_path': 'black_pawn.png',
    },
    'black_knight': {
        'hotkey': '8',
        'image_path': 'black_knight.png',
    },
    'black_bishop': {
        'hotkey': '9',
        'image_path': 'black_light_bishop.png',
    },
    'black_rook': {
        'hotkey': '-',
        'image_path': 'black_rook.png',
    },
    'black_queen': {
        'hotkey': '+',
        'image_path': 'black_queen.png',
    },
    'black_king': {
        'hotkey': '*',
        'image_path': 'black_king.png',
    },
}

# General settings
CONFIDENCE_THRESHOLD = 0.75
CLICK_AFTER_FINDING = True
CLICK_DELAY = 0.1
AUTO_SEARCH_RETRIES = 3
RETRY_DELAY = 0.2

# Global variables
loaded_pieces = {}
is_running = True
gui_window = None
message_box = None


class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Piece Selector - 12 Pieces")
        self.root.geometry("700x800")
        self.root.resizable(True, True)
        self.root.configure(bg='#1e1e1e')

        # Title
        title_frame = tk.Frame(root, bg='#2d2d2d')
        title_frame.pack(fill=tk.X, padx=0, pady=0)

        title = tk.Label(
            title_frame,
            text="♟ Chess Piece Selector - 12 Pieces",
            font=('Arial', 18, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00'
        )
        title.pack(pady=15)

        # Hotkey Map
        map_frame = tk.LabelFrame(
            root,
            text="Numpad Hotkeys (12 Pieces)",
            font=('Arial', 11, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00',
            padx=10,
            pady=10
        )
        map_frame.pack(fill=tk.X, padx=10, pady=10)

        # Create two columns for hotkeys
        left_frame = tk.Frame(map_frame, bg='#2d2d2d')
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        right_frame = tk.Frame(map_frame, bg='#2d2d2d')
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Left column (Numpad 1-6)
        left_text = "WHITE PIECES:\n"
        left_text += "  Numpad 1  →  white_pawn\n"
        left_text += "  Numpad 2  →  white_knight\n"
        left_text += "  Numpad 3  →  white_bishop\n"
        left_text += "  Numpad 4  →  white_rook\n"
        left_text += "  Numpad 5  →  white_queen\n"
        left_text += "  Numpad 6  →  white_king\n"

        left_label = tk.Label(
            left_frame,
            text=left_text,
            font=('Courier', 9),
            bg='#2d2d2d',
            fg='#00ff00',
            justify=tk.LEFT,
            anchor='nw'
        )
        left_label.pack(fill=tk.BOTH, expand=True, padx=(0, 10))

        # Right column (Numpad 7-*, +, -)
        right_text = "BLACK PIECES:\n"
        right_text += "  Numpad 7  →  black_pawn\n"
        right_text += "  Numpad 8  →  black_knight\n"
        right_text += "  Numpad 9  →  black_bishop\n"
        right_text += "  Numpad -  →  black_rook\n"
        right_text += "  Numpad +  →  black_queen\n"
        right_text += "  Numpad *  →  black_king\n"

        right_label = tk.Label(
            right_frame,
            text=right_text,
            font=('Courier', 9),
            bg='#2d2d2d',
            fg='#00ffff',
            justify=tk.LEFT,
            anchor='nw'
        )
        right_label.pack(fill=tk.BOTH, expand=True, padx=(10, 0))

        # Status
        status_frame = tk.LabelFrame(
            root,
            text="Status",
            font=('Arial', 11, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00',
            padx=10,
            pady=10
        )
        status_frame.pack(fill=tk.X, padx=10, pady=10)

        self.status_label = tk.Label(
            status_frame,
            text="Ready! Press a numpad key...",
            font=('Arial', 10, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00'
        )
        self.status_label.pack()

        # Messages
        msg_frame = tk.LabelFrame(
            root,
            text="Messages",
            font=('Arial', 11, 'bold'),
            bg='#2d2d2d',
            fg='#00ff00',
            padx=5,
            pady=5
        )
        msg_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.message_box = scrolledtext.ScrolledText(
            msg_frame,
            height=15,
            font=('Courier', 9),
            bg='#1a1a1a',
            fg='#00ff00',
            insertbackground='#00ff00',
            wrap=tk.WORD
        )
        self.message_box.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for colors
        self.message_box.tag_config('success', foreground='#00ff00')
        self.message_box.tag_config('error', foreground='#ff0000')
        self.message_box.tag_config('info', foreground='#00aaff')
        self.message_box.tag_config('warning', foreground='#ffaa00')
        self.message_box.tag_config('white', foreground='#aaffaa')
        self.message_box.tag_config('black', foreground='#aaaaff')

        # Buttons frame
        btn_frame = tk.Frame(root, bg='#1e1e1e')
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        clear_btn = tk.Button(
            btn_frame,
            text="Clear Messages",
            command=self.clear_messages,
            bg='#2d2d2d',
            fg='#00ff00',
            activebackground='#00ff00',
            activeforeground='#1e1e1e',
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

        stop_btn = tk.Button(
            btn_frame,
            text="Stop (ESC)",
            command=self.stop_selector,
            bg='#2d2d2d',
            fg='#ff0000',
            activebackground='#ff0000',
            activeforeground='#1e1e1e',
            font=('Arial', 10),
            padx=15,
            pady=5
        )
        stop_btn.pack(side=tk.LEFT, padx=5)

        self.root.protocol("WM_DELETE_WINDOW", self.stop_selector)

    def add_message(self, message, tag='info'):
        """Add a message to the message box with color."""
        self.message_box.insert(tk.END, message + '\n', tag)
        self.message_box.see(tk.END)
        self.root.update()

    def clear_messages(self):
        """Clear all messages."""
        self.message_box.delete('1.0', tk.END)
        self.add_message("Messages cleared.", 'info')

    def update_status(self, status_text):
        """Update the status label."""
        self.status_label.config(text=status_text)
        self.root.update()

    def stop_selector(self):
        """Stop the selector and close GUI."""
        global is_running
        is_running = False
        self.add_message("Stopping...", 'warning')
        self.root.update()
        self.root.destroy()


def load_all_pieces():
    """Load all chess piece reference images."""
    global loaded_pieces

    loaded_pieces = {}
    gui_window.add_message("Loading piece images...", 'info')
    gui_window.add_message("=" * 60, 'info')

    white_count = 0
    black_count = 0

    for piece_name, piece_config in CHESS_PIECES.items():
        image_path = piece_config['image_path']
        tag = 'white' if piece_name.startswith('white') else 'black'

        if not Path(image_path).exists():
            gui_window.add_message(f"⚠ {piece_name}: Image not found", 'warning')
            continue

        try:
            image = cv2.imread(image_path)
            if image is None:
                gui_window.add_message(f"✗ {piece_name}: Failed to load", 'error')
                continue

            loaded_pieces[piece_name] = image
            h, w = image.shape[:2]
            msg = f"✓ {piece_name}: Loaded ({w}x{h} px)"
            gui_window.add_message(msg, tag)

            if piece_name.startswith('white'):
                white_count += 1
            else:
                black_count += 1

        except Exception as e:
            gui_window.add_message(f"✗ {piece_name}: {str(e)}", 'error')

    if not loaded_pieces:
        gui_window.add_message("\n✗ No chess piece images loaded!", 'error')
        return False

    gui_window.add_message("=" * 60, 'info')
    gui_window.add_message(f"\n✓ WHITE: {white_count}/6 loaded", 'white')
    gui_window.add_message(f"✓ BLACK: {black_count}/6 loaded", 'black')
    gui_window.add_message(f"✓ TOTAL: {len(loaded_pieces)}/12 pieces ready\n", 'success')
    gui_window.update_status("✓ Ready! Press numpad keys...")
    return True


def find_piece_on_screen(piece_name):
    """Find a specific chess piece on the screen."""
    if piece_name not in loaded_pieces:
        gui_window.add_message(f"✗ Piece '{piece_name}' not loaded", 'error')
        return None

    reference_image = loaded_pieces[piece_name]

    try:
        screenshot = pyautogui.screenshot()
        screen_np = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

        result = cv2.matchTemplate(screen_np, reference_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val < CONFIDENCE_THRESHOLD:
            return None

        ref_height, ref_width = reference_image.shape[:2]
        center_x = max_loc[0] + ref_width // 2
        center_y = max_loc[1] + ref_height // 2

        return (center_x, center_y, max_val)

    except Exception as e:
        gui_window.add_message(f"✗ Error searching: {str(e)}", 'error')
        return None


def select_chess_piece(piece_name):
    """Find a chess piece and click on it."""
    tag = 'white' if piece_name.startswith('white') else 'black'
    gui_window.update_status(f"🔍 Searching for {piece_name}...")
    gui_window.add_message(f"\n[{time.strftime('%H:%M:%S')}] Searching for {piece_name}...", tag)

    for attempt in range(AUTO_SEARCH_RETRIES):
        result = find_piece_on_screen(piece_name)

        if result:
            center_x, center_y, confidence = result
            gui_window.add_message(f"✓ Found {piece_name}! (confidence: {confidence:.1%})", 'success')
            gui_window.add_message(f"  Position: X={center_x}, Y={center_y}", 'success')
            gui_window.update_status(f"✓ Found {piece_name}!")

            try:
                pyautogui.moveTo(center_x, center_y)

                if CLICK_AFTER_FINDING:
                    time.sleep(CLICK_DELAY)
                    pyautogui.click()
                    gui_window.add_message(f"✓ Clicked on {piece_name}", 'success')

            except Exception as e:
                gui_window.add_message(f"✗ Error moving/clicking: {str(e)}", 'error')

            return True

        if attempt < AUTO_SEARCH_RETRIES - 1:
            gui_window.add_message(f"  Retry {attempt + 1}/{AUTO_SEARCH_RETRIES - 1}...", 'warning')
            time.sleep(RETRY_DELAY)

    gui_window.add_message(f"✗ {piece_name} not found on screen", 'error')
    gui_window.update_status(f"✗ {piece_name} not found")
    return False


def create_hotkey_listeners():
    """Create hotkey listeners for all chess pieces."""
    for piece_name, piece_config in CHESS_PIECES.items():
        hotkey = piece_config['hotkey']

        def make_callback(pname):
            def callback():
                if is_running:
                    select_chess_piece(pname)

            return callback

        keyboard.add_hotkey(hotkey, make_callback(piece_name))


def main():
    """Main function."""
    global gui_window, is_running

    # Create GUI
    root = tk.Tk()
    gui_window = ChessGUI(root)

    gui_window.add_message("Chess Piece Selector - 12 Pieces Edition", 'success')
    gui_window.add_message("=" * 60, 'info')

    # Load pieces
    if not load_all_pieces():
        gui_window.add_message("\n✗ Cannot start without chess piece images", 'error')
        gui_window.add_message("Create a 'pieces' folder with these files:", 'warning')

        for piece_name in CHESS_PIECES.keys():
            gui_window.add_message(f"  pieces/{piece_name}.png", 'warning')
        return

    # Register hotkeys
    gui_window.add_message("Registering hotkeys...", 'info')
    create_hotkey_listeners()
    gui_window.add_message("✓ All hotkeys registered\n", 'success')

    # Start the GUI
    try:
        root.mainloop()
    except KeyboardInterrupt:
        is_running = False
        gui_window.add_message("\n✓ Stopped by user", 'warning')


if __name__ == "__main__":
    main()