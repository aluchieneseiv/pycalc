from re import sub

from kivy.app import App
from kivy.clock import Clock
from kivy.core.text import LabelBase
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.garden.navigationdrawer import NavigationDrawer
from kivy.lang import Builder
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.codeinput import CodeInput, TextInput
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from matplotlib.pyplot import gcf
from numpy import ndarray
from pygments.styles import get_style_by_name
from kivy.clock import Clock

from lexer import PycalcLexer, PycalcStyle
from newlang import State
from kivy.uix.popup import Popup

from matplotlib.figure import Figure

from kivy.storage.jsonstore import JsonStore
from functools import partial

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
    codeinput_touced_ind = [-1, -1]

    def __init__(self,  **kwargs):
        super(ScrollableText, self).__init__(**kwargs)

        self.layout = BoxLayout(orientation='vertical',
                                spacing=10, size_hint_y=None)
        self.layout.bind(minimum_height=self.layout.setter('height'))

        self.add_new_codeline()

        self.add_widget(self.layout)

    def add_new_codeline(self, ind=0):
        codeinput = PycalcCodeInput(lexer=lexer, style=style)

        codeinput.bind(on_text_validate=lambda _: self.code_interpret(codeinput))

        codeinput.bind(
            on_touch_down=self.twin_touch_start,
            on_touch_up=self.twin_touch_stop)

        codeinput.focus = True
        if ind == 0:
            codeinput.ind = len(self.layout.children)
        else:
            codeinput.ind = len(self.layout.children) - ind

        self.layout.add_widget(codeinput, index=ind)

    def twin_touch_start(self, instance, touch):
        if not instance.collide_point(*touch.pos):
            return

        if instance == self.layout.children[0]:
            return

        if self.codeinput_touced_ind == [-1, -1]:
            touch.ud['touch_ind'] = 0
            self.codeinput_touced_ind[0] = instance.ind
        else:
            touch.ud['touch_ind'] = 1
            self.codeinput_touced_ind[1] = instance.ind
        
        if self.codeinput_touced_ind != [-1, -1] and abs(self.codeinput_touced_ind[0] - self.codeinput_touced_ind[1]) == 2:
            ind_max = max(self.codeinput_touced_ind)

            for wid in self.layout.children:
                if hasattr(wid, 'ind') and wid.ind >= ind_max:
                    wid.ind += 2

            self.add_new_codeline(len(self.layout.children)-ind_max)

            self.codeinput_touched_ind = [-1, -1]

            return True

    def twin_touch_stop(self, instance, touch):
        if 'touch_ind' in touch.ud:
            self.codeinput_touced_ind[touch.ud['touch_ind']] = -1
            del touch.ud['touch_ind']

    def reinterpret_line(self, codeinput):
        if len(codeinput.text.strip()) == 0:
            if hasattr(codeinput, 'out'):
                self.layout.remove_widget(codeinput.out)
            self.layout.remove_widget(codeinput)

            for wid in list(reversed(self.layout.children))[codeinput.ind:]:
                if hasattr(wid, 'ind'):
                    wid.ind -= 2
            return

        res, err = state.parse(codeinput.text)

        if hasattr(codeinput, 'out'):
            self.print_output(codeinput.out, res, err)
        else:
            self.make_output(codeinput, res, err)

    def print_output(self, co, res, err):
        self._hide_widget(co, False)
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
        self._hide_widget(co, True)

    def code_interpret(self, codeinput):
        global state
        global lexer
        if codeinput != self.layout.children[0]:
            state = State()
            lexer.state = state

            for ci in reversed(self.layout.children):
                if isinstance(ci, CodeInput) and ci != self.layout.children[0]:
                    self.reinterpret_line(ci)
                    ci._trigger_refresh_text()

            if hasattr(codeinput, 'out'):
                self.open_output(codeinput.out)

            return

        if len(codeinput.text.strip()) == 0:
            return

        res, err = state.parse(codeinput.text)

        self.make_output(codeinput, res, err)

        self.add_new_codeline()

    def make_output(self, codeinput, res, err):
        codeoutput = CodeOutput()

        codeinput.bind(on_touch_down=lambda *_: self.open_output(codeoutput))

        self.print_output(codeoutput, res, err)
        self.open_output(codeoutput)

        codeinput.out = codeoutput
        ind = len(self.layout.children) - codeinput.ind - 1
        self.layout.add_widget(codeoutput, ind)

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
    def size_update(self, **kwargs):
        self.texture_update()
        self.size = self.texture_size


class PycalcCodeInput(CodeInput):
    pass


