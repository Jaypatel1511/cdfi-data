import pytest
from cdfidata.sources.tlr import TLRLoader
from cdfidata.sources.clr import CLRLoader
from cdfidata.sources.awards import AwardsLoader


@pytest.fixture
def tlr_sample():
    loader = TLRLoader()
    return loader.load_sample(n=500)


@pytest.fixture
def tlr_loader():
    loader = TLRLoader()
    loader.load_sample(n=500)
    return loader


@pytest.fixture
def clr_loader():
    loader = CLRLoader()
    loader.load_sample(n=500)
    return loader


@pytest.fixture
def awards_loader():
    loader = AwardsLoader()
    loader.load_sample(n=200)
    return loader
