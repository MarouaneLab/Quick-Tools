import tkinter as tk
from tkinter import ttk, scrolledtext
import pyperclip
import re


class TextCaseConverter:
    # --- Gradient Style Palettes ---
    GRADIENT_STYLES = {
        # --- Color Harmony Based Palettes (top choices) ---
        'Analogous': ['#FFB347', '#FFD700', '#ADFF2F', '#7FFF00', '#00FF7F', '#00FA9A'],
        'Complementary': ['#FF6F61', '#6B5B95', '#FF6F61', '#88B04B', '#6B5B95', '#FF6F61'],
        'Triadic': ['#FF6F61', '#6B5B95', '#88B04B', '#FF6F61', '#6B5B95', '#88B04B'],
        'Tetradic': ['#FF6F61', '#6B5B95', '#FFD700', '#88B04B', '#FF6F61', '#6B5B95', '#FFD700', '#88B04B'],
        # --- Original palettes ---
        'Warm':    ['#D98236', '#E8A34C', '#E6C87D', '#F6B48F', '#F7C873', '#F9E79F', '#FAD7A0', '#F5CBA7'],
        'Cool':    ['#36A2D9', '#4CC3E8', '#7DDDE6', '#8FCBF6', '#73C6F7', '#9FE7F9', '#A0D7FA', '#A7C5F5'],
        'Neutral': ['#B0B0B0', '#D3D3D3', '#E0E0E0', '#C8C8C8', '#B8B8B8', '#E8E8E8', '#CCCCCC', '#F0F0F0'],
        'Vibrant': ['#FF5E5B', '#D72660', '#3F88C5', '#F49D37', '#140F2D', '#16DB93', '#F5CB5C', '#247BA0'],
        'Muted':   ['#A39887', '#B7A99A', '#C9B6A7', '#A3A380', '#B2B09B', '#B5B5B5', '#A9A9A9', '#C0C0C0'],
        'Pastel':  ['#FFD1DC', '#B5EAD7', '#C7CEEA', '#FFDAC1', '#E2F0CB', '#FFB7B2', '#B5B9FF', '#FFFFB5'],
    }
    def _build_gradient_generator_section(self, parent):
        import random
        section = tk.Frame(parent, bg=self.PRIMARY_BG)
        section.pack(fill='x', pady=(18, 18), padx=(0,0), anchor='center')

        # --- Title for Gradient Generator (left-aligned, regular font, more breathing space) ---
        title = tk.Label(section, text="Gradient Generator", font=(self.FONT_FAMILY, 11), bg=self.PRIMARY_BG, fg=self.INPUT_FG)
        title.pack(anchor='w', pady=(28, 14), padx=(10,0))

        controls = tk.Frame(section, bg=self.PRIMARY_BG)
        controls.pack(anchor='center', pady=(0, 10))
        tk.Label(controls, text="Gradient Type:", font=(self.FONT_FAMILY, 11), bg=self.PRIMARY_BG).pack(side='left', padx=(0,2))
        self.gradient_type_var = tk.StringVar(value='Linear')
        type_combo = ttk.Combobox(controls, textvariable=self.gradient_type_var, state='readonly', font=self.FONT_INPUT, width=8, values=['Linear', 'Radial'])
        type_combo.pack(side='left', padx=(0, 12))
        tk.Label(controls, text="Number of Colors:", font=(self.FONT_FAMILY, 11), bg=self.PRIMARY_BG).pack(side='left', padx=(0,2))
        self.gradient_num_colors_var = tk.IntVar(value=3)
        num_combo = ttk.Combobox(controls, textvariable=self.gradient_num_colors_var, state='readonly', font=self.FONT_INPUT, width=3, values=list(range(2,9)))
        num_combo.pack(side='left', padx=(0, 12))
        tk.Label(controls, text="Color Style:", font=(self.FONT_FAMILY, 11), bg=self.PRIMARY_BG).pack(side='left', padx=(0,2))
        self.gradient_style_var = tk.StringVar(value='Warm')
        style_combo = ttk.Combobox(controls, textvariable=self.gradient_style_var, state='readonly', font=self.FONT_INPUT, width=8, values=list(self.GRADIENT_STYLES.keys()))
        style_combo.pack(side='left', padx=(0, 0))

        # --- Generate Button (centered above canvas) ---
        gen_btn = tk.Button(section, text="Generate Gradient", command=self._generate_gradient_random, font=(self.FONT_FAMILY, 11, 'bold'),
                            bg=self.ACCENT_BLUE, fg=self.TEXT_LIGHT, relief='flat', padx=16, pady=6, cursor='hand2', bd=0,
                            activebackground=self.HOVER_ACCENT_BLUE, activeforeground=self.TEXT_LIGHT)
        gen_btn.pack(anchor='center', pady=(18, 18))
        self._button_hover_colors[gen_btn] = {'original': self.ACCENT_BLUE, 'hover': self.HOVER_ACCENT_BLUE}

        # --- Responsive Canvas ---
        # Center the canvas frame and add equal horizontal padding for harmony
        # Reduce left space and center the canvas frame with balanced padding
        canvas_frame = tk.Frame(section, bg=self.PRIMARY_BG)
        # Shift canvas_frame slightly left to balance the right-side scrollbar
        canvas_frame.pack(fill='x', expand=True, pady=(0, 18), padx=(10,0), anchor='w')
        canvas_frame.grid_columnconfigure(0, weight=1)
        self._gradient_canvas_min_w = 350
        self._gradient_canvas_min_h = 180
        self._gradient_canvas_max_w = 700
        self._gradient_canvas_max_h = 320
        def get_canvas_size():
            parent_w = canvas_frame.winfo_width() if canvas_frame.winfo_width() > 0 else 800
            w = max(self._gradient_canvas_min_w, min(self._gradient_canvas_max_w, parent_w))
            h = int(w * 0.55)
            h = max(self._gradient_canvas_min_h, min(self._gradient_canvas_max_h, h))
            return w, h
        w, h = get_canvas_size()
        # Remove highlightthickness and highlightbackground so the border is not drawn by the canvas
        self.gradient_preview_canvas = tk.Canvas(canvas_frame, width=w, height=h, bg=self.INPUT_BG, highlightthickness=0, bd=0)
        self.gradient_preview_canvas.grid(row=0, column=0, sticky='nsew', padx=0, pady=0)
        # Add a Frame with the border color around the canvas for a true border effect
        border_frame = tk.Frame(canvas_frame, bg=self.SECONDARY_BG, highlightthickness=0, bd=0)
        border_frame.grid(row=0, column=0, sticky='nsew')
        border_frame.lower(self.gradient_preview_canvas)  # Put border behind canvas
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        # Make sure the canvas frame itself is centered and matches the color row above
        def on_resize(event=None):
            w, h = get_canvas_size()
            self.gradient_preview_canvas.config(width=w, height=h)
            self._draw_gradient_preview()
        canvas_frame.bind('<Configure>', on_resize)

        # --- HEX Codes Row ---
        self.gradient_hex_frame = tk.Frame(section, bg=self.PRIMARY_BG)
        # Align HEX codes row with canvas_frame (left-aligned, no right padding)
        self.gradient_hex_frame.pack(fill='x', pady=(2, 8), padx=(10,0), anchor='w')

        # --- Copy/Export Buttons ---
        btns_frame = tk.Frame(section, bg=self.PRIMARY_BG)
        btns_frame.pack(anchor='w', pady=(2, 0))
        copy_btn = tk.Button(btns_frame, text="Copy All HEX", command=self._copy_all_gradient_hex, font=(self.FONT_FAMILY, 10),
                            bg=self.SECONDARY_BG, fg=self.INPUT_FG, relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                            activebackground=self.HOVER_ACCENT_BLUE, activeforeground=self.INPUT_FG)
        copy_btn.pack(side='left', padx=(0, 10))
        self._button_hover_colors[copy_btn] = {'original': self.SECONDARY_BG, 'hover': self.HOVER_ACCENT_BLUE}
        export_btn = tk.Button(btns_frame, text="Export JPEG", command=self._export_gradient_jpeg, font=(self.FONT_FAMILY, 10),
                            bg=self.SECONDARY_BG, fg=self.INPUT_FG, relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                            activebackground=self.HOVER_ACCENT_BLUE, activeforeground=self.INPUT_FG)
        export_btn.pack(side='left', padx=(0, 0))
        self._button_hover_colors[export_btn] = {'original': self.SECONDARY_BG, 'hover': self.HOVER_ACCENT_BLUE}

        self._gradient_colors = []
        self._gradient_positions = []
        self._dragging_stop = None

        self._generate_gradient_random()

    def _generate_gradient_random(self):
        import random
        import colorsys
        style = self.gradient_style_var.get()
        n = self.gradient_num_colors_var.get()
        palette = self.GRADIENT_STYLES.get(style, list(self.GRADIENT_STYLES.values())[0])

        harmony_palettes = {'Analogous', 'Complementary', 'Triadic', 'Tetradic'}
        import time
        # Use time and random state to maximize variance
        random.seed(time.time_ns() + random.randint(0, 1_000_000))
        # Keep track of last gradient to avoid repeats
        if not hasattr(self, '_last_gradient_signature'):
            self._last_gradient_signature = None
        max_attempts = 10
        for attempt in range(max_attempts):
            if style in harmony_palettes:
                base_palette = palette[:]
                random.shuffle(base_palette)
                if style in {'Complementary', 'Triadic', 'Tetradic'}:
                    offset = random.randint(0, len(base_palette)-1)
                    base_palette = base_palette[offset:] + base_palette[:offset]
                if n > len(base_palette):
                    colors = [base_palette[i % len(base_palette)] for i in range(n)]
                else:
                    # For more variance, pick random indices without replacement if possible
                    if n <= len(base_palette):
                        indices = random.sample(range(len(base_palette)), n)
                        colors = [base_palette[i] for i in indices]
                    else:
                        start = random.randint(0, len(base_palette)-1)
                        step = max(1, len(base_palette)//n)
                        indices = [(start + i*step) % len(base_palette) for i in range(n)]
                        colors = [base_palette[i] for i in indices]
            else:
                base_palette = palette[:]
                def hex_to_hsv(hexcode):
                    hexcode = hexcode.lstrip('#')
                    r, g, b = int(hexcode[0:2], 16), int(hexcode[2:4], 16), int(hexcode[4:6], 16)
                    return colorsys.rgb_to_hsv(r/255, g/255, b/255)
                sorted_palette = sorted(base_palette, key=hex_to_hsv)
                offset = random.randint(0, len(sorted_palette)-1)
                sorted_palette = sorted_palette[offset:] + sorted_palette[:offset]
                if n > len(sorted_palette):
                    colors = [sorted_palette[i % len(sorted_palette)] for i in range(n)]
                else:
                    # For more variance, pick random indices without replacement if possible
                    if n <= len(sorted_palette):
                        indices = random.sample(range(len(sorted_palette)), n)
                        colors = [sorted_palette[i] for i in indices]
                    else:
                        start = random.randint(0, len(sorted_palette)-1)
                        step = max(1, len(sorted_palette)//n)
                        indices = [(start + i*step) % len(sorted_palette) for i in range(n)]
                        colors = [sorted_palette[i] for i in indices]
            # Create a signature to compare with last gradient
            signature = tuple(colors)
            if signature != self._last_gradient_signature:
                break
        self._last_gradient_signature = tuple(colors)
        self._gradient_colors = colors
        self._gradient_positions = [i/(n-1) if n>1 else 0.5 for i in range(n)]
        self._draw_gradient_preview()
        self._draw_gradient_hexes()

    def _generate_gradient(self):
        # Get style palette and number of colors
        style = self.gradient_style_var.get()
        n = self.gradient_num_colors_var.get()
        palette = self.GRADIENT_STYLES.get(style, list(self.GRADIENT_STYLES.values())[0])
        # Pick n colors evenly from the palette
        if n > len(palette):
            colors = palette + [palette[-1]] * (n - len(palette))
        else:
            step = (len(palette)-1)/(n-1) if n > 1 else 1
            colors = [palette[int(round(i*step))] for i in range(n)]
        self._gradient_colors = colors
        self._gradient_positions = [i/(n-1) if n>1 else 0.5 for i in range(n)]
        self._draw_gradient_preview()
        self._draw_gradient_hexes()

    def _draw_gradient_preview(self):
        c = self.gradient_preview_canvas
        c.delete('all')
        w = int(c['width'])
        h = int(c['height'])
        # Draw gradient fully to the canvas edges
        if self.gradient_type_var.get() == 'Radial':
            # Fill every pixel: for each pixel, compute its normalized distance from center (ellipse)
            cx, cy = w / 2, h / 2
            rx, ry = w / 2, h / 2
            for y in range(h):
                for x in range(w):
                    # Normalized elliptical distance from center (0 at center, 1 at edge)
                    dx = (x + 0.5 - cx) / rx if rx else 0
                    dy = (y + 0.5 - cy) / ry if ry else 0
                    dist = (dx ** 2 + dy ** 2) ** 0.5
                    frac = min(dist, 1.0)
                    color = self._interpolate_gradient(frac)
                    c.create_line(x, y, x + 1, y, fill=color)
        else:
            # Draw the gradient as a filled rectangle for each column, ensuring the rightmost pixel is filled
            for x in range(w):
                # Guarantee the rightmost pixel is filled by drawing a rectangle for the last column
                if w > 1:
                    frac = x / (w - 1)
                else:
                    frac = 0
                color = self._interpolate_gradient(frac)
                if x == w - 1:
                    # Draw a rectangle to ensure the rightmost border is filled
                    c.create_rectangle(x, 0, x + 1, h, outline=color, fill=color)
                else:
                    c.create_line(x, 0, x, h - 1, fill=color)
        # Draw draggable stops
        # Make the draggable color stops smaller and centered vertically
        stop_radius = 7  # smaller radius for less visual disturbance
        stop_height = 2 * stop_radius
        for idx, pos in enumerate(self._gradient_positions):
            x = int(round(pos * (w - 1)))
            y = h // 2
            c.create_oval(x - stop_radius, y - stop_radius, x + stop_radius, y + stop_radius,
                          fill=self._gradient_colors[idx], outline='#333', width=2, tags=(f'stop_{idx}', 'stop'))
        # Responsive, lively drag: bind to canvas, not just tag
        c.tag_bind('stop', '<ButtonPress-1>', self._on_gradient_stop_press)
        c.tag_bind('stop', '<B1-Motion>', self._on_gradient_stop_drag)
        c.tag_bind('stop', '<ButtonRelease-1>', self._on_gradient_stop_release)
        c.bind('<B1-Motion>', self._on_gradient_stop_drag)
        c.bind('<ButtonRelease-1>', self._on_gradient_stop_release)

    def _interpolate_gradient(self, frac):
        # Find which two stops frac is between
        stops = self._gradient_positions
        colors = self._gradient_colors
        if frac <= stops[0]:
            return colors[0]
        if frac >= stops[-1]:
            return colors[-1]
        for i in range(1, len(stops)):
            if frac < stops[i]:
                left, right = i-1, i
                break
        f = (frac - stops[left]) / (stops[right] - stops[left])
        c1 = colors[left].lstrip('#')
        c2 = colors[right].lstrip('#')
        r1,g1,b1 = int(c1[0:2],16),int(c1[2:4],16),int(c1[4:6],16)
        r2,g2,b2 = int(c2[0:2],16),int(c2[2:4],16),int(c2[4:6],16)
        r = int(r1 + (r2-r1)*f)
        g = int(g1 + (g2-g1)*f)
        b = int(b1 + (b2-b1)*f)
        return f'#{r:02X}{g:02X}{b:02X}'

    def _draw_gradient_hexes(self):
        frame = self.gradient_hex_frame
        for w in frame.winfo_children(): w.destroy()
        for idx, color in enumerate(self._gradient_colors):
            hex_lbl = tk.Label(frame, text=f"Color {idx+1}: {color}", font=(self.FONT_FAMILY, 11), bg=self.PRIMARY_BG, fg='#222', bd=0, padx=8, pady=2, cursor='hand2')
            hex_lbl.pack(side='left', padx=(0, 8))
            hex_lbl.bind('<Button-1>', lambda e, c=color: self._copy_to_clipboard_helper(c, f"{c} copied!"))

    def _on_gradient_stop_press(self, event):
        c = self.gradient_preview_canvas
        x = event.x
        w = int(c['width'])
        # Find which stop is closest
        idx = min(range(len(self._gradient_positions)), key=lambda i: abs(x - int(self._gradient_positions[i]*(w-1))))
        self._dragging_stop = idx
        self._drag_offset = x - int(self._gradient_positions[idx]*(w-1))

    def _on_gradient_stop_drag(self, event):
        if self._dragging_stop is None:
            return
        c = self.gradient_preview_canvas
        w = int(c['width'])
        # Use offset for smooth drag
        x = min(max(event.x - getattr(self, '_drag_offset', 0), 0), w-1)
        pos = x/(w-1)
        idx = self._dragging_stop
        n = len(self._gradient_positions)
        min_gap = 0.01
        # Keep stops in order, not overlapping
        if idx > 0:
            pos = max(pos, self._gradient_positions[idx-1]+min_gap)
        if idx < n-1:
            pos = min(pos, self._gradient_positions[idx+1]-min_gap)
        self._gradient_positions[idx] = pos
        self._draw_gradient_preview()
        self._draw_gradient_hexes()

    def _on_gradient_stop_release(self, event):
        self._dragging_stop = None
        self._drag_offset = 0

    def _copy_all_gradient_hex(self):
        hexes = ' '.join(self._gradient_colors)
        self._copy_to_clipboard_helper(hexes, "All HEX codes copied!")

    def _export_gradient_jpeg(self):
        try:
            from PIL import Image, ImageDraw
        except ImportError:
            import tkinter.messagebox as mb
            mb.showerror("Missing Dependency", "Pillow (PIL) is required to export JPEGs. Please install it via pip.")
            return
        w, h = 420, 44
        img = Image.new('RGB', (w, h), color='white')
        draw = ImageDraw.Draw(img)
        # Draw gradient
        for x in range(w):
            frac = x/(w-1)
            color = self._interpolate_gradient(frac)
            draw.line([(x,0),(x,h)], fill=color)
        # Save dialog
        from tkinter import filedialog as fd
        file = fd.asksaveasfilename(defaultextension='.jpeg', filetypes=[('JPEG Image', '*.jpeg'), ('JPG Image', '*.jpg')], title="Export Gradient as JPEG")
        if file:
            img.save(file, format='JPEG', quality=92)
    # --- Color Palette Constants (Your chosen palette) ---
    PRIMARY_BG = '#ffffff'
    SECONDARY_BG = '#b5baff'
    PALETTE_INDIGO = '#7B7EC5'  # New color added
    ACCENT_BLUE = '#cccfff'
    TEXT_LIGHT = '#000000'
    TEXT_MUTED = '#000000'
    INPUT_BG = '#FFFFFF'
    INPUT_FG = '#000000'
    WARNING_RED = '#b5baff'
    SUCCESS_GREEN = '#b5baff'

    # Hover Colors
    HOVER_PRIMARY_BG = '#FFDAAC'
    HOVER_ACCENT_BLUE = '#FFDAAC'
    HOVER_WARNING_RED = '#FFDAAC'

    STATUS_MESSAGE_DURATION_MS = 2500

    # --- Font Definitions ---
    FONT_FAMILY = "Montserrat"
    FONT_REGULAR = (FONT_FAMILY, 11)
    FONT_BOLD = (FONT_FAMILY, 11, "bold")
    FONT_TITLE = (FONT_FAMILY, 26, "bold")
    FONT_INPUT = (FONT_FAMILY, 12)
    FONT_STATS_COUNT = (FONT_FAMILY, 24, "bold")
    FONT_STATS_TEXT = (FONT_FAMILY, 11)
    
    # --- Unit Conversion Factors (Unchanged) ---
    LENGTH_CONVERSION_FACTORS = {
        'mm': 0.001, 'cm': 0.01, 'm': 1.0, 'km': 1000.0,
        'inch': 0.0254, 'ft': 0.3048, 'yd': 0.9144, 'mile': 1609.34
    }
    MASS_CONVERSION_FACTORS = {
        'mg': 0.001, 'g': 1.0, 'kg': 1000.0, 'oz': 28.3495, 'lb': 453.592
    }
    VOLUME_CONVERSION_FACTORS = {
        'ml': 0.001, 'L': 1.0, 'fl oz': 0.0295735, 'cup': 0.236588, 'gallon': 3.78541
    }
    UNITS_CATEGORIES = {
        "Length": sorted(list(LENGTH_CONVERSION_FACTORS.keys())),
        "Mass": sorted(list(MASS_CONVERSION_FACTORS.keys())),
        "Volume": sorted(list(VOLUME_CONVERSION_FACTORS.keys())),
        "Temperature": ['°C', '°F']
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Text Utilities & Converter")
        self.root.geometry("850x750")
        self.root.configure(bg=self.PRIMARY_BG)

        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
        self.root.minsize(750, 700) # Increased min height for new feature
        
        # --- Configure ttk Styles with new Fonts ---
        self.style = ttk.Style()
        self.style.theme_use('alt')

        self.style.configure('TFrame', background=self.PRIMARY_BG)
        self.style.configure('TLabel', background=self.PRIMARY_BG, foreground=self.TEXT_LIGHT, font=self.FONT_REGULAR)
        
        self.style.configure('Title.TLabel', font=self.FONT_TITLE)
        self.style.configure('InputLabel.TLabel', foreground=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12))
        self.style.configure('StatsCount.TLabel', foreground=self.TEXT_LIGHT, background=self.SECONDARY_BG, font=self.FONT_STATS_COUNT)
        self.style.configure('StatsText.TLabel', foreground=self.TEXT_MUTED, background=self.SECONDARY_BG, font=self.FONT_STATS_TEXT)

        self.style.configure('TNotebook', background=self.PRIMARY_BG, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.SECONDARY_BG, foreground=self.TEXT_MUTED, font=self.FONT_BOLD, padding=[20, 10])
        self.style.map('TNotebook.Tab',
                       background=[('selected', self.INPUT_BG)],
                       foreground=[('selected', self.TEXT_LIGHT)],
                       expand=[('selected', [1,1,1,0])])

        self.style.configure('TCombobox',
                             fieldbackground=self.INPUT_BG, 
                             foreground=self.INPUT_FG,      
                             selectbackground=self.ACCENT_BLUE,
                             selectforeground=self.TEXT_LIGHT,
                             background=self.SECONDARY_BG,
                             arrowcolor=self.INPUT_FG,
                             bordercolor=self.TEXT_MUTED, 
                             lightcolor=self.TEXT_MUTED,
                             darkcolor=self.TEXT_MUTED,
                             padding=[5, 5],
                             font=self.FONT_INPUT)
        
        self.root.option_add('*TCombobox*Listbox.background', self.INPUT_BG)      
        self.root.option_add('*TCombobox*Listbox.foreground', self.INPUT_FG)      
        self.root.option_add('*TCombobox*Listbox.selectBackground', self.ACCENT_BLUE)
        self.root.option_add('*TCombobox*Listbox.selectForeground', self.TEXT_LIGHT)
        self.root.option_add('*TCombobox*Listbox.font', self.FONT_REGULAR)

        self.style.configure('UnitLabel.TLabel', foreground=self.INPUT_FG, background=self.PRIMARY_BG, font=(self.FONT_FAMILY, 12))
        
        self.current_case_type = 'upper'
        self._button_hover_colors = {}
        
        # --- NEW: List to manage dynamic area calculator rows ---
        self.area_rows = []

        self.create_widgets()
        self.update_status("Ready.", self.TEXT_MUTED)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def _copy_to_clipboard(self, hex_code):
        self.root.clipboard_clear()
        self.root.clipboard_append(hex_code)
        self.root.update()  # Keeps clipboard after app closes

    def _hex_to_rgb(self, hex_code):
        hex_code = hex_code.lstrip('#')
        return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

    def _rgb_to_hex(self, rgb):
        return '#{:02X}{:02X}{:02X}'.format(*rgb)

    def _get_palette(self, base_hex):
        import colorsys
        base_rgb = self._hex_to_rgb(base_hex)
        r, g, b = [x/255.0 for x in base_rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        palettes = {}

        # Analogous: 6 colors, spaced by 30 deg (1/12), keep original logic
        def analogous_func(i):
            nh = (h + (i-2) * (1/12)) % 1.0  # 30 deg steps
            nl = l
            ns = s
            nr, ng, nb = colorsys.hls_to_rgb(nh, nl, ns)
            return self._rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
        palettes['Analogous'] = [analogous_func(i) for i in range(6)]

        # Monochromatic: 6 lightness steps, wide range for max variance
        def mono_func(i):
            nl = 0.12 + (i * (0.76/5))  # 0.12, 0.27, 0.42, 0.57, 0.72, 0.88
            nr, ng, nb = colorsys.hls_to_rgb(h, nl, s)
            return self._rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
        palettes['Monochromatic'] = [mono_func(i) for i in range(6)]

        # Shades: 6 steps, vary only saturation (gray to vivid), keep hue and lightness fixed
        def shade_func(i):
            ns = i / 5.0  # 0.0 (gray) to 1.0 (full color)
            nr, ng, nb = colorsys.hls_to_rgb(h, l, ns)
            return self._rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
        palettes['Shades'] = [shade_func(i) for i in range(6)]

        # Complementary: 3 base, 3 complement, add more variance (vary lightness and saturation for each)
        import random
        # 3 base, 3 complement, each with their own variance
        def comp_base(i):
            # Vary lightness and saturation for base
            nl = min(max(l + random.uniform(-0.18, 0.18), 0.12), 0.88)
            ns = min(max(s + random.uniform(-0.22, 0.22), 0.15), 1.0)
            nr, ng, nb = colorsys.hls_to_rgb(h, nl, ns)
            return self._rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
        def comp_complement(i):
            nhh = (h + 0.5) % 1.0
            nl = min(max(l + random.uniform(-0.18, 0.18), 0.12), 0.88)
            ns = min(max(s + random.uniform(-0.22, 0.22), 0.15), 1.0)
            nr, ng, nb = colorsys.hls_to_rgb(nhh, nl, ns)
            return self._rgb_to_hex((int(nr*255), int(ng*255), int(nb*255)))
        random.seed()
        palettes['Complementary'] = [comp_base(i) for i in range(3)] + [comp_complement(i) for i in range(3)]
        return palettes

    def _build_creative_tools_tab(self, notebook):

        # --- Make the Creative Tools tab scrollable (styled like Unit tab) ---
        creative_tab = tk.Frame(notebook, bg=self.PRIMARY_BG)
        notebook.add(creative_tab, text="Creative Tools")

        # Canvas for scrolling (fix: only scroll to fit content, not empty space)
        canvas = tk.Canvas(creative_tab, bg=self.PRIMARY_BG, highlightthickness=0, bd=0)
        canvas.grid(row=0, column=0, sticky='nsew')

        # Add a frame to hold the scrollbar, so we can add padding between scrollbar and content
        scrollbar_frame = tk.Frame(creative_tab, bg=self.PRIMARY_BG)
        scrollbar_frame.grid(row=0, column=1, sticky='ns', padx=(8, 0))

        # Custom themed scrollbar (reuse style from unit tab)
        style = ttk.Style()
        style.configure('Creative.Vertical.TScrollbar',
                        background=self.SECONDARY_BG,
                        troughcolor=self.PRIMARY_BG,
                        bordercolor=self.SECONDARY_BG,
                        arrowcolor=self.INPUT_FG,
                        relief='flat',
                        gripcount=0,
                        lightcolor=self.SECONDARY_BG,
                        darkcolor=self.SECONDARY_BG)
        vscroll = ttk.Scrollbar(scrollbar_frame, orient='vertical', style='Creative.Vertical.TScrollbar', command=canvas.yview)
        vscroll.pack(fill='y', expand=True)
        canvas.configure(yscrollcommand=vscroll.set)

        # Frame inside canvas for all widgets
        scrollable_frame = tk.Frame(canvas, bg=self.PRIMARY_BG)
        scrollable_frame_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Only scroll to fit content, not empty space
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

        # Enable mousewheel scrolling only when needed
        def _on_mousewheel(event):
            if canvas.bbox(scrollable_frame_id) and canvas.bbox(scrollable_frame_id)[3] > canvas.winfo_height():
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)

        creative_tab.grid_rowconfigure(0, weight=1)
        creative_tab.grid_columnconfigure(0, weight=1)

        # --- Title for Color Generator Section (styled like Gradient Generator) ---
        # --- Title for Color Generator (left-aligned, regular font, more breathing space) ---
        color_gen_title = tk.Label(scrollable_frame, text="Color Generator", font=(self.FONT_FAMILY, 11), bg=self.PRIMARY_BG, fg=self.INPUT_FG)
        color_gen_title.pack(anchor='w', pady=(28, 14), padx=(10,0))

        # ...existing code for color palettes...
        # (Separator line below color generator removed as requested)
        # Color Input
        color_input_label = tk.Label(scrollable_frame, text="HEX Color:", font=(self.FONT_FAMILY, 12), bg=self.PRIMARY_BG)
        color_input_label.pack(pady=(0, 6), padx=(90,0), anchor='w')
        self.creative_hex_var = tk.StringVar(value="#AABBCC")
        # --- Custom HEX color display with border ---
        # --- Aesthetic color border for HEX entry ---
        hex_border_frame = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        hex_border_frame.pack(pady=(0, 14), padx=(90,0), anchor='w')
        # Canvas for colored border
        border_canvas = tk.Canvas(hex_border_frame, width=112, height=36, highlightthickness=0, bg=self.PRIMARY_BG, bd=0)
        border_canvas.pack(side='left', padx=0, pady=0)
        # Place the entry on top of the canvas (absolute)
        color_input_entry = tk.Entry(hex_border_frame, textvariable=self.creative_hex_var, font=(self.FONT_FAMILY, 14), width=12, justify='center',
                                    relief='flat', bd=0, highlightthickness=0, bg=self.INPUT_BG, fg=self.INPUT_FG, exportselection=0,
                                    selectbackground=self.creative_hex_var.get() if len(self.creative_hex_var.get()) == 7 and self.creative_hex_var.get().startswith('#') else '#cccccc',
                                    selectforeground=self.INPUT_FG)
        color_input_entry.place(x=6, y=5, width=100, height=26)
        # Prevent auto-selection of text on tab open
        def prevent_auto_select(event):
            color_input_entry.selection_clear()
        color_input_entry.bind('<FocusIn>', prevent_auto_select, add='+')
        # Also clear selection after widget is created (in case of initial focus)
        color_input_entry.after(100, lambda: color_input_entry.selection_clear())
        # Dynamically update selection color when color changes
        def update_select_bg(*_):
            hex_code = self.creative_hex_var.get()
            sel_bg = hex_code if len(hex_code) == 7 and hex_code.startswith('#') else '#cccccc'
            try:
                color_input_entry.config(selectbackground=sel_bg)
            except Exception:
                pass
        self.creative_hex_var.trace_add('write', lambda *_: update_select_bg())
        update_select_bg()

        def update_hex_border(*_):
            border_canvas.delete('all')
            hex_code = self.creative_hex_var.get()
            # Use the selected color as the border
            border_color = hex_code if len(hex_code) == 7 and hex_code.startswith('#') else '#222'
            border_canvas.create_rectangle(2, 2, 110, 34, outline=border_color, width=2)
        self.creative_hex_var.trace_add('write', lambda *_: update_hex_border())
        update_hex_border()

        # Color Picker Row
        btn_row = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        btn_row.pack(pady=(0, 22), padx=(90,0), anchor='w')
        def pick_color(x=None, y=None):
            import colorsys
            from PIL import Image, ImageTk
            picker = tk.Toplevel(self.root)
            picker.title("Minimalist Color Picker")
            picker.configure(bg=self.PRIMARY_BG)
            picker.resizable(False, False)
            try:
                # Initial color
                initial_hex = self.creative_hex_var.get()
                rgb = [int(initial_hex[i:i+2], 16) for i in (1, 3, 5)] if initial_hex.startswith('#') and len(initial_hex) == 7 else [170, 187, 204]
                h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
                hue_var = tk.DoubleVar(value=h*360)
                hex_var = tk.StringVar(value=initial_hex.upper())
                area_size = 180
                left_margin = 20
                gradient_img = None
                gradient_tk = None
                color_area = tk.Label(picker, bd=2, relief='ridge', bg=self.PRIMARY_BG)
                color_area.place(x=left_margin, y=40, width=area_size, height=area_size)
                def make_gradient(hue):
                    from PIL import Image
                    img = Image.new('RGB', (area_size, area_size))
                    for y in range(area_size):
                        for x in range(area_size):
                            s = x / (area_size-1)
                            v = 1 - (y / (area_size-1))
                            r, g, b = colorsys.hsv_to_rgb(hue, s, v)
                            img.putpixel((x, y), (int(r*255), int(g*255), int(b*255)))
                    return img
                def update_gradient(*_):
                    nonlocal gradient_img, gradient_tk
                    hue = hue_var.get() / 360
                    gradient_img = make_gradient(hue)
                    from PIL import ImageTk
                    gradient_tk = ImageTk.PhotoImage(gradient_img)
                    color_area.config(image=gradient_tk)
                update_gradient()
                def area_pick(event):
                    x, y = event.x, event.y
                    if 0 <= x < area_size and 0 <= y < area_size:
                        s = x / (area_size-1)
                        v = 1 - (y / (area_size-1))
                        h = hue_var.get() / 360
                        r, g, b = colorsys.hsv_to_rgb(h, s, v)
                        hex_code = f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"
                        hex_var.set(hex_code)
                        preview.config(bg=hex_code)
                        self.creative_hex_var.set(hex_code)
                        generate_palettes()
                color_area.bind('<Button-1>', area_pick)
                color_area.bind('<B1-Motion>', area_pick)
                hue_slider_y = 210
                # Only use the original label (do not add a new one)
                hue_slider = tk.Scale(picker, from_=0, to=359, orient='horizontal', variable=hue_var, showvalue=True, length=area_size+10,
                                    bg=self.PRIMARY_BG, fg="#888", highlightthickness=0, troughcolor=self.SECONDARY_BG, bd=0, resolution=1)
                hue_slider.place(x=left_margin, y=hue_slider_y+10, width=area_size)
                hue_var.trace_add('write', lambda *_: update_gradient())
                hex_y = hue_slider_y + 60
                preview_size = 28
                preview = tk.Frame(picker, bg=hex_var.get(), width=preview_size, height=preview_size, bd=2, relief='ridge')
                preview.place(x=left_margin, y=hex_y)
                hex_label = tk.Label(picker, text="HEX", font=(self.FONT_FAMILY, 9, 'bold'), bg=self.PRIMARY_BG, fg="#888")
                hex_label.place(x=left_margin+50, y=hex_y+4)
                hex_entry = tk.Entry(picker, textvariable=hex_var, font=(self.FONT_FAMILY, 11), width=10, justify='center', bd=1, relief='solid', bg=self.INPUT_BG, fg=self.INPUT_FG)
                hex_entry.place(x=left_margin+85, y=hex_y, width=80, height=28)
                def update_from_hex(*_):
                    val = hex_var.get().strip()
                    if val.startswith('#') and len(val) == 7:
                        try:
                            r = int(val[1:3], 16)
                            g = int(val[3:5], 16)
                            b = int(val[5:7], 16)
                            preview.config(bg=val)
                            self.creative_hex_var.set(val.upper())
                            generate_palettes()
                        except Exception:
                            pass
                hex_var.trace_add('write', update_from_hex)
                picker.update_idletasks()
                window_width = area_size + 2*left_margin
                window_height = hex_y + 28 + 32
                picker.geometry(f"{window_width}x{window_height}")
                picker.minsize(window_width, window_height)
                picker.maxsize(window_width, window_height)
                preview.config(bg=hex_var.get())
                if x is not None and y is not None:
                    picker.geometry(f"{window_width}x{window_height}+{x}+{y}")
            except Exception as e:
                import traceback
                print("Error building color picker UI:", e)
                traceback.print_exc()
                error_label = tk.Label(picker, text="Error loading color picker", fg="red", bg=self.PRIMARY_BG)
                error_label.pack(expand=True, fill="both")
            else:
                # Always update and show the window, even on error
                picker.update_idletasks()
                picker.deiconify()
                picker.lift()
                picker.focus_force()
            hex_var.trace_add('write', update_from_hex)
            picker.update_idletasks()
            window_width = area_size + 2*left_margin
            window_height = hex_y + 28 + 32
            picker.geometry(f"{window_width}x{window_height}")
            picker.minsize(window_width, window_height)
            picker.maxsize(window_width, window_height)
            preview.config(bg=hex_var.get())
            if x is not None and y is not None:
                picker.geometry(f"{window_width}x{window_height}+{x}+{y}")
            return picker

            # Initial color
            initial_hex = self.creative_hex_var.get()
            rgb = [int(initial_hex[i:i+2], 16) for i in (1, 3, 5)] if initial_hex.startswith('#') and len(initial_hex) == 7 else [170, 187, 204]
            h, s, v = colorsys.rgb_to_hsv(rgb[0]/255, rgb[1]/255, rgb[2]/255)
            hue_var = tk.DoubleVar(value=h*360)
            hex_var = tk.StringVar(value=initial_hex.upper())

            # --- Color Gradient Area (fast, using PIL) ---
            area_size = 180
            gradient_img = None
            gradient_tk = None
            color_area = tk.Label(picker, bd=2, relief='ridge', bg=self.PRIMARY_BG)
            color_area.place(x=20, y=20, width=area_size, height=area_size)

            def make_gradient(hue):
                img = Image.new('RGB', (area_size, area_size))
                for y in range(area_size):
                    for x in range(area_size):
                        s = x / (area_size-1)
                        v = 1 - (y / (area_size-1))
                        r, g, b = colorsys.hsv_to_rgb(hue, s, v)
                        img.putpixel((x, y), (int(r*255), int(g*255), int(b*255)))
                return img

            def update_gradient(*_):
                nonlocal gradient_img, gradient_tk
                hue = hue_var.get() / 360
                gradient_img = make_gradient(hue)
                gradient_tk = ImageTk.PhotoImage(gradient_img)
                color_area.config(image=gradient_tk)

            update_gradient()

            # --- Color Area Mouse Events ---
            def area_pick(event):
                x, y = event.x, event.y
                if 0 <= x < area_size and 0 <= y < area_size:
                    s = x / (area_size-1)
                    v = 1 - (y / (area_size-1))
                    h = hue_var.get() / 360
                    r, g, b = colorsys.hsv_to_rgb(h, s, v)
                    hex_code = f"#{int(r*255):02X}{int(g*255):02X}{int(b*255):02X}"
                    hex_var.set(hex_code)
                    preview.config(bg=hex_code)
                    self.creative_hex_var.set(hex_code)
                    generate_palettes()

            color_area.bind('<Button-1>', area_pick)
            color_area.bind('<B1-Motion>', area_pick)

            # --- Hue Slider (fits window tightly below gradient) ---
            hue_slider_y = 210
            # (Hue label removed for minimalist look)
            hue_slider = tk.Scale(picker, from_=0, to=359, orient='horizontal', variable=hue_var, showvalue=True, length=area_size+10,
                                bg=self.PRIMARY_BG, fg="#888", highlightthickness=0, troughcolor=self.SECONDARY_BG, bd=0, resolution=1)
            # Add extra space between gradient and slider
            hue_slider.place(x=20, y=hue_slider_y+25, width=area_size)
            hue_var.trace_add('write', lambda *_: update_gradient())

            # --- Add space below the slider before HEX and preview ---
            hex_y = hue_slider_y + 60  # add more space below slider
            # Add left margin for preview and hex code
            left_margin = 20
            # Make preview box a small square, aligned with hex entry
            preview_size = 28
            preview = tk.Frame(picker, bg=hex_var.get(), width=preview_size, height=preview_size, bd=2, relief='ridge')
            preview.place(x=left_margin, y=hex_y)

            hex_label = tk.Label(picker, text="HEX", font=(self.FONT_FAMILY, 9, 'bold'), bg=self.PRIMARY_BG, fg="#888")
            hex_label.place(x=left_margin+50, y=hex_y+4)
            hex_entry = tk.Entry(picker, textvariable=hex_var, font=(self.FONT_FAMILY, 11), width=10, justify='center', bd=1, relief='solid', bg=self.INPUT_BG, fg=self.INPUT_FG)
            hex_entry.place(x=left_margin+85, y=hex_y, width=80, height=28)

            def update_from_hex(*_):
                val = hex_var.get().strip()
                if val.startswith('#') and len(val) == 7:
                    try:
                        r = int(val[1:3], 16)
                        g = int(val[3:5], 16)
                        b = int(val[5:7], 16)
                        preview.config(bg=val)
                        self.creative_hex_var.set(val.upper())
                        generate_palettes()
                    except Exception:
                        pass
            hex_var.trace_add('write', update_from_hex)

            # --- OK Button ---
            # Place OK button centered below hex/preview, with extra bottom margin and modern pastel gradient look
            # Add extra space below hex/preview for a clean look (no OK button)
            picker.update_idletasks()
            window_width = area_size + 2*left_margin
            window_height = hex_y + 28 + 32  # 28 for hex/preview, 32 for extra space
            picker.geometry(f"{window_width}x{window_height}")
            picker.minsize(window_width, window_height)
            picker.maxsize(window_width, window_height)

            # Resize window to fit all content with bottom padding (ensure OK button fits)
            picker.update_idletasks()
            window_width = max(area_size + 2*left_margin, btn_x + btn_width + left_margin)
            window_height = ok_y + 60
            picker.geometry(f"{window_width}x{window_height}")
            picker.minsize(window_width, window_height)
            picker.maxsize(window_width, window_height)

            # Initial preview
            preview.config(bg=hex_var.get())
        # Only keep the palette icon and add text beside it
        def open_picker_beside_icon(event=None):
            # Get the position of the pick_btn relative to the root window
            self.root.update_idletasks()  # Ensure geometry is up to date
            btn_x = pick_btn.winfo_rootx()
            btn_y = pick_btn.winfo_rooty() + pick_btn.winfo_height()
            # Use the placement you specified
            offset_x = -360  # move right (your value)
            offset_y = 320   # move up (your value)
            pick_color(x=btn_x + offset_x, y=btn_y - offset_y)

        pick_btn = tk.Button(
            btn_row, text="🎨", command=open_picker_beside_icon,
            font=(self.FONT_FAMILY, 14), fg='black', bg=self.INPUT_BG,
            relief='flat', bd=0, cursor='hand2', width=3
        )
        pick_btn.pack(side='left', padx=(0, 1))
        color_picker_label = tk.Label(
            btn_row, text="Color Picker", font=(self.FONT_FAMILY, 12, 'bold'),
            bg=self.PRIMARY_BG, fg=self.INPUT_FG, padx=2
        )
        color_picker_label.pack(side='left', padx=(0, 4))

        # Generate Button
        def export_palette_to_jpeg(colors, palette_name):
            try:
                from PIL import Image, ImageDraw, ImageFont
            except ImportError:
                import tkinter.messagebox as mb
                mb.showerror("Missing Dependency", "Pillow (PIL) is required to export JPEGs. Please install it via pip.")
                return
            # --- MANUAL SETTINGS FOR EXPORT ---
            swatch_width = 250  # width of each color swatch (manual)
            swatch_height = 350  # height of each color swatch (manual)
            hex_h = 40  # height of white area for hex text (manual)
            hex_font_size = 80  # <--- MANUALLY ADJUST THIS FOR TEXT SIZE
            hex_font_name = "Montserrat-Bold.ttf"  # or change to any .ttf you want
            n = len(colors)
            img_width = swatch_width * n
            img_height = swatch_height + hex_h
            img = Image.new('RGB', (img_width, img_height), color='#fff')
            draw = ImageDraw.Draw(img)
            try:
                font = ImageFont.truetype(hex_font_name, hex_font_size)
            except Exception:
                font = ImageFont.load_default()

            for i, color in enumerate(colors):
                x0 = i * swatch_width
                x1 = x0 + swatch_width
                draw.rectangle([x0, 0, x1, swatch_height], fill=color)
                hex_text = color.upper()
                # Center text in the white area
                try:
                    bbox = draw.textbbox((0, 0), hex_text, font=font)
                    text_w = bbox[2] - bbox[0]
                    text_h = bbox[3] - bbox[1]
                except Exception:
                    text_w, text_h = draw.textsize(hex_text, font=font)
                text_x = x0 + (swatch_width - text_w) // 2
                text_y = swatch_height + (hex_h - text_h) // 2
                draw.text((text_x, text_y), hex_text, fill='#000', font=font)
            import tkinter.filedialog as fd
            import os
            filetypes = [("JPEG Image", "*.jpeg"), ("JPG Image", "*.jpg")]
            base_name = f"{palette_name}_palette"
            ext = ".jpeg"
            # Do not set initialdir, let Tkinter remember last used directory
            import os
            # Try to use the last used directory, fallback to Downloads
            import sys
            if sys.platform.startswith('win'):
                downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            elif sys.platform.startswith('darwin'):
                downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            else:
                downloads_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            last_dir = getattr(self, '_last_palette_export_dir', downloads_dir)
            base_name = f"{palette_name}_palette"
            ext = ".jpeg"
            # Fast scan for all matching files in the directory
            try:
                files = os.listdir(last_dir)
            except Exception:
                files = []
            import re
            pattern = re.compile(rf"{re.escape(base_name)}(?: (\d+))?{re.escape(ext)}$")
            max_num = 0
            for f in files:
                m = pattern.match(f)
                if m:
                    num = m.group(1)
                    if num:
                        max_num = max(max_num, int(num))
                    else:
                        max_num = max(max_num, 1)
            next_num = max_num + 1 if max_num else 1
            candidate_name = f"{base_name} {next_num}{ext}"
            # Open save dialog with the next available name
            filename = fd.asksaveasfilename(defaultextension=ext, filetypes=filetypes, initialfile=candidate_name, initialdir=last_dir, title="Export Palette as JPEG")
            if filename:
                # Save the directory for next time
                self._last_palette_export_dir = os.path.dirname(filename)
                img.save(filename, format='JPEG', quality=92)

        def generate_palettes():
            hex_code = self.creative_hex_var.get().strip()
            if not hex_code.startswith('#') or len(hex_code) != 7:
                return  # Optionally show error
            palettes = self._get_palette(hex_code)
            for section in palette_sections.values():
                for widget in section.winfo_children():
                    widget.destroy()
            for name, colors in palettes.items():
                section = palette_sections[name]
                # ...existing code for swatches and hex labels...
                # Do NOT create export buttons here! Only in _build_creative_tools_tab
                # Use a grid: 2 rows (swatch, hex), 6 columns
                for i, c in enumerate(colors):
                    swatch = tk.Frame(section, bg=c, width=64, height=64, bd=2, relief='ridge', cursor='hand2')
                    swatch.grid(row=0, column=i, padx=8, pady=(4,2))
                    def on_palette_pick(hexval):
                        def handler(e):
                            self.creative_hex_var.set(hexval)
                        return handler
                    swatch.bind('<Button-1>', on_palette_pick(c))
                    # --- Modern Copy Clipboard Hover Effect for Hex Label ---
                    def copy_hex(hexval, label):
                        self._copy_to_clipboard(hexval)
                        orig_text = label.cget('text')
                        orig_bg = label.cget('bg')
                        orig_fg = label.cget('fg')
                        label.config(text='✔ Copied!', fg='#222', bg='#eaffc2')
                        label.after(900, lambda: label.config(text=orig_text, fg=orig_fg, bg=orig_bg))
                    def on_hex_hover(e, label):
                        label.config(bg=self.ACCENT_BLUE, fg='#222', cursor='hand2')
                    def on_hex_leave(e, label, orig_bg, orig_fg):
                        label.config(bg=orig_bg, fg=orig_fg, cursor='arrow')
                    hex_label = tk.Label(section, text=c, font=(self.FONT_FAMILY, 11), bg=self.PRIMARY_BG, fg='#000', bd=0, padx=8, pady=2)
                    hex_label.grid(row=1, column=i, padx=8, pady=(0,6))
                    hex_label.bind('<Button-1>', lambda e, hexval=c, label=hex_label: copy_hex(hexval, label))
                    hex_label.bind('<Enter>', lambda e, label=hex_label: on_hex_hover(e, label))
                    hex_label.bind('<Leave>', lambda e, label=hex_label: on_hex_leave(e, label, self.PRIMARY_BG, '#222'))
                # Make columns expand equally
                for i in range(6):
                    section.grid_columnconfigure(i, weight=1)

        # Make palette generation live as well
        self.creative_hex_var.trace_add('write', lambda *_: generate_palettes())


        # Palette Output Sections
        palette_sections = {}
        # Use a grid for the title row to align all export controls vertically
        for pname in ["Analogous", "Monochromatic", "Shades", "Complementary"]:
            title_row = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
            title_row.pack(pady=(10, 0), padx=(90,0), anchor='w', fill='x')
            # Use grid for alignment
            title_row.grid_columnconfigure(0, weight=0)
            title_row.grid_columnconfigure(1, weight=1)
            title_row.grid_columnconfigure(2, weight=0)
            section_label = tk.Label(title_row, text=pname, font=(self.FONT_FAMILY, 11, 'bold'), bg=self.PRIMARY_BG)
            section_label.grid(row=0, column=0, sticky='w')
            # Spacer to push export to the right, but keep all export controls in the same vertical space
            spacer = tk.Frame(title_row, width=40, bg=self.PRIMARY_BG)  # Set to 40px for user-specified spacing
            spacer.grid(row=0, column=1, sticky='ew')
            from functools import partial
            def export_handler(palette_name, event=None):
                hex_code = self.creative_hex_var.get().strip()
                if not hex_code.startswith('#') or len(hex_code) != 7:
                    return
                palettes = self._get_palette(hex_code)
                colors = palettes.get(palette_name)
                if colors:
                    export_palette_to_jpeg(colors, palette_name)
            export_frame = tk.Frame(title_row, bg=self.PRIMARY_BG)
            export_text = tk.Label(export_frame, text='Export as JPEG', font=(self.FONT_FAMILY, 9), bg=self.PRIMARY_BG, fg=self.PALETTE_INDIGO, cursor='hand2')
            export_text.pack(side='left', padx=(0, 0))
            export_frame.grid(row=0, column=2, sticky='e', pady=(2,0))
            export_frame.bind('<Button-1>', partial(export_handler, pname))
            export_text.bind('<Button-1>', partial(export_handler, pname))
            section = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
            section.pack(fill='x', pady=(0, 16), padx=(90,0))
            palette_sections[pname] = section

        # --- Section Separator (horizontal line) just above the Gradient Generator title ---
        sep = tk.Frame(scrollable_frame, bg='#E0E0E0', height=2)  # Gray separator for modern look
        sep.pack(fill='x', padx=10, pady=(10, 24))

        # --- Export to PNG logic: horizontal swatches, hex below, no extra spacing ---
        from PIL import Image, ImageDraw, ImageFont
        def export_palette_to_png(palette_name, colors):
            swatch_w, swatch_h = 120, 240  # Large, modern look
            hex_h = 38
            n = len(colors)
            width = swatch_w * n
            height = swatch_h + hex_h
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            # Try to use Montserrat, fallback to default
            try:
                font = ImageFont.truetype("Montserrat-Regular.ttf", 24)
            except Exception:
                font = ImageFont.load_default()
            for i, c in enumerate(colors):
                x0 = i * swatch_w
                draw.rectangle([x0, 0, x0+swatch_w, swatch_h], fill=c)
                # Draw hex code centered below
                hex_text = c.upper()
                text_w, text_h = draw.textsize(hex_text, font=font)
                tx = x0 + (swatch_w - text_w) // 2
                ty = swatch_h + (hex_h - text_h) // 2
                draw.text((tx, ty), hex_text, fill='#222', font=font)
            # Save dialog
            import tkinter.filedialog as fd
            file = fd.asksaveasfilename(
                defaultextension='.png',
                filetypes=[('PNG Image', '*.png')],
                title=f"Export {palette_name} Palette as PNG"
            )
            if file:
                img.save(file)
        # --- Add small Export as JPEG text (no icon) next to each palette title ---
        for pname in ["Analogous", "Monochromatic", "Shades", "Complementary"]:
            section_label = None
            for widget in palette_sections[pname].master.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget('text') == pname:
                    section_label = widget
                    break
            if section_label and not hasattr(section_label, '_has_export_icon'):
                def make_export_handler(palette_name):
                    def export_handler(event=None):
                        hex_code = self.creative_hex_var.get().strip()
                        if not hex_code.startswith('#') or len(hex_code) != 7:
                            return
                        palettes_now = self._get_palette(hex_code)
                        colors_now = palettes_now.get(palette_name)
                        if colors_now:
                            export_palette_to_jpeg(colors_now, palette_name)
                    return export_handler
                export_handler = make_export_handler(pname)
                export_frame = tk.Frame(section_label.master, bg=self.PRIMARY_BG)
                export_text = tk.Label(export_frame, text='Export as JPEG', font=(self.FONT_FAMILY, 9), bg=self.PRIMARY_BG, fg=self.PALETTE_INDIGO)
                export_text.pack(side='left')
                def on_enter(e):
                    export_frame.config(bg=self.ACCENT_BLUE)
                    export_text.config(bg=self.ACCENT_BLUE)
                def on_leave(e):
                    export_frame.config(bg=self.PRIMARY_BG)
                    export_text.config(bg=self.PRIMARY_BG)
                export_frame.bind('<Button-1>', export_handler)
                export_text.bind('<Button-1>', export_handler)
                export_frame.bind('<Enter>', on_enter)
                export_frame.bind('<Leave>', on_leave)
                export_text.bind('<Enter>', on_enter)
                export_text.bind('<Leave>', on_leave)
                export_frame.place(x=section_label.winfo_x() + section_label.winfo_reqwidth() + 10, y=section_label.winfo_y() + 1)
                section_label._has_export_icon = True

        # Initial palette
        generate_palettes()

        # --- Gradient Generator Section ---
        self._build_gradient_generator_section(scrollable_frame)

    def create_widgets(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=30, pady=(20, 6))  # Less space below tabs

        self.text_tools_frame = tk.Frame(self.notebook, bg=self.PRIMARY_BG)
        self.notebook.add(self.text_tools_frame, text="Text Tools")
        self._create_text_tools_widgets(self.text_tools_frame)

        self.unit_converter_frame = tk.Frame(self.notebook, bg=self.PRIMARY_BG)
        self.notebook.add(self.unit_converter_frame, text="Calculation Tools")
        self._create_unit_converter_widgets(self.unit_converter_frame)

        # Add Creative Tools Tab
        self._build_creative_tools_tab(self.notebook)

        self.status_label = tk.Label(self.root, text="Ready.",
                                     bg=self.SECONDARY_BG, fg=self.TEXT_MUTED,
                                     font=(self.FONT_FAMILY, 10), anchor='w', padx=20, pady=8)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

        self.bind_hover_effects()

    def _create_text_tools_widgets(self, parent_frame):
        # This function remains unchanged
        parent_frame.grid_columnconfigure(0, weight=1)
        parent_frame.grid_rowconfigure(2, weight=1)
        parent_frame.grid_rowconfigure(5, weight=1)

        title_label = ttk.Label(parent_frame, text="Text Case & Utilities:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 12, 'normal'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(10, 18), sticky='w', padx=(2,0))

        input_label = ttk.Label(parent_frame, text="Enter your text:", style='InputLabel.TLabel')
        input_label.grid(row=1, column=0, columnspan=4, sticky='w', pady=(0, 10))

        self.input_text = scrolledtext.ScrolledText(parent_frame,
                                                   height=8, wrap=tk.WORD,
                                                   font=self.FONT_INPUT,
                                                   bg=self.PRIMARY_BG, fg=self.INPUT_FG,
                                                   insertbackground=self.ACCENT_BLUE,
                                                   padx=0, pady=0, relief='solid', bd=1,
                                                   highlightbackground=self.SECONDARY_BG,
                                                   highlightcolor=self.SECONDARY_BG,
                                                   highlightthickness=1)
        self.input_text.grid(row=2, column=0, columnspan=4, sticky='nsew', pady=(0, 30))
        self.input_text.bind('<KeyRelease>', self.on_text_change)

        def create_styled_button(parent, text, command, bg_color, hover_color, row, col, columnspan=1):
            btn = tk.Button(parent, text=text, command=command,
                            bg=bg_color, fg=self.TEXT_LIGHT,
                            font=self.FONT_BOLD,
                            relief='flat', padx=5, pady=12,
                            cursor='hand2', bd=0,
                            activebackground=hover_color,
                            activeforeground=self.TEXT_LIGHT)
            btn.grid(row=row, column=col, columnspan=columnspan, padx=1, sticky='ew')
            self._button_hover_colors[btn] = {'original': bg_color, 'hover': hover_color}
            return btn

        case_buttons_frame = tk.Frame(parent_frame, bg=self.SECONDARY_BG, relief='flat', bd=0)
        case_buttons_frame.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(0, 30))
        for i in range(5): case_buttons_frame.grid_columnconfigure(i, weight=1)

        self.upper_btn = create_styled_button(case_buttons_frame, "UPPERCASE", lambda: self.set_case_type('upper'), self.SECONDARY_BG, self.HOVER_PRIMARY_BG, 0, 0)
        self.lower_btn = create_styled_button(case_buttons_frame, "lowercase", lambda: self.set_case_type('lower'), self.SECONDARY_BG, self.HOVER_PRIMARY_BG, 0, 1)
        self.title_btn = create_styled_button(case_buttons_frame, "Title Case", lambda: self.set_case_type('title'), self.SECONDARY_BG, self.HOVER_PRIMARY_BG, 0, 2)
        self.sentence_case_btn = create_styled_button(case_buttons_frame, "Sentence Case", lambda: self.set_case_type('sentence'), self.SECONDARY_BG, self.HOVER_PRIMARY_BG, 0, 3)
        self.clear_btn = create_styled_button(case_buttons_frame, "Clear All", self.clear_text, self.WARNING_RED, self.HOVER_WARNING_RED, 0, 4)

        output_label = ttk.Label(parent_frame, text="Result:", style='InputLabel.TLabel')
        output_label.grid(row=4, column=0, columnspan=4, sticky='w', pady=(0, 10))

        self.output_text = scrolledtext.ScrolledText(parent_frame,
                                                    height=8, wrap=tk.WORD,
                                                    font=self.FONT_INPUT,
                                                    bg=self.PRIMARY_BG, fg=self.INPUT_FG, state='disabled',
                                                    padx=0, pady=0, relief='solid', bd=1,
                                                    highlightbackground=self.SECONDARY_BG,
                                                    highlightcolor=self.SECONDARY_BG,
                                                    highlightthickness=1)
        self.output_text.grid(row=5, column=0, columnspan=4, sticky='nsew', pady=(0, 30))

        self.copy_btn = tk.Button(parent_frame, text="📋 Copy to Clipboard", command=self.copy_to_clipboard,
                                  bg=self.ACCENT_BLUE, fg=self.TEXT_LIGHT, font=self.FONT_BOLD,
                                  relief='flat', padx=20, pady=15, cursor='hand2', bd=0,
                                  activebackground=self.HOVER_ACCENT_BLUE,
                                  activeforeground=self.TEXT_LIGHT)
        self.copy_btn.grid(row=6, column=0, columnspan=4, sticky='ew')
        self._button_hover_colors[self.copy_btn] = {'original': self.ACCENT_BLUE, 'hover': self.HOVER_ACCENT_BLUE}

        stats_frame = tk.Frame(parent_frame, bg=self.SECONDARY_BG, relief='flat', bd=0,
                               highlightbackground=self.ACCENT_BLUE, highlightthickness=1)
        stats_frame.grid(row=7, column=0, columnspan=4, sticky='ew', pady=(20, 0))
        for i in range(3): stats_frame.grid_columnconfigure(i, weight=1)

        self.char_count_label = ttk.Label(stats_frame, text="0", style='StatsCount.TLabel')
        self.char_count_label.grid(row=0, column=0, pady=(15, 0))
        ttk.Label(stats_frame, text="Characters", style='StatsText.TLabel').grid(row=1, column=0, pady=(0, 15))

        self.word_count_label = ttk.Label(stats_frame, text="0", style='StatsCount.TLabel')
        self.word_count_label.grid(row=0, column=1, pady=(15, 0))
        ttk.Label(stats_frame, text="Words", style='StatsText.TLabel').grid(row=1, column=1, pady=(0, 15))

        self.line_count_label = ttk.Label(stats_frame, text="0", style='StatsCount.TLabel')
        self.line_count_label.grid(row=0, column=2, pady=(15, 0))
        ttk.Label(stats_frame, text="Lines", style='StatsText.TLabel').grid(row=1, column=2, pady=(0, 15))

    def _create_unit_converter_widgets(self, parent_frame):
        # --- Make the Unit Converter tab scrollable ---
        parent_frame.grid_rowconfigure(0, weight=1)
        parent_frame.grid_columnconfigure(0, weight=1)


        # Canvas for scrolling
        canvas = tk.Canvas(parent_frame, bg=self.PRIMARY_BG, highlightthickness=0, bd=0)
        canvas.grid(row=0, column=0, sticky='nsew')

        # Add a frame to hold the scrollbar, so we can add padding between scrollbar and content
        scrollbar_frame = tk.Frame(parent_frame, bg=self.PRIMARY_BG)
        scrollbar_frame.grid(row=0, column=1, sticky='ns', padx=(8, 0))  # 8px space between content and scrollbar

        # Custom themed scrollbar
        style = ttk.Style()
        style.configure('Custom.Vertical.TScrollbar',
                        background=self.SECONDARY_BG,
                        troughcolor=self.PRIMARY_BG,
                        bordercolor=self.SECONDARY_BG,
                        arrowcolor=self.INPUT_FG,
                        relief='flat',
                        gripcount=0,
                        lightcolor=self.SECONDARY_BG,
                        darkcolor=self.SECONDARY_BG)
        vscroll = ttk.Scrollbar(scrollbar_frame, orient='vertical', style='Custom.Vertical.TScrollbar', command=canvas.yview)
        vscroll.pack(fill='y', expand=True)
        canvas.configure(yscrollcommand=vscroll.set)

        # Frame inside canvas for all widgets
        scrollable_frame = tk.Frame(canvas, bg=self.PRIMARY_BG)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        scrollable_frame.bind_all("<MouseWheel>", _on_mousewheel)

        # --- All widgets go into scrollable_frame instead of parent_frame ---
        scrollable_frame.grid_columnconfigure(1, weight=1)
        scrollable_frame.grid_columnconfigure(3, weight=0)

        title_label = ttk.Label(scrollable_frame, text="Unit Conversion:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 12, 'normal'))
        title_label.grid(row=0, column=0, columnspan=4, pady=(10, 18), sticky='w', padx=(2,0))

        # --- General Unit Converter Section ---
        ttk.Label(scrollable_frame, text="From:", style='UnitLabel.TLabel').grid(row=1, column=0, sticky='w', padx=10, pady=10)
        self.unit_input_var = tk.StringVar(value="1.00")
        self.unit_input_entry = tk.Entry(scrollable_frame, textvariable=self.unit_input_var, font=self.FONT_INPUT, justify='right',
                                         bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1,
                                         highlightthickness=1, highlightbackground=self.TEXT_MUTED,
                                         highlightcolor=self.ACCENT_BLUE, insertbackground=self.INPUT_FG)
        self.unit_input_entry.grid(row=1, column=1, padx=5, pady=10, sticky='ew')
        self.unit_input_entry.bind('<KeyRelease>', lambda e: self._perform_unit_conversion())

        self.from_unit_var = tk.StringVar()
        self.from_unit_combobox = ttk.Combobox(scrollable_frame, textvariable=self.from_unit_var, state='readonly', font=self.FONT_INPUT, style='TCombobox')
        # Populate with all units from all categories
        all_units = sorted([u for sublist in self.UNITS_CATEGORIES.values() for u in sublist])
        self.from_unit_combobox['values'] = all_units
        self.from_unit_combobox.grid(row=1, column=2, padx=5, pady=10, sticky='ew')
        self.from_unit_combobox.bind('<<ComboboxSelected>>', lambda e: self._perform_unit_conversion())
        if 'm' in all_units: self.from_unit_var.set('m')

        swap_button = tk.Button(scrollable_frame, text="⇄", command=self._swap_units, bg=self.PRIMARY_BG, fg=self.INPUT_FG, font=(self.FONT_FAMILY, 12),
                                relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                activeforeground=self.HOVER_ACCENT_BLUE)
        swap_button.grid(row=1, column=3, padx=(5,0), sticky='w')
        self._button_hover_colors[swap_button] = {'original': self.INPUT_FG, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}

        ttk.Label(scrollable_frame, text="To:", style='UnitLabel.TLabel').grid(row=2, column=0, sticky='w', padx=10, pady=10)
        self.unit_result_var = tk.StringVar(value="0.00")
        self.unit_result_label = tk.Entry(scrollable_frame, textvariable=self.unit_result_var, font=self.FONT_INPUT, justify='right',
                                          disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                                          relief='solid', bd=1, state='disabled')
        self.unit_result_label.grid(row=2, column=1, padx=5, pady=10, sticky='ew')

        self.to_unit_var = tk.StringVar()
        self.to_unit_combobox = ttk.Combobox(scrollable_frame, textvariable=self.to_unit_var, state='readonly', font=self.FONT_INPUT, style='TCombobox')
        self.to_unit_combobox['values'] = all_units
        self.to_unit_combobox.grid(row=2, column=2, padx=5, pady=10, sticky='ew')
        self.to_unit_combobox.bind('<<ComboboxSelected>>', lambda e: self._perform_unit_conversion())
        if 'cm' in all_units: self.to_unit_var.set('cm')

        unit_copy_btn = tk.Button(scrollable_frame, text="📋", command=self._copy_unit_result, bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                                  relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                  activeforeground=self.HOVER_ACCENT_BLUE)
        unit_copy_btn.grid(row=2, column=3, padx=(5,0), sticky='w')
        self._button_hover_colors[unit_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}

        # --- Separator ---
        separator1 = ttk.Separator(scrollable_frame, orient='horizontal')
        separator1.grid(row=3, column=0, columnspan=4, sticky='ew', pady=20)

        # --- Height Converter ---
        ttk.Label(scrollable_frame, text="Height (ft/in → cm):", style='UnitLabel.TLabel').grid(row=4, column=0, sticky='w', padx=10, pady=10)

        height_frame = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        height_frame.grid(row=4, column=1, padx=5, pady=10, sticky='ew')

        self.feet_var = tk.StringVar()
        feet_entry = tk.Entry(height_frame, textvariable=self.feet_var, font=self.FONT_INPUT, width=5, justify='right',
                              bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
        feet_entry.pack(side=tk.LEFT)
        ttk.Label(height_frame, text="'", style='UnitLabel.TLabel').pack(side=tk.LEFT, padx=(2,10))

        self.inches_var = tk.StringVar()
        inches_entry = tk.Entry(height_frame, textvariable=self.inches_var, font=self.FONT_INPUT, width=5, justify='right',
                                bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
        inches_entry.pack(side=tk.LEFT)
        ttk.Label(height_frame, text='"', style='UnitLabel.TLabel').pack(side=tk.LEFT, padx=(2,0))

        self.height_cm_var = tk.StringVar()
        height_result_entry = tk.Entry(scrollable_frame, textvariable=self.height_cm_var, font=self.FONT_INPUT, justify='right',
                                       disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                                       relief='solid', bd=1, state='disabled')
        height_result_entry.grid(row=4, column=2, padx=5, pady=10, sticky='ew')

        height_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: self._copy_quick_result(self.height_cm_var), bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                                    relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                    activeforeground=self.HOVER_ACCENT_BLUE)
        height_copy_btn.grid(row=4, column=3, padx=(5,0), sticky='w')
        self._button_hover_colors[height_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}

        self.feet_var.trace_add("write", self._convert_height)
        self.inches_var.trace_add("write", self._convert_height)

        # --- Weight Converter ---
        weight_label = ttk.Label(scrollable_frame, text="Weight (lb → kg):", style='UnitLabel.TLabel')
        weight_label.grid(row=5, column=0, sticky='w', padx=10, pady=10)
        weight_frame = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        weight_frame.grid(row=5, column=1, padx=5, pady=10, sticky='ew')
        self.lbs_var = tk.StringVar()
        lbs_entry = tk.Entry(weight_frame, textvariable=self.lbs_var, font=self.FONT_INPUT, justify='right',
                             bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
        lbs_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        weight_unit_label = ttk.Label(weight_frame, text="lb", style='UnitLabel.TLabel')
        weight_unit_label.pack(side=tk.LEFT, padx=(5,0))
        self.weight_kg_var = tk.StringVar()
        weight_result_entry = tk.Entry(scrollable_frame, textvariable=self.weight_kg_var, font=self.FONT_INPUT, justify='right',
                                       disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                                       relief='solid', bd=1, state='disabled')
        weight_result_entry.grid(row=5, column=2, padx=5, pady=10, sticky='ew')
        weight_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: self._copy_quick_result(self.weight_kg_var), bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                                    relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                    activeforeground=self.HOVER_ACCENT_BLUE)
        weight_copy_btn.grid(row=5, column=3, padx=(5, 0), sticky='w')
        self._button_hover_colors[weight_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        def switch_weight():
            if getattr(self, '_weight_switch_state', 'lb_to_kg') == 'lb_to_kg':
                self._weight_switch_state = 'kg_to_lb'
                weight_label.config(text="Weight (kg → lb):")
                weight_unit_label.config(text="kg")
                self.weight_kg_var.set("")
                self.lbs_var.set("")
            else:
                self._weight_switch_state = 'lb_to_kg'
                weight_label.config(text="Weight (lb → kg):")
                weight_unit_label.config(text="lb")
                self.weight_kg_var.set("")
                self.lbs_var.set("")
            self._convert_weight()
        switch_btn = tk.Button(scrollable_frame, text="⇄", command=switch_weight, bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 11),
                               relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                               activeforeground=self.HOVER_ACCENT_BLUE, width=2)
        switch_btn.grid(row=5, column=4, padx=(5, 0), sticky='w')
        self._button_hover_colors[switch_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        self.lbs_var.trace_add("write", self._convert_weight)

        # --- Distance Converter (mile ↔ km) ---
        distance_label = ttk.Label(scrollable_frame, text="Distance (mile → km):", style='UnitLabel.TLabel')
        distance_label.grid(row=6, column=0, sticky='w', padx=10, pady=10)
        self._distance_switch_state = 'mile_to_km'
        self.mile_var = tk.StringVar()
        self.km_var = tk.StringVar()
        self.mile_entry = tk.Entry(scrollable_frame, textvariable=self.mile_var, font=self.FONT_INPUT, justify='right',
                                  bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
        self.mile_entry.grid(row=6, column=1, padx=5, pady=10, sticky='ew')
        self.km_entry = tk.Entry(scrollable_frame, textvariable=self.km_var, font=self.FONT_INPUT, justify='right',
                                disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                                relief='solid', bd=1, state='disabled')
        self.km_entry.grid(row=6, column=2, padx=5, pady=10, sticky='ew')
        km_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: self._copy_quick_result(self.km_var), bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                               relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                               activeforeground=self.HOVER_ACCENT_BLUE)
        km_copy_btn.grid(row=6, column=3, padx=(5,0), sticky='w')
        self._button_hover_colors[km_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        def switch_distance():
            if self._distance_switch_state == 'mile_to_km':
                self._distance_switch_state = 'km_to_mile'
                distance_label.config(text="Distance (km → mile):")
            else:
                self._distance_switch_state = 'mile_to_km'
                distance_label.config(text="Distance (mile → km):")
            self.mile_var.set("")
            self.km_var.set("")
            self.mile_entry.config(state='normal', bg=self.INPUT_BG)
            self.km_entry.config(state='disabled', disabledbackground=self.INPUT_BG)
        switch_distance_btn = tk.Button(scrollable_frame, text="⇄", command=switch_distance, bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 11),
                                        relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                        activeforeground=self.HOVER_ACCENT_BLUE, width=2)
        switch_distance_btn.grid(row=6, column=4, padx=(5, 0), sticky='w')
        self._button_hover_colors[switch_distance_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        self.mile_var.trace_add("write", lambda *a: self._convert_distance())
        self.mile_entry.config(state='normal', bg=self.INPUT_BG)
        self.km_entry.config(state='disabled', disabledbackground=self.INPUT_BG)

        # --- Area Converter (ft² ↔ m²) ---
        self._area_switch_state = 'ft2_to_m2'
        area_label = ttk.Label(scrollable_frame, text="Area (ft² → m²):", style='UnitLabel.TLabel')
        area_label.grid(row=7, column=0, sticky='w', padx=10, pady=10)
        self.ft2_var = tk.StringVar()
        self.m2_var = tk.StringVar()
        self.ft2_entry = tk.Entry(scrollable_frame, textvariable=self.ft2_var, font=self.FONT_INPUT, justify='right',
                                 bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
        self.ft2_entry.grid(row=7, column=1, padx=5, pady=10, sticky='ew')
        self.m2_entry = tk.Entry(scrollable_frame, textvariable=self.m2_var, font=self.FONT_INPUT, justify='right',
                                 disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                                 relief='solid', bd=1, state='disabled')
        self.m2_entry.grid(row=7, column=2, padx=5, pady=10, sticky='ew')
        m2_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: self._copy_quick_result(self.m2_var), bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                               relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                               activeforeground=self.HOVER_ACCENT_BLUE)
        m2_copy_btn.grid(row=7, column=3, padx=(5,0), sticky='w')
        self._button_hover_colors[m2_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        def switch_area():
            if self._area_switch_state == 'ft2_to_m2':
                self._area_switch_state = 'm2_to_ft2'
                area_label.config(text="Area (m² → ft²):")
            else:
                self._area_switch_state = 'ft2_to_m2'
                area_label.config(text="Area (ft² → m²):")
            self.ft2_var.set("")
            self.m2_var.set("")
            self.ft2_entry.config(state='normal', bg=self.INPUT_BG)
            self.m2_entry.config(state='disabled', disabledbackground=self.INPUT_BG)
        switch_area_btn = tk.Button(scrollable_frame, text="⇄", command=switch_area, bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 11),
                                    relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                    activeforeground=self.HOVER_ACCENT_BLUE, width=2)
        switch_area_btn.grid(row=7, column=4, padx=(5, 0), sticky='w')
        self._button_hover_colors[switch_area_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        self.ft2_var.trace_add("write", lambda *a: self._convert_area())
        self.ft2_entry.config(state='normal', bg=self.INPUT_BG)
        self.m2_entry.config(state='disabled', disabledbackground=self.INPUT_BG)

        # --- Temperature Converter (°F ↔ °C) ---
        temp_label = ttk.Label(scrollable_frame, text="Temperature (°F → °C):", style='UnitLabel.TLabel')
        temp_label.grid(row=8, column=0, sticky='w', padx=10, pady=10)
        self._temp_switch_state = 'f_to_c'
        self.f_var = tk.StringVar()
        self.c_var = tk.StringVar()
        self.f_entry = tk.Entry(scrollable_frame, textvariable=self.f_var, font=self.FONT_INPUT, justify='right',
                               bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
        self.f_entry.grid(row=8, column=1, padx=5, pady=10, sticky='ew')
        self.c_entry = tk.Entry(scrollable_frame, textvariable=self.c_var, font=self.FONT_INPUT, justify='right',
                               disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                               relief='solid', bd=1, state='disabled')
        self.c_entry.grid(row=8, column=2, padx=5, pady=10, sticky='ew')
        c_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: self._copy_quick_result(self.c_var), bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                             relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                             activeforeground=self.HOVER_ACCENT_BLUE)
        c_copy_btn.grid(row=8, column=3, padx=(5,0), sticky='w')
        self._button_hover_colors[c_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        def switch_temp():
            if self._temp_switch_state == 'f_to_c':
                self._temp_switch_state = 'c_to_f'
                temp_label.config(text="Temperature (°C → °F):")
            else:
                self._temp_switch_state = 'f_to_c'
                temp_label.config(text="Temperature (°F → °C):")
            self.f_var.set("")
            self.c_var.set("")
            self.f_entry.config(state='normal', bg=self.INPUT_BG)
            self.c_entry.config(state='disabled', disabledbackground=self.INPUT_BG)
        switch_temp_btn = tk.Button(scrollable_frame, text="⇄", command=switch_temp, bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 11),
                                    relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                    activeforeground=self.HOVER_ACCENT_BLUE, width=2)
        switch_temp_btn.grid(row=8, column=4, padx=(5, 0), sticky='w')
        self._button_hover_colors[switch_temp_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        self.f_var.trace_add("write", lambda *a: self._convert_temp())
        self.f_entry.config(state='normal', bg=self.INPUT_BG)
        self.c_entry.config(state='disabled', disabledbackground=self.INPUT_BG)

        # --- Speed Converter (mph ↔ km/h) ---
        speed_label = ttk.Label(scrollable_frame, text="Speed (mph → km/h):", style='UnitLabel.TLabel')
        speed_label.grid(row=9, column=0, sticky='w', padx=10, pady=10)
        self._speed_switch_state = 'mph_to_kmh'
        self.mph_var = tk.StringVar()
        self.kmh_var = tk.StringVar()
        self.mph_entry = tk.Entry(scrollable_frame, textvariable=self.mph_var, font=self.FONT_INPUT, justify='right',
                                 bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
        self.mph_entry.grid(row=9, column=1, padx=5, pady=10, sticky='ew')
        self.kmh_entry = tk.Entry(scrollable_frame, textvariable=self.kmh_var, font=self.FONT_INPUT, justify='right',
                                 disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                                 relief='solid', bd=1, state='disabled')
        self.kmh_entry.grid(row=9, column=2, padx=5, pady=10, sticky='ew')
        kmh_copy_btn = tk.Button(scrollable_frame, text="📋", command=lambda: self._copy_quick_result(self.kmh_var), bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                               relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                               activeforeground=self.HOVER_ACCENT_BLUE)
        kmh_copy_btn.grid(row=9, column=3, padx=(5,0), sticky='w')
        self._button_hover_colors[kmh_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        def switch_speed():
            if self._speed_switch_state == 'mph_to_kmh':
                self._speed_switch_state = 'kmh_to_mph'
                speed_label.config(text="Speed (km/h → mph):")
            else:
                self._speed_switch_state = 'mph_to_kmh'
                speed_label.config(text="Speed (mph → km/h):")
            self.mph_var.set("")
            self.kmh_var.set("")
            self.mph_entry.config(state='normal', bg=self.INPUT_BG)
            self.kmh_entry.config(state='disabled', disabledbackground=self.INPUT_BG)
        switch_speed_btn = tk.Button(scrollable_frame, text="⇄", command=switch_speed, bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 11),
                                     relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                     activeforeground=self.HOVER_ACCENT_BLUE, width=2)
        switch_speed_btn.grid(row=9, column=4, padx=(5, 0), sticky='w')
        self._button_hover_colors[switch_speed_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        self.mph_var.trace_add("write", lambda *a: self._convert_speed())
        self.mph_entry.config(state='normal', bg=self.INPUT_BG)
        self.kmh_entry.config(state='disabled', disabledbackground=self.INPUT_BG)

        # ...existing code...

        # --- Separator before Quick Calculation ---
        separator2 = ttk.Separator(scrollable_frame, orient='horizontal')
        separator2.grid(row=10, column=0, columnspan=4, sticky='ew', pady=20)

        # --- Quick Calculation Section (moved below new converters) ---
        ttk.Label(scrollable_frame, text="Quick Calculation:", style='UnitLabel.TLabel').grid(row=11, column=0, sticky='w', padx=10, pady=10)
        self.area_rows_container = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        self.area_rows_container.grid(row=12, column=0, columnspan=4, sticky='ew')
        area_controls_frame = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        area_controls_frame.grid(row=13, column=0, columnspan=4, sticky='ew', pady=(10,0))
        area_controls_frame.grid_columnconfigure(1, weight=1)
        add_row_btn = tk.Button(area_controls_frame, text="+", command=self._add_area_row, 
                                bg=self.SECONDARY_BG, fg=self.INPUT_FG, font=(self.FONT_FAMILY, 12, 'bold'),
                                relief='flat', bd=0, cursor='hand2')
        add_row_btn.grid(row=0, column=0, sticky='w', padx=10)
        ttk.Label(area_controls_frame, text="Result:", style='UnitLabel.TLabel').grid(row=0, column=1, sticky='e', padx=(0,10))
        self.area_result_var = tk.StringVar(value="0.00")
        area_result_entry = tk.Entry(area_controls_frame, textvariable=self.area_result_var, font=self.FONT_INPUT, justify='right',
                                     disabledbackground=self.INPUT_BG, disabledforeground=self.INPUT_FG,
                                     relief='solid', bd=1, state='disabled', width=12)
        area_result_entry.grid(row=0, column=2, padx=(0, 12), sticky='ew')
        area_copy_btn = tk.Button(area_controls_frame, text="📋", command=lambda: self._copy_quick_result(self.area_result_var), bg=self.PRIMARY_BG, fg=self.TEXT_MUTED, font=(self.FONT_FAMILY, 12),
                                  relief='flat', bd=0, cursor='hand2', activebackground=self.PRIMARY_BG,
                                  activeforeground=self.HOVER_ACCENT_BLUE)
        area_copy_btn.grid(row=0, column=3, padx=(0, 0), sticky='w')
        self._button_hover_colors[area_copy_btn] = {'original': self.TEXT_MUTED, 'hover': self.HOVER_ACCENT_BLUE, 'type': 'fg'}
        # Operation box beside result, with space
        ttk.Label(area_controls_frame, text="Operation:", style='UnitLabel.TLabel').grid(row=0, column=4, sticky='e', padx=(18, 4))
        self.area_operation_var = tk.StringVar(value="Addition")
        operation_combo = ttk.Combobox(area_controls_frame, textvariable=self.area_operation_var, state='readonly', font=self.FONT_INPUT, width=12,
                                      values=["Addition", "Subtraction", "Multiplication", "Division"])
        operation_combo.grid(row=0, column=5, sticky='w', padx=(0, 0))
        operation_combo.configure(foreground=self.INPUT_FG, background=self.INPUT_BG)
        operation_combo.bind('<<ComboboxSelected>>', lambda e: self._calculate_total_area())
        self._add_area_row()

        # Set a minimum height for the scrollable area
        scrollable_frame.update_idletasks()
        min_height = 600
        scrollable_frame.config(height=min_height)
        canvas.config(height=min_height)
        # Make sure the scrollable area expands horizontally
        canvas.bind('<Configure>', lambda e: canvas.itemconfig('all', width=e.width))

        # --- Separator after Quick Calculation Operation (with breathing space) ---
        separator3 = ttk.Separator(scrollable_frame, orient='horizontal')
        separator3.grid(row=14, column=0, columnspan=4, sticky='ew', pady=(24, 24))

        # --- Percentage Discount Calculator Section (Refined UI) ---
        discount_frame = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        discount_frame.grid(row=15, column=0, columnspan=4, sticky='ew', pady=(0, 10))
        for i in range(6): discount_frame.grid_columnconfigure(i, weight=1)

        # Title (smaller, muted)
        discount_title = ttk.Label(discount_frame, text="Percentage Discount Calculator", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 12, 'normal'))
        discount_title.grid(row=0, column=0, columnspan=6, sticky='w', padx=(2,0), pady=(0, 8))

        # Price Before Discount
        price_label = ttk.Label(discount_frame, text="Price:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11))
        price_label.grid(row=1, column=0, sticky='e', padx=(10, 10), pady=(0, 4))
        self.discount_price_var = tk.StringVar()
        price_entry = tk.Entry(discount_frame, textvariable=self.discount_price_var, font=(self.FONT_FAMILY, 11), justify='right',
                              bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1, width=10)
        price_entry.grid(row=1, column=1, sticky='ew', padx=(0, 2), pady=(0, 4))
        price_entry.config(highlightbackground=self.SECONDARY_BG, highlightcolor=self.ACCENT_BLUE, highlightthickness=1)

        # Discount Percentage
        percent_label = ttk.Label(discount_frame, text="Discount %:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11))
        percent_label.grid(row=1, column=2, sticky='e', padx=(2, 10), pady=(0, 4))
        self.discount_percent_var = tk.StringVar()
        percent_entry = tk.Entry(discount_frame, textvariable=self.discount_percent_var, font=(self.FONT_FAMILY, 11), justify='right',
                                bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1, width=8)
        percent_entry.grid(row=1, column=3, sticky='ew', padx=(0, 60), pady=(0, 4))
        percent_entry.config(highlightbackground=self.SECONDARY_BG, highlightcolor=self.ACCENT_BLUE, highlightthickness=1)

        # Calculate Button (smaller, right-aligned)
        calc_btn = tk.Button(discount_frame, text="Calculate", command=self._calculate_discount,
                            bg=self.ACCENT_BLUE, fg=self.TEXT_LIGHT, font=(self.FONT_FAMILY, 10, 'bold'),
                            relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                            activebackground=self.HOVER_ACCENT_BLUE, activeforeground=self.TEXT_LIGHT)
        calc_btn.grid(row=1, column=4, sticky='ew', padx=(0, 10), pady=(0, 4))
        self._button_hover_colors[calc_btn] = {'original': self.ACCENT_BLUE, 'hover': self.HOVER_ACCENT_BLUE}

        # Output Labels (smaller, compact, aligned)
        save_label = ttk.Label(discount_frame, text="You Save:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 10))
        save_label.grid(row=2, column=0, sticky='e', padx=(10, 2), pady=(0, 2))
        self.discount_save_var = tk.StringVar(value="$0.00")
        save_output = ttk.Label(discount_frame, textvariable=self.discount_save_var, style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11, 'bold'))
        save_output.grid(row=2, column=1, sticky='w', padx=(0, 6), pady=(0, 2))

        final_label = ttk.Label(discount_frame, text="Final Price:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 10))
        final_label.grid(row=2, column=2, sticky='e', padx=(2, 2), pady=(0, 2))
        self.discount_final_var = tk.StringVar(value="$0.00")
        final_output = ttk.Label(discount_frame, textvariable=self.discount_final_var, style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11, 'bold'))
        final_output.grid(row=2, column=3, sticky='w', padx=(0, 6), pady=(0, 2))

        # Bind Enter key for quick calculation
        price_entry.bind('<Return>', lambda e: self._calculate_discount())
        percent_entry.bind('<Return>', lambda e: self._calculate_discount())
        # Make calculation live as user types
        self.discount_price_var.trace_add('write', lambda *args: self._calculate_discount())
        self.discount_percent_var.trace_add('write', lambda *args: self._calculate_discount())

        # --- Separator below Percentage Discount Calculator ---
        separator4 = ttk.Separator(scrollable_frame, orient='horizontal')
        separator4.grid(row=16, column=0, columnspan=4, sticky='ew', pady=(18, 18))

        # --- Tax Calculator Section (Refined UI) ---
        tax_frame = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        tax_frame.grid(row=17, column=0, columnspan=4, sticky='ew', pady=(0, 10))
        for i in range(6): tax_frame.grid_columnconfigure(i, weight=1)

        # Title (smaller, muted)
        tax_title = ttk.Label(tax_frame, text="Tax Calculator", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 12, 'normal'))
        tax_title.grid(row=0, column=0, columnspan=6, sticky='w', padx=(2,0), pady=(0, 8))

        # Original Price
        tax_price_label = ttk.Label(tax_frame, text="Price:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11))
        tax_price_label.grid(row=1, column=0, sticky='e', padx=(10, 10), pady=(0, 4))
        self.tax_price_var = tk.StringVar()
        tax_price_entry = tk.Entry(tax_frame, textvariable=self.tax_price_var, font=(self.FONT_FAMILY, 11), justify='right',
                                   bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1, width=10)
        tax_price_entry.grid(row=1, column=1, sticky='ew', padx=(0, 2), pady=(0, 4))
        tax_price_entry.config(highlightbackground=self.SECONDARY_BG, highlightcolor=self.ACCENT_BLUE, highlightthickness=1)

        # Tax Percentage
        tax_percent_label = ttk.Label(tax_frame, text="Tax %:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11))
        tax_percent_label.grid(row=1, column=2, sticky='e', padx=(2, 10), pady=(0, 4))
        self.tax_percent_var = tk.StringVar()
        tax_percent_entry = tk.Entry(tax_frame, textvariable=self.tax_percent_var, font=(self.FONT_FAMILY, 11), justify='right',
                                     bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1, width=8)
        tax_percent_entry.grid(row=1, column=3, sticky='ew', padx=(0, 60), pady=(0, 4))
        tax_percent_entry.config(highlightbackground=self.SECONDARY_BG, highlightcolor=self.ACCENT_BLUE, highlightthickness=1)

        # Calculate Button (smaller, right-aligned)
        tax_calc_btn = tk.Button(tax_frame, text="Calculate", command=self._calculate_tax,
                                 bg=self.ACCENT_BLUE, fg=self.TEXT_LIGHT, font=(self.FONT_FAMILY, 10, 'bold'),
                                 relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                                 activebackground=self.HOVER_ACCENT_BLUE, activeforeground=self.TEXT_LIGHT)
        tax_calc_btn.grid(row=1, column=4, sticky='ew', padx=(0, 10), pady=(0, 4))
        self._button_hover_colors[tax_calc_btn] = {'original': self.ACCENT_BLUE, 'hover': self.HOVER_ACCENT_BLUE}

        # Output Labels (smaller, compact, aligned)
        tax_amount_label = ttk.Label(tax_frame, text="Tax Amount:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 10))
        tax_amount_label.grid(row=2, column=0, sticky='e', padx=(10, 2), pady=(0, 2))
        self.tax_amount_var = tk.StringVar(value="$0.00")
        tax_amount_output = ttk.Label(tax_frame, textvariable=self.tax_amount_var, style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11, 'bold'))
        tax_amount_output.grid(row=2, column=1, sticky='w', padx=(0, 6), pady=(0, 2))

        tax_total_label = ttk.Label(tax_frame, text="Total Price:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 10))
        tax_total_label.grid(row=2, column=2, sticky='e', padx=(2, 2), pady=(0, 2))
        self.tax_total_var = tk.StringVar(value="$0.00")
        tax_total_output = ttk.Label(tax_frame, textvariable=self.tax_total_var, style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11, 'bold'))
        tax_total_output.grid(row=2, column=3, sticky='w', padx=(0, 6), pady=(0, 2))

        # Bind Enter key for quick calculation
        tax_price_entry.bind('<Return>', lambda e: self._calculate_tax())
        tax_percent_entry.bind('<Return>', lambda e: self._calculate_tax())
        # Make calculation live as user types
        self.tax_price_var.trace_add('write', lambda *args: self._calculate_tax())
        self.tax_percent_var.trace_add('write', lambda *args: self._calculate_tax())

        # --- Separator below Tax Calculator ---
        separator_age = ttk.Separator(scrollable_frame, orient='horizontal')
        separator_age.grid(row=18, column=0, columnspan=4, sticky='ew', pady=(24, 24))

        # --- Age Calculator Section (Refined UI) ---
        age_frame = tk.Frame(scrollable_frame, bg=self.PRIMARY_BG)
        age_frame.grid(row=19, column=0, columnspan=4, sticky='ew', pady=(0, 10))
        for i in range(7): age_frame.grid_columnconfigure(i, weight=1)

        # Title
        age_title = ttk.Label(age_frame, text="Age Calculator", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 12, 'normal'))
        age_title.grid(row=0, column=0, columnspan=6, sticky='w', padx=(2,0), pady=(0, 8))

        # Birthdate Input (Year, Month, Day fields)
        # Use uniform spacing and alignment for all fields
        # Set a uniform width for all entry fields and equal padding between all elements
        entry_width = 6
        pad_x = 8
        year_label = ttk.Label(age_frame, text="Year:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11))
        year_label.grid(row=1, column=0, sticky='e', padx=(10, pad_x), pady=(0, 4))
        self.birth_year_var = tk.StringVar()
        year_entry = tk.Entry(age_frame, textvariable=self.birth_year_var, font=(self.FONT_FAMILY, 11),
                             bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1, width=entry_width, justify='left')
        year_entry.grid(row=1, column=1, sticky='ew', padx=(0, pad_x), pady=(0, 4))
        year_entry.config(highlightbackground=self.SECONDARY_BG, highlightcolor=self.ACCENT_BLUE, highlightthickness=1)

        month_label = ttk.Label(age_frame, text="Month:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11))
        month_label.grid(row=1, column=2, sticky='e', padx=(0, pad_x), pady=(0, 4))
        self.birth_month_var = tk.StringVar()
        month_entry = tk.Entry(age_frame, textvariable=self.birth_month_var, font=(self.FONT_FAMILY, 11),
                              bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1, width=entry_width, justify='left')
        month_entry.grid(row=1, column=3, sticky='ew', padx=(0, pad_x), pady=(0, 4))
        month_entry.config(highlightbackground=self.SECONDARY_BG, highlightcolor=self.ACCENT_BLUE, highlightthickness=1)

        day_label = ttk.Label(age_frame, text="Day:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11))
        day_label.grid(row=1, column=4, sticky='e', padx=(0, pad_x), pady=(0, 4))
        self.birth_day_var = tk.StringVar()
        day_entry = tk.Entry(age_frame, textvariable=self.birth_day_var, font=(self.FONT_FAMILY, 11),
                            bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1, width=entry_width, justify='left')
        # Add extra space after the day entry for breathing room before the Calculate button
        day_entry.grid(row=1, column=5, sticky='ew', padx=(0, 48), pady=(0, 4))
        day_entry.config(highlightbackground=self.SECONDARY_BG, highlightcolor=self.ACCENT_BLUE, highlightthickness=1)

        # Calculate Button
        age_calc_btn = tk.Button(age_frame, text="Calculate", command=self._calculate_age,
                                 bg=self.ACCENT_BLUE, fg=self.TEXT_LIGHT, font=(self.FONT_FAMILY, 10, 'bold'),
                                 relief='flat', padx=10, pady=4, cursor='hand2', bd=0,
                                 activebackground=self.HOVER_ACCENT_BLUE, activeforeground=self.TEXT_LIGHT)
        age_calc_btn.grid(row=1, column=6, sticky='ew', padx=(0, 10), pady=(0, 4))
        self._button_hover_colors[age_calc_btn] = {'original': self.ACCENT_BLUE, 'hover': self.HOVER_ACCENT_BLUE}

        # Output Label
        age_result_label = ttk.Label(age_frame, text="Age:", style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 10))
        age_result_label.grid(row=2, column=0, sticky='e', padx=(10, 2), pady=(0, 2))
        self.age_result_var = tk.StringVar(value="0 years")
        age_result_output = ttk.Label(age_frame, textvariable=self.age_result_var, style='UnitLabel.TLabel', font=(self.FONT_FAMILY, 11, 'bold'))
        age_result_output.grid(row=2, column=1, sticky='w', padx=(0, 6), pady=(0, 2))

        # Bind Enter key for quick calculation
        year_entry.bind('<Return>', lambda e: self._calculate_age())
        month_entry.bind('<Return>', lambda e: self._calculate_age())
        day_entry.bind('<Return>', lambda e: self._calculate_age())

        # Live calculation as user types
        self.birth_year_var.trace_add('write', lambda *args: self._calculate_age())
        self.birth_month_var.trace_add('write', lambda *args: self._calculate_age())
        self.birth_day_var.trace_add('write', lambda *args: self._calculate_age())
    def _calculate_age(self):
        import datetime
        import calendar
        year_str = self.birth_year_var.get().strip()
        month_str = self.birth_month_var.get().strip()
        day_str = self.birth_day_var.get().strip()
        today = datetime.date.today()
        try:
            if not year_str or not year_str.isdigit() or len(year_str) != 4:
                self.age_result_var.set("")
                return
            year = int(year_str)
            if not month_str or not month_str.isdigit():
                month = 1
            else:
                month = int(month_str)
                if not (1 <= month <= 12):
                    self.age_result_var.set("")
                    return
            if not day_str or not day_str.isdigit():
                day = 1
            else:
                day = int(day_str)
                if not (1 <= day <= calendar.monthrange(year, month)[1]):
                    self.age_result_var.set("")
                    return
            birthdate = datetime.date(year, month, day)
            years = today.year - birthdate.year
            months = today.month - birthdate.month
            days = today.day - birthdate.day
            if days < 0:
                months -= 1
                prev_month = today.month - 1 or 12
                prev_year = today.year if today.month > 1 else today.year - 1
                days += calendar.monthrange(prev_year, prev_month)[1]
            if months < 0:
                years -= 1
                months += 12
            result = f"{years} years"
            if month_str:
                result += f", {months} months"
            if day_str:
                result += f", {days} days"
            self.age_result_var.set(result)
        except Exception:
            self.age_result_var.set("")

    def _calculate_tax(self):
        """Calculate and display the tax amount and total price after tax."""
        try:
            price = float(self.tax_price_var.get().replace(',', '.'))
            percent = float(self.tax_percent_var.get().replace(',', '.'))
            if price < 0 or percent < 0:
                raise ValueError
            tax = price * percent / 100
            total = price + tax
            self.tax_amount_var.set(f"${tax:.2f}")
            self.tax_total_var.set(f"${total:.2f}")
            self.update_status("Tax calculated!", self.SUCCESS_GREEN)
        except Exception:
            self.tax_amount_var.set("$0.00")
            self.tax_total_var.set("$0.00")
            self.update_status("Invalid input for tax calculation.", self.WARNING_RED)

    def _calculate_discount(self):
        """Calculate and display the discount savings and final price."""
        try:
            price = float(self.discount_price_var.get().replace(',', '.'))
            percent = float(self.discount_percent_var.get().replace(',', '.'))
            if price < 0 or percent < 0:
                raise ValueError
            save = price * percent / 100
            final = price - save
            self.discount_save_var.set(f"${save:.2f}")
            self.discount_final_var.set(f"${final:.2f}")
            self.update_status("Discount calculated!", self.SUCCESS_GREEN)
        except Exception:
            self.discount_save_var.set("$0.00")
            self.discount_final_var.set("$0.00")
            self.update_status("Invalid input for discount calculation.", self.WARNING_RED)
    def _convert_distance(self, *args):
        try:
            if getattr(self, '_distance_switch_state', 'mile_to_km') == 'mile_to_km':
                miles = float(self.mile_var.get() or 0)
                km = miles * 1.60934
                self.km_var.set(f"{km:.2f} km")
            else:
                km = float(self.mile_var.get() or 0)
                miles = km / 1.60934
                self.km_var.set(f"{miles:.2f} mile")
        except ValueError:
            self.km_var.set("Invalid")

    def _convert_area(self, *args):
        try:
            if getattr(self, '_area_switch_state', 'ft2_to_m2') == 'ft2_to_m2':
                val = self.ft2_var.get()
                if val.strip() == "":
                    self.m2_var.set("")
                    return
                ft2 = float(val)
                m2 = ft2 * 0.092903
                self.m2_var.set(f"{m2:.2f} m²")
            else:
                val = self.ft2_var.get()
                if val.strip() == "":
                    self.m2_var.set("")
                    return
                m2 = float(val)
                ft2 = m2 / 0.092903
                self.m2_var.set(f"{ft2:.2f} ft²")
        except ValueError:
            self.m2_var.set("Invalid")

    def _convert_temp(self, *args):
        try:
            if getattr(self, '_temp_switch_state', 'f_to_c') == 'f_to_c':
                f = float(self.f_var.get() or 0)
                c = (f - 32) * 5/9
                self.c_var.set(f"{c:.2f} °C")
            else:
                c = float(self.f_var.get() or 0)
                f = (c * 9/5) + 32
                self.c_var.set(f"{f:.2f} °F")
        except ValueError:
            self.c_var.set("Invalid")

    def _convert_speed(self, *args):
        try:
            if getattr(self, '_speed_switch_state', 'mph_to_kmh') == 'mph_to_kmh':
                mph = float(self.mph_var.get() or 0)
                kmh = mph * 1.60934
                self.kmh_var.set(f"{kmh:.2f} km/h")
            else:
                kmh = float(self.mph_var.get() or 0)
                mph = kmh / 1.60934
                self.kmh_var.set(f"{mph:.2f} mph")
        except ValueError:
            self.kmh_var.set("Invalid")

        # Remove old Quick Calculation widgets (now handled in scrollable_frame)
    def _add_area_row(self):
        """Creates and adds a new row for the area calculator with up to 5 columns (numeric fields), equally spaced."""
        row_frame = tk.Frame(self.area_rows_container, bg=self.PRIMARY_BG)
        row_frame.pack(fill=tk.X, expand=True, pady=2)

        # Use a grid layout for equal spacing
        value_vars = []
        entry_widgets = []

        # Add column widgets in grid, up to 7
        def add_column():
            col = len(value_vars)
            if col >= 7:
                return
            value_var = tk.StringVar()
            entry = tk.Entry(row_frame, textvariable=value_var, font=self.FONT_INPUT, justify='right',
                             bg=self.INPUT_BG, fg=self.INPUT_FG, relief='solid', bd=1)
            entry.grid(row=0, column=col, padx=4, pady=2, sticky='ew')
            row_frame.grid_columnconfigure(col, weight=1, uniform='area')
            value_vars.append(value_var)
            entry_widgets.append(entry)
            value_var.trace_add("write", lambda *_: self._calculate_total_area())
            self._calculate_total_area()
            # If 7 columns, hide the plus button
            if len(value_vars) >= 7:
                plus_btn.grid_remove()
            else:
                plus_btn.grid(row=0, column=col+1, padx=(4,0), pady=2, sticky='ew')
            # Always keep remove button at the end
            remove_btn.grid(row=0, column=col+2, padx=(8,0), pady=2, sticky='ew')

        plus_btn = tk.Button(row_frame, text="+", font=(self.FONT_FAMILY, 12, 'bold'), bg=self.SECONDARY_BG, fg=self.INPUT_FG,
                             relief='flat', bd=0, cursor='hand2')
        remove_btn = tk.Button(row_frame, text="🗑️", font=(self.FONT_FAMILY, 12), bg=self.PRIMARY_BG, fg=self.WARNING_RED,
                               relief='flat', bd=0, cursor='hand2', command=lambda: self._remove_area_row(row_frame))
        plus_btn.configure(command=add_column)

        add_column()  # first column

        row_data = {
            'value_vars': value_vars,
            'frame': row_frame,
            'plus_btn': plus_btn,
            'remove_btn': remove_btn
        }
        self.area_rows.append(row_data)

        self._calculate_total_area()

    def _remove_area_row(self, row_frame):
        """Removes a row from the area calculator and updates the total."""
        for row in self.area_rows:
            if row['frame'] == row_frame:
                self.area_rows.remove(row)
                break
        row_frame.destroy()
        self._calculate_total_area()

    def _calculate_total_area(self, *args):
        """Performs the selected operation on all values from all columns in all dynamic area rows and updates the result live."""
        values = []
        for row in self.area_rows:
            for value_var in row.get('value_vars', []):
                try:
                    val_str = value_var.get()
                    if not val_str.strip():
                        continue
                    val = float(val_str)
                    values.append(val)
                except (ValueError, KeyError):
                    continue
        op = getattr(self, 'area_operation_var', None)
        operation = op.get() if op else "Addition"
        result = 0.0
        if not values:
            result = 0.0
        elif operation == "Addition":
            result = sum(values)
        elif operation == "Subtraction":
            result = values[0] - sum(values[1:]) if len(values) > 1 else values[0]
        elif operation == "Multiplication":
            result = 1.0
            for v in values:
                result *= v
        elif operation == "Division":
            result = values[0] if values else 0.0
            for v in values[1:]:
                try:
                    result /= v
                except ZeroDivisionError:
                    result = float('inf')
                    break
        self.area_result_var.set(f"{result:.2f}")

    # --- Other methods remain largely unchanged from here ---
    def _convert_height(self, *args):
        try:
            feet = float(self.feet_var.get() or 0)
            inches = float(self.inches_var.get() or 0)
            total_inches = (feet * 12) + inches
            cm = total_inches * 2.54
            self.height_cm_var.set(f"{cm:.2f} cm")
        except ValueError:
            self.height_cm_var.set("Invalid")
    
    def _convert_weight(self, *args):
        try:
            if getattr(self, '_weight_switch_state', 'lb_to_kg') == 'lb_to_kg':
                lbs = float(self.lbs_var.get() or 0)
                kg = lbs * 0.453592
                self.weight_kg_var.set(f"{kg:.2f} kg")
            else:
                kg = float(self.lbs_var.get() or 0)
                lbs = kg / 0.453592
                self.weight_kg_var.set(f"{lbs:.2f} lb")
        except ValueError:
            self.weight_kg_var.set("Invalid")

    def _copy_quick_result(self, string_var):
        full_text = string_var.get()
        numerical_part = full_text.split(" ")[0]
        if not numerical_part or "Invalid" in numerical_part:
            self.update_status("Nothing to copy!", self.WARNING_RED)
            return
        self._copy_to_clipboard_helper(numerical_part, "Result copied to clipboard!")

    def _copy_unit_result(self):
        result_text = self.unit_result_var.get()
        if not result_text or "Invalid" in result_text or "N/A" in result_text:
            self.update_status("Nothing to copy!", self.WARNING_RED)
            return
        self._copy_to_clipboard_helper(result_text, "Result copied to clipboard!")

    def _copy_to_clipboard_helper(self, text, success_message):
        try:
            pyperclip.copy(text)
            self.update_status(success_message, self.SUCCESS_GREEN)
        except Exception:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            self.update_status(f"{success_message} (fallback)", self.SUCCESS_GREEN)
        
    def _populate_unit_comboboxes(self):
        all_units = sorted([u for sublist in self.UNITS_CATEGORIES.values() for u in sublist])
        self.from_unit_combobox['values'] = all_units
        self.to_unit_combobox['values'] = all_units
        if 'm' in all_units: self.from_unit_var.set('m')
        if 'cm' in all_units: self.to_unit_var.set('cm')

    def _swap_units(self):
        from_val, to_val = self.from_unit_var.get(), self.to_unit_var.get()
        self.from_unit_var.set(to_val)
        self.to_unit_var.set(from_val)
        self._perform_unit_conversion()
        self.update_status("Units swapped!", self.TEXT_MUTED)

    def _perform_unit_conversion(self):
        try:
            value = float(self.unit_input_var.get().replace(',', '.'))
            from_u, to_u = self.from_unit_var.get(), self.to_unit_var.get()
            if not from_u or not to_u:
                return

            # Special case for temperature
            if from_u in ['°C', '°F'] and to_u in ['°C', '°F']:
                if from_u == to_u:
                    result = value
                elif from_u == '°C' and to_u == '°F':
                    result = (value * 9/5) + 32
                elif from_u == '°F' and to_u == '°C':
                    result = (value - 32) * 5/9
                else:
                    result = 'N/A'
                self.unit_result_var.set(f"{result:.2f}" if isinstance(result, float) or isinstance(result, int) else str(result))
                return

            # Find the category for both units
            from_cat = None
            to_cat = None
            for cat, units in self.UNITS_CATEGORIES.items():
                if from_u in units:
                    from_cat = cat
                if to_u in units:
                    to_cat = cat
            if from_cat != to_cat or from_cat is None:
                self.unit_result_var.set("N/A")
                return

            factors = getattr(self, f"{from_cat.upper()}_CONVERSION_FACTORS")
            base_val = value * factors[from_u]
            result = base_val / factors[to_u]
            self.unit_result_var.set(f"{result:.2f}")
        except (ValueError, KeyError):
            self.unit_result_var.set("Invalid Input")

    def on_tab_change(self, event):
        if self.notebook.tab(self.notebook.select(), "text") == "Text Tools":
            self.input_text.focus_set()
            self.update_stats()
            self.update_status("Ready (Text Tools).", self.TEXT_MUTED)
        else:
            self.unit_input_entry.focus_set()
            self._perform_unit_conversion()
            self.update_status("Ready (Unit Converter).", self.TEXT_MUTED)

    def bind_hover_effects(self):
        for btn, colors in self._button_hover_colors.items():
            if colors.get('type') == 'fg':
                btn.bind('<Enter>', lambda e, b=btn, hc=colors['hover']: b.config(fg=hc))
                btn.bind('<Leave>', lambda e, b=btn, oc=colors['original']: b.config(fg=oc))
            else:
                btn.bind('<Enter>', lambda e, b=btn, hc=colors['hover']: b.config(bg=hc))
                btn.bind('<Leave>', lambda e, b=btn, oc=colors['original']: b.config(bg=oc))

    def on_text_change(self, event=None):
        self.update_stats()
        self.apply_conversion()

    def update_stats(self):
        text = self.input_text.get('1.0', tk.END + '-1c')
        char_count = len(text)
        word_count = len(re.findall(r'\b\w+\b', text))
        line_count = text.count('\n') + 1 if text else 0
        
        self.char_count_label.config(text=str(char_count))
        self.word_count_label.config(text=str(word_count))
        self.line_count_label.config(text=str(line_count))

    def set_case_type(self, case_type):
        self.current_case_type = case_type
        self.apply_conversion()
        
        buttons = {'upper': self.upper_btn, 'lower': self.lower_btn, 'title': self.title_btn, 'sentence': self.sentence_case_btn}
        feedback_btn = buttons.get(case_type)
        if feedback_btn and feedback_btn in self._button_hover_colors:
            original_color = self._button_hover_colors[feedback_btn]['original']
            feedback_btn.config(bg=self.ACCENT_BLUE)
            self.root.after(200, lambda: feedback_btn.config(bg=original_color))

    def apply_conversion(self):
        input_text = self.input_text.get('1.0', tk.END + '-1c')
        result = input_text
        if self.current_case_type == 'upper': result = input_text.upper()
        elif self.current_case_type == 'lower': result = input_text.lower()
        elif self.current_case_type == 'title': result = input_text.title()
        elif self.current_case_type == 'sentence': result = self._to_sentence_case(input_text)
        
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.insert('1.0', result)
        self.output_text.config(state='disabled')

    def _to_sentence_case(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'([.!?])(\s*)([a-z])', lambda m: m.group(1) + m.group(2) + m.group(3).upper(), text)
        lines = text.split('\n')
        processed_lines = []
        for line in lines:
            stripped_line = line.lstrip()
            if stripped_line:
                first_char_index = line.find(stripped_line[0])
                capitalized_line = line[:first_char_index] + stripped_line[0].upper() + stripped_line[1:]
                processed_lines.append(capitalized_line)
            else:
                processed_lines.append(line)
        return '\n'.join(processed_lines)

    def clear_text(self):
        self.input_text.delete('1.0', tk.END)
        self.output_text.config(state='normal')
        self.output_text.delete('1.0', tk.END)
        self.output_text.config(state='disabled')
        self.update_stats()
        self.input_text.focus_set()
        self.update_status("All text cleared.", self.TEXT_MUTED)

    def copy_to_clipboard(self):
        output_text = self.output_text.get('1.0', tk.END + '-1c')
        self._copy_to_clipboard_helper(output_text, "Text copied to clipboard!")

    def update_status(self, message: str, color: str = None):
        self.status_label.config(text=message, fg=color or self.TEXT_LIGHT)
        if hasattr(self, '_status_timer'): self.root.after_cancel(self._status_timer)
        self._status_timer = self.root.after(self.STATUS_MESSAGE_DURATION_MS, lambda: self.status_label.config(text="Ready.", fg=self.TEXT_MUTED))

    def _show_eyedropper(self):
        import tkinter as tk
        from tkinter import colorchooser

        # Save main window geometry and state
        orig_geom = self.root.geometry()
        orig_state = self.root.state()

        # Open the native color chooser dialog
        color_tuple = colorchooser.askcolor(title="Pick a color")
        color_hex = color_tuple[1] if color_tuple else None

        # Restore main window
        self.root.deiconify()
        self.root.geometry(orig_geom)
        self.root.state(orig_state)
        self.root.lift()
        self.root.focus_force()

        if color_hex:
            try:
                self.creative_hex_var.set(color_hex.upper())
                self.update_status(f"Color picked: {color_hex.upper()}", self.SUCCESS_GREEN)
            except Exception:
                self.update_status("Color picked, but failed to update field.", self.WARNING_RED)
        else:
            self.update_status("Color picker cancelled.", self.TEXT_MUTED)
        

# --- Main block to launch the app ---
if __name__ == "__main__":
    import tkinter as tk
    try:
        root = tk.Tk()
        app = TextCaseConverter(root)
        root.mainloop()
    except Exception as e:
        import traceback
        print("Failed to launch the app:", e)
        traceback.print_exc()