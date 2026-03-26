# OEDISI OMOO Federate

Online Model-based Optimal Operation for distribution systems with high PV penetration.

## Overview

The OMOO federate implements a primal-dual optimization approach for voltage regulation. It uses linearized power flow sensitivity matrices to compute optimal PV curtailment and reactive power setpoints.

## Installation

```bash
pip install -e Components/omoo_federate
```

With dev dependencies:
```bash
pip install -e "Components/omoo_federate[dev]"
```

## Testing

```bash
pytest Components/omoo_federate/tests/ -v
```
