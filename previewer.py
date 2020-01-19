import os

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

        self._reverse_font_map = None
        self._font_buffer = None
        self._text_buffer = None



    def build_config(self, config):
        config.setdefaults("previewer", {
            "data_path": "."
        })

    def build_settings(self, settings):
        settings_json = """
        [
            { "type": "path",
              "title": "Data path",
              "desc": "The root path of the 46BYS project data to use.",
              "section": "previewer",
              "key": "data_path" }
        ]
        """

        settings.add_json_panel('Previewer settings', self.config, data=settings_json)

    def build(self):
        empty_window = bytearray(b'\x01' + b'\x02' * WIDTH + b'\x03' + \
                                 (b'\x08' + b'\x00' * WIDTH + b'\x0a') * LINES + \
                                 b'\x04' + b'\x05' * WIDTH + b'\x06')
        self._text_buffer = Buffer(empty_window)

        self._encoded_text = None
        self._current_page = 0



        map_source = BufferInterpreter(24, 'P', self._text_buffer)
        palette_source = BufferInterpreter(1, "RGB",
                                           Buffer(bytearray(b'\x00\x00\x73\x00\x00\x00\x7d\x7d\x7d\xff\xff\xff')))

        mapper = TileMapper(map_source, None, palette_source)

        self.pixel_provider = mapper

        self._load_common_assets()

    def on_config_change(self, config, section, key, value):
        self._load_common_assets()

    def on_text_changed(self, text):
        if self._reverse_font_map is not None:
            self._encoded_text = text_util.encode_text(text, self._reverse_font_map, pad_to_line_count=LINES).split(b'\xfe')

        self._redraw_text()

    def scroll_to_line(self, line):
        new_page = line // LINES
        if new_page != self._current_page:
            self._current_page = new_page

        self._redraw_text()

    def _load_common_assets(self):
        data_path = self.config.get('previewer', 'data_path')

        try:
            self._reverse_font_map = text_util.load_map_reverse(os.path.join(data_path, 'assets/text/font.tbl'))
            self._font_buffer = Buffer(open(os.path.join(data_path, 'assets/gfx/font.bin'), 'rb').read())

            self.pixel_provider.tile_source = BitplaneInterpreter(self._font_buffer, 2, 1)

        except FileNotFoundError:
            self._reverse_font_map = None
            self._font_buffer = None

            self.pixel_provider.tile_source = None

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
            writer.write((line_index - current_line + 1) * (WIDTH + 2) + 1, line.ljust(WIDTH, b'\x00')[:WIDTH])
        writer.end_write()

if __name__ == '__main__':
    PreviewerApp().run()
    pass
