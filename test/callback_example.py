"""
this is an example how to implement the callback feature in winotify
"""

import os
import sys

import winotify
from winotify import Notification

ID = "app name"


@winotify.callback
def notif():
    Notification(ID, "notif() called!", ", ".join(sys.argv)).build().show()


if __name__ == '__main__':
    # winotify.initialize must be called first in main
    winotify.initialize(ID, sys.executable + ' ' + os.path.abspath(__file__))

    toast = Notification("initial notif", "OK")
    toast.add_actions("notif()", callback=notif)
    toast.build().show()



