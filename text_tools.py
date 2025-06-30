# text_tools.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import re

# Import constants from the constants module
from constants import (
    PRIMARY_BG, SECONDARY_BG, ACCENT_BLUE, TEXT_LIGHT, TEXT_MUTED,
    INPUT_BG, INPUT_FG, WARNING_RED, HOVER_PRIMARY_BG, HOVER_ACCENT_BLUE,
    HOVER_WARNING_RED, FONT_FAMILY, FONT_INPUT, FONT_BOLD
)

def create_text_tools_widgets(app, parent_frame):
    """
    Builds the UI widgets for the Text Tools tab.

    Args:
        app: The main application instance (QuickToolsApp).
        parent_frame: The tkinter frame to place these widgets in.
    """
    # Configure grid layout for responsiveness
    parent_frame.grid_columnconfigure(0, weight=1)
    parent_frame.grid_rowconfigure(2, weight=1) # Input text area
    parent_frame.grid_rowconfigure(5, weight=1) # Output text area

    # Title for the section
    title_label = ttk.Label(parent_frame, text="Text Case & Utilities:",
                            style='UnitLabel.TLabel', font=(FONT_FAMILY, 12, 'normal'))
    title_label.grid(row=0, column=0, columnspan=4, pady=(10, 18), sticky='w', padx=(2,0))

    # Input text label
    input_label = ttk.Label(parent_frame, text="Enter your text:", style='InputLabel.TLabel')
    input_label.grid(row=1, column=0, columnspan=4, sticky='w', pady=(0, 10))

    # ScrolledText widget for user input
    app.text_tools_input_text = scrolledtext.ScrolledText(parent_frame,
                                                          height=8, wrap=tk.WORD,
                                                          font=FONT_INPUT,
                                                          bg=INPUT_BG, fg=INPUT_FG,
                                                          insertbackground=ACCENT_BLUE,
                                                          padx=0, pady=0, relief='solid', bd=1,
                                                          highlightbackground=SECONDARY_BG,
                                                          highlightcolor=SECONDARY_BG,
                                                          highlightthickness=1)
    app.text_tools_input_text.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=(0, 30))
    # Bind key release event to update stats and apply conversion live
    app.text_tools_input_text.bind('<KeyRelease>', lambda e: on_text_change(app, e))

    # Frame for case conversion buttons
    case_buttons_frame = tk.Frame(parent_frame, bg=SECONDARY_BG, relief='flat', bd=0)
    case_buttons_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(0, 30))
    for i in range(5): # Configure columns to expand equally
        case_buttons_frame.grid_columnconfigure(i, weight=1)

    # Helper function to create styled buttons for reusability
    def create_styled_button(parent, text, command, bg_color, hover_color, row, col, columnspan=1):
        btn = tk.Button(parent, text=text, command=command,
                        bg=bg_color, fg=TEXT_LIGHT,
                        font=FONT_BOLD,
                        relief='flat', padx=5, pady=12,
                        cursor='hand2', bd=0,
                        activebackground=hover_color,
                        activeforeground=TEXT_LIGHT)
        btn.grid(row=row, column=col, columnspan=columnspan, padx=1, sticky='ew')
        # Store button and its colors for hover effects managed by the main app
        app._button_hover_colors[btn] = {'original': bg_color, 'hover': hover_color}
        return btn

    # Create case conversion buttons
    app.upper_btn = create_styled_button(case_buttons_frame, "UPPERCASE", lambda: set_case_type(app, 'upper'), SECONDARY_BG, HOVER_PRIMARY_BG, 0, 0)
    app.lower_btn = create_styled_button(case_buttons_frame, "lowercase", lambda: set_case_type(app, 'lower'), SECONDARY_BG, HOVER_PRIMARY_BG, 0, 1)
    app.title_btn = create_styled_button(case_buttons_frame, "Title Case", lambda: set_case_type(app, 'title'), SECONDARY_BG, HOVER_PRIMARY_BG, 0, 2)
    app.sentence_case_btn = create_styled_button(case_buttons_frame, "Sentence Case", lambda: set_case_type(app, 'sentence'), SECONDARY_BG, HOVER_PRIMARY_BG, 0, 3)
    app.clear_btn = create_styled_button(case_buttons_frame, "Clear All", lambda: clear_text(app), WARNING_RED, HOVER_WARNING_RED, 0, 4)

    # Output text label
    output_label = ttk.Label(parent_frame, text="Result:", style='InputLabel.TLabel')
    output_label.grid(row=4, column=0, columnspan=4, sticky='w', pady=(0, 10))

    # ScrolledText widget for displaying results (read-only)
    app.output_text = scrolledtext.ScrolledText(parent_frame,
                                                height=8, wrap=tk.WORD,
                                                font=FONT_INPUT,
                                                bg=INPUT_BG, fg=INPUT_FG, state='disabled', # Start as disabled
                                                padx=0, pady=0, relief='solid', bd=1,
                                                highlightbackground=SECONDARY_BG,
                                                highlightcolor=SECONDARY_BG,
                                                highlightthickness=1)
    app.output_text.grid(row=5, column=0, columnspan=4, sticky='nsew', pady=(0, 30))

    # Copy to Clipboard button
    app.copy_btn = tk.Button(parent_frame, text="📋 Copy to Clipboard", command=lambda: copy_to_clipboard(app),
                              bg=ACCENT_BLUE, fg=TEXT_LIGHT, font=FONT_BOLD,
                              relief='flat', padx=20, pady=15, cursor='hand2', bd=0,
                              activebackground=HOVER_ACCENT_BLUE,
                              activeforeground=TEXT_LIGHT)
    app.copy_btn.grid(row=6, column=0, columnspan=4, sticky='ew')
    app._button_hover_colors[app.copy_btn] = {'original': ACCENT_BLUE, 'hover': HOVER_ACCENT_BLUE}

    # Frame for text statistics
    stats_frame = tk.Frame(parent_frame, bg=SECONDARY_BG, relief='flat', bd=0,
                           highlightbackground=ACCENT_BLUE, highlightthickness=1)
    stats_frame.grid(row=7, column=0, columnspan=4, sticky='ew', pady=(20, 0))
    for i in range(3): # Configure columns to expand equally
        stats_frame.grid_columnconfigure(i, weight=1)

    # Character count
    app.char_count_label = ttk.Label(stats_frame, text="0", style='StatsCount.TLabel')
    app.char_count_label.grid(row=0, column=0, pady=(15, 0))
    ttk.Label(stats_frame, text="Characters", style='StatsText.TLabel').grid(row=1, column=0, pady=(0, 15))

    # Word count
    app.word_count_label = ttk.Label(stats_frame, text="0", style='StatsCount.TLabel')
    app.word_count_label.grid(row=0, column=1, pady=(15, 0))
    ttk.Label(stats_frame, text="Words", style='StatsText.TLabel').grid(row=1, column=1, pady=(0, 15))

    # Line count
    app.line_count_label = ttk.Label(stats_frame, text="0", style='StatsCount.TLabel')
    app.line_count_label.grid(row=0, column=2, pady=(15, 0))
    ttk.Label(stats_frame, text="Lines", style='StatsText.TLabel').grid(row=1, column=2, pady=(0, 15))

