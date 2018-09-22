import tkinter as tk
from PIL import ImageTk
from pyy_chr import Renderer, StandardBitplaneTileInterpreter, StandardMapInterpreter, GrayscalePaletteInterpreter

class PreviewDisplayWindow:
    def __init__(self, master):
        self.display_width, self.display_height = 22, 6
        self.start_column, self.start_row = 5, 2

        self.map_data = bytearray(32 * 32)

        self.renderer = Renderer()
        self.renderer.set_map_interpreter(StandardMapInterpreter((32, 32)))
        self.renderer.set_tile_interpreter(StandardBitplaneTileInterpreter(interleaved_count = 2, layered_count = 1))
        self.renderer.set_palette_interpreter(GrayscalePaletteInterpreter(4))
        self.renderer.load_tile_data(open('assets/gfx/font.bin', 'rb').read())
        self.renderer.load_map_data(self.map_data)

        self.master = master
        self.master.title('46BYS gfx previewer')

        self.master.bind('<Down>', self.on_next_page)
        self.master.bind('<Up>', self.on_prev_page)
        self.master.bind('<Right>', self.on_next_entry)
        self.master.bind('<Left>', self.on_prev_entry)
        self.master.bind('r', self.on_reload)

        self.display = tk.Label(self.master)
        self.display.pack(side="bottom", fill="both", expand="yes")
        self.display.configure(background='darkblue')

        self.current_entry = 0
        self.current_page = 0
        self.scroll_offset = 0

    def write_window(self, left, top, width, height):
        self.write_tiles(bytes([1] + [2] * (width - 2) + [3]), (left, top))
        for r in range(top + 1, top + height - 1):
            self.write_tiles(bytes([8] + [0] * (width - 2) + [10]), (left, r))
        self.write_tiles(bytes([4] + [5] * (width - 2) + [6]), (left, top + height - 1))

    def write_tiles(self, tiles, pos):
        index = pos[1] * 32 + pos[0]
        self.map_data[index:index + len(tiles)] = tiles

    def refresh_display(self):
        img = self.renderer.render()
        self.tkimage = ImageTk.PhotoImage(img.resize([3 * d for d in img.size]))
        self.display.configure(image=self.tkimage)

    def on_next_page(self, event):
        pass

    def on_prev_page(self, event):
        pass

    def on_next_entry(self, event):
        pass

    def on_prev_entry(self, event):
        pass

    def on_reload(self, event):
        pass
