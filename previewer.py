from kivy.app import App
from kivy.properties import ObjectProperty

from pyy_chr.core import Buffer, BitplaneInterpreter, BufferInterpreter, ColorGradient, TileMapper

import text_util

LINES = 6
WIDTH = 22

class PreviewerApp(App):
    pixel_provider = ObjectProperty()

    def __init__(self):
        super(PreviewerApp, self).__init__()

        print(self.directory)

        self._reverse_font_map = text_util.load_map_reverse('assets/text/font.tbl')

        empty_window = bytearray(b'\x01' + b'\x02' * WIDTH + b'\x03' +\
                                 (b'\x08' + b'\x00' * WIDTH + b'\x0a') * LINES +\
                                 b'\x04' + b'\x05' * WIDTH + b'\x06')

        self._text_buffer = Buffer(empty_window)
        self._encoded_text = None
        self._current_page = 0

        buffer = Buffer(open('assets/gfx/font.bin', 'rb').read())

        map_source = BufferInterpreter(24, 'P', self._text_buffer)
        tile_source = BitplaneInterpreter(buffer, 2, 1)
        palette_source = ColorGradient('RGB', (0, 0, 0), (255, 255, 255), 4)

        mapper = TileMapper(map_source, tile_source, palette_source)

        self.pixel_provider = mapper

    def on_text_changed(self, text):
        self._encoded_text = text_util.encode_text(text, self._reverse_font_map, pad_to_line_count=LINES).split(b'\xfe')

        self._redraw_text()

    def scroll_to_line(self, line):
        new_page = line // LINES
        if new_page != self._current_page:
            self._current_page = new_page

        self._redraw_text()

    def _redraw_text(self):
        if self._encoded_text is None:
            return

        current_line = self._current_page * LINES

        writer = self._text_buffer.begin_write()
        for line_index, line in enumerate(self._encoded_text):
            if line_index < current_line:
                continue
            if line_index >= current_line + LINES:
                break
            writer.write((line_index - current_line + 1) * (WIDTH + 2) + 1, line.ljust(WIDTH, b'\x00'))
        writer.end_write()

if __name__ == '__main__':
    PreviewerApp().run()
    pass