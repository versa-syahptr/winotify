import queue

from winotify import audio
from winotify._registry import Registry, format_name
from winotify.communication import Listener, Sender

import os
import subprocess
import sys
import atexit
from tempfile import gettempdir
from typing import Callable, Union


TEMPLATE = r"""
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
[Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$Template = @"
<toast {launch} duration="{duration}">
    <visual>
        <binding template="ToastImageAndText02">
            <image id="1" src="{icon}" />
            <text id="1"><![CDATA[{title}]]></text>
            <text id="2"><![CDATA[{msg}]]></text>
        </binding>
    </visual>
    <actions>
        {actions}
    </actions>
    {audio}
</toast>
"@

$SerializedXml = New-Object Windows.Data.Xml.Dom.XmlDocument
$SerializedXml.LoadXml($Template)

$Toast = [Windows.UI.Notifications.ToastNotification]::new($SerializedXml)
$Toast.Tag = "{tag}"
$Toast.Group = "{group}"

$Notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{app_id}")
$Notifier.Show($Toast);
"""

tempdir = gettempdir()


def _run_ps(*, file='', command=''):
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    cmd = ["powershell.exe", "-ExecutionPolicy", "Bypass"]
    if file and command:
        raise ValueError
    elif file:
        cmd.extend(["-file", file])
    elif command:
        cmd.extend(['-Command', command])
    else:
        raise ValueError

    subprocess.Popen(
        cmd,
        # stdin, stdout, and stderr have to be defined here, because windows tries to duplicate these if not null
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,  # set to null because we don't need the output :)
        stderr=subprocess.DEVNULL,
        startupinfo=si
    )


class Notification(object):
    def __init__(self,
                 app_id: str,
                 title: str,
                 msg: str = "",
                 icon: str = "",
                 duration: str = 'short',
                 launch: str = ''):
        """
        Notification class

        :param app_id: your app name, make it readable to your user. It can contain spaces, however special characters
                       (eg. é) are not supported.
        :param title: The heading of the toast.
        :param msg: The content/message of the toast.
        :param icon: An optional app_path to an image on the OS to display to the left of the title & message.
                     Make sure you use an absolute app_path to the image.
        :param duration: How long the toast should show up for (short/long), default is short.
        :param launch: The url to launch (invoked when the user clicks the notification)
        """
        self.app_id = app_id
        self.title = title
        self.msg = msg
        self.icon = icon
        self.duration = duration
        self.launch = launch
        self.audio = audio.Silent
        self.tag = self.title
        self.group = self.app_id
        self.actions = []
        self.script = ""
        if duration not in ("short", "long"):
            raise ValueError("Duration is not 'short' or 'long'")

    def set_audio(self, sound: audio.Sound, loop: bool):
        """
        Set audio to the notification object.

        :param sound: The audio to play when the notification is showing. Choose one from audio class,
                      (eg. audio.Default). If not calling this method, default audio is silent
        :param loop: A boolean indicating the audio should looping or not
        :return: None
        """
        self.audio = '<audio src="{}" loop="{}" />'.format(sound, str(loop).lower())

    def add_actions(self, label: str, launch: Union[str, Callable] = ""):
        """
        Add action button to the notification. You can have up to 5 buttons each toast.

        :param label: The label of the button
        :param launch: The url to launch when clicking the button, 'file:///' protocol is allowed. Or a registered
                        callback function
        :return: None
        """
        if callable(launch):
            if hasattr(launch, 'url'):
                url = launch.url
            else:
                raise ValueError(f"{launch} is not registered")
        else:
            url = launch

        xml = '<action activationType="protocol" content="{label}" arguments="{link}" />'
        if len(self.actions) < 5:
            self.actions.append(xml.format(label=label, link=url))

    def build(self):
        import warnings
        """
        :return: self
        """
        warnings.warn("build method is deprecated, call show directly instead", DeprecationWarning)
        return self

    def show(self):
        """
        Invoke the temporary created script to Powershell to show the toast.
        Note: Running the PowerShell script is by far the slowest process here, and can take a few
        seconds in some cases.

        :return: None
        """
        if self.actions:
            self.actions = '\n'.join(self.actions)
        else:
            self.actions = ''

        if self.audio == audio.Silent:
            self.audio = '<audio silent="true" />'

        if self.launch:
            self.launch = 'activationType="protocol" launch="{}"'.format(self.launch)

        self.script = TEMPLATE.format(**self.__dict__)

        _run_ps(command=self.script)


