"""
OEDISI OMOO Federate - Online Model-based Optimal Operation.

This component provides:
- Primal-dual optimization for voltage regulation
- PV curtailment and reactive power control
- Linearized power flow model (sensitivity matrices)
- HELICS co-simulation integration
"""

__version__ = "0.1.0"

from .omoo import OMOO, OMOOFederate, OMOOParameters

__all__ = [
    "__version__",
    "OMOO",
    "OMOOFederate",
    "OMOOParameters",
]
