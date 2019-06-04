# https://stackoverflow.com/a/19581754/4212158
import cairo
import gtk
from PIL import Image
import time
import string
import random
import os
import gobject, threading
from utils import XboxController
import csv

gobject.threads_init()

SREENSHOT_SAVE_DIR
ABS_PATH = os.path.abspath(os.path.dirname(__file__))
VID_DIR = os.path.join(ABS_PATH, 'data/')


def rand_name(len_ = 4):
    """generates a random string for naming recording sessions"""
    return ''.join(random.SystemRandom().choice(string.ascii_letters + string.digits) for _ in range(len_))


class Recording_Window(gtk.Window):
    """draw transparent window"""
    def __init__(self):
        super(Recording_Window, self).__init__()

        self.currently_recording = False

        # Init controller
        self.controller = XboxController()

        # stuff for window drawing
        self.width = 640
        self.height = 480
        self.set_gravity(gtk.gdk.GRAVITY_STATIC)
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_title('Place me over recording area')
        self.set_size_request(self.width, self.height)
        self.set_border_width(11)
        self.screen = self.get_screen()
        colormap = self.screen.get_rgba_colormap()
        if (colormap is not None and self.screen.is_composited()):
            self.set_colormap(colormap)

        self.set_app_paintable(True)
        self.connect("expose-event", self.area_draw)
        self.show_all()

        # button stuff
        self.connect('delete_event', self.delete_event)
        self.connect('destroy', self.destroy)

        # key presses
        self.connect("key-press-event", self.on_window_key_press_event)

        # self.box = gtk.HBox()
        # self.box.set_size_request(20, 5)

        # self.record_button = gtk.ToggleButton('Press to start a recording session')
        # self.record_button.connect('toggled', self.toggle_recording, 'record_button')
        self.show_all()

        # stuff for screenshots
        self._window = gtk.gdk.get_default_root_window()
        self._pb = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, False, 8, self.width, self.height)

    def on_window_key_press_event(self, widget, event):
        key = gtk.gdk.keyval_name(event.keyval)
        print("{} button pressed".format(key))
        if key in ['Return', 'space']:
            self.toggle_recording(None, None)

    def area_draw(self, widget, event):
        cr = widget.get_window().cairo_create()
        cr.set_source_rgba(.2, .2, .2, 0.3)
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        return False

    def screenshot(self):
        """takes a single screenshot within the window box"""
        x, y = self.get_position()
        pb = self._pb.get_from_drawable(self._window, self._window.get_colormap(), x, y, 0, 0, self.width, self.height)
        image = Image.frombuffer('RGB', (self.width, self.height), pb.get_pixels(), 'raw', 'RGB', pb.get_rowstride(), 1)
        return image

    def toggle_recording(self, event, widget):
        """ FIXME this should start and stop self.record_video"""
        if self.currently_recording:
            self.currently_recording = False
            self.set_title('Recording stopped. Press space or enter to start a new session.')
        else:
            self.currently_recording = True
            self.set_title('[RECORDING]. Press space or enter to stop.')
            self.record_data()

    def record_data(self):
        """takes screenshots at a given FPS"""
        save_interval = 1.0 / FPS
        start_time = time.time()

        # put each recording sess in its own folder
        session_dir = os.path.join(VID_DIR, rand_name())
        print("new session recording at {}".format(session_dir))
        try:
            os.makedirs(session_dir)
        except OSError:
            if not os.path.isdir(session_dir):
                raise

        controller_data_path = os.path.join(session_dir, 'controller_inputs.csv')

        # start recording
        # while loops are not the way to go: https://stackoverflow.com/a/13108681/4212158
        while self.currently_recording:

            now = time.time()
            elapsed = now - start_time
            time.sleep(save_interval - (elapsed % save_interval))  # record ss at correct FPS

            ss = self.screenshot()
            controller_data = self.controller.read()
            controller_data = [elapsed] + controller_data
            print(controller_data)
            # save inputs
            with open(controller_data_path, 'a') as csv_file:
                wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)
                wr.writerow(controller_data)

            # save ss
            # note: label data with "elapsed" so that everything is sync'd in case we need
            # to trim the start/end
            img_dir = os.path.join(session_dir, 'img_{}.png'.format(str(elapsed)))
            ss.save(img_dir)


    def delete_event(self, widget, event, data=None):
        print('window was closed')
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()


if __name__=='__main__':
    my_window = Recording_Window()
    # print(my_window.get_position())  # (0,0)
    my_window.main()
