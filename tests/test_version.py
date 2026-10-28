import re

import pytest


def test_version_looks_like_x_y_z():
    # Imported inside the test so a missing __version__ fails THIS test
    # instead of breaking the whole test run at collection time.
    from mousebattery import __version__

    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
