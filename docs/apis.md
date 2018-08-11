# API Document
The API document of Electricity Monitor. Note that this library only supports Python 3.

**Functions**

* [ElectricityMonitor.login](#electricitymonitorlogin)
* [ElectricityMonitor.query](#electricitymonitorquery)
* [ElectricityMonitor.loop](#electricitymonitorloop)
* [ElectricityMonitor.stop_loop](#electricitymonitorstop_loop)
* [ElectricityMonitor.get_part_list](#electricitymonitorget_part_list)
* [ElectricityMonitor.get_floor_list](#electricitymonitorget_floor_list)
* [ElectricityMonitor.get_dorm_list](#electricitymonitorget_dorm_list)
* [ElectricityMonitor.get_electricity_data](#electricitymonitorget_electricity_data)

## Initialization
Create an ``ElectricityMonitor`` object.
```python
import buptelecmon
em = buptelecmon.electricitymonitor.ElectricityMonitor()
```
The following examples are assumed that we have created an ``ElectricityMonitor`` object named ``em``.

## ElectricityMonitor.login
### Definition
```python
def login(self, username, password)
```

### Description
Log in to the query interface. **Note that** we must log in before doing any queries.

### Parameters
Parameter | Type | Description
--------- | ---- | -----------
username | ``str`` | Student number for logging in.
password | ``str`` | Password for logging in.

### Return Value
No return values.

### Exceptions
Exception | Raising Condition
--------- | -----------------
``buptelecmon.exceptions.LoginFailed`` | Login failed. It's usually because the username or password is wrong.
``buptelecmon.exceptions.RemoteError`` | An error occurred on the remote server.

### Example
```python
>>> em.login('2011111111', 'acomplexpassword')
```

## ElectricityMonitor.query
### Definition
```python
def query(self, dormitory_list)
```

### Description
Query electricity information of dormitories.

### Parameters
Parameter | Type | Description
--------- | ---- | -----------
dormitory_list | ``list`` | A list of dormitories to be queried.

### Return Value
A ``dict`` whose key is dormitory number and value is the result. Each result is also a ``dict``, which contains the following keys:

Key | Type | Type that can be converted to | Description (Guess)
--- | ---- | ----------------------------- | -------------------
phone | ``str`` | ``int`` | The phone number of the apartment administrator.
floorName | ``str`` | ``int`` | The floor number.
model | ``str`` | ``int`` | Unknown. It seems that it's always zero.
time | ``str`` | ``datetime.datetime`` | Updated time. Format: ``%Y-%m-%d %H:%M:%S``.
vTotal | ``str`` | ``float`` | Voltage.
price | ``str`` | ``float`` | Unit price of electricity.
iTotal | ``str`` | ``float`` | Current.
parName | ``str`` | - | Apartment name.
freeEnd | ``str`` | ``float`` | Surplus of free electricity.
cosTotal | ``str`` | ``float`` | Power factory.
pTotal | ``str`` | ``float`` | Power. Unit: ``kW``.
surplus | ``str`` | ``float`` | Surplus of non-free electricity.
totalActiveDisp | ``str`` | ``float`` | Total power consumption.

**Note:** The dormitory that failed the query won't appear in the result ``dict``. Therefore, sometimes you will find the length of the returned ``dict`` is not equal to the length of the input ``list``.

### Exceptions
Exception | Raising Condition
--------- | -----------------
``buptelecmon.exceptions.NeedLogin`` | Execute a query before logging in.
``buptelecmon.exceptions.InvalidDormitoryNumber`` | One of the dormitory numbers is in incorrect format.
``buptelecmon.exceptions.PartmentNameNotFound`` | All of the formats are correct, but one of the apartment numbers doesn't exist.
``buptelecmon.exceptions.RemoteError`` | An error occured on the remote server.

### Example
```python
>>> em.query(['1-101','2-202'])
{'1-101': {'phone': '62285706', 'floorName': 1, ...}, '2-202': {'phone': '62219584', 'floorName': 2, ...}}
```

## ElectricityMonitor.loop
### Definition
```python
def loop(self, dormitory_list, callback_function, params=None, time_interval=60)
```

### Description
Query electricity data at a regular interval. This function will calls the callback function when successfully completing a query for a dormitory, and it never returns unless the ``ElectricityMonitor.stop_loop`` is called.

The definition of the callback function should look like this:
```python
def output(dormitory, data, params)
```

Parameter | Type | Description
--------- | ---- | -----------
dormitory | ``str`` | A dormitory number that successfully queried.
data | ``dict`` | Electricity data. The definition of the *key-value* pair is the same as the table in [Return Values of ElectricityMonitor.query](#return-value-1).
params | Any | User-specified additional data.

### Parameters
Parameter | Type | Description
--------- | ---- | -----------
dormitory_list | ``list`` | A list of dormitories to be queried.
callback_function | ``types.FunctionType`` | Callback function.
params | Any | User-specified additional data. These data will be passed directly to the callback function.
time_interval | ``int`` | Time interval of queries.

### Return Value
No return values.

### Exceptions
Same as the [Exceptions of ElectricityMonitor.query](#exceptions-1)

### Example
```python
>>> em.loop(['1-101','2-202'], lambda dorm, data, param: print(dorm, data))
1-101 {'phone': '62285706', 'floorName': 1, ...}
2-202 {'phone': '62219584', 'floorName': 2, ...}
1-101 {'phone': '62285706', 'floorName': 1, ...}
2-202 {'phone': '62219584', 'floorName': 2, ...}
^C
```

## ElectricityMonitor.stop_loop
### Definition
```python
def stop_looping(self)
```

### Description
Stop looping query. The ``ElectricityMonitor.loop`` function will return after its HTTP requests are all responsed.

### Parameters
No parameters.

### Return Value
No return values.

### Exceptions
No exceptions.

### Example
```python
>>> em.stop_looping()
```

## ElectricityMonitor.get_part_list
### Definition
```python
def get_part_list(self)
```
### Description
Get student apartment list.

### Parameters
No parameters.

### Return Value
A ``list`` that contains all the information of apartments. Each item in the ``list`` is a ``dict``, which is defined here:

Key | Type | Type that can be converted to | Description (Guess)
--- | ---- | ----------------------------- | -------------------
partmentId | ``str`` | - | Apartment ID.
partmentName | ``str`` | - | Apartment name.
partmentFloor | ``str`` | ``int`` | The total number of floors of the apartment.
prartmentWeixiu | ``str`` | - | The repairer name.
prartmentWxphone | ``str`` | - | The phone number of the repairers.

### Exceptions
Exception | Raising Condition
--------- | -----------------
``buptelecmon.exceptions.NeedLogin`` | Execute a query before logging in.
``buptelecmon.exceptions.RemoteError`` | An error occured on the remote server.

### Example
```python
>>> em.get_part_list()
[{'partmentId': 'c526d2367cd24fcdac2538975d1bec75', 'partmentName': '学四楼', 'prartmentFloor': '12', 'prartmentWeixiu': '董玉芳', 'prartmentWxphone': '62284810'}, {'partmentId': 'd5cf9743f0864692a18c25efb02bf16a', 'partmentName': '学十楼', 'prartmentFloor': '15', 'prartmentWeixiu': '周建民/常亮生', 'prartmentWxphone': '62297919/61197908'}, ...]
```

## ElectricityMonitor.get_floor_list
### Definition
```python
def get_floor_list(self, partmentId)
```

### Description
Get floor list of a specified student apartment.

### Parameters
Parameter | Type | Description
--------- | ---- | -----------
partmentId | ``str`` | Apartment ID to be queried.

### Return Value
A ``list`` of ``dict``s. Each ``dict`` represents a floor, contains the following keys:

Key | Type | Type can be converted to | Description
--- | ---- | ------------------------ | -----------
floorId | ``str`` | ``int`` | Floor ID.
floorName | ``str`` | ``int`` | Floor Name. Same as the floor ID.

### Exceptions
Same as the [Exceptions of ElectricityMonitor.get_part_list](#exceptions-4)

### Example
```python
>>> em.get_floor_list('c526d2367cd24fcdac2538975d1bec75')
[{'floorId': '1', 'floorName': '1'}, {'floorId': '2', 'floorName': '2'}, ...]
```

## ElectricityMonitor.get_dorm_list
### Definition
```python
def get_dorm_list(self, partmentId, floorId)
```

### Description
Get dormitory list on a specified floor of a specified student apartment.

### Parameters
Parameter | Type | Description
--------- | ---- | -----------
partmentId | ``str`` | Apartment ID.
floorId | ``str`` | Floor ID.

### Return Value
A ``list`` of ``dict``s. Each ``dict`` contains the following keys:

Key | Type | Description (Guess)
--- | ---- | -------------------
dormPeople | ``int`` | The number of people in the dormitory.
dromName | ``str`` | Dormitory name.
dromNum | ``str`` | Dormitory number.
freeEng | ``int`` | Unknown.
holidayStatus | ``str`` | Holiday status.
id | ``str`` | Dormitory ID.
live | ``str`` | Living status.
partmentId | ``str`` | Apartment ID.
partmentName | ``str`` | Apartment name.
prartmentFloor | ``int`` | Floor.
status | ``str`` | Unknown.
statusLevel | ``str`` | Unknown.

### Exceptions
Same as the [Exceptions of ElectricityMonitor.get_part_list](#exceptions-4)

### Example
```python
>>> em.get_dorm_list('ac3a79c0e22e495096577d3aef1f5532', '6')
[{'dormPeople': 0, 'dromName': '6-601-1', 'dromNum': '6-601-1', 'freeEng': 40, ...}, {'dormPeople': 0, 'dromName': '6-610', 'dromNum': '6-610', 'freeEng': 40, ...}, ...]
```

## ElectricityMonitor.get_electricity_data
### Definition
```python
def get_electricity_data(self, partmentId, floorId, dromNumber)
```

### Description
Get electricity information of a specified dormitory.

### Parameters
Parameter | Type | Description
--------- | ---- | -----------
partmentId | ``str`` | Apartment ID.
floorId | ``int`` | Floor ID.
dromNumber | ``str`` | Dormitory number.

### Return Value
A ``dict``. The definition of the *key-value* pairs is the same as the table in [Return Values of ElectricityMonitor.query](#return-value-1).

### Exception
Same as the [Exceptions of ElectricityMonitor.get_part_list](#exceptions-4)

### Example
```python
>>> em.get_electricity_data('c526d2367cd24fcdac2538975d1bec75', 6, '4-602')
{'phone': '62284810', 'floorName': 6, ...}
```