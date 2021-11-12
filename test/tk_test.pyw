import tkinter, sys, os
from tkinter import ttk

from winotify import Notifier, register

appid = "tkt"
path = os.path.abspath(__file__)

registry = register(appid, script_path=path)
notifier = Notifier(registry)


root = tkinter.Tk()
big_frame = ttk.Frame(root)
big_frame.pack(fill='both', expand=True)


@notifier.register_callback
def change_text(txt="yo you click the notification"):
    label['text'] = txt


def show_notif():
    toast = notifier.create_notification("Winotify GUI Test", "click me!", launch=notifier.callback_to_url(change_text))
    toast.add_actions('print abc', notifier.callback_to_url(change_text))
    toast.add_actions('with keyword', notifier.callback_to_url(change_text))
    toast.show()
    print(toast.script)
    print(notifier.callbacks)


label = ttk.Label(big_frame, text="This is a button test.")
label.pack()
button = ttk.Button(big_frame, text="Click me!", command=show_notif)
button.pack()

root.title("Button Test")
root.geometry('200x100')
root.minsize(150, 50)

if __name__ == '__main__':
    notifier.start()
    root.mainloop()