class Notifier:
    def __init__(self, registry: Registry):
        """


        then call a callback functions from self.callbacks if the script called from protocol

        :param registry: a Registry object from winotify.Registry()
        """
        self.app_id = registry.app
        self.icon = ""
        pidfile = os.path.join(tempdir, f'{self.app_id}.pid')

        # alias for callback_to_url()
        self.cb_url = self.callback_to_url

        if self._protocol_launched():
            # communicate to main process if it's alive
            self.func_to_call = sys.argv[1].split(':')[1]
            self._cb = {}  # callbacks are stored here because we have no listener
            if os.path.isfile(pidfile):
                sender = Sender(self.app_id)
                sender.send(self.func_to_call)
                sys.exit()
        else:
            self.listener = Listener(self.app_id)
            open(pidfile, 'w').write(str(os.getpid()))  # pid file
            atexit.register(os.unlink, pidfile)

    @property
    def callbacks(self):
        if hasattr(self, 'listener'):
            return self.listener.callbacks
        else:
            return self._cb

    def set_icon(self, path: str):
        """
        set global icon
        :param path:
        :return:
        """
        self.icon = path

    def create_notification(self,
                            title: str,
                            msg: str = '',
                            icon: str = '',
                            duration: str = 'short',
                            launch: Union[str, Callable] = '') -> Notification:
        """
        create new Notification object. See Notification() for documentation

        :param title:
        :param msg:
        :param icon:
        :param duration:
        :param launch:
        :return: Notification object
        """
        if self.icon:
            icon = self.icon

        if callable(launch):
            url = self.callback_to_url(launch)
        else:
            url = launch

        notif = Notification(self.app_id, title, msg, icon, duration, url)
        return notif

    def start(self):
        """
        start the thread
        :return:
        """
        if self._protocol_launched():  # call the callback directly
            self.callbacks.get(self.func_to_call)()

        else:
            self.listener.callbacks.update(self.callbacks)
            self.listener.thread.start()

    def update(self):
        """
        check for available callback function in queue then call it
        this method must be called every time in loop
        """
        if self._protocol_launched():
            return

        q = self.listener.queue
        try:
            func = q.get_nowait()
            if callable(func):
                func()
            else:
                print(f"{func.__name__} ")
        except queue.Empty:
            pass

    def _protocol_launched(self) -> bool:
        """
        check whether the app is opened directly or via notification
        :return: True, if opened from notification; False if opened directly
        """
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            return format_name(self.app_id) + ':' in arg and len(arg.split(':')) > 0
        else:
            return False

    def register_callback(self, _func=None, *, run_in_main_thread=False):
        def inner(func):
            if run_in_main_thread:
                func.rimt = run_in_main_thread
                # setattr(func, 'rimt', run_in_main_thread)
            self.callbacks[func.__name__] = func
            func.url = self.callback_to_url(func)
            return func

        if _func is None:
            return inner
        else:
            return inner(_func)

    def callback_to_url(self, func: Callable) -> str:
        """
        change registered callback to url notation
            my-app-id:function_name
        :param func: registered callback function
        :return: url-notation string
        """
        if callable(func) and func.__name__ in self.callbacks:
            url = format_name(self.app_id) + ":" + func.__name__
            return url

    def clear(self):
        cmd = f"""\
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
        [Windows.UI.Notifications.ToastNotificationManager]::History.Clear('{self.app_id}')
        """
        _run_ps(command=cmd)
