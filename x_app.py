# __version__ = "0.121"
import kivy

kivy.require('1.11.1')
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty, NumericProperty
from kivy.logger import Logger
from kivy.config import Config
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.core.text import Label as CoreLabel
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.app import App
from kivy.graphics import Color, RoundedRectangle
from kivy.uix.widget import Widget
from functools import partial
from kivy.animation import Animation
from kivy.uix.scrollview import ScrollView
from kivy.graphics.texture import Texture,TextureRegion
from kivy.core.image import Image as CoreImage

Config.set('kivy', 'log_level', 'debug')
import threading
import pickle
import socket
import io, os, re


class Fetching_title(threading.Thread):
    def __init__(self, func, page):
        super(Fetching_title, self).__init__()
        self._func = func
        self._page = page

    def run(self):
        title = os.path.basename(self._page)
        title_img = os.path.join(self._page, x_screen_1App.APP_TITLE_IMG)
        self._func((title, title_img))


class Fetching_txt(threading.Thread):
    def __init__(self, screen: 'ScreenTwo'):
        super(Fetching_txt, self).__init__()
        self.screen = screen
        self.messager = None
        self.current_line_num = 0



    def run(self):
        # Logger.debug(self.screen.screen_container.size)
        check_height = self.screen.page.size[1]
        # self.screen.ready_enent.set()
        self.is_new_page=True
        self.is_new_mix=False
        #前一个文字标签
        self.pre_c:'Label'=None
        new_c=None
        self.new_label=None
        self.exceed_line=''
        self.current_line=''

        def bind_func(inst, vlu):
            Logger.debug(f'readed label height change to {vlu}')
            if vlu[1] > (self.screen.page.size[1] - 0.1*self.screen.height):
                anim1 = Animation(x=-self.screen.move_l.size[0], y=self.screen.move_l.pos[1], duration=5)
                anim2 = Animation(x=self.screen.size[0], y=self.screen.move_r.pos[1], duration=5)


                anim1.start(self.screen.move_l)
                anim2.start(self.screen.move_r)
                return
                # self.exceed_line=self.current_line
                # self.screen.page_remove_label(new_c, new_label, current_line)
                #
                # # Clock.schedule_once(lambda dt:self.screen.messager1.display_message(self.screen.messager2.pos, f'载入{len(self.screen.page_list)}页f', timeout=0),
                # #                     0)
                # if not bool(self.messager):
                #     self.messager = self.screen.messager1
                #     self.messager.loop_message(self.screen.messager2.pos, f'载入行数{self.current_line_num}...', timeout=0)
                # else:
                #     self.messager.text=f'载入行数{self.current_line_num}'
                #
                # # return
                # self.is_new_page=True
                # self.pre_c=self.new_label
            self.screen.ready_event.set()


        with open(self.screen.f_path) as f:
            for line in f:
                if self.screen.stop_reading_event.isSet():
                    Logger.debug(f'fetching txt stop')
                    return
                self.current_line_num += 1
                if self.is_new_page:
                    self.is_new_page=False
                    new_c=self.screen.page_add_newpage()
                    new_label=Page_label()
                    new_c.add_widget(new_label)
                    if bool(self.pre_c):
                        self.pre_c.unbind(texture_size=bind_func)
                    new_label.bind(texture_size=bind_func)

                if not bool(line.rsplit()):
                    continue
                current_line=line
                if bool(self.exceed_line):
                    line+=self.exceed_line
                self.screen.page_add_label(new_c, new_label, line)
                self.screen.ready_event.wait()
                self.screen.ready_event.clear()
"""            FloatLayout:
                AnchorLayout:
                    anchor_x:'left'
                    anchor_y:'top'

                AnchorLayout:
                    anchor_x:'center'
                    anchor_y:'top'
                    Page:
                        id:page
                AnchorLayout:
                    anchor_x:'right'
                    anchor_y:'top'
                    size_hint_x:0.2
"""


class Txt_Img(BoxLayout):
    pass


class Page(BoxLayout):
    pass


class Item_Container(BoxLayout):
    lable_img = ObjectProperty(None)
    lable_txt = ObjectProperty(None)
    # lable_source = StringProperty('')
    lable_title = StringProperty('这里是标题')
    parent_screen = ObjectProperty(None)

    @mainthread
    def set_lable(self, data):
        self.lable_img.source = data[1]
        self.lable_title = data[0] * 100

    def setup_item(self):
        t_img = Fetching_title(self.set_lable, self.page_path)
        t_img.start()

    def __init__(self, page_path, root_screen, **kwargs):
        super(Item_Container, self).__init__(**kwargs)
        self.parent_screen = root_screen
        self.page_path = page_path
        self.height = Window.size[1] / 8
        self.setup_item()


