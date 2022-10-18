# Creation of components

```{.py3 title="Creation of a simple Resistance"}
class R(Component):
    def __init__(self, ports , params = None):
        defaults: Params = {"R": 1e3}
        user_params = dict(params) if params else {}
        super(R, self).__init__(ports, {**defaults, **user_params}, name="Res")

    def fmt(self) -> str:
        def fmt_net(net):
            return f"net{net}" if isinstance(net, int) else net

        ports = " ".join(map(fmt_net, self.ports))
        return f'R{self.num_id} ({ports}) R {self.params["R"]}'
```

A component may implement an additional method called `fmt()`. This method accepts no argument and should return the string representation of the component.

## Wrapper for simple components

The process of creating multiple simple components can be tedious. The wrapper ``@simple_component`` allows to create components similarly to a dataclass.

```python
@simple_component
class C(Component):
    name: "Capacitor"
    letter: "C"
    defaults: Params = {"C": 1e3, "T": None}
```

# Component models

A model allows to reuse a component name and a set of parameters across multiple definitions.

```{.py3 title="Creation of a NMOS model"}
NMOS = Model(
    name="nmosfet",
    params={
        "w": 0.135,
        ...
    },
)
```

```{.py3 hl_lines="3 8"}
@simple_component
class NMosfet(Component):
    model = NMOS

class NMosfet(Component):
    def __init__(self, ports, params = None, name = None):
        parameters = params if params else {}
        super(Mosfet, self).__init__(ports, parameters, model=NMOS, name=name)
```

## Models in YAML

Models can be stored in a YAML file. Each document inside the YAML represents a single model.

A different YAML file can be created for a different technology, so that the same netlist can be created with the same code for different technologies just by changing the file.


```{.yaml title="Example of a YAML configuration" hl_lines="15"}
name: NMOS
params:
    w: 0.135
    nfing: 1
    mult: 1
    srcefirst: 1
    ngcon: 1
    mismatch: 1
    lpe: 0
    dnoise_mdev: 0
    dmu_mdev: 0
    dvt_mdev: 0
    numcos: 1
    numcod: 1
---
name: PMOS
params:
    from: NMOS # Use the parameters of NMOS
    w: 0.27 # Parameters can be updated
    new_val: 42 # New parameters can be added
    mismatch: ~ # Values can also be deleted
```

The function ``models_from_yaml()`` creates a dictionary with the models from the YAML file.

```{.py3}
models = models_from_yaml("/path/to/models.yml")

@simple_component
class NMosfet(Component):
    model = models['NMOS']
```

To automatically convert an Eldo library file to a YAML containing the subcircuits definitions, use the function ``eldo_to_yaml()``

```{.py3}
eldo_to_yaml("/path/to/eldo.lib", "/path/to/models.yml")
```

!!! info

    As of today, only Eldo library files can be parsed. Parsers for other simulators will be added in the future.


# Serialization and deserialization

Components can be serialized to a dict by using the ``to_dict()`` method. To serialize to JSON, use the ``to_json()`` method.

```{.py3 title="Example of serializing and deserialization"}
mosfet = NMosfet(["in", "out", GND, VDD])

data = mosfet.to_dict()
assert mosfet == NMosfet.from_dict(data)

json_str = mosfet.to_json()
assert mosfet == NMosfet.from_json(json_str)
```
