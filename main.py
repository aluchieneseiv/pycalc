from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput

from newlang import State

Builder.load_file('./main.kv')

state = State()

class TextLine(RelativeLayout):

    def code_interpret(self):
        codeinput = self.children[1]
        codeoutput = self.children[0]

        res, err = state.parse(codeinput.text)

        if err:
            codeoutput.text = str(err)
            codeoutput.color = (1, 0, 0, 1)
        else:
            codeoutput.text = str(res)


class ScrollableText(ScrollView):
    def __init__(self,  **kwargs):
        super(ScrollableText, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.add_new_textline()

        self.add_widget(self.layout)

    def add_new_textline(self):
        textline = TextLine()

        codeinput = textline.children[1]

        codeinput.bind(on_text_validate=lambda _: self.add_new_textline())
        codeinput.bind(on_text_validate=lambda _: textline.code_interpret())
        codeinput.focus = True
        
        self.layout.add_widget(textline)

class AppView(BoxLayout):
    pass

class CodeOutput(Label):
    pass

class CodeInput(TextInput):
    pass

class CalcPyApp(App):
    def build(self):
        return AppView()

if __name__ == '__main__':
    CalcPyApp().run()
