"""Tests for individual feeder components."""

import localfeeder.sender_cosim as sender_cosim
import numpy as np


def test_true_angles():
    """Test phase calculations for various angles."""
    for angle in np.random.uniform(-np.pi, np.pi, 100):
        assert (sender_cosim.get_true_phases(angle) - angle) <= np.pi / 6

    for angle in np.linspace(-np.pi, np.pi, 7):
        assert np.isclose(sender_cosim.get_true_phases(angle), angle)
