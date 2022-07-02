import os
import random
import pytest

@pytest.fixture()
def test_dormitories():
    return ['A-111', '1-111']