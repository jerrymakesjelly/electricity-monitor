import os
import random
import pytest

@pytest.fixture()
def test_dormitories():
    cases = os.environ['MENGXIAO_TEST_QUERY_LIST'].split()
    start_pt = random.randint(0, len(cases))
    return cases[start_pt:start_pt+2]