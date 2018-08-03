import buptelecmon.configurationmanager

def test_confman():
    # Test cases
    obj = {
        'abcd': 'efgh', 'hjik': 2
    }
    # Test
    cm = buptelecmon.configurationmanager.ConfigMan('confman-tester', 'test.json')
    cm.write_back(obj)
    assert cm.read() == obj