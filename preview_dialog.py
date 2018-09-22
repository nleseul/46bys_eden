import csv
import tkinter as tk

import text_util
import preview_util

class DialogPreviewDisplayWindow(preview_util.PreviewDisplayWindow):
    def __init__(self, master):
        super().__init__(master)

        self.reverse_font_map = text_util.load_map_reverse('assets/text/font.tbl')

        self.__reload()

    def on_next_page(self, event):
        if not self.__is_last_page() and self.scroll_offset == 0:
            self.current_page += 1
            self.scroll_offset = -6

            self.__on_scroll()

    def on_prev_page(self, event):
        if self.current_page > 0 and self.scroll_offset == 0:
            self.current_page -= 1
            self.scroll_offset = 6

            self.__on_scroll()

    def on_next_entry(self, event):
        if self.current_entry < len(self.entries) - 1 and self.scroll_offset == 0:
            self.current_entry += 1
            self.current_page = 0

            self.__typeset()

    def on_prev_entry(self, event):
        if self.current_entry > 0 and self.scroll_offset == 0:
            self.current_entry -= 1
            self.current_page = 0

            self.__typeset()

    def on_reload(self, event):
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
        self.write_window(self.start_column - 1, self.start_row - 1, self.display_width + 2, self.display_height + 4)

        for typeset_line in range(0, self.display_height):
            start_index = (self.current_page * self.display_height + typeset_line + self.scroll_offset) * self.display_width
            end_index = start_index + self.display_width
            self.write_tiles(self.typeset_buffer[start_index:end_index], (self.start_column, self.start_row + typeset_line))

        if not self.__is_last_page():
            self.write_tiles(b'\x0f', (self.start_column + self.display_width // 2, self.start_row + self.display_height + 1))

        self.refresh_display()

    def __is_last_page(self):
        return (self.current_page + 1) * self.display_height * self.display_width >= len(self.typeset_buffer)

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
    window = DialogPreviewDisplayWindow(tk_root)
    tk_root.mainloop()
