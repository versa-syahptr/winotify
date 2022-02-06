## Winotify

You can use the [editor on GitHub](https://github.com/versa-syahptr/winotify/edit/gh-pages/index.md) to maintain and preview the content for your website in Markdown files.

Whenever you commit to this repository, GitHub Pages will run [Jekyll](https://jekyllrb.com/) to rebuild the pages in your site, from the content in your Markdown files.

## Examples

#### A simple title and text notification
```python
from winotify import Notification
toast = Notification(app_id="example app",
                     title="Winotify Test Toast",
                     msg="New Notification!")
toast.build().show()
```

**Result:**

![image1](https://github.com/versa-syahptr/winotify/blob/master/image/winotify%20ss1.png?raw=true)

**The notification stays in the action center!**

![image2](https://github.com/versa-syahptr/winotify/blob/master/image/winotify%20ss2.png?raw=true)

#### Show notification with icon
```python
from winotify import Notification
toast = Notification(icon=r"c:\path\to\icon.png"
                    ...)
```
> Note that the icon path must be **absolute** otherwise
the notification will not show
#### Set sound of the notification

All supported audio are in the ```audio``` class
```python
from winotify import Notification, audio
toast = Notification(...)
toast.set_audio(audio.Mail, loop=False)
```

#### Add action button
```python
from winotify import Notification
toast = Notification(...)
toast.add_actions(label="Button text", 
                  link="https://github.com")
```
> You can add up to 5 buttons each notification


See [docs](/docs/index.html)