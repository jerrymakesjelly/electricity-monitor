Electricity Monitor
====================
|GPL|

This program can help you to query, record and report the power usage of a dormitory in Beijing University of Posts and Telecommunications via Mengxiao. 

**FEATURES**

* Get the power data easily, including power remaining, voltage, current, power and power factor.
* Save the data into database if you want.
* Report the statistics of power usage every weekend.

Note that the interface of Mengxiao only supports querying the dormitories in Xitucheng Campus at the moment. The other campus is not available now.

.. |GPL| image:: https://img.shields.io/badge/license-GPL-green.svg
   :target: https://github.com/jerrymakesjelly/electricity-monitor/blob/master/LICENSE

Requirements
--------------
* Python 3

Depending on your needs, you may need to install additional modules/packages. They will be given below.

Quick Start
-------------
Download the codes
++++++++++++++++++
::

    git clone https://github.com/jerrymakesjelly/electricity-monitor.git
    pip3 install requests
    cd electricity-monitor

Write a configuration file
+++++++++++++++++++++++++++
The configuration file helps you save the information of your partment, floor and dormitory.

Create an empty file named *elecmon.json*, and then make your own configurations. For example::

    {
        "username":"2018003028",
        "password":"asimplepassword",
        "dormitory_list":[
            {
                "partment":"学六楼",
                "floor":"6",
                "dormitory":"6-666"
            }
        ]
    }

As you can see, this is a JSON structure configuration file. The file should contain the following fields:

* *username*: Username to login Mengxiao. Generally it's your student number.
* *password*: Password. Generally it's the same as your password of Information Portal.
* *dormitory_list*: An array list of dormitories. Each item is an object, which contains the following fields:

  - *partment*: The partment of your dormitory in Chinese.
  - *floor*: Floor. Note that it's a string.
  - *dormitory*: Dormitory name.

Run
++++
::

    python3 run.py

Wait a moment, and you will see a result like this::

    6-666 2018-03-28 12:08:31 - Remaining: 295.64 kWh (Free: 175.84 kWh).
        - Voltage/Current/Power/Power Factory: 223.6 V, 0.703 A, 130.0 W, 0.83.
        - Expected to use up: 2018-07-01 06:17:44.

If you want to keep running, use the following command line. It will collect electricity data and print it every minute::

    python3 run.py --loop


Daemon Mode
------------
Electricity Monitor can keep collecting and recording electricity data and send you a report on weekends if it is running in daemon mode. For more information, please see the `wiki`_.

.. _wiki: https://github.com/jerrymakesjelly/electricity-monitor/wiki

Screenshots
------------
|Demo|

This charts were generated in Daemon Mode and were included in the report.

|BarChartDemo|

|LineChartDemo|

.. |Demo| image:: https://user-images.githubusercontent.com/6760674/38181027-15170a14-3663-11e8-9c06-0d55f02ff02e.gif
.. |BarChartDemo| image:: https://user-images.githubusercontent.com/6760674/38181120-afc8c6a6-3663-11e8-8b17-d294ec870dc4.png
.. |LineChartDemo| image:: https://user-images.githubusercontent.com/6760674/38181132-bf85a046-3663-11e8-9e34-01ac20e7147b.png

Changelog
----------
Fri, 30 Mar 2018: First version. :smile:

If you have any problem, please submit `issues`_. This software is distributed under the `GPL license`_.

.. _issues: https://github.com/jerrymakesjelly/electricity-monitor/issues
.. _GPL license: https://github.com/jerrymakesjelly/electricity-monitor/blob/master/LICENSE