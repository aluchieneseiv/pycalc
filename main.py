from functools import partial
from re import sub

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from matplotlib.pyplot import gcf
from numpy import ndarray
from pygments.styles import get_style_by_name

from lexer import PycalcLexer, PycalcStyle
from newlang import State

from matplotlib.figure import Figure

Builder.load_file('./main.kv')

state = State()
lexer = PycalcLexer()
lexer.state = state

style = PycalcStyle

FONTS = [
    {
        "name": "VeraMono",
        "fn_regular": "fonts/VeraMono.ttf",
        "fn_bold": "fonts/VeraMono-Bold.ttf",
        "fn_italic": "fonts/VeraMono-Italic.ttf",
        "fn_bolditalic": "fonts/VeraMono-Bold-Italic.ttf"
    }
]

for font in FONTS:
    LabelBase.register(**font)


class ScrollableText(ScrollView):
    def __init__(self,  **kwargs):
        super(ScrollableText, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical',
                                spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.add_new_codeline()

        self.add_widget(self.layout)

    def add_new_codeline(self):
        codeinput = PycalcCodeInput(lexer=lexer, style=style)

        codeinput.bind(on_text_validate=lambda _: partial(
            self.code_interpret, codeinput=codeinput)())
        codeinput.focus = True
        codeinput.ind = len(self.layout.children)

        self.layout.add_widget(codeinput)

    def reinterpret_line(self, codeinput):
        res, err = state.parse(codeinput.text)

        self.print_output(codeinput.out, res, err)

    def print_output(self, co, res, err):
        co.clear_widgets()

        if err:
            co.text = str(err)
            co.color = (1, 0, 0, 1)
        else:
            if isinstance(res, ndarray):
                co.text = ' ' + sub(r'[\[\]]', '', str(res))
            elif isinstance(res, Figure):
                plot_widget = FigureCanvasKivyAgg(res)
                plot_widget.size = self.size
                co.size = plot_widget.size
                co.add_widget(plot_widget)
                return
            else:
                co.text = str(res)
            co.color = (1, 1, 1, 1)

        co.text_size = self.width, None
        co.size_update()

    def code_interpret(self, codeinput):
        global state
        global lexer
        if codeinput.ind != len(self.layout.children) - 1:
            state = State()
            lexer.state = state

            for ci in reversed(self.layout.children):
                if isinstance(ci, CodeInput) and ci.ind < len(self.layout.children) - 1:
                    self.reinterpret_line(ci)
                    ci._trigger_refresh_text()

            return

        codeoutput = CodeOutput()

        codeinput.bind(
            on_touch_down=lambda *_: partial(self.open_output, codeoutput=codeoutput)())
        self.open_output(codeoutput)

        res, err = state.parse(codeinput.text)

        self.print_output(codeoutput, res, err)

        codeinput.out = codeoutput
        self.layout.add_widget(codeoutput)
        self.add_new_codeline()

    def open_output(self, codeoutput):
        for c in self.layout.children:
            if isinstance(c, CodeOutput):
                self._hide_widget(c, True)

        self._hide_widget(codeoutput, False)

    def _hide_widget(self, wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity
            wid.height, wid.size_hint_y, wid.opacity = 0, None, 0


class AppView(BoxLayout):
    pass


class CodeOutput(Label):
    def size_update(self, **kwargs):
        self.texture_update()
        self.size = self.texture_size


class PycalcCodeInput(CodeInput):
    pass


class CalcPyApp(App):
    def build(self):
        return AppView()


if __name__ == '__main__':
    CalcPyApp().run()
