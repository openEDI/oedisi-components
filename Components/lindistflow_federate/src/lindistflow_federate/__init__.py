"""OEDISI LinDistFlow Federate - Optimal power flow using linear distflow formulation.

This component provides:
- Three-phase power flow analysis using linear distflow
- Convex optimization for optimal power flow (cvxpy)
- Network graph operations (networkx)
- Distribution system optimization
"""

__version__ = "0.1.0"

from .opf_federate import EchoFederate, StaticConfig, Subscriptions

__all__ = [
    "__version__",
    "EchoFederate",
    "StaticConfig",
    "Subscriptions",
]
