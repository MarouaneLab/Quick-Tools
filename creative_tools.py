# creative_tools.py
import tkinter as tk
from tkinter import ttk, filedialog as fd, Toplevel
import random
import colorsys
import time
import math
from functools import partial
import os
import re

try:
    from PIL import Image, ImageTk, ImageDraw, ImageFont
except ImportError:
    # Fallback for systems without Pillow, showing a warning
    Image = None
    ImageTk = None
    ImageDraw = None
    ImageFont = None
    print("Pillow library not found. Image export features will be disabled. Please install it with: pip install Pillow")

# Import constants and helper functions
from constants import (
    PRIMARY_BG, SECONDARY_BG, PALETTE_INDIGO, ACCENT_BLUE, TEXT_LIGHT, TEXT_MUTED,
    INPUT_BG, INPUT_FG, WARNING_RED, SUCCESS_GREEN, HOVER_ACCENT_BLUE,
    FONT_FAMILY, FONT_INPUT, GRADIENT_STYLES, GRADIENT_PRESETS
)
import helpers

def build_creative_tools_tab(app, notebook):
    """
    Builds the 'Creative Tools' tab, which includes the Color Generator
    and Gradient Generator sections.

    Args:
        app: The main application instance (QuickToolsApp).
        notebook: The ttk.Notebook widget to add the tab to.
    """
    creative_tab = tk.Frame(notebook, bg=PRIMARY_BG)
    notebook.add(creative_tab, text="Creative Tools")

    # Canvas for scrolling
    canvas = tk.Canvas(creative_tab, bg=PRIMARY_BG, highlightthickness=0, bd=0)
    canvas.grid(row=0, column=0, sticky='nsew')

    # Scrollbar frame for padding
    scrollbar_frame = tk.Frame(creative_tab, bg=PRIMARY_BG)
    scrollbar_frame.grid(row=0, column=1, sticky='ns', padx=(8, 0))

    # Custom themed scrollbar
    style = ttk.Style()
    style.configure('Creative.Vertical.TScrollbar',
                    background=SECONDARY_BG,
                    troughcolor=PRIMARY_BG,
                    bordercolor=SECONDARY_BG,
                    arrowcolor=INPUT_FG,
                    relief='flat',
                    gripcount=0,
                    lightcolor=SECONDARY_BG,
                    darkcolor=SECONDARY_BG)
    vscroll = ttk.Scrollbar(scrollbar_frame, orient='vertical', style='Creative.Vertical.TScrollbar', command=canvas.yview)
    vscroll.pack(fill='y', expand=True)
    canvas.configure(yscrollcommand=vscroll.set)

    # Frame inside canvas for all widgets
    scrollable_frame = tk.Frame(canvas, bg=PRIMARY_BG)
    scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Update scroll region to fit content
    def _update_scrollregion(event=None):
        canvas.update_idletasks()
        bbox = canvas.bbox(scrollable_frame_id)
        if bbox:
            canvas.configure(scrollregion=bbox)
            # If content is smaller than canvas, anchor to top
            if bbox[3] < canvas.winfo_height():
                canvas.yview_moveto(0)
    scrollable_frame.bind("<Configure>", _update_scrollregion)
    canvas.bind('<Configure>', _update_scrollregion)

    # Mousewheel scrolling
    def _on_mousewheel(event):
        if canvas.bbox(scrollable_frame_id) and canvas.bbox(scrollable_frame_id)[3] > canvas.winfo_height():
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)

    creative_tab.grid_rowconfigure(0, weight=1)
    creative_tab.grid_columnconfigure(0, weight=1)

    # --- Color Generator Section ---
    color_gen_title = tk.Label(scrollable_frame, text="Color Generator", font=(FONT_FAMILY, 11), bg=PRIMARY_BG, fg=INPUT_FG)
    color_gen_title.pack(anchor='w', pady=(28, 14), padx=(10,0))

    color_input_label = tk.Label(scrollable_frame, text="HEX Color:", font=(FONT_FAMILY, 12), bg=PRIMARY_BG)
    color_input_label.pack(pady=(0, 6), padx=(90,0), anchor='w')

    # HEX color input and preview with border
    hex_border_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    hex_border_frame.pack(pady=(0, 14), padx=(90,0), anchor='w')
    border_canvas = tk.Canvas(hex_border_frame, width=112, height=36, highlightthickness=0, bg=PRIMARY_BG, bd=0)
    border_canvas.pack(side='left', padx=0, pady=0)

    app.creative_hex_entry = tk.Entry(hex_border_frame, textvariable=app.creative_hex_var, font=(FONT_FAMILY, 14), width=12, justify='center',
                                      relief='flat', bd=0, highlightthickness=0, bg=INPUT_BG, fg=INPUT_FG, exportselection=0,
                                      selectbackground=app.creative_hex_var.get() if len(app.creative_hex_var.get()) == 7 and app.creative_hex_var.get().startswith('#') else '#cccccc',
                                      selectforeground=INPUT_FG)
    app.creative_hex_entry.place(x=6, y=5, width=100, height=26)

    # Prevent auto-selection of text on tab open
    def prevent_auto_select(event):
        app.creative_hex_entry.selection_clear()
    app.creative_hex_entry.bind('<FocusIn>', prevent_auto_select, add='+')
    app.creative_hex_entry.after(100, lambda: app.creative_hex_entry.selection_clear())

    # Update selection color dynamically
    def update_select_bg(*_):
        hex_code = app.creative_hex_var.get()
        sel_bg = hex_code if len(hex_code) == 7 and hex_code.startswith('#') else '#cccccc'
        try:
            app.creative_hex_entry.config(selectbackground=sel_bg)
        except Exception:
            pass
    app.creative_hex_var.trace_add('write', lambda *_: update_select_bg())
    update_select_bg()

    # Update hex border color dynamically
    def update_hex_border(*_):
        border_canvas.delete('all')
        hex_code = app.creative_hex_var.get()
        border_color = hex_code if len(hex_code) == 7 and hex_code.startswith('#') else '#222'
        border_canvas.create_rectangle(2, 2, 110, 34, outline=border_color, width=2)
    app.creative_hex_var.trace_add('write', lambda *_: update_hex_border())
    update_hex_border()

    # Color Picker Row (icon and label)
    btn_row = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
    btn_row.pack(pady=(0, 22), padx=(90,0), anchor='w')

    # Color Picker button
    def open_picker_beside_icon(event=None):
        app.root.update_idletasks()
        btn_x = pick_btn.winfo_rootx()
        btn_y = pick_btn.winfo_rooty() + pick_btn.winfo_height()
        # Adjusted offsets to position picker next to the icon, relative to the main app window
        offset_x = -360
        offset_y = 320
        _show_color_picker(app, x=btn_x + offset_x, y=btn_y - offset_y, on_pick_callback=lambda: _generate_palettes(app, palette_sections))

    pick_btn = tk.Button(
        btn_row, text="🎨", command=open_picker_beside_icon,
        font=(FONT_FAMILY, 14), fg='black', bg=INPUT_BG,
        relief='flat', bd=0, cursor='hand2', width=3
    )
    pick_btn.pack(side='left', padx=(0, 1))
    color_picker_label = tk.Label(
        btn_row, text="Color Picker", font=(FONT_FAMILY, 12, 'bold'),
        bg=PRIMARY_BG, fg=INPUT_FG, padx=2
    )
    color_picker_label.pack(side='left', padx=(0, 4))

    # Palette Output Sections
    palette_sections = {}
    for pname in ["Analogous", "Monochromatic", "Shades", "Complementary"]:
        title_row = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
        title_row.pack(pady=(10, 0), padx=(90,0), anchor='w', fill='x')
        title_row.grid_columnconfigure(0, weight=0)
        title_row.grid_columnconfigure(1, weight=1)
        title_row.grid_columnconfigure(2, weight=0)

        section_label = tk.Label(title_row, text=pname, font=(FONT_FAMILY, 11, 'bold'), bg=PRIMARY_BG)
        section_label.grid(row=0, column=0, sticky='w')

        spacer = tk.Frame(title_row, width=40, bg=PRIMARY_BG)
        spacer.grid(row=0, column=1, sticky='ew')

        # Export as JPEG text link
        def export_handler(palette_name, event=None):
            hex_code = app.creative_hex_var.get().strip()
            if not hex_code.startswith('#') or len(hex_code) != 7:
                return
            palettes = _get_palette(hex_code)
            colors = palettes.get(palette_name)
            if colors:
                _export_palette_to_jpeg(app, colors, palette_name)
        export_frame = tk.Frame(title_row, bg=PRIMARY_BG)
        export_text = tk.Label(export_frame, text='Export as JPEG', font=(FONT_FAMILY, 9), bg=PRIMARY_BG, fg=PALETTE_INDIGO, cursor='hand2')
        export_text.pack(side='left', padx=(0, 0))
        export_frame.grid(row=0, column=2, sticky='e', pady=(2,0))
        export_frame.bind('<Button-1>', partial(export_handler, pname))
        export_text.bind('<Button-1>', partial(export_handler, pname))
        # Add hover effect for export text
        def on_enter_export(e):
            export_frame.config(bg=HOVER_ACCENT_BLUE)
            export_text.config(bg=HOVER_ACCENT_BLUE, fg=TEXT_LIGHT)
        def on_leave_export(e):
            export_frame.config(bg=PRIMARY_BG)
            export_text.config(bg=PRIMARY_BG, fg=PALETTE_INDIGO)
        export_frame.bind('<Enter>', on_enter_export)
        export_frame.bind('<Leave>', on_leave_export)
        export_text.bind('<Enter>', on_enter_export)
        export_text.bind('<Leave>', on_leave_export)


        section = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
        section.pack(fill='x', pady=(0, 16), padx=(90,0))
        palette_sections[pname] = section

    # Initial palette generation
    def _generate_palettes(app_instance, sections):
        hex_code = app_instance.creative_hex_var.get().strip()
        if not hex_code.startswith('#') or len(hex_code) != 7:
            # Optionally show an error or just return
            return
        palettes = _get_palette(hex_code)
        for name, section_frame in sections.items():
            for widget in section_frame.winfo_children():
                widget.destroy() # Clear previous swatches

            colors = palettes.get(name)
            if colors:
                for i, c in enumerate(colors):
                    # Color swatch
                    swatch = tk.Frame(section_frame, bg=c, width=64, height=64, bd=2, relief='ridge', cursor='hand2')
                    swatch.grid(row=0, column=i, padx=8, pady=(4,2))
                    swatch.bind('<Button-1>', lambda e, hexval=c: app_instance.creative_hex_var.set(hexval.upper())) # Set main hex input on click

                    # Hex label with copy effect
                    hex_label = tk.Label(section_frame, text=c.upper(), font=(FONT_FAMILY, 11), bg=PRIMARY_BG, fg=INPUT_FG, bd=0, padx=8, pady=2)
                    hex_label.grid(row=1, column=i, padx=8, pady=(0,6))

                    # Copy effect for hex label
                    def copy_hex_effect(event, hexval, label_widget):
                        helpers.copy_to_clipboard_helper(app_instance, hexval, f"{hexval} copied!")
                        orig_text = label_widget.cget('text')
                        orig_bg = label_widget.cget('bg')
                        orig_fg = label_widget.cget('fg')
                        label_widget.config(text='✔ Copied!', fg='#222', bg='#eaffc2')
                        label_widget.after(900, lambda: label_widget.config(text=orig_text, fg=orig_fg, bg=orig_bg))
                    hex_label.bind('<Button-1>', partial(copy_hex_effect, hexval=c.upper(), label_widget=hex_label))

                    # Hover effect for hex label
                    def on_hex_hover(event, label_widget):
                        label_widget.config(bg=ACCENT_BLUE, fg='#222', cursor='hand2')
                    def on_hex_leave(event, label_widget, orig_bg, orig_fg):
                        label_widget.config(bg=orig_bg, fg=orig_fg, cursor='arrow')
                    hex_label.bind('<Enter>', partial(on_hex_hover, label_widget=hex_label))
                    hex_label.bind('<Leave>', partial(on_hex_leave, label_widget=hex_label, orig_bg=PRIMARY_BG, orig_fg=INPUT_FG))

                # Make columns expand equally
                for i in range(len(colors)):
                    section_frame.grid_columnconfigure(i, weight=1)

    # Initial palette generation when the tab is first loaded
    app.creative_hex_var.trace_add('write', lambda *_: _generate_palettes(app, palette_sections))
    _generate_palettes(app, palette_sections)


    # --- Section Separator before Gradient Generator ---
    sep = tk.Frame(scrollable_frame, bg='#E0E0E0', height=2)
    sep.pack(fill='x', padx=10, pady=(10, 24))

    # --- Gradient Generator Section ---
    _build_gradient_generator_section(app, scrollable_frame)


