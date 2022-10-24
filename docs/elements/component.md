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

The process of creating multiple simple components can be tedious. The wrapper [`@simple_component`][nimphel.component.simple_component] allows to create components similarly to a dataclass.

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

To see more about generating and storing models, please see [parsers](../parsers.md) and [exporters](../exporters.md)

# Serialization and deserialization

Components can be serialized to a dict by using the [`to_dict`][nimphel.component.Component.to_dict] method. To serialize to JSON, use the [`to_json`][nimphel.component.Component.to_json] method.

```{.py3 title="Example of serializing and deserialization"}
mosfet = NMosfet(["in", "out", GND, VDD])

data = mosfet.to_dict()
assert mosfet == NMosfet.from_dict(data)

json_str = mosfet.to_json()
assert mosfet == NMosfet.from_json(json_str)
```
