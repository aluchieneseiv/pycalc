from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.anchorlayout import AnchorLayout
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from kivy.lang import Builder
from kivy.uix.label import Label
from newlang import State

Builder.load_string('''
<AppView>:
    orientation: 'vertical'
    ActionBar:
        pos_hint: {'top':1}
        ActionView:
            use_separator: True
            ActionPrevious:
                title: 'CalcPy'
                with_previous: False
            ActionOverflow:
            ActionButton:
                important: True
                text: 'Clear'
            ActionGroup:
                ActionButton:
                    text: 'Save'
                ActionButton:
                    text: 'Load'
    ScrollableText:

<ScrollableText>:
    BoxLayout:
        size_hint_y: None
        orientation: 'vertical'
        height: self.minimum_height

        TextLine:
        TextLine:
        TextLine:
        TextLine:
        TextLine:
        TextLine:
        TextLine:
        TextLine:
        TextLine:
        TextLine:
        
<TextLine>:
    input: "test input"
    output: "test output"
    focused: input.focused
    size_hint_y: None
    orientation: 'vertical'
    height: self.minimum_height
    TextInput:
        id: input
        size_hint_y: None
        multiline: False
        height: self.font_size * 1.25 + 10
        text: root.input
        foreground_color: (1, 1, 1, 1)
        cursor_color: (0.8, 0.8, 0.8, 0.9)
        background_color: (0.2, 0.2, 0.2, 1) if self.focus else (0.1, 0.1, 0.1, 1)
    TextOutput:
        output: "oof test\\n" * 3

<TextOutput>:
    size_hint_y: None
    id: label
    height: self.texture_size[1]
    text_size: self.width, None
    text: self.output
    padding: 5, 5
''')

state = State()

class TextLine(BoxLayout):
    input = StringProperty()
    output = StringProperty()

class ScrollableText(ScrollView):
    pass

class AppView(BoxLayout):
    pass

class TextOutput(Label):
    output = StringProperty()

class CalcPyApp(App):
    def build(self):
        return AppView()

if __name__ == '__main__':
    CalcPyApp().run()
