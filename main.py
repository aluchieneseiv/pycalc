from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.codeinput import CodeInput
from functools import partial
from newlang import State
from lexer import PycalcLexer

Builder.load_file('./main.kv')

state = State()
lexer = PycalcLexer()
lexer.state = state


class ScrollableText(ScrollView):
    def __init__(self,  **kwargs):
        super(ScrollableText, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.add_new_codeline()

        self.add_widget(self.layout)

    def add_new_codeline(self):
        codeinput = PycalcCodeInput(lexer=lexer)

        codeinput.bind(on_text_validate=lambda _: self.add_new_codeline())
        codeinput.bind(on_text_validate=lambda _: partial(self.code_interpret, codeinput=codeinput)())
        codeinput.focus = True
        
        self.layout.add_widget(codeinput)
    
    def code_interpret(self, codeinput):
        codeoutput = CodeOutput()

        codeinput.bind(on_touch_down=lambda *_: partial(self.open_output, codeoutput=codeoutput)())
        self.open_output(codeoutput)

        res, err = state.parse(codeinput.text)

        if err:
            codeoutput.text = str(err)
            codeoutput.color = (1, 0, 0, 1)
        else:
            codeoutput.text = str(res)

        self.layout.add_widget(codeoutput)

    def open_output(self, codeoutput):
        for c in self.layout.children:
            if isinstance(c, CodeOutput):
                self._hide_widget(c, True)
        
        self._hide_widget(codeoutput, False)


    def _hide_widget(self, wid, dohide=True):
        if hasattr(wid, 'saved_attrs'):
            if not dohide:
                wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
                del wid.saved_attrs
        elif dohide:
            wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True


class AppView(BoxLayout):
    pass

class CodeOutput(Label):
    pass

class PycalcCodeInput(CodeInput):
    pass

class CalcPyApp(App):
    def build(self):
        return AppView()

if __name__ == '__main__':
    CalcPyApp().run()
