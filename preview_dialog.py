import csv
import tkinter as tk

from PIL import ImageTk
from pyy_chr import Renderer

import text_util

class DisplayWindow:
    def __init__(self, master):
        self.display_width, self.display_height = 22, 6
        self.start_column, self.start_row = 5, 2

        self.reverse_font_map = text_util.load_map_reverse('assets/text/font.tbl')

        self.renderer = Renderer()
        self.renderer.resize((32, 32))
        self.renderer.load_tile_data(open('assets/gfx/font.bin', 'rb').read())

        self.master = master
        self.master.title('46BYS gfx previewer')

        self.master.bind('<Down>', self.__on_next_page)
        self.master.bind('<Up>', self.__on_prev_page)
        self.master.bind('<Right>', self.__on_next_entry)
        self.master.bind('<Left>', self.__on_prev_entry)
        self.master.bind('r', self.__on_reload)

        self.display = tk.Label(self.master)
        self.display.pack(side="bottom", fill="both", expand="yes")
        self.display.configure(background='darkblue')

        self.current_entry = 0
        self.current_page = 0
        self.scroll_offset = 0

        self.__reload()

    def __reload(self):
        self.entries = []
        self.total_length = 0
        for bank_index in range(1, 4):
            with open('assets/text/dialog_bank_{0}.csv'.format(bank_index), 'r', encoding='shift-jis') as in_file:
                reader = csv.reader(in_file, lineterminator='\n')
                for i, row in enumerate(reader):
                    entry = text_util.encode_text(row[4], self.reverse_font_map, pad_to_line_count=6)
                    self.total_length += len(entry)
                    self.entries.append(entry)

        self.__typeset()

    def __typeset(self):
        self.typeset_buffer = b''

        wrap_counter = self.display_width
        for b_int in self.entries[self.current_entry]:
            b = bytes([b_int])
            if b == b'\xff':
                break
            elif b == b'\xfe':
                while wrap_counter > 0:
                    self.typeset_buffer += b'\x00'
                    wrap_counter -= 1
                wrap_counter = self.display_width
            else:
                self.typeset_buffer += b
                wrap_counter -= 1
                if wrap_counter < 0:
                    wrap_counter = self.display_width

        self.__draw()

    def __draw(self):
        self.renderer.write_tiles(bytes([1] + [2] * self.display_width + [3]), self.start_column - 1, self.start_row - 1)
        for r in range(self.start_row, self.start_row + self.display_height + 2):
            self.renderer.write_tiles(bytes([8] + [0] * self.display_width + [10]), self.start_column - 1, r)
        self.renderer.write_tiles(bytes([4] + [5] * self.display_width + [6]), self.start_column - 1, self.start_row + self.display_height + 2)

        for typeset_line in range(0, self.display_height):
            start_index = (self.current_page * self.display_height + typeset_line + self.scroll_offset) * self.display_width
            end_index = start_index + self.display_width
            self.renderer.write_tiles(self.typeset_buffer[start_index:end_index], self.start_column, self.start_row + typeset_line)

        if not self.__is_last_page():
            self.renderer.write_tiles(b'\x0f', self.start_column + self.display_width // 2, self.start_row + self.display_height + 1)

        img = self.renderer.render()
        self.tkimage = ImageTk.PhotoImage(img.resize([3 * d for d in img.size]))
        self.display.configure(image=self.tkimage)

    def __is_last_page(self):
        return (self.current_page + 1) * self.display_height * self.display_width >= len(self.typeset_buffer)

    def __on_next_page(self, event):
        if not self.__is_last_page() and self.scroll_offset == 0:
            self.current_page += 1
            self.scroll_offset = -6

            self.__on_scroll()

    def __on_prev_page(self, event):
        if self.current_page > 0 and self.scroll_offset == 0:
            self.current_page -= 1
            self.scroll_offset = 6

            self.__on_scroll()

    def __on_next_entry(self, event):
        if self.current_entry < len(self.entries) - 1 and self.scroll_offset == 0:
            self.current_entry += 1
            self.current_page = 0

            self.__typeset()

    def __on_prev_entry(self, event):
        if self.current_entry > 0 and self.scroll_offset == 0:
            self.current_entry -= 1
            self.current_page = 0

            self.__typeset()

    def __on_reload(self, event):
        self.__reload()

    def __on_scroll(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1
        elif self.scroll_offset < 0:
            self.scroll_offset += 1

        self.__draw()

        if self.scroll_offset != 0:
            self.master.after(16, self.__on_scroll)

if __name__ == '__main__':
    tk_root = tk.Tk()
    window = DisplayWindow(tk_root)
    tk_root.mainloop()
