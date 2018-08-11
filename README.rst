BUPT Electricity Monitor
=========================
.. image:: https://www.travis-ci.org/jerrymakesjelly/electricity-monitor.svg
    :target: https://www.travis-ci.org/jerrymakesjelly/electricity-monitor

.. image:: https://ci.appveyor.com/api/projects/status/lqxj0s3fo21payke?svg=true
    :target: https://ci.appveyor.com/project/jerrymakesjelly/electricity-monitor

.. image:: https://codecov.io/gh/jerrymakesjelly/electricity-monitor/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/jerrymakesjelly/electricity-monitor

.. image:: https://img.shields.io/lgtm/alerts/g/jerrymakesjelly/electricity-monitor.svg?logo=lgtm&logoWidth=18
  :target: https://lgtm.com/projects/g/jerrymakesjelly/electricity-monitor/alerts/

.. image:: https://img.shields.io/lgtm/grade/python/g/jerrymakesjelly/electricity-monitor.svg?logo=lgtm&logoWidth=18
  :target: https://lgtm.com/projects/g/jerrymakesjelly/electricity-monitor/context:python

.. image:: https://img.shields.io/github/license/jerrymakesjelly/electricity-monitor.svg
  :target: LICENSE

.. image:: https://img.shields.io/badge/Pull%20Requests-welcomed-ff69b4.svg


Free yourself from the tedious operation, now you can just use a one-line command to view the electricity information of your dormitory.

The data comes from the BUPT Work WeChat. But please **notice that** this utility tool can only query the dormitory which is located on Xitucheng Campus. The other campuses are not supported at the moment.

**FEATURES**

* Get your power data easily, including surplus, voltage, current, power, etc.
* Calculate available time.

Requirements
-------------
* Python 3

Quick Start
------------
Step 1: Install from PyPI
++++++++++++++++++++++++++
::

  pip install buptelecmon

Step 2: Set your authorization information
+++++++++++++++++++++++++++++++++++++++++++
This information is used to log in to the query interface. We won't send your information to other sites.
::

  elecinfo --set-auth

And input your student ID and your password. The password is usually the same as your Information Portal (my.bupt.edu.cn).
::

  Student ID:
  Password:

Your authorization information will be saved to ``~/.elecmon/elecmon.json``.

Step 3: Run it
++++++++++++++++
::

  elecinfo <dormitory-number>

The *dormitory-number* must be in the correct format (ApartmentNumber-DormitoryNumber, e.g 1-101).

Also, this command tool will remember the dormitory number of the last query. Next time, if you want to query the same dormitory as last query, just type::

  elecinfo

Advanced Usage
---------------
Full Command Line
++++++++++++++++++
::

  elecinfo [ --version | --set-auth | [--loop] dormitory-list]

==============  ======================================================================
 Option         Description
==============  ======================================================================
--version       Display the version of this tool.
--set-auth      Set your authorization information, as the Quick Start - Step 2 shows.
--loop          Repeat querying electricity information every 60 seconds.
dormitory-list  A list of dormitories to be queried, separated by whitespaces.
==============  ======================================================================

**Note:** Please DO NOT query too many dormitories at the same time or query too frequently, otherwise you may receive ``HTTP 500 Internal Server Error`` s from the remote server.

APIs
+++++
We allow you to use the APIs to build your applications, for example::

  import buptelecmon
  em = buptelecmon.electricitymonitor.ElectricityMonitor()
  em.login('student_id', 'password')
  em.query(['x-xxx'])

For more information, please read the `APIs Document`_.

.. _APIs Document: docs/apis.md

Screenshot
------------
.. image:: https://user-images.githubusercontent.com/6760674/43949495-4454d694-9cc0-11e8-88c2-cfd98e2291a6.gif

Changelog
----------
**Fri, 10 Aug 2018**: 1.1.0 Released :label:

* Removed daemon mode 
* Added configuration mode - We don't need to write json file manually anymore 
* Published to PyPI 

**Fri, 30 Mar 2018**: First version. :tada:

License
--------
This software is distributed under the `GPL License`_.

.. _GPL License: LICENSE