"""OEDISI Recorder - Data recording federate for HELICS co-simulation outputs.

This component provides:
- HELICS subscription data recording
- Feather (PyArrow) format output for efficient columnar storage
- CSV format output for compatibility
- Time-series data aggregation
"""

__version__ = "0.1.0"

from .record_subscription import Recorder

__all__ = [
    "__version__",
    "Recorder",
]
