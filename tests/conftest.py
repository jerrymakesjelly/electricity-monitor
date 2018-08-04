import os
import random
import pytest

@pytest.fixture()
def test_dormitories():
    return random.sample(os.environ['MENGXIAO_TEST_QUERY_LIST'].split(), 2)