import os

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup():
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