def _get_palette(base_hex):
    """
    Generates various color palettes (Analogous, Monochromatic, Shades, Complementary)
    based on a given base HEX color.

    Args:
        base_hex (str): The base color in HEX format (e.g., "#RRGGBB").

    Returns:
        dict: A dictionary where keys are palette names and values are lists of HEX colors.
    """
    import colorsys
    import random

    base_rgb = helpers.hex_to_rgb(base_hex)
    r, g, b = [x/255.0 for x in base_rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b) # Hue, Lightness, Saturation
    palettes = {}

    # Analogous: Colors adjacent on the color wheel
    def analogous_func(i):
        nh = (h + (i-2) * (1/12)) % 1.0 # 30 deg steps on hue (1/12 of 360 deg)
        nr, ng, nb = colorsys.hls_to_rgb(nh, l, s)
        return helpers.rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
    palettes['Analogous'] = [analogous_func(i) for i in range(6)]

    # Monochromatic: Variations of lightness for the same hue and saturation
    def mono_func(i):
        nl = 0.12 + (i * (0.76/5)) # Lightness steps from 0.12 to 0.88
        nr, ng, nb = colorsys.hls_to_rgb(h, nl, s)
        return helpers.rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
    palettes['Monochromatic'] = [mono_func(i) for i in range(6)]

    # Shades: Variations of saturation for the same hue and lightness
    def shade_func(i):
        ns = i / 5.0 # Saturation steps from 0.0 (gray) to 1.0 (full color)
        nr, ng, nb = colorsys.hls_to_rgb(h, l, ns)
        return helpers.rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
    palettes['Shades'] = [shade_func(i) for i in range(6)]

    # Complementary: Base color and its complement, with variations
    def comp_base(i):
        # Vary lightness and saturation for base colors randomly
        nl = min(max(l + random.uniform(-0.18, 0.18), 0.12), 0.88)
        ns = min(max(s + random.uniform(-0.22, 0.22), 0.15), 1.0)
        nr, ng, nb = colorsys.hls_to_rgb(h, nl, ns)
        return helpers.rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))

    def comp_complement(i):
        nhh = (h + 0.5) % 1.0 # Complementary hue
        # Vary lightness and saturation for complementary colors randomly
        nl = min(max(l + random.uniform(-0.18, 0.18), 0.12), 0.88)
        ns = min(max(s + random.uniform(-0.22, 0.22), 0.15), 1.0)
        nr, ng, nb = colorsys.hls_to_rgb(nhh, nl, ns)
        return helpers.rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))

    random.seed() # Initialize random seed
    palettes['Complementary'] = [comp_base(i) for i in range(3)] + [comp_complement(i) for i in range(3)]
    return palettes


def _show_color_picker(app, x=None, y=None, on_pick_callback=None):
    """
    Opens a minimalist color picker Toplevel window.

    Args:
        app: The main application instance.
        x (int, optional): X coordinate for the picker window.
        y (int, optional): Y coordinate for the picker window.
        on_pick_callback (callable, optional): A callback function to run when a color is picked.
    """
    if Image is None or ImageTk is None:
        tk.messagebox.showerror("Missing Dependency", "Pillow library is required for the color picker. Please install it with: pip install Pillow")
        return

    picker = Toplevel(app.root)
    picker.title("Minimalist Color Picker")
    picker.configure(bg=PRIMARY_BG)
    picker.resizable(False, False)

    try:
        initial_hex = app.creative_hex_var.get()
        # Convert hex to RGB, handle invalid hex by defaulting to a gray color
        rgb = [int(initial_hex[i:i+2], 16) for i in (1, 3, 5)] if initial_hex.startswith('#') and len(initial_hex) == 7 else [170, 187, 204]
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255) # Convert RGB to HSV
        hue_var = tk.DoubleVar(value=h*360) # Hue as 0-359 degrees
        hex_var = tk.StringVar(value=initial_hex.upper()) # Current hex value

        area_size = 180 # Size of the main color selection area (saturation/value)
        left_margin = 20 # Left padding for elements
        gradient_img = None
        gradient_tk = None

        color_area = tk.Label(picker, bd=2, relief='ridge', bg=PRIMARY_BG)
        color_area.place(x=left_margin, y=40, width=area_size, height=area_size)

        def make_gradient(hue_val):
            """Creates the HSV gradient image for the color selection area."""
            img = Image.new('RGB', (area_size, area_size))
            pixels = img.load() # Optimize pixel access
            for y_coord in range(area_size):
                for x_coord in range(area_size):
                    saturation = x_coord / (area_size-1) # X-axis maps to saturation
                    value = 1 - (y_coord / (area_size-1)) # Y-axis maps to value (inverted)
                    r_val, g_val, b_val = colorsys.hsv_to_rgb(hue_val, saturation, value)
                    pixels[x_coord, y_coord] = (int(r_val*255), int(g_val*255), int(b_val*255))
            return img

        def update_gradient(*_):
            """Updates the gradient image when the hue slider changes."""
            nonlocal gradient_img, gradient_tk
            hue = hue_var.get() / 360 # Convert hue back to 0-1 range
            gradient_img = make_gradient(hue)
            gradient_tk = ImageTk.PhotoImage(gradient_img)
            color_area.config(image=gradient_tk)

        update_gradient() # Initial draw

        def area_pick(event):
            """Handles mouse clicks/drags on the color selection area."""
            x_click, y_click = event.x, event.y
            if 0 <= x_click < area_size and 0 <= y_click < area_size:
                saturation = x_click / (area_size-1)
                value = 1 - (y_click / (area_size-1))
                hue = hue_var.get() / 360
                r_val, g_val, b_val = colorsys.hsv_to_rgb(hue, saturation, value)
                hex_code = f"#{int(r_val*255):02X}{int(g_val*255):02X}{int(b_val*255):02X}"
                hex_var.set(hex_code.upper()) # Update internal hex var
                preview.config(bg=hex_code) # Update color preview swatch
                app.creative_hex_var.set(hex_code.upper()) # Update main app's hex var

        color_area.bind('<Button-1>', area_pick)
        color_area.bind('<B1-Motion>', area_pick)

        hue_slider_y = 210 # Position for hue slider
        hue_slider = tk.Scale(picker, from_=0, to=359, orient='horizontal', variable=hue_var, showvalue=True, length=area_size+10,
                            bg=PRIMARY_BG, fg="#888", highlightthickness=0, troughcolor=SECONDARY_BG, bd=0, resolution=1)
        hue_slider.place(x=left_margin, y=hue_slider_y+10, width=area_size)
        hue_var.trace_add('write', lambda *_: update_gradient()) # Bind hue slider to update gradient

        hex_y = hue_slider_y + 60 # Position for hex input and preview
        preview_size = 28
        preview = tk.Frame(picker, bg=hex_var.get(), width=preview_size, height=preview_size, bd=2, relief='ridge')
        preview.place(x=left_margin, y=hex_y)

        hex_label = tk.Label(picker, text="HEX", font=(FONT_FAMILY, 9, 'bold'), bg=PRIMARY_BG, fg="#888")
        hex_label.place(x=left_margin+50, y=hex_y+4)

        hex_entry = tk.Entry(picker, textvariable=hex_var, font=(FONT_FAMILY, 11), width=10, justify='center', bd=1, relief='solid', bg=INPUT_BG, fg=INPUT_FG)
        hex_entry.place(x=left_margin+85, y=hex_y, width=80, height=28)

        def update_from_hex(*_):
            """Updates the picker's state when hex input is manually changed."""
            val = hex_var.get().strip()
            if val.startswith('#') and len(val) == 7:
                try:
                    r_val = int(val[1:3], 16)
                    g_val = int(val[3:5], 16)
                    b_val = int(val[5:7], 16)
                    preview.config(bg=val) # Update preview swatch
                    app.creative_hex_var.set(val.upper()) # Update main app's hex var
                    # Re-calculate palettes in main app if callback exists
                    if on_pick_callback:
                        on_pick_callback()
                except ValueError:
                    pass # Ignore invalid hex codes without erroring out

        hex_var.trace_add('write', update_from_hex)

        # Set window size and position
        picker.update_idletasks()
        window_width = area_size + 2*left_margin
        window_height = hex_y + 28 + 32 # Height for hex/preview + padding
        picker.geometry(f"{window_width}x{window_height}")
        picker.minsize(window_width, window_height)
        picker.maxsize(window_width, window_height)

        preview.config(bg=hex_var.get()) # Ensure initial preview color is correct

        # Position picker if coordinates are provided
        if x is not None and y is not None:
            picker.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Close on focus out or Escape key
        picker.bind('<FocusOut>', lambda e: picker.destroy())
        picker.bind('<Escape>', lambda e: picker.destroy())

    except Exception as e:
        import traceback
        print("Error building color picker UI:", e)
        traceback.print_exc()
        error_label = tk.Label(picker, text="Error loading color picker", fg="red", bg=PRIMARY_BG)
        error_label.pack(expand=True, fill="both")
    finally:
        # Always make sure the window is displayed and focused
        picker.update_idletasks()
        picker.deiconify()
        picker.lift()
        picker.focus_force()