class CalcPyApp(App):
    def build(self):
        self.store = JsonStore('scripts.json')

        self.appview = NavigationDrawer() 
        self.appview.anim_type = 'reveal_below_anim'

        side_panel = BoxLayout(orientation='vertical')

        title = Label(text='Pycalc')
        title.size = self.appview.width, 30
        title.size_hint_y = None
        side_panel.add_widget(title)

        new_btn = Button(text='New Script')
        new_btn.size = self.appview.width, 50
        new_btn.size_hint_y = None
        new_btn.bind(on_press=lambda _: self.new_script())
        side_panel.add_widget(new_btn)

        s_in = TextInput()
        s_in.multiline = False
        s_in.size = self.appview.width, 50
        s_in.size_hint_y = None

        def show_s_in():
            s_in.height, s_in.opacity, s_in.disabled = 50, 1, False
            save_btn.height, save_btn.opacity, save_btn.disabled = 0, 0, True
            def focus():
                s_in.focus = True
            Clock.schedule_once(lambda dt: focus(), 0.1)
        def hide_s_in(x = False):
            if x:
                return
            s_in.height, s_in.opacity, s_in.disabled = 0, 0, True
            save_btn.height, save_btn.opacity, save_btn.disabled = 50, 1, False

        save_btn = Button(text='Save Script')
        save_btn.size = self.appview.width, 50
        save_btn.size_hint_y = None
        save_btn.bind(on_press=lambda _: show_s_in())
        side_panel.add_widget(save_btn)

        s_in.bind(on_text_validate= lambda instance: self.save_script(instance.text.strip()))
        s_in.bind(focused=lambda _, x: hide_s_in(x))
        hide_s_in()

        side_panel.add_widget(s_in)

        load_btn = Button(text='Load Script')
        load_btn.size = self.appview.width, 50
        load_btn.size_hint_y = None
        load_btn.bind(on_press=lambda _: self.load_script())
        side_panel.add_widget(load_btn)

        self.appview.add_widget(side_panel)

        self.main_panel = ScrollableText()
        self.appview.add_widget(self.main_panel)

        return self.appview

    def new_script(self):
        global state
        global lexer
        state = State()
        lexer.state = state
        self.main_panel.layout.clear_widgets()
        self.main_panel.add_new_codeline()

    def save_script(self, name):
        lines = []
        for wid in reversed(self.main_panel.layout.children):
            if isinstance(wid, CodeInput) and len(wid.text) > 0:
                lines.append(wid.text)

        if len(lines) > 0:
            self.store.put(name, data=lines)
    
    def load_script(self):
        popup = Popup(title='Load script')

        def want_delete(btn, choice_callback, _):
            def delete(name):
                self.store.delete(name)
                btn.height, btn.opacity, btn.disabled = 0, 0, True

            saved_text = btn.text
            callback = lambda _: delete(saved_text)

            def lost_focus(_):
                btn.text = saved_text
                btn.color = (1, 1, 1, 1)
                btn.unbind(on_press=callback)
                btn.bind(on_release=choice_callback)

            btn.text = 'delete?'
            btn.color = (1, 0, 0, 1)
            btn.bind(on_press=callback)
            Clock.schedule_once(lost_focus, 2)
            btn.unbind(on_release=choice_callback)

        def create_clock(self, touch, widget, choice_callback, *args):
            if not widget.collide_point(*touch.pos):
                return False

            callback = partial(want_delete, widget, choice_callback)
            Clock.schedule_once(callback, 0.5)
            touch.ud['event'] = callback


        def delete_clock(self, touch, widget, *args):
            if not self.collide_point(*touch.pos):
                return
            if 'event' in touch.ud:
                Clock.unschedule(touch.ud['event'])
                del touch.ud['event']

        def choice(name):
            self.new_script()

            data = self.store.get(name)['data']

            for line in data:
                codeinput = self.main_panel.layout.children[0]

                codeinput.text = line
                self.main_panel.code_interpret(codeinput)

            popup.dismiss()

        content = BoxLayout(orientation='vertical')
        for item in self.store:
            btn = Button(text=item)
            btn.size= content.width, 50
            btn.size_hint_y = None

            choice_callback = lambda _:choice(item)
            btn.bind(
                on_touch_down=partial(create_clock, widget=btn, choice_callback=choice_callback),
                on_touch_up=partial(delete_clock, widget=btn))
            btn.bind(on_release=choice_callback)
            content.add_widget(btn)
        close_btn = Button(text='Cancel')
        close_btn.size_hint = 0.3, None
        close_btn.height = 50
        close_btn.bind(on_press=popup.dismiss)
        content.add_widget(close_btn)
        popup.content = content

        popup.open()


if __name__ == '__main__':
    CalcPyApp().run()