def on_text_change(app, event=None):
    """
    Callback for text input changes. Updates statistics and applies case conversion.
    """
    update_stats(app)
    apply_conversion(app)

def update_stats(app):
    """
    Calculates and displays character, word, and line counts for the input text.
    """
    text = app.text_tools_input_text.get('1.0', tk.END + '-1c')
    char_count = len(text)
    word_count = len(re.findall(r'\b\w+\b', text)) # Use regex to find words
    line_count = text.count('\n') + 1 if text else 0 # Count newlines + 1 for total lines

    app.char_count_label.config(text=str(char_count))
    app.word_count_label.config(text=str(word_count))
    app.line_count_label.config(text=str(line_count))

def set_case_type(app, case_type):
    """
    Sets the current case conversion type and applies the conversion.
    Provides visual feedback on the button pressed.

    Args:
        app: The main application instance.
        case_type (str): The desired case type ('upper', 'lower', 'title', 'sentence').
    """
    app.current_case_type = case_type
    apply_conversion(app)

    # Provide visual feedback on the button that was pressed
    buttons = {
        'upper': app.upper_btn,
        'lower': app.lower_btn,
        'title': app.title_btn,
        'sentence': app.sentence_case_btn
    }
    feedback_btn = buttons.get(case_type)
    if feedback_btn and feedback_btn in app._button_hover_colors:
        original_color = app._button_hover_colors[feedback_btn]['original']
        feedback_btn.config(bg=ACCENT_BLUE) # Temporarily change background
        app.root.after(200, lambda: feedback_btn.config(bg=original_color)) # Revert after 200ms

def apply_conversion(app):
    """
    Applies the selected case conversion to the input text and displays the result.
    """
    input_text = app.text_tools_input_text.get('1.0', tk.END + '-1c')
    result = input_text

    # Perform conversion based on current_case_type
    if app.current_case_type == 'upper':
        result = input_text.upper()
    elif app.current_case_type == 'lower':
        result = input_text.lower()
    elif app.current_case_type == 'title':
        result = input_text.title()
    elif app.current_case_type == 'sentence':
        result = _to_sentence_case(input_text)

    # Update the output text area (enable, delete, insert, then disable)
    app.output_text.config(state='normal')
    app.output_text.delete('1.0', tk.END)
    app.output_text.insert('1.0', result)
    app.output_text.config(state='disabled')

def _to_sentence_case(text: str) -> str:
    """
    Converts the given text to sentence case.
    (Capitalizes the first letter of each sentence and after punctuation).
    """
    text = text.lower() # Start by converting all to lowercase
    # Capitalize first letter after a sentence-ending punctuation mark
    text = re.sub(r'([.!?])(\s*)([a-z])', lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)

    # Handle capitalization of the first letter of each line
    lines = text.split('\n')
    processed_lines = []
    for line in lines:
        stripped_line = line.lstrip() # Get line content without leading whitespace
        if stripped_line:
            # Find the index of the first non-whitespace character
            first_char_index = line.find(stripped_line[0])
            # Capitalize the actual first letter of the content, preserving leading whitespace
            capitalized_line = line[:first_char_index] + stripped_line[0].upper() + stripped_line[1:]
            processed_lines.append(capitalized_line)
        else:
            processed_lines.append(line) # Keep empty lines as they are
    return '\n'.join(processed_lines)

def clear_text(app):
    """
    Clears the input and output text areas, resets statistics, and sets focus.
    """
    app.text_tools_input_text.delete('1.0', tk.END)
    app.output_text.config(state='normal') # Enable to clear
    app.output_text.delete('1.0', tk.END)
    app.output_text.config(state='disabled') # Disable again
    update_stats(app) # Reset stats to zero
    app.text_tools_input_text.focus_set() # Set focus back to input
    app.update_status("All text cleared.", TEXT_MUTED)

def copy_to_clipboard(app):
    """
    Copies the content of the output text area to the system clipboard.
    """
    output_text = app.output_text.get('1.0', tk.END + '-1c') # Get all text except last newline
    helpers.copy_to_clipboard_helper(app, output_text, "Text copied to clipboard!")

