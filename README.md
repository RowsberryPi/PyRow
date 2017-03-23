PyRow
=====

[![Build Status](https://travis-ci.org/JamieMagee/PyRow.svg?branch=master)](https://travis-ci.org/JamieMagee/PyRow)
[![Coverage Status](https://coveralls.io/repos/github/JamieMagee/PyRow/badge.svg?branch=master)](https://coveralls.io/github/JamieMagee/PyRow?branch=master)

PyRow is python code that allows one to interact with a Concept2 PM3, PM4 or PM5 monitors using python. PyRow aims to be easy to use and allow anyone to interact with Concept2 indoor rowers.

Installation
------------

PyRow is supported on Python 3.3+. The recommended way to install PyRow is via [pip](https://pypi.python.org/pypi/pip)

```python
pip install pyrow
```

For instructions on installing python and pip see "The Hitchhiker's Guide to Python" [Installation Guides.](http://docs.python-guide.org/en/latest/starting/installation/)

Quickstart
----------

Assuming that you have connected the indoor rower via USB you can instantiate an instance of `PerformanceMonitor` like so

```python
from pyrow.performance_monitor import PerformanceMonitor
ergs = list(PerformanceMonitor.find())
erg = PerformanceMonitor(ergs[0])
```

Then using the `PerformanceMonitor` instance, you can interact with the indoor rower

```python
workout = erg.get_workout()
while workout.get_status() == 1:
    monitor = erg.get_monitor()
    print(monitor.get_time())
    print(monitor.get_distance())
    print(monitor.get_spm())
    print(monitor.get_pace())
    workout = erg.get_workout()
```

Documentation
-------------

TODO

License
-------

Copyright (c) 2017, Jamie Magee
Copyright (c) 2011 - 2015, Sam Gambrell

Licensed under the Simplified BSD License.