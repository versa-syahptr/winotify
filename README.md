# Winotify
A pure python module to show notification toast on Windowss 10.

## Installation
Install winotify using pip

```sh
pip install winotify
```

## Usage & Examples

* **A simple title and text notification**
```python
from winotify import Notification

toast = Notification(app_id="example app",
                     title="Hello",
                     msg="World!")

toast.build().show()
```
[image]
* **Notification with icon**
```python
toast = Notification(app_id="example app",
                     title="Hello",
                     msg="World!",
                     icon=r"c:\path\to\icon.png")
```
[image2]

