Electricity Monitor
====================
|GPL|

该程序可以帮助你查询、记录和报告北京邮电大学宿舍的用电情况。

**特性**

* 轻松获取电力数据，包括剩余电量，电压，电流，功率和功率因数。
* 如果需要，可以将数据保存到数据库中。
* 每周末发送电量统计报告。

请注意，目前的接口仅支持查询西土城校区的宿舍。其它校区暂时不能查询。

.. |GPL| image:: https://img.shields.io/badge/license-GPL-green.svg
    :target: https://github.com/jerrymakesjelly/electricity-monitor/blob/master/LICENSE

要求
--------------
* Python 3

根据你的需要，你可能需要安装额外的模块/软件包，它们会在下面给出。

快速开始
-------------
下载代码
++++++++++++++++++
::

    git clone https://github.com/jerrymakesjelly/electricity-monitor.git
    pip3 install requests
    cd electricity-monitor

编写配置文件
+++++++++++++++++++++++++++
配置文件可以帮助你保存你的公寓，楼层和宿舍的信息。

创建一个名为 *elecmon.json* 的文本文件，然后写入自己的配置。例如::

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


显然，这是一个JSON结构的配置文件。该文件应该包含以下字段：

* *username*: 一般来说，这里填你的学号。
* *password*: 一般来说，它与你的信息门户的密码相同。
* *dormitory_list*: 宿舍列表。列表中的每个项目都是一个对象，其中包含以下字段：

  - *partment*: 公寓名。
  - *floor*: 楼层。注意这是一个字符串。
  - *dormitory*: 宿舍。

运行
++++
::

    python3 run.py


稍等几秒，就能看到如下结果::

    6-666 2018-03-28 12:08:31 - Remaining: 295.64 kWh (Free: 175.84 kWh).
        - Voltage/Current/Power/Power Factory: 223.6 V, 0.703 A, 130.0 W, 0.83.
        - Expected to use up: 2018-07-01 06:17:44.

如果你想让它持续运行，请使用以下命令行。它会每分钟收集一次电量数据并显示::

    python3 run.py --loop


后台模式
------------
如果 Electricity Monitor 后台模式下运行，它可以持续收集和记录电力数据，并且会在周末向你发送电量统计报告。有关更多信息，请参阅 `wiki`_。

.. _wiki: https://github.com/jerrymakesjelly/electricity-monitor/wiki/%E4%B8%BB%E9%A1%B5

截图
------------
|Demo|

下面这些图表是在后台模式下生成的，并自动包含在报告中。

|BarChartDemo|

|LineChartDemo|

.. |Demo| image:: https://user-images.githubusercontent.com/6760674/38181027-15170a14-3663-11e8-9c06-0d55f02ff02e.gif
.. |BarChartDemo| image:: https://user-images.githubusercontent.com/6760674/38181120-afc8c6a6-3663-11e8-8b17-d294ec870dc4.png
.. |LineChartDemo| image:: https://user-images.githubusercontent.com/6760674/38181132-bf85a046-3663-11e8-9e34-01ac20e7147b.png

更新日志
----------
2018年3月30日 星期五：第一个版本。 :smile:

如果您有任何问题，请提交 `issue`_ 。该软件在 `GPL许可证`_ 下分发。

.. _issue: https://github.com/jerrymakesjelly/electricity-monitor/issues
.. _GPL许可证: https://github.com/jerrymakesjelly/electricity-monitor/blob/master/LICENSE