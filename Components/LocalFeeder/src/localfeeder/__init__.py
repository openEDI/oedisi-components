"""OEDISI LocalFeeder - OpenDSS-based power distribution feeder simulator.

This component provides:
- OpenDSS integration for power flow simulation
- SMART-DS data integration via S3/boto3
- Multi-dimensional data handling (xarray)
- HELICS co-simulation wrapper for distribution feeders
"""

__version__ = "0.1.0"

from .FeederSimulator import FeederConfig, FeederSimulator

__all__ = [
    "__version__",
    "FeederSimulator",
    "FeederConfig",
]
