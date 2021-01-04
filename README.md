# Winotify
A pure python module to show notification toast on Windowss 10.

## Installation
Install winotify using pip

```sh
pip install winotify
```

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


## CLI
```batch
winotify ^
-id myApp ^
-t "A Title" ^
-m "A message" ^
-i "c:\path\to\icon.png" ^
--audio default ^
--open-url "http://google.com" ^
--action "open github" ^
--action_url "http://github.com"         
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Licence
[MIT](https://github.com/versa-syahptr/winotify/blob/master/LICENSE)