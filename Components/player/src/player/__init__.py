"""OEDISI Player - Dataset playback federate for HELICS co-simulation.

This component provides:
- HELICS publication of pre-recorded MeasurementArray datasets
- Support for all MeasurementArray subtypes with Pydantic validation
- Feather and CSV file format support (auto-detected by extension)
- EquipmentNodeArray support via sidecar metadata JSON
"""

__version__ = "0.1.0"

from .play_dataset import Player, ComponentParameters, TYPE_MAP

__all__ = [
    "__version__",
    "Player",
    "ComponentParameters",
    "TYPE_MAP",
]
