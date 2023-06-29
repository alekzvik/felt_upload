import pytest
import responses


@pytest.fixture(autouse=True)
def mocked_responses() -> responses.RequestsMock:
    with responses.RequestsMock() as rsps:
        yield rsps
