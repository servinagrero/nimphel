# Exporting to a netlist

Any circuit can be exported to a netlist.

```{.py3 title="Exporting a circuit"}
from nimphel.exporters import Exporter

netlist.export(Exporter)
```

To export directly to a file, use the method ``export_to_file()``.

```{.py3 title="Exporting a circuit to a file"}
netlist.export_to_file("/path/to/file")
```

## Custom Exporter

A custom exporter can be created by implementing the following interface.

!!! Info
    When writing an exporter, it is advised to check if a component implements the ``fmt()`` method and use it instead to format the component.

```python
class Exporter:
    """Interface for a Exporter."""

    def fmt_component(self, component) -> str:
        """Format a component instance."""
        raise NotImplementedError

    def fmt_subckt(self, subcircuit) -> str:
        """Format a subcircuit definition."""
        raise NotImplementedError

    def fmt_net(self, net) -> str:
        """Format a net."""
        raise NotImplementedError
```