def _export_palette_to_jpeg(app, colors, palette_name):
    """
    Exports a color palette as a JPEG image with color swatches and HEX codes.
    """
    if Image is None or ImageDraw is None or ImageFont is None:
        tk.messagebox.showerror("Missing Dependency", "Pillow (PIL) is required to export JPEGs. Please install it with: pip install Pillow")
        return

    # --- MANUAL SETTINGS FOR EXPORT ---
    swatch_width = 250
    swatch_height = 350
    hex_h = 40 # Height of white area for hex text
    hex_font_size = 80 # Adjust for text size
    hex_font_name = "Montserrat-Bold.ttf" # Or change to any .ttf you want

    n = len(colors)
    img_width = swatch_width * n
    img_height = swatch_height + hex_h
    img = Image.new('RGB', (img_width, img_height), color='#fff')
    draw = ImageDraw.Draw(img)

    try:
        # Try to load custom font, fallback to default if not found
        font = ImageFont.truetype(hex_font_name, hex_font_size)
    except IOError:
        print(f"Warning: Font '{hex_font_name}' not found. Using default font.")
        font = ImageFont.load_default()

    for i, color in enumerate(colors):
        x0 = i * swatch_width
        x1 = x0 + swatch_width
        draw.rectangle([x0, 0, x1, swatch_height], fill=color) # Draw color swatch

        hex_text = color.upper()
        # Center text in the white area
        try:
            # textbbox is more accurate for font metrics
            bbox = draw.textbbox((0, 0), hex_text, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
        except Exception: # Fallback for older Pillow versions or issues
            text_w, text_h = draw.textsize(hex_text, font=font)

        text_x = x0 + (swatch_width - text_w) // 2
        text_y = swatch_height + (hex_h - text_h) // 2
        draw.text((text_x, text_y), hex_text, fill='#000', font=font)

    # File dialog for saving
    filetypes = [("JPEG Image", "*.jpeg"), ("JPG Image", "*.jpg")]
    base_name = f"{palette_name}_palette"
    ext = ".jpeg"

    # Determine initial directory for saving
    # Use the last used directory, or fallback to OS-specific Downloads folder
    if sys.platform.startswith('win'):
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    elif sys.platform.startswith('darwin'):
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
    else:
        downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads') # Linux/other

    last_dir = getattr(app, '_last_palette_export_dir', downloads_dir)

    # Generate a candidate filename to avoid overwriting existing files
    try:
        files_in_dir = os.listdir(last_dir)
    except FileNotFoundError:
        files_in_dir = [] # Directory might not exist yet

    pattern = re.compile(rf"{re.escape(base_name)}(?: (\d+))?{re.escape(ext)}$")
    max_num = 0
    for f_name in files_in_dir:
        m = pattern.match(f_name)
        if m:
            num = m.group(1)
            if num:
                max_num = max(max_num, int(num))
            else:
                max_num = max(max_num, 1) # If file exists without number, treat as #1

    next_num = max_num + 1 if max_num else 1
    candidate_name = f"{base_name} {next_num}{ext}"

    filename = fd.asksaveasfilename(defaultextension=ext, filetypes=filetypes,
                                    initialfile=candidate_name, initialdir=last_dir,
                                    title="Export Palette as JPEG")

    if filename:
        app._last_palette_export_dir = os.path.dirname(filename) # Save the directory
        try:
            img.save(filename, format='JPEG', quality=92) # Save image with quality
            app.update_status(f"Palette '{palette_name}' exported successfully!", SUCCESS_GREEN)
        except Exception as e:
            app.update_status(f"Failed to export palette: {str(e)}", WARNING_RED)

def _build_gradient_generator_section(app, parent):
    """
    Builds the UI for the Gradient Generator section.

    Args:
        app: The main application instance.
        parent: The tkinter frame to place these widgets in.
    """
    section = tk.Frame(parent, bg=PRIMARY_BG)
    section.pack(fill='x', pady=(18, 18), padx=(0,0), anchor='center')

    # Title for Gradient Generator
    title = tk.Label(section, text="Gradient Generator", font=(FONT_FAMILY, 11), bg=PRIMARY_BG, fg=INPUT_FG)
    title.pack(anchor='w', pady=(28, 14), padx=(10,0))

    # Controls for gradient type, number of colors, and color style
    controls = tk.Frame(section, bg=PRIMARY_BG)
    controls.pack(anchor='center', pady=(0, 10))

    tk.Label(controls, text="Gradient Type:", font=(FONT_FAMILY, 11), bg=PRIMARY_BG).pack(side='left', padx=(0,2))
    type_combo = ttk.Combobox(controls, textvariable=app.gradient_type_var, state='readonly', font=FONT_INPUT, width=8, values=['Linear', 'Radial'])
    type_combo.pack(side='left', padx=(0, 12))
    # Bind type change to redraw preview
    app.gradient_type_var.trace_add('write', lambda *_: _draw_gradient_preview(app))

    tk.Label(controls, text="Number of Colors:", font=(FONT_FAMILY, 11), bg=PRIMARY_BG).pack(side='left', padx=(0,2))
    num_combo = ttk.Combobox(controls, textvariable=app.gradient_num_colors_var, state='readonly', font=FONT_INPUT, width=3, values=list(range(2,9)))
    num_combo.pack(side='left', padx=(0, 12))
    # Bind number of colors change to re-generate gradient and redraw
    app.gradient_num_colors_var.trace_add('write', lambda *_: _generate_gradient_random(app))

    tk.Label(controls, text="Color Style:", font=(FONT_FAMILY, 11), bg=PRIMARY_BG).pack(side='left', padx=(0,2))
    style_combo = ttk.Combobox(controls, textvariable=app.gradient_style_var, state='readonly', font=FONT_INPUT, width=8, values=list(GRADIENT_STYLES.keys()))
    style_combo.pack(side='left', padx=(0, 0))
    # Bind style change to re-generate gradient and redraw
    app.gradient_style_var.trace_add('write', lambda *_: _generate_gradient_random(app))


    # Generate & Preset Buttons Row
    btn_row = tk.Frame(section, bg=PRIMARY_BG)
    btn_row.pack(anchor='center', pady=(18, 10))

    gen_btn = tk.Button(
        btn_row, text="Generate Gradient", command=lambda: _generate_gradient_random(app),
        font=(FONT_FAMILY, 11, 'bold'),
        bg=ACCENT_BLUE, fg=TEXT_LIGHT, relief='flat', padx=16, pady=6, cursor='hand2', bd=0,
        activebackground=HOVER_ACCENT_BLUE, activeforeground=TEXT_LIGHT
    )
    gen_btn.pack(side='left', padx=(0, 10))
    app._button_hover_colors[gen_btn] = {'original': ACCENT_BLUE, 'hover': HOVER_ACCENT_BLUE}

    # Frame to hold preset button and rotation control
    preset_rotate_frame = tk.Frame(btn_row, bg=PRIMARY_BG)
    preset_rotate_frame.pack(side='left', padx=(0, 0))

    preset_btn = tk.Button(
        preset_rotate_frame, text="Load Preset", command=lambda: _show_gradient_presets(app),
        font=(FONT_FAMILY, 11, 'bold'),
        bg=SECONDARY_BG, fg=INPUT_FG, relief='flat', padx=16, pady=6, cursor='hand2', bd=0,
        activebackground=HOVER_ACCENT_BLUE, activeforeground=INPUT_FG
    )
    preset_btn.pack(side='left', padx=(0, 8))
    app._button_hover_colors[preset_btn] = {'original': SECONDARY_BG, 'hover': HOVER_ACCENT_BLUE}

    # Circular Rotation Control (for Linear gradients)
    class CircularDial(tk.Canvas):
        """A custom Tkinter Canvas widget to act as a circular dial for angle input."""
        def __init__(self, master, variable, min_angle=0, max_angle=359, size=38, **kwargs):
            # Use parent's PRIMARY_BG if available, else fallback to white
            bg = getattr(master.master, 'PRIMARY_BG', '#ffffff') if hasattr(master, 'master') and hasattr(master.master, 'PRIMARY_BG') else '#ffffff'
            super().__init__(master, width=size, height=size, bg=bg, highlightthickness=0, bd=0, **kwargs)
            self.size = size
            self.radius = size//2 - 4
            self.center = (size//2, size//2)
            self.variable = variable
            self.min_angle = min_angle
            self.max_angle = max_angle
            self.indicator = None
            self.bg_color = bg
            self.bind('<Button-1>', self._on_click)
            self.bind('<B1-Motion>', self._on_drag)
            self.bind('<Enter>', lambda e: self.config(cursor='hand2'))
            self.bind('<Leave>', lambda e: self.config(cursor=''))
            self._draw_dial()

        def _draw_dial(self):
            self.delete('all')
            x, y = self.center
            # Outer circle
            self.create_oval(x-self.radius, y-self.radius, x+self.radius, y+self.radius, outline='#b5baff', width=2, fill=self.bg_color)
            # Dots for every 45°
            for deg in range(0, 360, 45):
                rad = deg * math.pi / 180
                dx = self.radius * 0.82 * math.cos(rad)
                dy = self.radius * 0.82 * math.sin(rad)
                self.create_oval(x+dx-2, y+dy-2, x+dx+2, y+dy+2, fill='#b5baff', outline='')
            # Indicator line
            angle = self.variable.get() % 360
            rad = angle * math.pi / 180
            dx = self.radius * 0.7 * math.cos(rad)
            dy = self.radius * 0.7 * math.sin(rad)
            self.indicator = self.create_line(x, y, x+dx, y+dy, fill='#5F27CD', width=3, capstyle='round')
            # Center dot
            self.create_oval(x-3, y-3, x+3, y+3, fill='#5F27CD', outline='')

        def _set_angle_from_event(self, event):
            x_mouse, y_mouse = event.x - self.center[0], event.y - self.center[1]
            angle = (math.degrees(math.atan2(y_mouse, x_mouse)) + 360) % 360
            self.variable.set(int(angle))
            self._draw_dial()
            # If the variable has a callback attribute, call it (for live updates)
            if hasattr(self.variable, 'callback'):
                self.variable.callback(angle)

        def _on_click(self, event):
            self._set_angle_from_event(event)

        def _on_drag(self, event):
            self._set_angle_from_event(event)

    dial = CircularDial(preset_rotate_frame, app.gradient_rotation_var)
    dial.pack(side='left', padx=(0, 0))
    _create_tooltip(dial, "Rotate linear gradient direction (0° = left→right)")

    # Numeric entry for rotation angle
    rot_entry = tk.Entry(preset_rotate_frame, textvariable=app.gradient_rotation_var, width=3, font=(FONT_FAMILY, 10), justify='center', bd=0, relief='flat', bg=INPUT_BG, fg=INPUT_FG)
    rot_entry.pack(side='left', padx=(4, 0))
    _create_tooltip(rot_entry, "Set gradient angle (0-359°)")
    # Update on entry change
    app.gradient_rotation_var.trace_add('write', lambda *_: (dial._draw_dial(), _draw_gradient_preview(app)))

    # Instructions label
    instructions = tk.Label(section, text="💡 Drag color stops • Double-click canvas to add • Right-click stop to delete • Double-click stop to edit color",
                           font=(FONT_FAMILY, 9), bg=PRIMARY_BG, fg=TEXT_MUTED)
    instructions.pack(anchor='center', pady=(0, 8))

    # Responsive Canvas for gradient preview
    canvas_frame = tk.Frame(section, bg=PRIMARY_BG)
    canvas_frame.pack(fill='x', expand=True, pady=(0, 18), padx=(10,0), anchor='w')
    canvas_frame.grid_columnconfigure(0, weight=1)

    app._gradient_canvas_min_w = 350
    app._gradient_canvas_min_h = 180
    app._gradient_canvas_max_w = 700
    app._gradient_canvas_max_h = 320

    def get_canvas_size():
        """Calculates optimal canvas size based on parent width."""
        parent_w = canvas_frame.winfo_width() if canvas_frame.winfo_width() > 0 else 800
        w = max(app._gradient_canvas_min_w, min(app._gradient_canvas_max_w, parent_w))
        aspect = app._gradient_canvas_min_h / app._gradient_canvas_min_w
        h = int(w * aspect)
        h = max(app._gradient_canvas_min_h, min(app._gradient_canvas_max_h, h))
        return w, h

    w, h = get_canvas_size()
    app.gradient_preview_canvas = tk.Canvas(canvas_frame, width=w, height=h, bg=INPUT_BG, highlightthickness=0, bd=0)
    app.gradient_preview_canvas.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
    # Add a subtle border frame behind the canvas for visual appeal
    border_frame = tk.Frame(canvas_frame, bg=SECONDARY_BG, highlightthickness=0, bd=0)
    border_frame.grid(row=0, column=0, sticky='nsew')
    border_frame.lower(app.gradient_preview_canvas) # Place border behind canvas

    canvas_frame.grid_rowconfigure(0, weight=1)
    canvas_frame.grid_columnconfigure(0, weight=1)

    # Debounced resize handler for the canvas
    def on_resize(event=None):
        if hasattr(app, '_resize_timer'):
            app.root.after_cancel(app._resize_timer)

        def do_resize():
            new_w, new_h = get_canvas_size()
            current_w = int(app.gradient_preview_canvas['width'])
            current_h = int(app.gradient_preview_canvas['height'])
            # Only resize if there's a significant change
            if abs(new_w - current_w) > 2 or abs(new_h - current_h) > 2:
                app.gradient_preview_canvas.config(width=new_w, height=new_h)
                _draw_gradient_preview(app) # Redraw gradient after resize
            delattr(app, '_resize_timer')

        app._resize_timer = app.root.after(50, do_resize) # 50ms debounce
    canvas_frame.bind('<Configure>', on_resize)

    # Event bindings for gradient stops and canvas interactions
    app.gradient_preview_canvas.tag_bind('stop', '<ButtonPress-1>', lambda e: _on_gradient_stop_press(app, e))
    app.gradient_preview_canvas.tag_bind('stop', '<B1-Motion>', lambda e: _on_gradient_stop_drag(app, e))
    app.gradient_preview_canvas.tag_bind('stop', '<ButtonRelease-1>', lambda e: _on_gradient_stop_release(app, e))
    app.gradient_preview_canvas.tag_bind('stop', '<Double-Button-1>', lambda e: _on_gradient_stop_double_click(app, e))
    app.gradient_preview_canvas.tag_bind('stop', '<Button-3>', lambda e: _on_gradient_stop_right_click(app, e)) # Right-click to delete
    app.gradient_preview_canvas.bind('<B1-Motion>', lambda e: _on_gradient_stop_drag(app, e)) # Global drag on canvas for safety
    app.gradient_preview_canvas.bind('<ButtonRelease-1>', lambda e: _on_gradient_stop_release(app, e)) # Global release
    app.gradient_preview_canvas.bind('<Double-Button-1>', lambda e: _on_gradient_canvas_double_click(app, e)) # Double-click to add stop

    # HEX Codes Row (will be populated dynamically)
    app.gradient_hex_frame = tk.Frame(section, bg=PRIMARY_BG)
    app.gradient_hex_frame.pack(fill='x', pady=(2, 8), padx=(10,0), anchor='w')

    # Copy/Export Buttons
    btns_frame = tk.Frame(section, bg=PRIMARY_BG)
    btns_frame.pack(anchor='w', pady=(2, 0))

    copy_btn = tk.Button(btns_frame, text="Copy All HEX", command=lambda: _copy_all_gradient_hex(app), font=(FONT_FAMILY, 10),
                        bg=SECONDARY_BG, fg=INPUT_FG, relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                        activebackground=HOVER_ACCENT_BLUE, activeforeground=INPUT_FG)
    copy_btn.pack(side='left', padx=(0, 10))
    app._button_hover_colors[copy_btn] = {'original': SECONDARY_BG, 'hover': HOVER_ACCENT_BLUE}

    # Export options with dropdown
    export_var = tk.StringVar(value="PNG")
    export_menu = ttk.Combobox(btns_frame, textvariable=export_var, state='readonly',
                              font=(FONT_FAMILY, 10), width=8,
                              values=['PNG', 'JPEG', 'SVG', 'CSS Code'])
    export_menu.pack(side='left', padx=(0, 5))

    export_btn = tk.Button(btns_frame, text="Export", command=lambda: _export_gradient(app, export_var.get()),
                        font=(FONT_FAMILY, 10),
                        bg=SECONDARY_BG, fg=INPUT_FG, relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                        activebackground=HOVER_ACCENT_BLUE, activeforeground=INPUT_FG)
    export_btn.pack(side='left', padx=(0, 10))
    app._button_hover_colors[export_btn] = {'original': SECONDARY_BG, 'hover': HOVER_ACCENT_BLUE}

    # Export Size settings
    size_frame = tk.Frame(btns_frame, bg=PRIMARY_BG)
    size_frame.pack(side='left', padx=(0, 0))
    tk.Label(size_frame, text="Export Size:", font=(FONT_FAMILY, 9), bg=PRIMARY_BG).pack(side='left')
    width_entry = tk.Entry(size_frame, textvariable=app.export_width_var, font=(FONT_FAMILY, 9), width=4)
    width_entry.pack(side='left', padx=(2, 0))
    tk.Label(size_frame, text="×", font=(FONT_FAMILY, 9), bg=PRIMARY_BG).pack(side='left')
    height_entry = tk.Entry(size_frame, textvariable=app.export_height_var, font=(FONT_FAMILY, 9), width=4)
    height_entry.pack(side='left', padx=(0, 2))

    _generate_gradient_random(app) # Generate an initial random gradient on load


def _generate_gradient_random(app):
    """
    Generates a random gradient based on the selected style and number of colors.
    Attempts to prevent immediate repetition of the previous gradient.
    """
    import random
    import colorsys
    import time

    style = app.gradient_style_var.get()
    n = app.gradient_num_colors_var.get()
    palette = GRADIENT_STYLES.get(style, list(GRADIENT_STYLES.values())[0])

    # Enhanced random seeding for better variance
    random.seed(time.time_ns() + random.randint(0, 10_000_000))

    # Prevent immediate repetition
    if not hasattr(app, '_last_gradient_signature'):
        app._last_gradient_signature = None

    max_attempts = 15 # Max attempts to find a non-repetitive gradient
    for attempt in range(max_attempts):
        colors = []
        if style in ['Analogous', 'Complementary', 'Triadic', 'Tetradic']:
            # Harmony-based generation
            base_hex = random.choice(palette)
            h, s, v = colorsys.rgb_to_hsv(*[x/255.0 for x in helpers.hex_to_rgb(base_hex)])

            if style == 'Analogous':
                angle_range = random.uniform(30, 90) # Variable angle range for analogy
                start_offset = random.uniform(-angle_range/2, angle_range/2)
                for i in range(n):
                    angle = start_offset + (i * angle_range / max(n-1, 1))
                    new_h = (h + angle/360) % 1.0
                    new_s = min(max(s + random.uniform(-0.15, 0.15), 0.3), 1.0)
                    new_v = min(max(v + random.uniform(-0.2, 0.2), 0.4), 1.0)
                    colors.append(helpers.hsv_to_hex(new_h, new_s, new_v))

            elif style == 'Complementary':
                comp_h = (h + 0.5) % 1.0
                for i in range(n):
                    current_h = h if i % 2 == 0 else comp_h
                    new_h = (current_h + random.uniform(-15, 15)/360) % 1.0
                    new_s = min(max(s + random.uniform(-0.2, 0.2), 0.4), 1.0)
                    new_v = min(max(v + random.uniform(-0.25, 0.25), 0.3), 1.0)
                    colors.append(helpers.hsv_to_hex(new_h, new_s, new_v))

            elif style == 'Triadic':
                triad_hues = [(h + i * 120/360) % 1.0 for i in range(3)]
                for i in range(n):
                    base_h = triad_hues[i % 3]
                    new_h = (base_h + random.uniform(-10, 10)/360) % 1.0
                    new_s = min(max(s + random.uniform(-0.18, 0.18), 0.35), 1.0)
                    new_v = min(max(v + random.uniform(-0.22, 0.22), 0.35), 1.0)
                    colors.append(helpers.hsv_to_hex(new_h, new_s, new_v))

            elif style == 'Tetradic':
                tetrad_hues = [(h + i * 90/360) % 1.0 for i in range(4)]
                for i in range(n):
                    base_h = tetrad_hues[i % 4]
                    new_h = (base_h + random.uniform(-8, 8)/360) % 1.0
                    new_s = min(max(s + random.uniform(-0.15, 0.15), 0.4), 1.0)
                    new_v = min(max(v + random.uniform(-0.2, 0.2), 0.4), 1.0)
                    colors.append(helpers.hsv_to_hex(new_h, new_s, new_v))
        else:
            # Theme-based generation (e.g., Warm, Cool, Vibrant)
            if len(palette) >= n:
                if n == 2: # For 2 colors, pick distinct ones
                    colors = random.sample(palette, 2)
                elif n <= len(palette) // 2: # For small n, ensure spacing
                    step = len(palette) // n
                    start = random.randint(0, step-1)
                    colors = [palette[(start + i*step) % len(palette)] for i in range(n)]
                else: # General random selection
                    colors = random.sample(palette, n)
            else:
                # Interpolate if more colors are needed than in the palette
                for i in range(n):
                    base_color = palette[i % len(palette)]
                    h_base, s_base, v_base = colorsys.rgb_to_hsv(*[x/255.0 for x in helpers.hex_to_rgb(base_color)])

                    # Add controlled variation based on style
                    if style == 'Vibrant':
                        new_h = (h_base + random.uniform(-30, 30)/360) % 1.0
                        new_s = min(max(s_base + random.uniform(-0.1, 0.1), 0.7), 1.0)
                        new_v = min(max(v_base + random.uniform(-0.15, 0.15), 0.6), 1.0)
                    elif style == 'Pastel':
                        new_h = (h_base + random.uniform(-20, 20)/360) % 1.0
                        new_s = min(max(s_base + random.uniform(-0.15, 0.05), 0.2), 0.6)
                        new_v = min(max(v_base + random.uniform(-0.05, 0.1), 0.8), 1.0)
                    elif style == 'Muted':
                        new_h = (h_base + random.uniform(-25, 25)/360) % 1.0
                        new_s = min(max(s_base + random.uniform(-0.1, 0.1), 0.1), 0.5)
                        new_v = min(max(v_base + random.uniform(-0.1, 0.1), 0.4), 0.8)
                    else:
                        new_h = (h_base + random.uniform(-20, 20)/360) % 1.0
                        new_s = min(max(s_base + random.uniform(-0.12, 0.12), 0.3), 1.0)
                        new_v = min(max(v_base + random.uniform(-0.15, 0.15), 0.4), 1.0)

                    colors.append(helpers.hsv_to_hex(new_h, new_s, new_v))

            if random.random() < 0.3: # Occasionally shuffle for more variety
                random.shuffle(colors)

        signature = tuple(colors)
        if signature != app._last_gradient_signature:
            break # Found a new unique gradient

    app._last_gradient_signature = tuple(colors)
    app._gradient_colors = colors
    # Initialize positions evenly for new colors
    app._gradient_positions = [i/(n-1) if n > 1 else 0.5 for i in range(n)]
    _draw_gradient_preview(app)
    _draw_gradient_hexes(app)

def _draw_gradient_preview(app):
    """
    Draws the gradient on the preview canvas based on current colors, type, and rotation.
    """
    c = app.gradient_preview_canvas
    c.delete('all')
    w = int(c['width'])
    h = int(c['height'])

    if app.gradient_type_var.get() == 'Radial':
        # Radial gradient using concentric rectangles for performance
        cx, cy = w / 2, h / 2
        max_radius = min(w, h) // 2
        steps = 50 # Number of concentric steps

        for i in range(steps, 0, -1): # Draw from outside in
            frac = i / steps
            color = _interpolate_gradient(app, frac)
            radius = (frac * max_radius * 1.5) # Slightly larger to cover edges
            x1, y1 = max(0, cx - radius), max(0, cy - radius)
            x2, y2 = min(w, cx + radius), min(h, cy + radius)
            c.create_rectangle(x1, y1, x2, y2, fill=color, outline=color)
    else: # Linear gradient
        angle = app.gradient_rotation_var.get()
        theta = math.radians(angle)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        strips = min(h, 60) # Number of horizontal strips to draw for linear gradient
        strip_height = h / strips

        for i in range(strips):
            y = i * strip_height
            row_colors = []

            # Sample colors across the width for this row
            for x_coord in range(0, w, max(1, w//40)): # Sample every ~40 pixels horizontally
                # Normalize coordinates to [-0.5, 0.5] for rotation math
                nx = (x_coord / (w-1)) - 0.5 if w > 1 else 0
                ny = (y / (h-1)) - 0.5 if h > 1 else 0

                # Apply rotation transformation and normalize to 0-1 range
                frac = nx * cos_theta + ny * sin_theta + 0.5
                frac = min(max(frac, 0), 1) # Clamp fraction between 0 and 1

                color = _interpolate_gradient(app, frac)
                row_colors.append((x_coord, color))

            # Draw rectangles for this row
            for j in range(len(row_colors)):
                x_start = row_colors[j][0]
                color = row_colors[j][1]

                if j < len(row_colors) - 1:
                    x_end = row_colors[j + 1][0]
                else:
                    x_end = w # Last rectangle extends to canvas edge

                y1_coord = int(y)
                y2_coord = int(y + strip_height + 1) # Slight overlap to prevent gaps
                c.create_rectangle(x_start, y1_coord, x_end, y2_coord, fill=color, outline=color)

    # Draw draggable stops on top
    stop_radius = 7
    for idx, pos in enumerate(app._gradient_positions):
        x_stop = int(round(pos * (w - 1)))
        y_stop = h // 2 # Stops are drawn in the middle vertically
        # Draw the oval stop, filled with its color, and tag it for event handling
        c.create_oval(x_stop - stop_radius, y_stop - stop_radius, x_stop + stop_radius, y_stop + stop_radius,
                      fill=app._gradient_colors[idx], outline='#333', width=2, tags=(f'stop_{idx}', 'stop'))


def _interpolate_gradient(app, frac):
    """
    Interpolates a color at a given fraction (0.0 to 1.0) along the gradient.

    Args:
        app: The main application instance.
        frac (float): The fraction (position) along the gradient.

    Returns:
        str: The interpolated HEX color code.
    """
    stops = app._gradient_positions
    colors = app._gradient_colors

    # Handle edge cases where fraction is outside defined stops
    if frac <= stops[0]:
        return colors[0]
    if frac >= stops[-1]:
        return colors[-1]

    # Find the two stops that 'frac' is between
    for i in range(1, len(stops)):
        if frac < stops[i]:
            left_stop_idx, right_stop_idx = i-1, i
            break
    else: # Should not be reached if frac is within bounds and stops exist
        return colors[-1]

    # Calculate interpolation factor 'f' between the two bounding stops
    f = (frac - stops[left_stop_idx]) / (stops[right_stop_idx] - stops[left_stop_idx])

    # Get RGB components of the two bounding colors
    c1_rgb = helpers.hex_to_rgb(colors[left_stop_idx])
    c2_rgb = helpers.hex_to_rgb(colors[right_stop_idx])

    # Interpolate each RGB component
    r = int(c1_rgb[0] + (c2_rgb[0] - c1_rgb[0]) * f)
    g = int(c1_rgb[1] + (c2_rgb[1] - c1_rgb[1]) * f)
    b = int(c1_rgb[2] + (c2_rgb[2] - c1_rgb[2]) * f)

    return helpers.rgb_to_hex((r, g, b))

def _draw_gradient_hexes(app):
    """
    Draws the HEX code labels for each gradient stop, with dynamic sizing and effects.
    """
    frame = app.gradient_hex_frame

    # Store frame dimensions to prevent layout changes during redraw
    # This helps in maintaining a stable UI for HEX code row
    if hasattr(app, '_gradient_hex_frame_configured'):
        frame_width = frame.winfo_width()
        frame_height = frame.winfo_height()
    else:
        frame_width = frame_height = None
        app._gradient_hex_frame_configured = True # Mark as configured after first setup

    # Destroy all existing widgets in the frame before redrawing
    for w in frame.winfo_children():
        w.destroy()
    app._gradient_hex_labels = [] # Reset list for hover effects

    num_colors = len(app._gradient_colors)
    canvas_width = int(app.gradient_preview_canvas['width']) if hasattr(app, 'gradient_preview_canvas') else 600

    # Dynamic sizing logic based on number of colors
    if num_colors <= 3:
        canvas_w, canvas_h = 112, 36
        entry_w, entry_h = 74, 26
        entry_x, entry_y = 28, 5
        preview_size = 18
        preview_x, preview_y = 6, 9
        font_size = 11
        spacing = 8
    elif num_colors <= 5:
        canvas_w, canvas_h = 100, 32
        entry_w, entry_h = 68, 22
        entry_x, entry_y = 24, 5
        preview_size = 16
        preview_x, preview_y = 5, 8
        font_size = 10
        spacing = 6
    elif num_colors <= 7:
        canvas_w, canvas_h = 88, 30
        entry_w, entry_h = 58, 20
        entry_x, entry_y = 22, 5
        preview_size = 14
        preview_x, preview_y = 5, 8
        font_size = 9
        spacing = 4
    else: # For 8 colors
        canvas_w, canvas_h = 76, 28
        entry_w, entry_h = 50, 18
        entry_x, entry_y = 20, 5
        preview_size = 12
        preview_x, preview_y = 4, 8
        font_size = 8
        spacing = 2

    # Adjust sizes further if total width exceeds canvas width
    total_width = num_colors * canvas_w + (num_colors - 1) * spacing
    if total_width > canvas_width and num_colors > 0:
        scale_factor = canvas_width / total_width
        canvas_w = int(canvas_w * scale_factor)
        entry_w = int(entry_w * scale_factor)
        preview_size = max(10, int(preview_size * scale_factor))
        spacing = max(1, int(spacing * scale_factor))
        font_size = max(7, int(font_size * scale_factor))


    for idx, color in enumerate(app._gradient_colors):
        # Styled border frame for each hex code
        hex_border_frame = tk.Frame(frame, bg=PRIMARY_BG)
        hex_border_frame.pack(side='left', padx=(0, spacing))

        # Canvas for colored border around the entry
        border_canvas = tk.Canvas(hex_border_frame, width=canvas_w, height=canvas_h, highlightthickness=0, bg=PRIMARY_BG, bd=0)
        border_canvas.pack(side='left', padx=0, pady=0)

        # Hex code entry widget
        hex_var = tk.StringVar(value=color.upper())
        hex_entry = tk.Entry(hex_border_frame, textvariable=hex_var, font=(FONT_FAMILY, font_size), width=12, justify='center',
                             relief='flat', bd=0, highlightthickness=0, bg=INPUT_BG, fg=INPUT_FG, exportselection=0,
                             selectbackground=color if helpers.is_valid_hex(color) else '#cccccc',
                             selectforeground=INPUT_FG, cursor='hand2')
        hex_entry.place(x=entry_x, y=entry_y, width=entry_w, height=entry_h)

        # Draw border rectangle
        border_color = color if helpers.is_valid_hex(color) else '#222'
        border_rect = border_canvas.create_rectangle(2, 2, canvas_w-2, canvas_h-2, outline=border_color, width=2)

        # Color preview square (small swatch)
        color_preview = tk.Canvas(hex_border_frame, width=preview_size, height=preview_size, bg=color,
                                  highlightthickness=1, highlightbackground='#333')
        color_preview.place(x=preview_x, y=preview_y)
        color_preview.bind('<Button-1>', partial(_edit_gradient_color, app, color_index=idx))

        # Hover effects for color swatch (left-click to edit, right-click to copy)
        def on_swatch_enter(event, swatch_widget=color_preview):
            swatch_widget.config(highlightbackground='#b5eab5', highlightthickness=2)
            swatch_widget.config(cursor='hand2')
        def on_swatch_leave(event, swatch_widget=color_preview):
            swatch_widget.config(highlightbackground='#333', highlightthickness=1)
            swatch_widget.config(cursor='')
        def on_swatch_click(event, current_color=color, swatch_widget=color_preview, entry_widget=hex_entry):
            helpers.copy_to_clipboard_helper(app, current_color, f"{current_color.upper()} copied!")
            # Flash effect
            orig_bg = swatch_widget['highlightbackground']
            orig_text = entry_widget.get()
            orig_fg = entry_widget['fg']
            orig_entry_bg = entry_widget['bg']
            swatch_widget.config(highlightbackground='#4CAF50', highlightthickness=3)
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, "✔ Copied!")
            entry_widget.config(fg='#222', bg='#eaffc2')
            def reset_swatch():
                swatch_widget.config(highlightbackground=orig_bg, highlightthickness=1)
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, orig_text)
                entry_widget.config(fg=orig_fg, bg=orig_entry_bg)
            swatch_widget.after(900, reset_swatch)
        color_preview.bind('<Enter>', on_swatch_enter)
        color_preview.bind('<Leave>', on_swatch_leave)
        color_preview.bind('<Button-3>', partial(on_swatch_click, current_color=color)) # Right-click to copy

        # Copy to clipboard effect and hover effect for hex entry
        def copy_effect(event=None, entry_widget=hex_entry, current_color=color, border_canvas_widget=border_canvas, border_rect_id=border_rect):
            helpers.copy_to_clipboard_helper(app, current_color, f"{current_color.upper()} copied!")
            orig_bg = entry_widget['bg']
            orig_fg = entry_widget['fg']
            orig_text = entry_widget.get()
            entry_widget.config(bg='#eaffc2', fg='#222')
            entry_widget.delete(0, 'end')
            entry_widget.insert(0, "✔ Copied!")
            border_canvas_widget.itemconfig(border_rect_id, outline='#4CAF50') # Change border color
            def reset():
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, orig_text)
                entry_widget.config(bg=orig_bg, fg=orig_fg)
                border_canvas_widget.itemconfig(border_rect_id, outline=border_color) # Revert border
            entry_widget.after(900, reset)
        hex_entry.bind('<Button-1>', copy_effect) # Left-click to copy

        # Hover effect for hex entry
        def on_enter_hex(event, entry_widget=hex_entry, border_canvas_widget=border_canvas, border_rect_id=border_rect):
            entry_widget.config(bg="#eaffcc")
            border_canvas_widget.itemconfig(border_rect_id, outline="#b5eab5")
        def on_leave_hex(event, entry_widget=hex_entry, border_canvas_widget=border_canvas, border_rect_id=border_rect):
            entry_widget.config(bg=INPUT_BG)
            border_canvas_widget.itemconfig(border_rect_id, outline=border_color)
        hex_entry.bind('<Enter>', on_enter_hex)
        hex_entry.bind('<Leave>', on_leave_hex)

        _create_tooltip(color_preview, f"Left-click to edit • Right-click to copy {color.upper()}")
        _create_tooltip(hex_entry, f"Click to copy {color.upper()}")
        app._gradient_hex_labels.append(hex_entry) # Store for potential future use (e.g., refreshing effects)

    # Maintain frame dimensions if they were previously set
    if frame_width and frame_height:
        frame.update_idletasks()
        if frame.winfo_reqwidth() != frame_width or frame.winfo_reqheight() != frame_height:
            frame.config(width=frame_width, height=frame_height)

def _edit_gradient_color(app, color_index):
    """
    Opens a minimalist color picker for editing a specific gradient color stop.

    Args:
        app: The main application instance.
        color_index (int): The index of the color in _gradient_colors to edit.
    """
    if Image is None or ImageTk is None:
        tk.messagebox.showerror("Missing Dependency", "Pillow library is required for the color picker. Please install it with: pip install Pillow")
        return

    picker = Toplevel(app.root)
    picker.title("Minimalist Color Picker")
    picker.configure(bg=PRIMARY_BG)
    picker.resizable(False, False)

    def on_color_picked(new_hex):
        """Callback executed when a color is selected in the picker."""
        if new_hex and helpers.is_valid_hex(new_hex):
            app._gradient_colors[color_index] = new_hex.upper()
            _draw_gradient_preview(app) # Redraw gradient with new color
            _draw_gradient_hexes(app) # Update hex labels
            app.update_status(f"Color {color_index+1} updated!", SUCCESS_GREEN)
        else:
            app.update_status("Color edit cancelled.", TEXT_MUTED)

    try:
        initial_hex = app._gradient_colors[color_index]
        rgb = [int(initial_hex[i:i+2], 16) for i in (1, 3, 5)] if helpers.is_valid_hex(initial_hex) else [170, 187, 204]
        h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
        hue_var = tk.DoubleVar(value=h*360)
        hex_var = tk.StringVar(value=initial_hex.upper())

        area_size = 180
        left_margin = 20
        gradient_img = None
        gradient_tk = None

        color_area = tk.Label(picker, bd=2, relief='ridge', bg=PRIMARY_BG)
        color_area.place(x=left_margin, y=40, width=area_size, height=area_size)

        def make_gradient(hue_val):
            img = Image.new('RGB', (area_size, area_size))
            pixels = img.load()
            for y_coord in range(area_size):
                for x_coord in range(area_size):
                    saturation = x_coord / (area_size-1)
                    value = 1 - (y_coord / (area_size-1))
                    r_val, g_val, b_val = colorsys.hsv_to_rgb(hue_val, saturation, value)
                    pixels[x_coord, y_coord] = (int(r_val*255), int(g_val*255), int(b_val*255))
            return img

        def update_gradient(*_):
            nonlocal gradient_img, gradient_tk
            hue = hue_var.get() / 360
            gradient_img = make_gradient(hue)
            gradient_tk = ImageTk.PhotoImage(gradient_img)
            color_area.config(image=gradient_tk)
        update_gradient()

        def area_pick(event):
            x_click, y_click = event.x, event.y
            if 0 <= x_click < area_size and 0 <= y_click < area_size:
                saturation = x_click / (area_size-1)
                value = 1 - (y_click / (area_size-1))
                hue = hue_var.get() / 360
                r_val, g_val, b_val = colorsys.hsv_to_rgb(hue, saturation, value)
                hex_code = f"#{int(r_val*255):02X}{int(g_val*255):02X}{int(b_val*255):02X}"
                hex_var.set(hex_code.upper())
                preview.config(bg=hex_code)

        color_area.bind('<Button-1>', area_pick)
        color_area.bind('<B1-Motion>', area_pick)

        hue_slider_y = 210
        hue_slider = tk.Scale(picker, from_=0, to=359, orient='horizontal', variable=hue_var, showvalue=True, length=area_size+10,
                            bg=PRIMARY_BG, fg="#888", highlightthickness=0, troughcolor=SECONDARY_BG, bd=0, resolution=1)
        hue_slider.place(x=left_margin, y=hue_slider_y+10, width=area_size)
        hue_var.trace_add('write', lambda *_: update_gradient())

        hex_y = hue_slider_y + 60
        preview_size = 28
        preview = tk.Frame(picker, bg=hex_var.get(), width=preview_size, height=preview_size, bd=2, relief='ridge')
        preview.place(x=left_margin, y=hex_y)

        hex_label = tk.Label(picker, text="HEX", font=(FONT_FAMILY, 9, 'bold'), bg=PRIMARY_BG, fg="#888")
        hex_label.place(x=left_margin+50, y=hex_y+4)

        hex_entry = tk.Entry(picker, textvariable=hex_var, font=(FONT_FAMILY, 11), width=10, justify='center', bd=1, relief='solid', bg=INPUT_BG, fg=INPUT_FG)
        hex_entry.place(x=left_margin+85, y=hex_y, width=80, height=28)

        def update_from_hex(*_):
            val = hex_var.get().strip()
            if helpers.is_valid_hex(val):
                try:
                    r_val = int(val[1:3], 16)
                    g_val = int(val[3:5], 16)
                    b_val = int(val[5:7], 16)
                    preview.config(bg=val)
                    # Live update the gradient color as hex is typed
                    if hasattr(picker, '_update_timer'):
                        picker.after_cancel(picker._update_timer)

                    def do_update_color():
                        on_color_picked(hex_var.get())
                        if hasattr(picker, '_update_timer'):
                            delattr(picker, '_update_timer')

                    picker._update_timer = picker.after(100, do_update_color) # 100ms debounce
                except ValueError:
                    pass # Invalid hex string, do nothing

        hex_var.trace_add('write', update_from_hex)

        picker.update_idletasks()
        window_width = area_size + 2*left_margin
        window_height = hex_y + 28 + 32
        picker.geometry(f"{window_width}x{window_height}")
        picker.minsize(window_width, window_height)
        picker.maxsize(window_width, window_height)
        preview.config(bg=hex_var.get())

        picker.bind('<FocusOut>', lambda e: picker.destroy()) # Close on focus out
        picker.bind('<Escape>', lambda e: picker.destroy()) # Close on Escape
    except Exception as e:
        import traceback
        print("Error building color picker UI:", e)
        traceback.print_exc()
        error_label = tk.Label(picker, text="Error loading color picker", fg="red", bg=PRIMARY_BG)
        error_label.pack(expand=True, fill="both")
    else:
        picker.update_idletasks()
        picker.deiconify()
        picker.lift()
        picker.focus_force()

def _create_tooltip(widget, text):
    """
    Creates a simple tooltip that appears when the mouse hovers over a widget.

    Args:
        widget: The Tkinter widget to attach the tooltip to.
        text (str): The text to display in the tooltip.
    """
    def on_enter(event):
        tooltip = Toplevel(widget) # Use widget as master for proper parenting
        tooltip.wm_overrideredirect(True) # Remove window decorations
        # Position tooltip slightly below and to the right of the mouse cursor
        tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

        label = tk.Label(tooltip, text=text, font=(FONT_FAMILY, 9),
                       bg='#ffffe0', fg='#000000', relief='solid', bd=1)
        label.pack()

        widget.tooltip = tooltip # Store tooltip reference on the widget

    def on_leave(event):
        if hasattr(widget, 'tooltip') and widget.tooltip:
            widget.tooltip.destroy()
            del widget.tooltip

    widget.bind('<Enter>', on_enter)
    widget.bind('<Leave>', on_leave)


def _on_gradient_stop_press(app, event):
    """
    Handles mouse button press on a gradient stop. Identifies the stop being dragged.
    """
    c = app.gradient_preview_canvas
    x = event.x
    w = int(c['width'])

    # Find the closest gradient stop to the mouse click (by X-coordinate)
    idx = min(range(len(app._gradient_positions)), key=lambda i: abs(x - int(app._gradient_positions[i]*(w-1))))
    app._dragging_stop = idx # Store the index of the stop being dragged

    # Store the offset between mouse click position and the center of the stop
    stop_x = int(app._gradient_positions[idx] * (w-1))
    stop_y = int(c['height']) // 2
    app._drag_mouse_offset_x = x - stop_x
    app._drag_mouse_offset_y = event.y - stop_y # Store Y offset too, though only X is used for movement


def _on_gradient_stop_drag(app, event):
    """
    Handles mouse drag event on a gradient stop. Updates the stop's position.
    """
    if app._dragging_stop is None: # Only proceed if a stop is currently being dragged
        return

    c = app.gradient_preview_canvas
    w = int(c['width'])
    idx = app._dragging_stop
    n = len(app._gradient_positions)
    min_gap = 0.01 # Minimum fractional distance between stops to prevent overlap

    # Calculate new position based on mouse X, adjusting for initial click offset
    # Only use X offset for horizontal movement
    mouse_offset_x = getattr(app, '_drag_mouse_offset_x', 0)
    stop_x = event.x - mouse_offset_x
    new_pos = stop_x / (w - 1) if w > 1 else 0 # Normalize to 0-1 fraction

    # Clamp position to be within 0.0 and 1.0
    new_pos = min(max(new_pos, 0.0), 1.0)

    # Ensure stops maintain their relative order and don't overlap
    if idx > 0:
        new_pos = max(new_pos, app._gradient_positions[idx-1] + min_gap)
    if idx < n-1:
        new_pos = min(new_pos, app._gradient_positions[idx+1] - min_gap)

    app._gradient_positions[idx] = new_pos # Update the stop's position

    # During drag, only redraw the canvas preview for smoother interaction
    _draw_gradient_preview(app)

def _on_gradient_stop_release(app, event):
    """
    Handles mouse button release after dragging a gradient stop. Resets drag state.
    """
    app._dragging_stop = None # Reset dragging state
    app._drag_mouse_offset_x = None
    app._drag_mouse_offset_y = None
    # Update hex codes only after drag is complete to prevent UI "wiggling"
    _draw_gradient_hexes(app)

def _on_gradient_stop_double_click(app, event):
    """
    Handles double-click on a gradient stop to open the color editor for that stop.
    """
    c = app.gradient_preview_canvas
    x = event.x
    w = int(c['width'])

    # Find the closest gradient stop
    idx = min(range(len(app._gradient_positions)),
             key=lambda i: abs(x - int(app._gradient_positions[i]*(w-1))))
    _edit_gradient_color(app, idx) # Open color picker for the selected stop

    return "break" # Prevent event from bubbling up to canvas (which would add a new stop)

def _on_gradient_stop_right_click(app, event):
    """
    Handles right-click on a gradient stop to delete it. Requires at least 2 stops to remain.
    """
    if len(app._gradient_colors) <= 2:
        app.update_status("Cannot delete - minimum 2 colors required!", WARNING_RED)
        return

    c = app.gradient_preview_canvas
    x = event.x
    w = int(c['width'])

    # Find the closest gradient stop
    idx = min(range(len(app._gradient_positions)),
             key=lambda i: abs(x - int(app._gradient_positions[i]*(w-1))))

    # Remove the color and its position
    app._gradient_colors.pop(idx)
    app._gradient_positions.pop(idx)

    # Recalculate positions to maintain even distribution if only one left or newly evened
    n = len(app._gradient_colors)
    if n > 1:
        app._gradient_positions = [i/(n-1) for i in range(n)]
    elif n == 1: # If only one color left, center its position
        app._gradient_positions = [0.5]


    _draw_gradient_preview(app) # Redraw the gradient
    _draw_gradient_hexes(app) # Redraw HEX codes
    app.update_status(f"Removed color stop {idx+1}!", SUCCESS_GREEN)

def _on_gradient_canvas_double_click(app, event):
    """
    Handles double-click on the gradient canvas to add a new color stop.
    Limits the total number of color stops.
    """
    if len(app._gradient_colors) >= 8:
        app.update_status("Maximum 8 colors allowed!", WARNING_RED)
        return

    c = app.gradient_preview_canvas
    x = event.x
    w = int(c['width'])

    # Check if the click is too close to an existing stop to prevent accidental additions
    stop_radius = 7
    margin = 5
    detection_radius = stop_radius + margin

    for idx, pos in enumerate(app._gradient_positions):
        stop_x = int(round(pos * (w - 1)))
        if abs(x - stop_x) <= detection_radius:
            return # Click is too close to an existing stop, do not add new one

    # Calculate the new stop's fractional position based on click X
    new_stop_pos = x / (w - 1) if w > 1 else 0.5

    # Determine where to insert the new stop to maintain order
    insert_idx = 0
    for i, stop_pos in enumerate(app._gradient_positions):
        if new_stop_pos > stop_pos:
            insert_idx = i + 1
        else:
            break

    # Interpolate a color for the new stop based on its position
    new_color = _interpolate_gradient(app, new_stop_pos)

    # Insert the new color and position into the lists
    app._gradient_colors.insert(insert_idx, new_color)
    app._gradient_positions.insert(insert_idx, new_stop_pos)

    # Ensure positions are re-normalized and sorted after insertion to keep consistent
    # If not specifically user-controlled, distributing evenly is often preferred.
    # For user-added stops, keep exact position but sort.
    app._gradient_positions, app._gradient_colors = zip(*sorted(zip(app._gradient_positions, app._gradient_colors)))
    app._gradient_positions = list(app._gradient_positions)
    app._gradient_colors = list(app._gradient_colors)


    _draw_gradient_preview(app) # Redraw the gradient
    _draw_gradient_hexes(app) # Redraw HEX codes
    app.update_status(f"Added new color stop: {new_color}!", SUCCESS_GREEN)

def _copy_all_gradient_hex(app):
    """Copies all gradient HEX codes to the clipboard, separated by spaces."""
    hexes = ' '.join(app._gradient_colors)
    helpers.copy_to_clipboard_helper(app, hexes, "All HEX codes copied!")

def _export_gradient(app, format_type):
    """
    Exports the current gradient in the specified format (CSS, SVG, PNG, JPEG).

    Args:
        app: The main application instance.
        format_type (str): The desired export format (e.g., "PNG", "CSS Code").
    """
    try:
        width = int(app.export_width_var.get())
        height = int(app.export_height_var.get())
        if width <= 0 or height <= 0:
            raise ValueError("Dimensions must be positive.")
    except ValueError:
        app.update_status("Invalid export dimensions! Please enter positive numbers.", WARNING_RED)
        return

    if format_type == "CSS Code":
        _export_css_gradient(app)
    elif format_type == "SVG":
        _export_svg_gradient(app, width, height)
    else: # PNG or JPEG
        _export_image_gradient(app, format_type, width, height)


def _export_css_gradient(app):
    """Generates and displays CSS code for the current gradient."""
    gradient_type = app.gradient_type_var.get().lower()

    color_stops_css = []
    # Create CSS color stops (e.g., "#RRGGBB 0%")
    for i, color in enumerate(app._gradient_colors):
        pos = app._gradient_positions[i] * 100
        color_stops_css.append(f"{color} {pos:.1f}%")

    css_code = ""
    if gradient_type == "linear":
        # Linear gradient: add angle based on rotation variable
        angle = app.gradient_rotation_var.get()
        css_code = f"background: linear-gradient({angle}deg, {', '.join(color_stops_css)});"
    else: # Radial gradient
        css_code = f"background: radial-gradient(circle, {', '.join(color_stops_css)});"

    # Show CSS code in a popup window
    css_window = tk.Toplevel(app.root)
    css_window.title("CSS Gradient Code")
    css_window.geometry("600x300")
    css_window.configure(bg=PRIMARY_BG)
    css_window.transient(app.root) # Make it an overlay for the main window
    css_window.grab_set() # Make it modal

    # Center the window
    css_window.update_idletasks()
    x = (css_window.winfo_screenwidth() // 2) - (css_window.winfo_width() // 2)
    y = (css_window.winfo_screenheight() // 2) - (css_window.winfo_height() // 2)
    css_window.geometry(f"+{x}+{y}")

    # Title label in the popup
    title = tk.Label(css_window, text="CSS Gradient Code",
                    font=(FONT_FAMILY, 12, 'bold'), bg=PRIMARY_BG, fg=INPUT_FG)
    title.pack(pady=10)

    # Text area to display CSS code
    text_frame = tk.Frame(css_window, bg=PRIMARY_BG)
    text_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

    css_text = tk.Text(text_frame, font=('Courier', 11), bg=INPUT_BG,
                      fg=INPUT_FG, relief='solid', bd=1)
    css_text.pack(fill='both', expand=True)
    css_text.insert('1.0', css_code)
    css_text.config(state='disabled') # Make it read-only

    # Copy button in the popup
    copy_btn = tk.Button(css_window, text="Copy CSS Code",
                       command=lambda: helpers.copy_to_clipboard_helper(app, css_code, "CSS code copied!"),
                       bg=ACCENT_BLUE, fg=TEXT_LIGHT, font=(FONT_FAMILY, 10),
                       relief='flat', padx=15, pady=5, cursor='hand2')
    copy_btn.pack(pady=(0, 10))

    css_window.protocol("WM_DELETE_WINDOW", css_window.destroy) # Ensure grab_release on close

def _export_svg_gradient(app, width, height):
    """
    Exports the current gradient as an SVG (Scalable Vector Graphics) file.
    """
    file = fd.asksaveasfilename(
        defaultextension='.svg',
        filetypes=[('SVG Image', '*.svg')],
        title="Export Gradient as SVG"
    )

    if not file:
        return # User cancelled

    gradient_type = app.gradient_type_var.get().lower()

    # Build SVG content string
    svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>'''

    if gradient_type == "linear":
        angle = app.gradient_rotation_var.get()
        # SVG linear gradients work with x1, y1, x2, y2 from 0-1, representing start/end of gradient line
        # For a given angle, we need to map to these coordinates.
        # Simple mapping for a 0-360 degree angle:
        # 0deg (right): x1="0%" y1="0%" x2="100%" y2="0%"
        # 90deg (down): x1="0%" y1="0%" x2="0%" y2="100%"
        # This is a simplified approach, full angle mapping is more complex for SVG.
        # For simplicity, we can default to left-to-right for linear.
        # A more accurate mapping would involve trigonometry or a library.
        # For now, let's keep it simple for a default horizontal gradient in SVG.
        svg_content += f'''
    <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">''' # Default horizontal for simplicity
    else: # Radial
        svg_content += f'''
    <radialGradient id="gradient" cx="50%" cy="50%" r="50%">'''

    # Add color stops to SVG
    for i, color in enumerate(app._gradient_colors):
        offset = app._gradient_positions[i] * 100
        svg_content += f'''
      <stop offset="{offset:.1f}%" stop-color="{color}"/>'''

    if gradient_type == "linear":
        svg_content += '''
    </linearGradient>'''
    else:
        svg_content += '''
    </radialGradient>'''

    svg_content += f'''
  </defs>
  <rect width="{width}" height="{height}" fill="url(#gradient)"/>
</svg>'''

    try:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(svg_content)
        app.update_status("SVG gradient exported successfully!", SUCCESS_GREEN)
    except Exception as e:
        app.update_status(f"Failed to export SVG: {str(e)}", WARNING_RED)

def _export_image_gradient(app, format_type, width, height):
    """
    Exports the current gradient as a raster image (PNG or JPEG).
    """
    if Image is None or ImageDraw is None:
        tk.messagebox.showerror("Missing Dependency",
                            "Pillow (PIL) is required to export images. Please install it with: pip install Pillow")
        return

    file = fd.asksaveasfilename(
        defaultextension=f'.{format_type.lower()}',
        filetypes=[(f'{format_type} Image', f'*.{format_type.lower()}')],
        title=f"Export Gradient as {format_type}"
    )

    if not file:
        return

    # Create a new blank image
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)

    gradient_type = app.gradient_type_var.get().lower()

    if gradient_type == "radial":
        center_x, center_y = width // 2, height // 2
        # Calculate max radius to cover corners of the image
        max_radius = ((width/2)**2 + (height/2)**2)**0.5

        # Draw concentric circles from outside to inside for smoother gradient
        num_rings = min(max(width, height), 500) # Adaptive quality
        ring_step = max_radius / num_rings if num_rings > 0 else 1

        for ring_idx in range(num_rings, 0, -1): # Iterate from outer ring inwards
            radius = ring_idx * ring_step
            # Fraction from center (0) to max radius (1)
            frac = min(radius / max_radius, 1.0)
            color_hex = _interpolate_gradient(app, frac)
            color_rgb = helpers.hex_to_rgb(color_hex) # Convert hex to RGB tuple

            # Draw filled circle (ellipse with equal width/height)
            bbox = [center_x - radius, center_y - radius,
                   center_x + radius, center_y + radius]
            draw.ellipse(bbox, fill=color_rgb, outline=color_rgb) # Outline same as fill to avoid borders
    else: # Linear gradient
        angle = app.gradient_rotation_var.get()
        theta = math.radians(angle)
        cos_theta = math.cos(theta)
        sin_theta = math.sin(theta)

        # Iterate over each pixel (or small strip) to calculate color
        for x_coord in range(width):
            for y_coord in range(height):
                # Normalize coordinates to [-0.5, 0.5] range
                nx = (x_coord / (width-1)) - 0.5 if width > 1 else 0
                ny = (y_coord / (height-1)) - 0.5 if height > 1 else 0

                # Apply rotation and normalize to 0-1 for interpolation
                frac = nx * cos_theta + ny * sin_theta + 0.5
                frac = min(max(frac, 0), 1) # Clamp fraction

                color_hex = _interpolate_gradient(app, frac)
                color_rgb = helpers.hex_to_rgb(color_hex)
                img.putpixel((x_coord, y_coord), color_rgb) # Set pixel color

    try:
        if format_type == "PNG":
            img.save(file, format='PNG')
        else: # JPEG
            img.save(file, format='JPEG', quality=95) # High quality for JPEG
        app.update_status(f"{format_type} gradient exported successfully!", SUCCESS_GREEN)
    except Exception as e:
        app.update_status(f"Failed to export {format_type}: {str(e)}", WARNING_RED)

def _show_gradient_presets(app):
    """
    Displays a popup window with predefined gradient presets.
    Users can select a preset to load into the gradient generator.
    """
    preset_window = Toplevel(app.root)
    preset_window.title("Gradient Presets")
    preset_window.geometry("600x500")
    preset_window.configure(bg=PRIMARY_BG)
    preset_window.transient(app.root)
    preset_window.grab_set() # Make it modal

    # Center the window
    preset_window.update_idletasks()
    x = (preset_window.winfo_screenwidth() // 2) - (preset_window.winfo_width() // 2)
    y = (preset_window.winfo_screenheight() // 2) - (preset_window.winfo_height() // 2)
    preset_window.geometry(f"+{x}+{y}")

    # Title
    title = tk.Label(preset_window, text="Choose a Gradient Preset",
                    font=(FONT_FAMILY, 14, 'bold'), bg=PRIMARY_BG, fg=INPUT_FG)
    title.pack(pady=10)

    # Scrollable frame for presets
    canvas = tk.Canvas(preset_window, bg=PRIMARY_BG)
    scrollbar = ttk.Scrollbar(preset_window, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg=PRIMARY_BG)

    canvas.configure(yscrollcommand=scrollbar.set)
    scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel) # Bind to all for global effect

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Create preset entries (frame, preview, info, button)
    for name, colors in GRADIENT_PRESETS.items():
        preset_frame = tk.Frame(scrollable_frame, bg=PRIMARY_BG)
        preset_frame.pack(fill='x', padx=10, pady=5)

        # Gradient preview canvas
        preview_canvas = tk.Canvas(preset_frame, width=300, height=40, bg=INPUT_BG, highlightthickness=1)
        preview_canvas.pack(side='left', padx=(0, 10))
        _draw_preset_gradient(preview_canvas, colors) # Draw the gradient preview

        # Preset info and button
        info_frame = tk.Frame(preset_frame, bg=PRIMARY_BG)
        info_frame.pack(side='left', fill='both', expand=True)

        name_label = tk.Label(info_frame, text=name, font=(FONT_FAMILY, 11, 'bold'),
                             bg=PRIMARY_BG, fg=INPUT_FG)
        name_label.pack(anchor='w')

        colors_label = tk.Label(info_frame, text=' → '.join(colors),
                               font=(FONT_FAMILY, 9), bg=PRIMARY_BG, fg=TEXT_MUTED)
        colors_label.pack(anchor='w')

        use_btn = tk.Button(info_frame, text="Use This",
                           command=partial(_load_preset_gradient, app, colors, preset_window),
                           bg=ACCENT_BLUE, fg=TEXT_LIGHT, font=(FONT_FAMILY, 9),
                           relief='flat', padx=10, pady=2, cursor='hand2')
        use_btn.pack(anchor='w', pady=(5, 0))

    scrollable_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    preset_window.protocol("WM_DELETE_WINDOW", preset_window.destroy) # Ensure grab_release on close


def _draw_preset_gradient(canvas, colors):
    """
    Draws a simple linear gradient preview on a given canvas for presets.

    Args:
        canvas: The Tkinter Canvas widget to draw on.
        colors (list): A list of HEX color codes for the gradient.
    """
    canvas.update_idletasks()
    w = canvas.winfo_reqwidth()
    h = canvas.winfo_reqheight()

    if not colors:
        return # Nothing to draw

    # Draw simple linear gradient from left to right
    for x in range(w):
        if len(colors) == 1:
            color = colors[0] # Solid color if only one
        else:
            frac = x / (w - 1) if w > 1 else 0 # Normalized position
            # Interpolate between colors
            # Find the position in the color array (e.g., if 3 colors, pos will be 0 to 2)
            pos_in_array = frac * (len(colors) - 1)
            idx = int(pos_in_array) # Integer part is the left color index

            if idx >= len(colors) - 1: # At or beyond the last color
                color = colors[-1]
            else:
                t = pos_in_array - idx # Fractional part for interpolation between idx and idx+1
                color = _interpolate_colors(colors[idx], colors[idx + 1], t)

        canvas.create_line(x, 0, x, h, fill=color) # Draw a vertical line for each x


def _interpolate_colors(color1, color2, t):
    """
    Interpolates between two HEX color codes using a factor t (0.0 to 1.0).

    Args:
        color1 (str): First HEX color.
        color2 (str): Second HEX color.
        t (float): Interpolation factor (0.0 = color1, 1.0 = color2).

    Returns:
        str: The interpolated HEX color code.
    """
    c1_rgb = helpers.hex_to_rgb(color1)
    c2_rgb = helpers.hex_to_rgb(color2)

    # Interpolate each RGB component
    r = int(c1_rgb[0] + (c2_rgb[0] - c1_rgb[0]) * t)
    g = int(c1_rgb[1] + (c2_rgb[1] - c1_rgb[1]) * t)
    b = int(c1_rgb[2] + (c2_rgb[2] - c1_rgb[2]) * t)

    return helpers.rgb_to_hex((r, g, b))

def _load_preset_gradient(app, colors, window):
    """
    Loads a selected gradient preset into the main gradient generator.

    Args:
        app: The main application instance.
        colors (list): A list of HEX colors for the preset.
        window: The Toplevel preset window to destroy after loading.
    """
    app._gradient_colors = list(colors) # Copy colors
    n = len(colors)
    # Re-distribute positions evenly for the loaded preset
    app._gradient_positions = [i/(n-1) if n > 1 else 0.5 for i in range(n)]

    _draw_gradient_preview(app) # Redraw gradient preview
    _draw_gradient_hexes(app) # Redraw HEX code labels
    window.destroy() # Close the preset selection window
    app.update_status(f"Loaded preset gradient with {n} colors!", SUCCESS_GREEN)

