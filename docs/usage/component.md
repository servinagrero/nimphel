# Usage

## Creation of models
```python
NMOS = Model(
    name="nmosfet",
    params={
        "w": 0.135,
        ...
    },
)
```

## Creation of components

```python
class R(Component):
    def __init__(self, ports: Ports, params: Optional[Params] = None):
        defaults: Params = {"R": 1e3}
        user_params = dict(params) if params else {}
        super(R, self).__init__(ports, {**defaults, **user_params}, name="R")

    def fmt(self) -> str:
        def fmt_net(net):
            return f"net{net}" if isinstance(net, int) else net

        ports = " ".join(map(fmt_net, self.ports))
        return f'R{self.num_id} ({ports}) R {self.params["R"]}'

class Mosfet(Component):
    def __init__(self, ports: Ports, params: Optional[Params] = None, name=None):
        parameters = params if params else {}
        super(Mosfet, self).__init__(ports, parameters, model=NMOS, name=name)
```

### Wrapper for simple components

```python
@simple_component
class C(Component):
    defaults: Params = {"C": 1e3, "T": None}
```
