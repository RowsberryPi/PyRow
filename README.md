PyRow
=====

[![Build Status](https://travis-ci.org/RowsberryPi/PyRow.svg?branch=master)](https://travis-ci.org/RowsberryPi/PyRow)
[![Coverage Status](https://coveralls.io/repos/github/RowsberryPi/PyRow/badge.svg?branch=master)](https://coveralls.io/github/RowsberryPi/PyRow?branch=master)
[![License](https://img.shields.io/badge/License-BSD%202--Clause-blue.svg)](https://opensource.org/licenses/BSD-2-Clause)

PyRow is a Python package that allows one to interact with a Concept2 PM3, PM4 or PM5 monitors using python. PyRow aims to be easy to use and allow anyone to interact with Concept2 indoor rowers.

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

Licensed under the Simplified BSD License.
