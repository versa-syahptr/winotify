from . import audio
from ._registry import register, format_name
from .communication import Listener, Sender

import os
import subprocess
import sys
import typing
import atexit
from tempfile import gettempdir


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
        self.tag, self.group = '', ''  # you can set this value outside __init__
        self.actions = []
        self.script = ""
        self.__dict__.update(
            tag=self.tag or self.app_id,
            group=self.group or self.app_id
        )
        if duration not in ("short", "long"):
            raise ValueError("Duration is not 'short' or 'long'")

    def set_audio(self, audio: audio.Sound, loop: bool):
        """
        Set audio to the notification object.

        :param audio: The audio to play when the notification is showing. Choose one from audio class,
                      (eg. audio.Default). If not calling this method, default audio is silent
        :param loop: A boolean indicating the audio should looping or not
        :return: None
        """
        self.audio = '<audio src="{}" loop="{}" />'.format(audio, str(loop).lower())

    def add_actions(self, label: str, url: str = ""):
        """
        Add action button to the notification. You can have up to 5 buttons each toast.

        :param label: The label of the button
        :param url: The url to launch when clicking the button, 'file:///' protocol is allowed. Or a user defined
                    protocol to execute a callback function
        :return: None
        """

        xml = '<action activationType="protocol" content="{label}" arguments="{link}" />'
        if len(self.actions) < 5:
            self.actions.append(xml.format(label=label, link=url))

    def build(self):
        import warnings
        """
        :return: self
        """
        warnings.warn("build is deprecated, call show directly instead", DeprecationWarning)
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
    def __init__(self, app_id, app_path, *,
                 listener_class: typing.Type[Listener] = Listener,
                 sender_class: typing.Type[Sender] = Sender):
        """
        register app_id to windows registry as a protocol,
        eg. the app_id is "My Awesome App" can be called from browser or run.exe by typing "my-awesome-app:[Params]"
        Params is optional

        then call a callback functions from self.callback if the script called from protocol

        :param app_id: your app name, make it readable to your user. It can contain spaces, however special characters
                           (eg. é) are not supported.
        :param app_path: absolute path to your script entry point + its interpreter
                            eg. os.path.join(sys.executable, C:/myscript.py)
        """
        self.app_id = app_id
        self.app_path = app_path
        self.icon = ""
        self.callbacks = {}
        pidfile = os.path.join(tempdir, f'{self.app_id}.pid')

        register(self.app_id, self.app_path)

        if self._protocol_launched():
            # communicate to main process if it's alive
            self.func_to_call = sys.argv[1].split(':')[1]
            if os.path.isfile(pidfile):
                sender = sender_class()
                sender.send(self.func_to_call)
                sys.exit()
        else:
            self.listener = listener_class()
            open(pidfile, 'w').write(str(os.getpid()))  # pid file
            atexit.register(os.unlink, pidfile)

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
                            launch: str = '') -> Notification:
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

        notif = Notification(self.app_id, title, msg, icon, duration, launch)
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

    def _protocol_launched(self) -> bool:
        if len(sys.argv) > 1:
            arg = sys.argv[1]
            return format_name(self.app_id) + ':' in arg and len(arg.split(':')) > 0
        else:
            return False

    def callback(self, func: typing.Callable):
        self.callbacks[func.__name__] = func
        return func

    def callback_to_url(self, func: typing.Callable) -> str:
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



