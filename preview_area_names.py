import csv
import tkinter as tk

import text_util
import preview_util

class AreaNamesPreviewDisplayWindow(preview_util.PreviewDisplayWindow):
    def __init__(self, master):
        super().__init__(master)

        self.reverse_font_map = text_util.load_map_reverse('assets/text/font.tbl')

        self.base_offset, self.width = 0xe5 // 2, 22

        self.current_entry = 0

        self.__reload()

    def on_next_entry(self, event):
        if self.current_entry < len(self.entries) - 1:
            self.current_entry += 1
            self.__typeset()

    def on_prev_entry(self, event):
        if self.current_entry > 0:
            self.current_entry -= 1
            self.__typeset()

    def on_reload(self, event):
        self.__reload()

    def __reload(self):
        self.entries = []
        with open('assets/text/area_names.csv', 'r', encoding='shift-jis') as in_file:
            reader = csv.reader(in_file, lineterminator='\n')
            for i, row in enumerate(reader):
                entry = text_util.encode_text_interleaved(row[4], self.reverse_font_map)
                self.entries.append(entry)

        self.__typeset()

    def __typeset(self):

        base_x, base_y = self.__offset_to_coords(self.base_offset)

        self.write_window(base_x - 1, base_y - 1, self.width + 2, 4)

        line = self.entries[self.current_entry]
        offset = int.from_bytes(line[0:1], byteorder='little') // 2
        if offset != 0:
            x, y = self.__offset_to_coords(offset)
            line_data = line[4:]

            for i, b in enumerate(line_data):
                self.write_tiles([b], (x, y))
                if i % 2 == 0:
                    y += 1
                else:
                    y -= 1
                    x += 1


        #self.write_tiles([0x10] * self.width, (base_x, base_y))
        #self.write_tiles([0x20] * self.width, (base_x, base_y+1))

        self.refresh_display()

    def __offset_to_coords(self, offset):
        return (offset % self.display_width, offset // self.display_width)

if __name__ == '__main__':
    tk_root = tk.Tk()
    window = AreaNamesPreviewDisplayWindow(tk_root)
    tk_root.mainloop()
