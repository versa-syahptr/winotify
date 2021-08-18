"""
this is an example how to implement the callback feature in winotify
"""

import time
import sys

import winotify

# instantiate Notifier class
app_id = "winotify test"
app_path = sys.executable + ' ' + __file__

notifier = winotify.Notifier(app_id, app_path)


@notifier.callback
def do_somethin():
    print('yo hey')
    for x in range(3, 0, -1):
        print(f"toast in {x} secs")
        time.sleep(1)

    toast = notifier.create_notification("a new notification", "this is called from another thread",
                                         launch=notifier.callback_to_url(quit_))
    toast.build().show()


@notifier.callback  # register quit func
def quit_():
    # this wont work if called from the thread
    sys.exit()


if __name__ == '__main__':
    notifier.start()

    # no need to specify app_id every time
    toast = notifier.create_notification("a notification", 'a notification test with callback',
                                         launch=notifier.callback_to_url(do_somethin))
    # generic url still works
    toast.add_actions("Open Github", "https://github.com/versa-syahptr/winotify")
    toast.add_actions("Quit app", notifier.callback_to_url(quit_))
    toast.build().show()

    print(toast.script)

    while True:
        time.sleep(1)
        print("i'm running")







