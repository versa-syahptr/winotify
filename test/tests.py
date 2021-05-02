import unittest
import os
from winotify import Notification, audio


class MyTestCase(unittest.TestCase):
    def test_toast(self):
        toast = Notification(app_id="winotify test",
                             title="Winotify Test Toast",
                             msg="New Notification!")

        toast.build().show()
        print(toast.script)

    def test_toast_with_icon(self):
        toast = Notification(app_id="winotify test",
                             title="Winotify Test Toast With Icon",
                             msg="New Notification!",
                             icon=os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png"))

        toast.build().show()
        print(toast.script)

    def test_toast_with_sound(self):
        toast = Notification(app_id="winotify test",
                             title="Winotify Test Toast",
                             msg="New Notification!")
        toast.set_audio(audio.SMS, loop=False)

        toast.build().show()
        print(toast.script)

    def test_toast_illegal_char(self):
        toast = Notification(app_id="winotify test",
                             title="This is illegal >>",
                             msg="< [YEAH] >")

        toast.build().show()
        print(toast.script)


if __name__ == '__main__':
    unittest.main()
