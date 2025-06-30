# main_app.py
import tkinter as tk
from tkinter import ttk
import sys

# Import constants and functional modules
from constants import (
    PRIMARY_BG, SECONDARY_BG, TEXT_MUTED, ACCENT_BLUE, TEXT_LIGHT, INPUT_BG, INPUT_FG,
    WARNING_RED, HOVER_PRIMARY_BG, HOVER_ACCENT_BLUE, HOVER_WARNING_RED,
    STATUS_MESSAGE_DURATION_MS, FONT_FAMILY, FONT_REGULAR, FONT_BOLD, FONT_TITLE,
    FONT_INPUT, FONT_STATS_COUNT, FONT_STATS_TEXT, PALETTE_INDIGO,
    LENGTH_CONVERSION_FACTORS, MASS_CONVERSION_FACTORS, VOLUME_CONVERSION_FACTORS,
    UNITS_CATEGORIES, GRADIENT_STYLES, GRADIENT_PRESETS
)

# Import functional modules
import text_tools
import calc_tools
import creative_tools
import helpers

class QuickToolsApp:
    """
    Main application class for Quick Tools, handling UI setup,
    tab management, and integrating various utility modules.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Quick Tools")
        self.root.geometry("850x750")
        self.root.configure(bg=PRIMARY_BG)

        # Center the window on the screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.minsize(750, 700) # Increased min height for new features

        # --- Configure ttk Styles with new Fonts ---
        self.style = ttk.Style()
        self.style.theme_use('alt') # Use a theme that allows more customization

        # General styles for TFrame and TLabel
        self.style.configure('TFrame', background=PRIMARY_BG)
        self.style.configure('TLabel', background=PRIMARY_BG, foreground=TEXT_LIGHT, font=FONT_REGULAR)

        # Specific styles for titles and stats
        self.style.configure('Title.TLabel', font=FONT_TITLE)
        self.style.configure('InputLabel.TLabel', foreground=TEXT_MUTED, font=(FONT_FAMILY, 12))
        self.style.configure('StatsCount.TLabel', foreground=TEXT_LIGHT, background=SECONDARY_BG, font=FONT_STATS_COUNT)
        self.style.configure('StatsText.TLabel', foreground=TEXT_MUTED, background=SECONDARY_BG, font=FONT_STATS_TEXT)

        # Notebook (tabs) styles
        self.style.configure('TNotebook', background=PRIMARY_BG, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=SECONDARY_BG, foreground=TEXT_MUTED, font=FONT_BOLD, padding=[20, 10])
        self.style.map('TNotebook.Tab',
                       background=[('selected', INPUT_BG)],
                       foreground=[('selected', TEXT_LIGHT)],
                       expand=[('selected', [1,1,1,0])]) # Visual effect for selected tab

        # Combobox styles
        self.style.configure('TCombobox',
                             fieldbackground=INPUT_BG,
                             foreground=INPUT_FG,
                             selectbackground=ACCENT_BLUE,
                             selectforeground=TEXT_LIGHT,
                             background=SECONDARY_BG,
                             arrowcolor=INPUT_FG,
                             bordercolor=TEXT_MUTED,
                             lightcolor=TEXT_MUTED,
                             darkcolor=TEXT_MUTED,
                             padding=[5, 5],
                             font=FONT_INPUT)

        # Listbox within Combobox styles (for dropdown options)
        self.root.option_add('*TCombobox*Listbox.background', INPUT_BG)
        self.root.option_add('*TCombobox*Listbox.foreground', INPUT_FG)
        self.root.option_add('*TCombobox*Listbox.selectBackground', ACCENT_BLUE)
        self.root.option_add('*TCombobox*Listbox.selectForeground', TEXT_LIGHT)
        self.root.option_add('*TCombobox*Listbox.font', FONT_REGULAR)

        # Unit converter specific label style
        self.style.configure('UnitLabel.TLabel', foreground=INPUT_FG, background=PRIMARY_BG, font=(FONT_FAMILY, 12))

        # Initialize attributes for dynamic elements and state management
        self.current_case_type = 'upper' # Default text case for Text Tools
        self._button_hover_colors = {} # Dictionary to manage button hover effects
        self.area_rows = [] # List to manage dynamic area calculator rows

        # Initialize specific vars that are used across modules
        self.creative_hex_var = tk.StringVar(value="#AABBCC") # For Color Generator
        self.gradient_type_var = tk.StringVar(value='Linear') # For Gradient Generator
        self.gradient_num_colors_var = tk.IntVar(value=3) # For Gradient Generator
        self.gradient_style_var = tk.StringVar(value='Warm') # For Gradient Generator
        self.gradient_rotation_var = tk.IntVar(value=45) # For Gradient Generator
        self.export_width_var = tk.StringVar(value="800") # For Gradient Export
        self.export_height_var = tk.StringVar(value="400") # For Gradient Export
        self._gradient_colors = [] # Current gradient colors
        self._gradient_positions = [] # Current gradient stop positions
        self._dragging_stop = None # State for gradient stop dragging
        self._drag_mouse_offset_x = None # X offset for gradient stop drag
        self._drag_mouse_offset_y = None # Y offset for gradient stop drag
        self._last_gradient_signature = None # To prevent repetitive random gradients

        # Unit Converter variables
        self.unit_input_var = tk.StringVar(value="1.00")
        self.from_unit_var = tk.StringVar()
        self.to_unit_var = tk.StringVar()
        self.unit_result_var = tk.StringVar(value="0.00")

        self.feet_var = tk.StringVar()
        self.inches_var = tk.StringVar()
        self.height_cm_var = tk.StringVar()

        self.lbs_var = tk.StringVar()
        self.weight_kg_var = tk.StringVar()
        self._weight_switch_state = 'lb_to_kg'

        self.mile_var = tk.StringVar()
        self.km_var = tk.StringVar()
        self._distance_switch_state = 'mile_to_km'

        self.ft2_var = tk.StringVar()
        self.m2_var = tk.StringVar()
        self._area_switch_state = 'ft2_to_m2'

        self.f_var = tk.StringVar()
        self.c_var = tk.StringVar()
        self._temp_switch_state = 'f_to_c'

        self.mph_var = tk.StringVar()
        self.kmh_var = tk.StringVar()
        self._speed_switch_state = 'mph_to_kmh'

        self.area_result_var = tk.StringVar(value="0.00")
        self.area_operation_var = tk.StringVar(value="Addition")

        self.discount_price_var = tk.StringVar()
        self.discount_percent_var = tk.StringVar()
        self.discount_save_var = tk.StringVar(value="$0.00")
        self.discount_final_var = tk.StringVar(value="$0.00")

        self.tax_price_var = tk.StringVar()
        self.tax_percent_var = tk.StringVar()
        self.tax_amount_var = tk.StringVar(value="$0.00")
        self.tax_total_var = tk.StringVar(value="$0.00")

        self.birth_year_var = tk.StringVar()
        self.birth_month_var = tk.StringVar()
        self.birth_day_var = tk.StringVar()
        self.age_result_var = tk.StringVar(value="0 years")

        # Create the main UI widgets
        self.create_widgets()

        # Set initial status message
        self.update_status("Ready.", TEXT_MUTED)

        # Bind tab change event to update focus and status
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def create_widgets(self):
        """
        Sets up the main notebook (tabbed interface) and
        calls functions to populate each tab.
        """
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=30, pady=(20, 6))

        # Text Tools Tab
        self.text_tools_frame = tk.Frame(self.notebook, bg=PRIMARY_BG)
        self.notebook.add(self.text_tools_frame, text="Text Tools")
        text_tools.create_text_tools_widgets(self, self.text_tools_frame)

        # Calculation Tools Tab (Unit Converter, Quick Calc, Discount, Tax, Age)
        self.unit_converter_frame = tk.Frame(self.notebook, bg=PRIMARY_BG)
        self.notebook.add(self.unit_converter_frame, text="Calculation Tools")
        calc_tools.create_unit_converter_widgets(self, self.unit_converter_frame)

        # Creative Tools Tab (Color Generator, Gradient Generator)
        creative_tools.build_creative_tools_tab(self, self.notebook)

        # Status bar at the bottom of the main window
        self.status_label = tk.Label(self.root, text="Ready.",
                                     bg=SECONDARY_BG, fg=TEXT_MUTED,
                                     font=(FONT_FAMILY, 10), anchor='w', padx=20, pady=8)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        # Apply hover effects to all registered buttons
        self.bind_hover_effects()

    def on_tab_change(self, event):
        """
        Handles actions when the notebook tab is changed,
        such as setting focus and updating status messages.
        """
        selected_tab_text = self.notebook.tab(self.notebook.select(), "text")
        if selected_tab_text == "Text Tools":
            self.text_tools_input_text.focus_set() # Focus on text input in Text Tools tab
            text_tools.update_stats(self) # Update stats when switching to Text Tools
            self.update_status("Ready (Text Tools).", TEXT_MUTED)
        elif selected_tab_text == "Calculation Tools":
            self.unit_input_entry.focus_set() # Focus on unit input in Calculation Tools tab
            calc_tools._perform_unit_conversion(self) # Perform initial conversion
            self.update_status("Ready (Calculation Tools).", TEXT_MUTED)
        elif selected_tab_text == "Creative Tools":
            self.creative_hex_entry.focus_set() # Focus on hex input in Creative Tools tab
            self.update_status("Ready (Creative Tools).", TEXT_MUTED)


    def bind_hover_effects(self):
        """
        Applies universal hover effects to buttons registered
        in the _button_hover_colors dictionary.
        """
        for btn, colors in self._button_hover_colors.items():
            if colors.get('type') == 'fg': # If type is 'fg', change foreground color on hover
                btn.bind('<Enter>', lambda e, b=btn, hc=colors['hover']: b.config(fg=hc))
                btn.bind('<Leave>', lambda e, b=btn, oc=colors['original']: b.config(fg=oc))
            else: # Otherwise, change background color on hover
                btn.bind('<Enter>', lambda e, b=btn, hc=colors['hover']: b.config(bg=hc))
                btn.bind('<Leave>', lambda e, b=btn, oc=colors['original']: b.config(bg=oc))

    def update_status(self, message: str, color: str = None):
        """
        Updates the status bar with a given message and color,
        and sets a timer to revert it to 'Ready.'
        """
        self.status_label.config(text=message, fg=color or TEXT_LIGHT)
        # Cancel any existing status timer to prevent message flickers
        if hasattr(self, '_status_timer'):
            self.root.after_cancel(self._status_timer)
        # Set a new timer to revert the status message
        self._status_timer = self.root.after(STATUS_MESSAGE_DURATION_MS,
                                            lambda: self.status_label.config(text="Ready.", fg=TEXT_MUTED))

# --- Main block to launch the app ---
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = QuickToolsApp(root)
        root.mainloop()
    except Exception as e:
        import traceback
        print("Failed to launch the app:", e)
        traceback.print_exc()
        sys.exit(1) # Exit with an error code

