This section provides a small list of real life use cases that nimphel was designed to solve.

## Process variability

As it was stated in the rationale, this project started from a set of utility functions and scripts to perform parametric analysis at large scale.

Since component and instance parameters can be manipulated with python dictionaries, process variability comes basically for free.

```python title="Example of process variability"
from nimphel import Circuit, Component
from nimphel.writer import SpectreWriter
from nimphel.reader import Reader
import random

circuit = Reader("spectre").read("/path/to/netlist_template")

# We want to modify the next component
# mos = Component("nmos", ["D", "G", "S", "GND"], {})
W_NOM = 65e-9
L_NOM = 100e-9

def params():
    return {
        "w": random.gauss(W_NOM, 0.1 * W_NOM),
        "l": random.gauss(L_NOM, 0.1 * W_NOM),
    }


for inst in circuit.instances:
    if inst.name != "nmos":
        continue
    updated = params()
    inst.params = {**inst.params, **updated}

writer = SpectreWriter()
print(writer.writes(circuit))

```

## Chain of components

```python title="Example of a chain of components"
from nimphel.core import Component, Circuit

circuit = Circuit()
R = Component("resistor", ["GND", "VDD"], {"R": 1e3})

chain_length = 42

for i in range(chain_length):
    start, end = i, i+1
    inst = R.new([start,end], params={"R": 1e3 * i})
    circuit.add(inst)
```

```python title="Using a list comprehension"
from itertools import pairwise

pairs = enumerate(pairwise(range(chain_length), 1)

chain = [R.new([f,s], params={"R": 1e3 * i}) for i, (f,s) in pairs]
circuit.add(chain)
```

Both of the examples above produce the following SPICE netlist. We can see from this example that we can easily parametrize the structure of the chain, since we can define the length of the chain and create a different instance at every index of the chain.

```text title="Generated SPICE netlist"
M0 (0 1) resistor R=1k
M1 (1 2) resistor R=2k
M2 (2 3) resistor R=3k
M3 (3 4) resistor R=4k
...
M41 (41 42) resistor R=42k
```

## 2D array of components

```python title="Example creating a 2D array"
for x in range(n):
    for y in range(n):
        comp.new([x, y])

# Reduced version
from itertools import product

coords = product(range(n), range(m))
matrix = [comp.new([x, y]) for x, y in coords]
```