class Items_Layout(GridLayout):
    parent_screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Items_Layout, self).__init__(**kwargs)
        try:
            with os.scandir(path='./asset') as it:
                _l = [_it.path for _it in it if bool(_it.is_dir() and re.match(r't_.*', _it.name))]
                _l.sort(key=os.path.getctime, reverse=True)
                self._page_list = _l
        except Exception as e:
            Logger.error(e)
            self._page_list = []
        threading.Thread(target=self.setup_items).start()

    @mainthread
    def setup_items(self):
        Logger.debug('setup screen 1 items')
        for fo in self._page_list:
            self.add_widget(Item_Container(fo, self.parent_screen))


class Popup_message(Label):
    bg_alhpa = NumericProperty(0)

    def __init__(self, **kwargs):
        super(Popup_message, self).__init__(**kwargs)

    def loop_message(self, start_pos, message_txt='messager txt', timeout=2):
        self.text = message_txt
        self.pos = start_pos
        self.opacity = 1
        self.disabled = False

        def _lamb(dt):
            # Logger.debug(f'message texture size{self.texture_size}')
            _x = -(self.width / 2 + self.texture_size[0] / 2) if self.texture_size[0] < self.width else - \
            self.texture_size[0]
            anim1=Animation(x=_x, y=self.pos[1], duration=5)
            anim2=Animation(x=start_pos[0], y=start_pos[1], duration=0)
            anim =anim1+anim2
            anim.repeat=True
            anim.start(self)

        Clock.schedule_once(_lamb, -1)

        if bool(timeout):
            Clock.schedule_once(lambda dt: self.hide(), timeout)

    def hide(self):
        self.opacity = 0
        self.disabled = True

    def show(self):
        self.opacity = 0
        self.disabled = True

class Page_container(BoxLayout):
    pass


class Page_label(Label):
    pass


class ScreenTwo(Screen):
    f_path = StringProperty('')
    messager1 = ObjectProperty(None)
    messager2 = ObjectProperty(None)
    page_count=NumericProperty()
    page = ObjectProperty(None)
    move_l=ObjectProperty(None)
    move_r=ObjectProperty(None)


    def __init__(self, **kwargs):
        super(ScreenTwo, self).__init__(**kwargs)
        self.stop_reading_event = threading.Event()
        self.ready_event=threading.Event()
        # self.ready_enent = threading.Event()
        self.page_list = []
        self.current_pagecontainer=None
        pass

    def test_on_enter(self, item_pos):

        _f = os.path.join(item_pos, 'details.txt')
        Logger.debug(f'Entering {item_pos}')
        self.stop_reading_event.clear()
        if os.path.isfile(_f):
            self.f_path = _f
        else:
            self.messager1.(f'无文件{_f}')
            return
            # _p._txt.text=','.join(str(a) for a in range(5))
            # self.screen_container.add_widget(_p)
        if bool(self.page_list):
            self.page_list.clear()

        Fetching_txt(self).start()
        # Clock.schedule_once(partial(_p.test,self.screen_container), -1)
        # Clock.schedule_once(lambda dt: _t.start(), 1)
        pass

    def page_add_newpage(self):
        new_page_container = Page_container()
        self.page.add_widget(new_page_container)
        self.page_list.append(new_page_container)
        self.page_count=len(self.page_list)
        return new_page_container


    @mainthread
    def page_add_label(self, container: 'Page_container', current_label: 'Page_label', new_txt: str, new_lnum: int = 0):
        current_label.text += new_txt

        pass

    @mainthread
    def page_remove_label(self, container: 'Page_container', current_label: 'Page_label', new_txt: str, new_lnum: int = 0):
        current_label.text = current_label.text.replace(new_txt,'')
        pass


    def on_leave(self):
        self.stop_reading_event.set()
        pass

    def remove_pages(self):
        for p in self.page_list:
            self.page.remove_widget(p)

    def onBackBtn(self):
        self.stop_reading_event.set()
        self.remove_pages()
        Logger.debug(f'back to screen 1')
        # self.manager.current = self.manager.list_of_prev_screens.pop()
        self.manager.current = 'screen1'


class ScreenOne(Screen):
    current_pos = NumericProperty(0)

    def onNextScreen(self, item_pos):
        # self.manager.list_of_prev_screens.append(btn.parent.name)
        self.manager.current = 'screen2'
        self.manager.screen_two.test_on_enter(item_pos)
        Logger.debug(f'pass {item_pos} to player')


class Manager(ScreenManager):
    transition = NoTransition()
    screen_one = ObjectProperty(None)
    screen_two = ObjectProperty(None)
    screen_three = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        # list to keep track of screens we were in
        # self.list_of_prev_screens = []


class x_screen_1App(App):
    """0 small 1 middle 2 big"""
    APP_FONT_SIZE = 0
    """0-dark 1-light"""
    APP_COLOR_SET = 0
    APP_TITLE_IMG = 'Tulips.jpg'
    APP_TXT = 'details.txt'

    def build(self):
        return Manager()


if __name__ == "__main__":
    x_screen_1App().run()
