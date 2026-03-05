"""
OEDISI Measuring Federate - Sensor/measurement simulation with noise injection.

This component provides:
- Sensor/measurement relay functionality
- Additive and multiplicative noise injection
- Configurable noise characteristics
- Seeded random number generation for reproducibility
"""

__version__ = "0.1.0"

from .measuring_federate import MeasurementConfig, MeasurementRelay

__all__ = [
    "__version__",
    "MeasurementRelay",
    "MeasurementConfig",
]
