import csv
import tkinter as tk

import text_util
import preview_util

class EvoOptionsPreviewDisplayWindow(preview_util.PreviewDisplayWindow):
    def __init__(self, master):
        super().__init__(master)

        self.reverse_font_map = text_util.load_map_reverse('assets/text/font.tbl')

        self.x, self.y, self.width, self.height = 2, 4, 17, 20

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
        with open('assets/text/evo_options.csv', 'r', encoding='shift-jis') as in_file:
            reader = csv.reader(in_file, lineterminator='\n')
            for i, row in enumerate(reader):
                entry = text_util.encode_text(row[4], self.reverse_font_map)
                self.entries.append(entry)

        self.__typeset()

    def __typeset(self):

        self.write_window(self.x - 1, self.y - 1, self.width + 2, self.height + 2)

        line = self.entries[self.current_entry]
        x, y = self.x, self.y
        for b in line:
            if b == 0xfe:
                x = self.x
                y += 1
            elif b == 0xff:
                break
            else:
                self.write_tiles([b], (x, y))
                x += 1

        self.refresh_display()

if __name__ == '__main__':
    tk_root = tk.Tk()
    window = EvoOptionsPreviewDisplayWindow(tk_root)
    tk_root.mainloop()
