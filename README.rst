BUPT Electricity Monitor 
==========================
|PyPI| |Codacy| |CodacyCoverage| |License|

Free yourself from the tedious operation, now you can just use a one-line command to view the electricity information of your dormitory.

The data comes from the BUPT Work WeChat. But please **notice that** this utility tool can only query the dormitory which is located on Xitucheng Campus. The other campuses are not supported at the moment.

**FEATURES**

* Get your power data easily, including surplus, voltage, current, power, etc.
* Calculate available time.

.. |PyPI| image:: https://badge.fury.io/py/buptelecmon.svg
    :target: https://pypi.org/project/buptelecmon

.. |License| image:: https://img.shields.io/github/license/jerrymakesjelly/electricity-monitor.svg
  :target: https://github.com/jerrymakesjelly/electricity-monitor/blob/master/LICENSE

.. |Codacy| image:: https://app.codacy.com/project/badge/Grade/b42cf7e1c8c44e5ab0c5d65514dca4bf
  :target: https://www.codacy.com/gh/jerrymakesjelly/electricity-monitor/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jerrymakesjelly/electricity-monitor&amp;utm_campaign=Badge_Grade

.. |CodacyCoverage| image:: https://app.codacy.com/project/badge/Coverage/b42cf7e1c8c44e5ab0c5d65514dca4bf
    :target: https://www.codacy.com/gh/jerrymakesjelly/electricity-monitor/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=jerrymakesjelly/electricity-monitor&amp;utm_campaign=Badge_Coverage

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

Recharge
---------
Use this tool to visit the recharge page directly.
::

    elecinfo --recharge <dormitory-number>

Then, a QR code will be shown on your terminal. Please use your WeChat to scan the QR code and pay for it.

Advanced Usage
---------------
Full Command Line
++++++++++++++++++
::

  elecinfo [ --version | --set-auth | [--loop] <dormitory-number-1> [... <dormitory-number-n>] | --recharge <dormitory-number>]

==============  ======================================================================
 Option         Description
==============  ======================================================================
--version       Display the version of this tool.
--set-auth      Set your authorization information, as the Quick Start - Step 2 shows.
--loop          Repeat querying electricity information every 60 seconds.
--recharge      Display a recharge QR code.
==============  ======================================================================

**Note:** Please DO NOT query too many dormitories at the same time or query too frequently, otherwise you may receive ``HTTP 500 Internal Server Error`` s from the remote server.

APIs
+++++
We allow you to use the APIs to build your applications, for example:

.. code:: python

  import buptelecmon
  em = buptelecmon.electricitymonitor.ElectricityMonitor()
  em.login('student_id', 'password')
  em.query(['x-xxx'])

For more information, please read the `APIs Document`_.

.. _APIs Document: https://github.com/jerrymakesjelly/electricity-monitor/blob/master/docs/apis.md

Screenshot
------------
.. image:: https://user-images.githubusercontent.com/6760674/43949495-4454d694-9cc0-11e8-88c2-cfd98e2291a6.gif

Changelog
----------
**Mon, 13 Aug 2018**: 1.2.2 released. Fix a bug that prevent the program from quitting when an exception raises. :bookmark:

**Mon, 13 Aug 2018**: 1.2.1 released. Fix documentation error. :bookmark:

**Sun, 12 Aug 2018**: 1.2.0 released :bookmark:

* Added recharge mode

**Sat, 11 Aug 2018**: 1.1.0 released :bookmark:

* Removed daemon mode 
* Added configuration mode - We don't need to write json file manually anymore 
* Published to PyPI 

**Fri, 30 Mar 2018**: First version. :tada:

License
--------
This software is distributed under the `MIT License`_.

.. _MIT License: https://github.com/jerrymakesjelly/electricity-monitor/blob/master/LICENSE