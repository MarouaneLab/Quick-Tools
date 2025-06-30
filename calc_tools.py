# calc_tools.py
import tkinter as tk
from tkinter import ttk
import calendar
import datetime

# Import constants and helper functions
from constants import (
    PRIMARY_BG, SECONDARY_BG, TEXT_MUTED, INPUT_BG, INPUT_FG, ACCENT_BLUE,
    HOVER_ACCENT_BLUE, FONT_FAMILY, FONT_INPUT, UNITS_CATEGORIES,
    LENGTH_CONVERSION_FACTORS, MASS_CONVERSION_FACTORS, VOLUME_CONVERSION_FACTORS,
    TEXT_LIGHT, WARNING_RED, SUCCESS_GREEN
)
import helpers

def create_unit_converter_widgets(app, parent_frame):
    """
    Builds the UI widgets for the Calculation Tools tab,
    including unit converters and quick calculators.

    Args:
        app: The main application instance (QuickToolsApp).
        parent_frame: The tkinter frame to place these widgets in.
    """
    # Configure grid layout for the parent frame to accommodate scrolling
    parent_frame.grid_rowconfigure(0, weight=1)
    parent_frame.grid_columnconfigure(0, weight=1)

    # Canvas for scrolling
    canvas = tk.Canvas(parent_frame, bg=PRIMARY_BG, highlightthickness=0, bd=0)
    canvas.grid(row=0, column=0, sticky='nsew')

    # Frame to hold the scrollbar, allowing padding between scrollbar and content
    scrollbar_frame = tk.Frame(parent_frame, bg=PRIMARY_BG)
    scrollbar_frame.grid(row=0, column=1, sticky='ns', padx=(8, 0)) # 8px space

    # Custom themed scrollbar
    style = ttk.Style()
    style.configure('Custom.Vertical.TScrollbar',
                    background=SECONDARY_BG,
                    troughcolor=PRIMARY_BG,
                    bordercolor=SECONDARY_BG,
                    arrowcolor=INPUT_FG,
                    relief='flat',
                    gripcount=0,
                    lightcolor=SECONDARY_BG,
                    darkcolor=SECONDARY_BG)
    vscroll = ttk.Scrollbar(scrollbar_frame, orient='vertical', style='Custom.Vertical.TScrollbar', command=canvas.yview)
    vscroll.pack(fill='y', expand=True)
    canvas.configure(yscrollcommand=vscroll.set)

    # Frame inside the canvas for all scrollable widgets
    scrollable_frame = tk.Frame(canvas, bg=PRIMARY_BG)
    # Bind configure event to update the scroll region
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    # Create window inside canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Enable mousewheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)

    # Configure columns for responsiveness within the scrollable frame
    scrollable_frame.grid_columnconfigure(1, weight=1)
    scrollable_frame.grid_columnconfigure(3, weight=0) # Make column 3 fixed width for copy buttons

    # --- Section Title: Unit Conversion ---
    title_label = ttk.Label(scrollable_frame, text="Unit Conversion:",
                            style='UnitLabel.TLabel', font=(FONT_FAMILY, 12, 'normal'))
    title_label.grid(row=0, column=0, columnspan=4, pady=(10, 18), sticky='w', padx=(2,0))

    # --- General Unit Converter Section ---
    ttk.Label(scrollable_frame, text="From:", style='UnitLabel.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=10)
    app.unit_input_entry = tk.Entry(scrollable_frame, textvariable=app.unit_input_var, font=FONT_INPUT, justify='right',
                                     bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1,
                                     highlightthickness=1, highlightbackground=TEXT_MUTED,
                                     highlightcolor=ACCENT_BLUE, insertbackground=INPUT_FG)
    app.unit_input_entry.grid(row=1, column=1, padx=5, pady=10, sticky='ew')
    app.unit_input_entry.bind('<KeyRelease>', lambda e: _perform_unit_conversion(app))

    app.from_unit_combobox = ttk.Combobox(scrollable_frame, textvariable=app.from_unit_var, state='readonly', font=FONT_INPUT, style='TCombobox')
    app.from_unit_combobox.grid(row=1, column=2, padx=5, pady=10, sticky='ew')
    app.from_unit_combobox.bind('<<ComboboxSelected>>', lambda e: _perform_unit_conversion(app))

    # Swap button for general unit converter
    swap_button = tk.Button(scrollable_frame, text="⇄", command=lambda: _swap_units(app),
                            bg=PRIMARY_BG, fg=INPUT_FG, font=(FONT_FAMILY, 12),
                            relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                            activeforeground=HOVER_ACCENT_BLUE)
    swap_button.grid(row=1, column=3, padx=(5,0), sticky='w')
    app._button_hover_colors[swap_button] = {'original': INPUT_FG, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    ttk.Label(scrollable_frame, text="To:", style='UnitLabel.TLabel').grid(row=2, column=0, sticky='w', padx=10, pady=10)
    app.unit_result_label = tk.Entry(scrollable_frame, textvariable=app.unit_result_var, font=FONT_INPUT, justify='right',
                                      disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                                      relief='solid', bd=1, state='disabled')
    app.unit_result_label.grid(row=2, column=1, padx=5, pady=10, sticky='ew')

    app.to_unit_combobox = ttk.Combobox(scrollable_frame, textvariable=app.to_unit_var, state='readonly', font=FONT_INPUT, style='TCombobox')
    app.to_unit_combobox.grid(row=2, column=2, padx=5, pady=10, sticky='ew')
    app.to_unit_combobox.bind('<<ComboboxSelected>>', lambda e: _perform_unit_conversion(app))

    # Populate dropdowns after both comboboxes are created
    _populate_unit_comboboxes(app)

    # Copy button for general unit converter result
    unit_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: _copy_unit_result(app),
                              bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                              relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                              activeforeground=HOVER_ACCENT_BLUE)
    unit_copy_btn.grid(row=2, column=3, padx=(5,0), sticky='w')
    app._button_hover_colors[unit_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    # --- Separator ---
    separator1 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator1.grid(row=3, column=0, columnspan=5, sticky='ew', pady=20) # Span all columns

    # --- Height Converter ---
    ttk.Label(scrollable_frame, text="Height (ft/in → cm):", style='UnitLabel.TLabel').grid(row=4, column=0, sticky='w', padx=10, pady=10)
    height_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    height_frame.grid(row=4, column=1, padx=5, pady=10, sticky='ew')

    feet_entry = tk.Entry(height_frame, textvariable=app.feet_var, font=FONT_INPUT, width=5, justify='right',
                          bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
    feet_entry.pack(side=tk.LEFT)
    ttk.Label(height_frame, text="'", style='UnitLabel.TLabel').pack(side=tk.LEFT, padx=(2,10))

    inches_entry = tk.Entry(height_frame, textvariable=app.inches_var, font=FONT_INPUT, width=5, justify='right',
                            bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
    inches_entry.pack(side=tk.LEFT)
    ttk.Label(height_frame, text='"', style='UnitLabel.TLabel').pack(side=tk.LEFT, padx=(2,0))

    height_result_entry = tk.Entry(scrollable_frame, textvariable=app.height_cm_var, font=FONT_INPUT, justify='right',
                                   disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                                   relief='solid', bd=1, state='disabled')
    height_result_entry.grid(row=4, column=2, padx=5, pady=10, sticky='ew')

    height_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: _copy_quick_result(app, app.height_cm_var),
                                bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                                relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                                activeforeground=HOVER_ACCENT_BLUE)
    height_copy_btn.grid(row=4, column=3, padx=(5,0), sticky='w')
    app._button_hover_colors[height_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    app.feet_var.trace_add("write", lambda *a: _convert_height(app))
    app.inches_var.trace_add("write", lambda *a: _convert_height(app))

    # --- Weight Converter ---
    weight_label = ttk.Label(scrollable_frame, text="Weight (lb → kg):", style='UnitLabel.TLabel')
    weight_label.grid(row=5, column=0, sticky='w', padx=10, pady=10)
    weight_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    weight_frame.grid(row=5, column=1, padx=5, pady=10, sticky='ew')
    lbs_entry = tk.Entry(weight_frame, textvariable=app.lbs_var, font=FONT_INPUT, justify='right',
                         bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
    lbs_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
    weight_unit_label = ttk.Label(weight_frame, text="lb", style='UnitLabel.TLabel')
    weight_unit_label.pack(side=tk.LEFT, padx=(5,0))
    weight_result_entry = tk.Entry(scrollable_frame, textvariable=app.weight_kg_var, font=FONT_INPUT, justify='right',
                                   disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                                   relief='solid', bd=1, state='disabled')
    weight_result_entry.grid(row=5, column=2, padx=5, pady=10, sticky='ew')
    weight_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: _copy_quick_result(app, app.weight_kg_var),
                                bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                                relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                                activeforeground=HOVER_ACCENT_BLUE)
    weight_copy_btn.grid(row=5, column=3, padx=(5, 0), sticky='w')
    app._button_hover_colors[weight_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    def switch_weight():
        if getattr(app, '_weight_switch_state', 'lb_to_kg') == 'lb_to_kg':
            app._weight_switch_state = 'kg_to_lb'
            weight_label.config(text="Weight (kg → lb):")
            weight_unit_label.config(text="kg")
        else:
            app._weight_switch_state = 'lb_to_kg'
            weight_label.config(text="Weight (lb → kg):")
            weight_unit_label.config(text="lb")
        app.weight_kg_var.set("") # Clear results on switch
        app.lbs_var.set("") # Clear input on switch
        _convert_weight(app) # Recalculate
    switch_btn = tk.Button(scrollable_frame, text="⇄", command=switch_weight,
                           bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 11),
                           relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                           activeforeground=HOVER_ACCENT_BLUE, width=2)
    switch_btn.grid(row=5, column=4, padx=(5, 0), sticky='w')
    app._button_hover_colors[switch_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}
    app.lbs_var.trace_add("write", lambda *a: _convert_weight(app))

    # --- Distance Converter (mile ↔ km) ---
    distance_label = ttk.Label(scrollable_frame, text="Distance (mile → km):", style='UnitLabel.TLabel')
    distance_label.grid(row=6, column=0, sticky='w', padx=10, pady=10)
    app.mile_entry = tk.Entry(scrollable_frame, textvariable=app.mile_var, font=FONT_INPUT, justify='right',
                              bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
    app.mile_entry.grid(row=6, column=1, padx=5, pady=10, sticky='ew')
    app.km_entry = tk.Entry(scrollable_frame, textvariable=app.km_var, font=FONT_INPUT, justify='right',
                            disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                            relief='solid', bd=1, state='disabled')
    app.km_entry.grid(row=6, column=2, padx=5, pady=10, sticky='ew')
    km_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: _copy_quick_result(app, app.km_var),
                           bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                           relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                           activeforeground=HOVER_ACCENT_BLUE)
    km_copy_btn.grid(row=6, column=3, padx=(5,0), sticky='w')
    app._button_hover_colors[km_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    def switch_distance():
        if app._distance_switch_state == 'mile_to_km':
            app._distance_switch_state = 'km_to_mile'
            distance_label.config(text="Distance (km → mile):")
        else:
            app._distance_switch_state = 'mile_to_km'
            distance_label.config(text="Distance (mile → km):")
        app.mile_var.set("") # Clear input
        app.km_var.set("") # Clear result
        _convert_distance(app) # Recalculate
    switch_distance_btn = tk.Button(scrollable_frame, text="⇄", command=switch_distance,
                                    bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 11),
                                    relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                                    activeforeground=HOVER_ACCENT_BLUE, width=2)
    switch_distance_btn.grid(row=6, column=4, padx=(5, 0), sticky='w')
    app._button_hover_colors[switch_distance_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}
    app.mile_var.trace_add("write", lambda *a: _convert_distance(app))

    # --- Area Converter (ft² ↔ m²) ---
    area_label = ttk.Label(scrollable_frame, text="Area (ft² → m²):", style='UnitLabel.TLabel')
    area_label.grid(row=7, column=0, sticky='w', padx=10, pady=10)
    app.ft2_entry = tk.Entry(scrollable_frame, textvariable=app.ft2_var, font=FONT_INPUT, justify='right',
                             bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
    app.ft2_entry.grid(row=7, column=1, padx=5, pady=10, sticky='ew')
    app.m2_entry = tk.Entry(scrollable_frame, textvariable=app.m2_var, font=FONT_INPUT, justify='right',
                            disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                            relief='solid', bd=1, state='disabled')
    app.m2_entry.grid(row=7, column=2, padx=5, pady=10, sticky='ew')
    m2_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: _copy_quick_result(app, app.m2_var),
                           bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                           relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                           activeforeground=HOVER_ACCENT_BLUE)
    m2_copy_btn.grid(row=7, column=3, padx=(5,0), sticky='w')
    app._button_hover_colors[m2_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    def switch_area():
        if app._area_switch_state == 'ft2_to_m2':
            app._area_switch_state = 'm2_to_ft2'
            area_label.config(text="Area (m² → ft²):")
        else:
            app._area_switch_state = 'ft2_to_m2'
            area_label.config(text="Area (ft² → m²):")
        app.ft2_var.set("") # Clear input
        app.m2_var.set("") # Clear result
        _convert_area(app) # Recalculate
    switch_area_btn = tk.Button(scrollable_frame, text="⇄", command=switch_area,
                                bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 11),
                                relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                                activeforeground=HOVER_ACCENT_BLUE, width=2)
    switch_area_btn.grid(row=7, column=4, padx=(5, 0), sticky='w')
    app._button_hover_colors[switch_area_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}
    app.ft2_var.trace_add("write", lambda *a: _convert_area(app))

    # --- Temperature Converter (°F ↔ °C) ---
    temp_label = ttk.Label(scrollable_frame, text="Temperature (°F → °C):", style='UnitLabel.TLabel')
    temp_label.grid(row=8, column=0, sticky='w', padx=10, pady=10)
    app.f_entry = tk.Entry(scrollable_frame, textvariable=app.f_var, font=FONT_INPUT, justify='right',
                           bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
    app.f_entry.grid(row=8, column=1, padx=5, pady=10, sticky='ew')
    app.c_entry = tk.Entry(scrollable_frame, textvariable=app.c_var, font=FONT_INPUT, justify='right',
                           disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                           relief='solid', bd=1, state='disabled')
    app.c_entry.grid(row=8, column=2, padx=5, pady=10, sticky='ew')
    c_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: _copy_quick_result(app, app.c_var),
                           bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                           relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                           activeforeground=HOVER_ACCENT_BLUE)
    c_copy_btn.grid(row=8, column=3, padx=(5,0), sticky='w')
    app._button_hover_colors[c_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    def switch_temp():
        if app._temp_switch_state == 'f_to_c':
            app._temp_switch_state = 'c_to_f'
            temp_label.config(text="Temperature (°C → °F):")
        else:
            app._temp_switch_state = 'f_to_c'
            temp_label.config(text="Temperature (°F → °C):")
        app.f_var.set("") # Clear input
        app.c_var.set("") # Clear result
        _convert_temp(app) # Recalculate
    switch_temp_btn = tk.Button(scrollable_frame, text="⇄", command=switch_temp,
                                bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 11),
                                relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                                activeforeground=HOVER_ACCENT_BLUE, width=2)
    switch_temp_btn.grid(row=8, column=4, padx=(5, 0), sticky='w')
    app._button_hover_colors[switch_temp_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}
    app.f_var.trace_add("write", lambda *a: _convert_temp(app))

    # --- Speed Converter (mph ↔ km/h) ---
    speed_label = ttk.Label(scrollable_frame, text="Speed (mph → km/h):", style='UnitLabel.TLabel')
    speed_label.grid(row=9, column=0, sticky='w', padx=10, pady=10)
    app.mph_entry = tk.Entry(scrollable_frame, textvariable=app.mph_var, font=FONT_INPUT, justify='right',
                             bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
    app.mph_entry.grid(row=9, column=1, padx=5, pady=10, sticky='ew')
    app.kmh_entry = tk.Entry(scrollable_frame, textvariable=app.kmh_var, font=FONT_INPUT, justify='right',
                             disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                             relief='solid', bd=1, state='disabled')
    app.kmh_entry.grid(row=9, column=2, padx=5, pady=10, sticky='ew')
    kmh_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: _copy_quick_result(app, app.kmh_var),
                            bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                            relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                            activeforeground=HOVER_ACCENT_BLUE)
    kmh_copy_btn.grid(row=9, column=3, padx=(5,0), sticky='w')
    app._button_hover_colors[kmh_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    def switch_speed():
        if app._speed_switch_state == 'mph_to_kmh':
            app._speed_switch_state = 'kmh_to_mph'
            speed_label.config(text="Speed (km/h → mph):")
        else:
            app._speed_switch_state = 'mph_to_kmh'
            speed_label.config(text="Speed (mph → km/h):")
        app.mph_var.set("") # Clear input
        app.kmh_var.set("") # Clear result
        _convert_speed(app) # Recalculate
    switch_speed_btn = tk.Button(scrollable_frame, text="⇄", command=switch_speed,
                                 bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 11),
                                 relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                                 activeforeground=HOVER_ACCENT_BLUE, width=2)
    switch_speed_btn.grid(row=9, column=4, padx=(5, 0), sticky='w')
    app._button_hover_colors[switch_speed_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}
    app.mph_var.trace_add("write", lambda *a: _convert_speed(app))


    # --- Separator before Quick Calculation ---
    separator2 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator2.grid(row=10, column=0, columnspan=5, sticky='ew', pady=20)

    # --- Quick Calculation Section ---
    ttk.Label(scrollable_frame, text="Quick Calculation:", style='UnitLabel.TLabel').grid(row=11, column=0, sticky='w', padx=10, pady=10)
    app.area_rows_container = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    app.area_rows_container.grid(row=12, column=0, columnspan=5, sticky='ew')
    area_controls_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    area_controls_frame.grid(row=13, column=0, columnspan=5, sticky='ew', pady=(10,0))
    area_controls_frame.grid_columnconfigure(1, weight=1) # Makes the column for result label expand

    # Add row button for quick calculation
    add_row_btn = tk.Button(area_controls_frame, text="+", command=lambda: _add_area_row(app),
                            bg=SECONDARY_BG, fg=INPUT_FG, font=(FONT_FAMILY, 12, 'bold'),
                            relief='flat', bd=0, cursor='hand2')
    add_row_btn.grid(row=0, column=0, sticky='w', padx=10)

    ttk.Label(area_controls_frame, text="Result:", style='UnitLabel.TLabel').grid(row=0, column=1, sticky='e', padx=(0,10))
    area_result_entry = tk.Entry(area_controls_frame, textvariable=app.area_result_var, font=FONT_INPUT, justify='right',
                                 disabledbackground=INPUT_BG, disabledforeground=INPUT_FG,
                                 relief='solid', bd=1, state='disabled', width=12)
    area_result_entry.grid(row=0, column=2, padx=(0, 12), sticky='ew')
    area_copy_btn = tk.Button(area_controls_frame, text="📋", command=lambda: _copy_quick_result(app, app.area_result_var),
                              bg=PRIMARY_BG, fg=TEXT_MUTED, font=(FONT_FAMILY, 12),
                              relief='flat', bd=0, cursor='hand2', activebackground=PRIMARY_BG,
                              activeforeground=HOVER_ACCENT_BLUE)
    area_copy_btn.grid(row=0, column=3, padx=(0, 0), sticky='w')
    app._button_hover_colors[area_copy_btn] = {'original': TEXT_MUTED, 'hover': HOVER_ACCENT_BLUE, 'type': 'fg'}

    # Operation selection for quick calculation
    ttk.Label(area_controls_frame, text="Operation:", style='UnitLabel.TLabel').grid(row=0, column=4, sticky='e', padx=(18, 4))
    operation_combo = ttk.Combobox(area_controls_frame, textvariable=app.area_operation_var, state='readonly', font=FONT_INPUT, width=12,
                                  values=["Addition", "Subtraction", "Multiplication", "Division"])
    operation_combo.grid(row=0, column=5, sticky='w', padx=(0, 0))
    operation_combo.configure(foreground=INPUT_FG, background=INPUT_BG) # Set colors explicitly
    operation_combo.bind('<<ComboboxSelected>>', lambda e: _calculate_total_area(app))
    _add_area_row(app) # Add the first row by default

    # Set a minimum height for the scrollable area
    scrollable_frame.update_idletasks()
    min_height = 600
    scrollable_frame.config(height=min_height)
    canvas.config(height=min_height)
    # Make sure the scrollable area expands horizontally
    canvas.bind('<Configure>', lambda e: canvas.itemconfig('all', width=e.width))

    # --- Separator after Quick Calculation Operation ---
    separator3 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator3.grid(row=14, column=0, columnspan=5, sticky='ew', pady=(24, 24))

    # --- Percentage Discount Calculator Section ---
    discount_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    discount_frame.grid(row=15, column=0, columnspan=5, sticky='ew', pady=(0, 10))
    for i in range(6): discount_frame.grid_columnconfigure(i, weight=1)

    # Title
    discount_title = ttk.Label(discount_frame, text="Percentage Discount Calculator",
                               style='UnitLabel.TLabel', font=(FONT_FAMILY, 12, 'normal'))
    discount_title.grid(row=0, column=0, columnspan=6, sticky='w', padx=(2,0), pady=(0, 8))

    # Price Before Discount
    price_label = ttk.Label(discount_frame, text="Price:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 11))
    price_label.grid(row=1, column=0, sticky='e', padx=(10, 10), pady=(0, 4))
    price_entry = tk.Entry(discount_frame, textvariable=app.discount_price_var, font=(FONT_FAMILY, 11), justify='right',
                           bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1, width=10)
    price_entry.grid(row=1, column=1, sticky='ew', padx=(0, 2), pady=(0, 4))
    price_entry.config(highlightbackground=SECONDARY_BG, highlightcolor=ACCENT_BLUE, highlightthickness=1)

    # Discount Percentage
    percent_label = ttk.Label(discount_frame, text="Discount %:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 11))
    percent_label.grid(row=1, column=2, sticky='e', padx=(2, 10), pady=(0, 4))
    percent_entry = tk.Entry(discount_frame, textvariable=app.discount_percent_var, font=(FONT_FAMILY, 11), justify='right',
                             bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1, width=8)
    percent_entry.grid(row=1, column=3, sticky='ew', padx=(0, 60), pady=(0, 4))
    percent_entry.config(highlightbackground=SECONDARY_BG, highlightcolor=ACCENT_BLUE, highlightthickness=1)

    # Calculate Button
    calc_btn = tk.Button(discount_frame, text="Calculate", command=lambda: _calculate_discount(app),
                          bg=ACCENT_BLUE, fg=TEXT_LIGHT, font=(FONT_FAMILY, 10, 'bold'),
                          relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                          activebackground=HOVER_ACCENT_BLUE, activeforeground=TEXT_LIGHT)
    calc_btn.grid(row=1, column=4, sticky='ew', padx=(0, 10), pady=(0, 4))
    app._button_hover_colors[calc_btn] = {'original': ACCENT_BLUE, 'hover': HOVER_ACCENT_BLUE}

    # Output Labels
    save_label = ttk.Label(discount_frame, text="You Save:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 10))
    save_label.grid(row=2, column=0, sticky='e', padx=(10, 2), pady=(0, 2))
    save_output = ttk.Label(discount_frame, textvariable=app.discount_save_var, style='UnitLabel.TLabel', font=(FONT_FAMILY, 11, 'bold'))
    save_output.grid(row=2, column=1, sticky='w', padx=(0, 6), pady=(0, 2))

    final_label = ttk.Label(discount_frame, text="Final Price:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 10))
    final_label.grid(row=2, column=2, sticky='e', padx=(2, 2), pady=(0, 2))
    final_output = ttk.Label(discount_frame, textvariable=app.discount_final_var, style='UnitLabel.TLabel', font=(FONT_FAMILY, 11, 'bold'))
    final_output.grid(row=2, column=3, sticky='w', padx=(0, 6), pady=(0, 2))

    # Bind Enter key and live update
    price_entry.bind('<Return>', lambda e: _calculate_discount(app))
    percent_entry.bind('<Return>', lambda e: _calculate_discount(app))
    app.discount_price_var.trace_add('write', lambda *args: _calculate_discount(app))
    app.discount_percent_var.trace_add('write', lambda *args: _calculate_discount(app))

    # --- Separator below Percentage Discount Calculator ---
    separator4 = ttk.Separator(scrollable_frame, orient='horizontal')
    separator4.grid(row=16, column=0, columnspan=5, sticky='ew', pady=(18, 18))

    # --- Tax Calculator Section ---
    tax_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    tax_frame.grid(row=17, column=0, columnspan=5, sticky='ew', pady=(0, 10))
    for i in range(6): tax_frame.grid_columnconfigure(i, weight=1)

    # Title
    tax_title = ttk.Label(tax_frame, text="Tax Calculator", style='UnitLabel.TLabel', font=(FONT_FAMILY, 12, 'normal'))
    tax_title.grid(row=0, column=0, columnspan=6, sticky='w', padx=(2,0), pady=(0, 8))

    # Original Price
    tax_price_label = ttk.Label(tax_frame, text="Price:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 11))
    tax_price_label.grid(row=1, column=0, sticky='e', padx=(10, 10), pady=(0, 4))
    tax_price_entry = tk.Entry(tax_frame, textvariable=app.tax_price_var, font=(FONT_FAMILY, 11), justify='right',
                               bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1, width=10)
    tax_price_entry.grid(row=1, column=1, sticky='ew', padx=(0, 2), pady=(0, 4))
    tax_price_entry.config(highlightbackground=SECONDARY_BG, highlightcolor=ACCENT_BLUE, highlightthickness=1)

    # Tax Percentage
    tax_percent_label = ttk.Label(tax_frame, text="Tax %:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 11))
    tax_percent_label.grid(row=1, column=2, sticky='e', padx=(2, 10), pady=(0, 4))
    tax_percent_entry = tk.Entry(tax_frame, textvariable=app.tax_percent_var, font=(FONT_FAMILY, 11), justify='right',
                                 bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1, width=8)
    tax_percent_entry.grid(row=1, column=3, sticky='ew', padx=(0, 60), pady=(0, 4))
    tax_percent_entry.config(highlightbackground=SECONDARY_BG, highlightcolor=ACCENT_BLUE, highlightthickness=1)

    # Calculate Button
    tax_calc_btn = tk.Button(tax_frame, text="Calculate", command=lambda: _calculate_tax(app),
                             bg=ACCENT_BLUE, fg=TEXT_LIGHT, font=(FONT_FAMILY, 10, 'bold'),
                             relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                             activebackground=HOVER_ACCENT_BLUE, activeforeground=TEXT_LIGHT)
    tax_calc_btn.grid(row=1, column=4, sticky='ew', padx=(0, 10), pady=(0, 4))
    app._button_hover_colors[tax_calc_btn] = {'original': ACCENT_BLUE, 'hover': HOVER_ACCENT_BLUE}

    # Output Labels
    tax_amount_label = ttk.Label(tax_frame, text="Tax Amount:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 10))
    tax_amount_label.grid(row=2, column=0, sticky='e', padx=(10, 2), pady=(0, 2))
    tax_amount_output = ttk.Label(tax_frame, textvariable=app.tax_amount_var, style='UnitLabel.TLabel', font=(FONT_FAMILY, 11, 'bold'))
    tax_amount_output.grid(row=2, column=1, sticky='w', padx=(0, 6), pady=(0, 2))

    tax_total_label = ttk.Label(tax_frame, text="Total Price:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 10))
    tax_total_label.grid(row=2, column=2, sticky='e', padx=(2, 2), pady=(0, 2))
    tax_total_output = ttk.Label(tax_frame, textvariable=app.tax_total_var, style='UnitLabel.TLabel', font=(FONT_FAMILY, 11, 'bold'))
    tax_total_output.grid(row=2, column=3, sticky='w', padx=(0, 6), pady=(0, 2))

    # Bind Enter key and live update
    tax_price_entry.bind('<Return>', lambda e: _calculate_tax(app))
    tax_percent_entry.bind('<Return>', lambda e: _calculate_tax(app))
    app.tax_price_var.trace_add('write', lambda *args: _calculate_tax(app))
    app.tax_percent_var.trace_add('write', lambda *args: _calculate_tax(app))

    # --- Separator below Tax Calculator ---
    separator_age = ttk.Separator(scrollable_frame, orient='horizontal')
    separator_age.grid(row=18, column=0, columnspan=5, sticky='ew', pady=(24, 24))

    # --- Age Calculator Section ---
    age_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    age_frame.grid(row=19, column=0, columnspan=5, sticky='ew', pady=(0, 10))
    for i in range(7): age_frame.grid_columnconfigure(i, weight=1)

    # Title
    age_title = ttk.Label(age_frame, text="Age Calculator", style='UnitLabel.TLabel', font=(FONT_FAMILY, 12, 'normal'))
    age_title.grid(row=0, column=0, columnspan=6, sticky='w', padx=(2,0), pady=(0, 8))

    # Birthdate Input (Year, Month, Day fields)
    entry_width = 6
    pad_x = 8
    year_label = ttk.Label(age_frame, text="Year:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 11))
    year_label.grid(row=1, column=0, sticky='e', padx=(10, pad_x), pady=(0, 4))
    year_entry = tk.Entry(age_frame, textvariable=app.birth_year_var, font=(FONT_FAMILY, 11),
                         bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1, width=entry_width, justify='left')
    year_entry.grid(row=1, column=1, sticky='ew', padx=(0, pad_x), pady=(0, 4))
    year_entry.config(highlightbackground=SECONDARY_BG, highlightcolor=ACCENT_BLUE, highlightthickness=1)

    month_label = ttk.Label(age_frame, text="Month:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 11))
    month_label.grid(row=1, column=2, sticky='e', padx=(0, pad_x), pady=(0, 4))
    month_entry = tk.Entry(age_frame, textvariable=app.birth_month_var, font=(FONT_FAMILY, 11),
                          bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1, width=entry_width, justify='left')
    month_entry.grid(row=1, column=3, sticky='ew', padx=(0, pad_x), pady=(0, 4))
    month_entry.config(highlightbackground=SECONDARY_BG, highlightcolor=ACCENT_BLUE, highlightthickness=1)

    day_label = ttk.Label(age_frame, text="Day:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 11))
    day_label.grid(row=1, column=4, sticky='e', padx=(0, pad_x), pady=(0, 4))
    day_entry = tk.Entry(age_frame, textvariable=app.birth_day_var, font=(FONT_FAMILY, 11),
                        bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1, width=entry_width, justify='left')
    day_entry.grid(row=1, column=5, sticky='ew', padx=(0, 48), pady=(0, 4)) # Extra padding
    day_entry.config(highlightbackground=SECONDARY_BG, highlightcolor=ACCENT_BLUE, highlightthickness=1)

    # Calculate Button
    age_calc_btn = tk.Button(age_frame, text="Calculate", command=lambda: _calculate_age(app),
                             bg=ACCENT_BLUE, fg=TEXT_LIGHT, font=(FONT_FAMILY, 10, 'bold'),
                             relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                             activebackground=HOVER_ACCENT_BLUE, activeforeground=TEXT_LIGHT)
    age_calc_btn.grid(row=1, column=6, sticky='ew', padx=(0, 10), pady=(0, 4))
    app._button_hover_colors[age_calc_btn] = {'original': ACCENT_BLUE, 'hover': HOVER_ACCENT_BLUE}

    # Output Label
    age_result_label = ttk.Label(age_frame, text="Age:", style='UnitLabel.TLabel', font=(FONT_FAMILY, 10))
    age_result_label.grid(row=2, column=0, sticky='e', padx=(10, 2), pady=(0, 2))
    age_result_output = ttk.Label(age_frame, textvariable=app.age_result_var, style='UnitLabel.TLabel', font=(FONT_FAMILY, 11, 'bold'))
    age_result_output.grid(row=2, column=1, sticky='w', padx=(0, 6), pady=(0, 2))

    # Bind Enter key and live update
    year_entry.bind('<Return>', lambda e: _calculate_age(app))
    month_entry.bind('<Return>', lambda e: _calculate_age(app))
    day_entry.bind('<Return>', lambda e: _calculate_age(app))
    app.birth_year_var.trace_add('write', lambda *args: _calculate_age(app))
    app.birth_month_var.trace_add('write', lambda *args: _calculate_age(app))
    app.birth_day_var.trace_add('write', lambda *args: _calculate_age(app))


def _populate_unit_comboboxes(app):
    """
    Populates the 'From' and 'To' unit comboboxes with all available units.
    """
    all_units = sorted([u for sublist in UNITS_CATEGORIES.values() for u in sublist])
    app.from_unit_combobox['values'] = all_units
    app.to_unit_combobox['values'] = all_units
    # Set default values if they exist in the list
    if 'm' in all_units: app.from_unit_var.set('m')
    if 'cm' in all_units: app.to_unit_var.set('cm')

def _swap_units(app):
    """
    Swaps the 'From' and 'To' units in the general unit converter.
    """
    from_val, to_val = app.from_unit_var.get(), app.to_unit_var.get()
    app.from_unit_var.set(to_val)
    app.to_unit_var.set(from_val)
    _perform_unit_conversion(app) # Recalculate after swap
    app.update_status("Units swapped!", TEXT_MUTED)

def _perform_unit_conversion(app):
    """
    Performs unit conversion based on user input and selected units.
    Handles standard units and special cases like temperature.
    """
    try:
        value_str = app.unit_input_var.get().replace(',', '.')
        value = float(value_str) if value_str.strip() else 0.0 # Handle empty input gracefully

        from_u, to_u = app.from_unit_var.get(), app.to_unit_var.get()
        if not from_u or not to_u:
            app.unit_result_var.set("N/A")
            return

        # Special case for temperature conversion (non-linear)
        if from_u in ['°C', '°F'] and to_u in ['°C', '°F']:
            if from_u == to_u:
                result = value
            elif from_u == '°C' and to_u == '°F':
                result = (value * 9/5) + 32
            elif from_u == '°F' and to_u == '°C':
                result = (value - 32) * 5/9
            else: # Should not happen with current unit lists
                result = 'N/A'
            app.unit_result_var.set(f"{result:.2f}" if isinstance(result, (float, int)) else str(result))
            return

        # For other unit types, find their category and use conversion factors
        from_cat = None
        to_cat = None
        for cat, units in UNITS_CATEGORIES.items():
            if from_u in units:
                from_cat = cat
            if to_u in units:
                to_cat = cat

        # Ensure both units belong to the same category
        if from_cat != to_cat or from_cat is None:
            app.unit_result_var.set("N/A")
            return

        # Get the appropriate conversion factors dictionary
        factors = None
        if from_cat == "Length":
            factors = LENGTH_CONVERSION_FACTORS
        elif from_cat == "Mass":
            factors = MASS_CONVERSION_FACTORS
        elif from_cat == "Volume":
            factors = VOLUME_CONVERSION_FACTORS

        if factors:
            # Convert 'from' value to base unit, then from base unit to 'to' unit
            base_val = value * factors[from_u]
            result = base_val / factors[to_u]
            app.unit_result_var.set(f"{result:.2f}")
        else:
            app.unit_result_var.set("N/A") # Should not happen if categories are correctly mapped
    except ValueError:
        app.unit_result_var.set("Invalid Input")
    except KeyError:
        app.unit_result_var.set("Unit Not Found") # Fallback for unexpected unit issues

def _convert_height(app, *args):
    """Converts feet and inches to centimeters."""
    try:
        feet = float(app.feet_var.get() or 0)
        inches = float(app.inches_var.get() or 0)
        total_inches = (feet * 12) + inches
        cm = total_inches * 2.54
        app.height_cm_var.set(f"{cm:.2f} cm")
    except ValueError:
        app.height_cm_var.set("Invalid")

def _convert_weight(app, *args):
    """Converts weight between pounds and kilograms based on switch state."""
    try:
        if getattr(app, '_weight_switch_state', 'lb_to_kg') == 'lb_to_kg':
            lbs = float(app.lbs_var.get() or 0)
            kg = lbs * 0.453592
            app.weight_kg_var.set(f"{kg:.2f} kg")
        else: # kg_to_lb
            kg = float(app.lbs_var.get() or 0)
            lbs = kg / 0.453592
            app.weight_kg_var.set(f"{lbs:.2f} lb")
    except ValueError:
        app.weight_kg_var.set("Invalid")

def _convert_distance(app, *args):
    """Converts distance between miles and kilometers based on switch state."""
    try:
        if getattr(app, '_distance_switch_state', 'mile_to_km') == 'mile_to_km':
            miles = float(app.mile_var.get() or 0)
            km = miles * 1.60934
            app.km_var.set(f"{km:.2f} km")
        else: # km_to_mile
            km = float(app.mile_var.get() or 0)
            miles = km / 1.60934
            app.km_var.set(f"{miles:.2f} mile")
    except ValueError:
        app.km_var.set("Invalid")

def _convert_area(app, *args):
    """Converts area between square feet and square meters based on switch state."""
    try:
        if getattr(app, '_area_switch_state', 'ft2_to_m2') == 'ft2_to_m2':
            val_str = app.ft2_var.get()
            if not val_str.strip(): # Handle empty input string
                app.m2_var.set("")
                return
            ft2 = float(val_str)
            m2 = ft2 * 0.092903
            app.m2_var.set(f"{m2:.2f} m²")
        else: # m2_to_ft2
            val_str = app.ft2_var.get()
            if not val_str.strip(): # Handle empty input string
                app.m2_var.set("")
                return
            m2 = float(val_str)
            ft2 = m2 / 0.092903
            app.m2_var.set(f"{ft2:.2f} ft²")
    except ValueError:
        app.m2_var.set("Invalid")

def _convert_temp(app, *args):
    """Converts temperature between Fahrenheit and Celsius based on switch state."""
    try:
        if getattr(app, '_temp_switch_state', 'f_to_c') == 'f_to_c':
            f_temp = float(app.f_var.get() or 0)
            c_temp = (f_temp - 32) * 5/9
            app.c_var.set(f"{c_temp:.2f} °C")
        else: # c_to_f
            c_temp = float(app.f_var.get() or 0)
            f_temp = (c_temp * 9/5) + 32
            app.c_var.set(f"{f_temp:.2f} °F")
    except ValueError:
        app.c_var.set("Invalid")

def _convert_speed(app, *args):
    """Converts speed between miles per hour and kilometers per hour based on switch state."""
    try:
        if getattr(app, '_speed_switch_state', 'mph_to_kmh') == 'mph_to_kmh':
            mph = float(app.mph_var.get() or 0)
            kmh = mph * 1.60934
            app.kmh_var.set(f"{kmh:.2f} km/h")
        else: # kmh_to_mph
            kmh = float(app.mph_var.get() or 0)
            mph = kmh / 1.60934
            app.kmh_var.set(f"{mph:.2f} mph")
    except ValueError:
        app.kmh_var.set("Invalid")

def _add_area_row(app):
    """
    Creates and adds a new row for the area calculator, allowing up to 7 numeric input fields.
    Each row has a '+' button to add more columns and a '🗑️' button to remove the row.
    """
    row_frame = tk.Frame(app.area_rows_container, bg=PRIMARY_BG)
    row_frame.pack(fill=tk.X, expand=True, pady=2)

    # Use a grid layout for equal spacing of input fields
    value_vars = []
    entry_widgets = []

    # Function to add a new column (input field) to the current row
    def add_column():
        col = len(value_vars)
        if col >= 7: # Limit to 7 input fields per row
            return

        value_var = tk.StringVar()
        entry = tk.Entry(row_frame, textvariable=value_var, font=FONT_INPUT, justify='right',
                         bg=INPUT_BG, fg=INPUT_FG, relief='solid', bd=1)
        entry.grid(row=0, column=col, padx=4, pady=2, sticky='ew')
        # Configure column to expand equally, using a uniform group for consistency
        row_frame.grid_columnconfigure(col, weight=1, uniform='area')
        value_vars.append(value_var)
        entry_widgets.append(entry)
        value_var.trace_add("write", lambda *_: _calculate_total_area(app)) # Live update calculation

        # Update visibility/position of '+' and '🗑️' buttons
        if len(value_vars) >= 7: # Hide '+' button if max columns reached
            plus_btn.grid_remove()
        else:
            # Place '+' button after the last input field
            plus_btn.grid(row=0, column=col + 1, padx=(4, 0), pady=2, sticky='ew')
        # Always keep remove button at the very end
        remove_btn.grid(row=0, column=col + 2, padx=(8, 0), pady=2, sticky='ew')
        _calculate_total_area(app) # Recalculate after adding a column

    # Create '+' (add column) and '🗑️' (remove row) buttons
    plus_btn = tk.Button(row_frame, text="+", font=(FONT_FAMILY, 12, 'bold'),
                         bg=SECONDARY_BG, fg=INPUT_FG, relief='flat', bd=0, cursor='hand2')
    remove_btn = tk.Button(row_frame, text="🗑️", font=(FONT_FAMILY, 12),
                            bg=PRIMARY_BG, fg=WARNING_RED, relief='flat', bd=0, cursor='hand2',
                            command=lambda: _remove_area_row(app, row_frame)) # Pass row_frame for removal

    plus_btn.configure(command=add_column) # Bind '+' button to add_column function

    add_column() # Add the first column when a new row is created

    # Store row data for later management
    row_data = {
        'value_vars': value_vars,
        'frame': row_frame,
        'plus_btn': plus_btn,
        'remove_btn': remove_btn
    }
    app.area_rows.append(row_data) # Add this row's data to the main app's list

    _calculate_total_area(app) # Recalculate total area after adding a new row

def _remove_area_row(app, row_frame):
    """
    Removes a specific row from the area calculator and updates the total.

    Args:
        app: The main application instance.
        row_frame: The tkinter frame of the row to be removed.
    """
    for row in app.area_rows:
        if row['frame'] == row_frame:
            app.area_rows.remove(row)
            break
    row_frame.destroy() # Destroy the tkinter frame to remove it from UI
    _calculate_total_area(app) # Recalculate total area after removal

def _calculate_total_area(app, *args):
    """
    Performs the selected arithmetic operation (addition, subtraction,
    multiplication, division) on all values from all input fields
    across all dynamic area rows.
    """
    values = []
    # Collect all numerical values from all rows and columns
    for row in app.area_rows:
        for value_var in row.get('value_vars', []):
            try:
                val_str = value_var.get()
                if not val_str.strip(): # Skip empty inputs
                    continue
                val = float(val_str)
                values.append(val)
            except (ValueError, KeyError):
                continue # Ignore non-numeric inputs

    operation = app.area_operation_var.get() # Get the selected operation
    result = 0.0

    if not values:
        result = 0.0 # If no values, result is 0
    elif operation == "Addition":
        result = sum(values)
    elif operation == "Subtraction":
        # For subtraction, subtract subsequent values from the first one
        result = values[0] if values else 0.0
        for v in values[1:]:
            result -= v
    elif operation == "Multiplication":
        result = 1.0 # Start with 1 for multiplication
        for v in values:
            result *= v
    elif operation == "Division":
        result = values[0] if values else 0.0
        for v in values[1:]:
            try:
                if v == 0: # Handle division by zero
                    result = float('inf') if result > 0 else float('-inf') if result < 0 else float('nan')
                    break
                result /= v
            except ZeroDivisionError: # Explicitly catch ZeroDivisionError
                result = float('inf') # Set to infinity for visual feedback
                break # Stop further calculations
    
    # Update the result display, handling potential infinite/NaN results
    if result == float('inf') or result == float('-inf'):
        app.area_result_var.set("Infinity")
    elif result == float('nan'):
        app.area_result_var.set("Error")
    else:
        app.area_result_var.set(f"{result:.2f}")


def _calculate_discount(app):
    """Calculates and displays the discount savings and final price."""
    try:
        price_str = app.discount_price_var.get().replace(',', '.')
        percent_str = app.discount_percent_var.get().replace(',', '.')

        # Handle empty inputs by treating them as 0 for calculation purposes
        price = float(price_str) if price_str.strip() else 0.0
        percent = float(percent_str) if percent_str.strip() else 0.0

        if price < 0 or percent < 0:
            raise ValueError("Price or percentage cannot be negative.")

        save = price * percent / 100
        final = price - save

        app.discount_save_var.set(f"${save:.2f}")
        app.discount_final_var.set(f"${final:.2f}")
        app.update_status("Discount calculated!", SUCCESS_GREEN)
    except ValueError as e:
        app.discount_save_var.set("$0.00")
        app.discount_final_var.set("$0.00")
        app.update_status(f"Invalid input: {e}", WARNING_RED)
    except Exception as e:
        app.discount_save_var.set("$0.00")
        app.discount_final_var.set("$0.00")
        app.update_status(f"Error calculating discount: {e}", WARNING_RED)


def _calculate_tax(app):
    """Calculates and displays the tax amount and total price after tax."""
    try:
        price_str = app.tax_price_var.get().replace(',', '.')
        percent_str = app.tax_percent_var.get().replace(',', '.')

        # Handle empty inputs by treating them as 0 for calculation purposes
        price = float(price_str) if price_str.strip() else 0.0
        percent = float(percent_str) if percent_str.strip() else 0.0

        if price < 0 or percent < 0:
            raise ValueError("Price or percentage cannot be negative.")

        tax = price * percent / 100
        total = price + tax

        app.tax_amount_var.set(f"${tax:.2f}")
        app.tax_total_var.set(f"${total:.2f}")
        app.update_status("Tax calculated!", SUCCESS_GREEN)
    except ValueError as e:
        app.tax_amount_var.set("$0.00")
        app.tax_total_var.set("$0.00")
        app.update_status(f"Invalid input: {e}", WARNING_RED)
    except Exception as e:
        app.tax_amount_var.set("$0.00")
        app.tax_total_var.set("$0.00")
        app.update_status(f"Error calculating tax: {e}", WARNING_RED)

def _calculate_age(app):
    """
    Calculates the age based on the provided birth year, month, and day.
    Displays age in years, months, and days.
    """
    year_str = app.birth_year_var.get().strip()
    month_str = app.birth_month_var.get().strip()
    day_str = app.birth_day_var.get().strip()
    today = datetime.date.today()

    try:
        # Validate year input (4 digits)
        if not year_str or not year_str.isdigit() or len(year_str) != 4:
            app.age_result_var.set("") # Clear result if year is invalid
            return
        year = int(year_str)

        # Validate month input (1-12)
        if not month_str or not month_str.isdigit():
            month = 1 # Default to January if month is empty
        else:
            month = int(month_str)
            if not (1 <= month <= 12):
                app.age_result_var.set("")
                return

        # Validate day input based on month and year (including leap years)
        if not day_str or not day_str.isdigit():
            day = 1 # Default to 1st if day is empty
        else:
            day = int(day_str)
            # calendar.monthrange returns (weekday_of_first_day, num_days_in_month)
            if not (1 <= day <= calendar.monthrange(year, month)[1]):
                app.age_result_var.set("")
                return

        birthdate = datetime.date(year, month, day)

        # Calculate difference
        years = today.year - birthdate.year
        months = today.month - birthdate.month
        days = today.day - birthdate.day

        # Adjust for negative days (if current day is before birth day in the month)
        if days < 0:
            months -= 1
            # Get days in previous month relative to today's date
            prev_month = today.month - 1 if today.month > 1 else 12
            prev_year = today.year if today.month > 1 else today.year - 1
            days += calendar.monthrange(prev_year, prev_month)[1]

        # Adjust for negative months (if current month is before birth month)
        if months < 0:
            years -= 1
            months += 12

        # Format result string based on input completeness
        result = f"{years} years"
        if month_str: # Only add months if month input was provided
            result += f", {months} months"
        if day_str: # Only add days if day input was provided
            result += f", {days} days"

        app.age_result_var.set(result)
    except ValueError:
        app.age_result_var.set("Invalid Date") # General error for parsing issues
    except Exception: # Catch any other unexpected errors
        app.age_result_var.set("") # Clear result for unknown errors

def _copy_quick_result(app, string_var):
    """
    Copies the numerical part of a quick calculation result (e.g., '123.45 cm' -> '123.45')
    to the clipboard.
    """
    full_text = string_var.get()
    # Extract only the numerical part by splitting at the first space
    numerical_part = full_text.split(" ")[0]

    if not numerical_part or "Invalid" in numerical_part or "Error" in numerical_part:
        app.update_status("Nothing to copy!", WARNING_RED)
        return

    helpers.copy_to_clipboard_helper(app, numerical_part, "Result copied to clipboard!")

def _copy_unit_result(app):
    """
    Copies the full text of the general unit converter result
    (e.g., '123.45 cm') to the clipboard.
    """
    result_text = app.unit_result_var.get()

    if not result_text or "Invalid" in result_text or "N/A" in result_text:
        app.update_status("Nothing to copy!", WARNING_RED)
        return

    helpers.copy_to_clipboard_helper(app, result_text, "Result copied to clipboard!")

