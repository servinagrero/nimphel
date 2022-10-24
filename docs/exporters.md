# Exporters

Exporters allow the generation of a text file based on a series of elements. Their main use is to generate a SPICE netlist from a Circuit. There are however, exporters to save models to files to be loaded later on.


## Exporting to a netlist

Any circuit can be exported to a netlist by using the [`export`][nimphel.circuit.Circuit.export] method. This method only requires the exporter class.

```{.py3 title="Exporting a circuit"}
from nimphel.exporters import Exporter

netlist.export(Exporter)
```

To export directly to a file, use the method [`export_to_file`][nimphel.circuit.Circuit.export_to_file].

```{.py3 title="Exporting a circuit to a file"}
netlist.export_to_file("/path/to/file", Exporter)
```

## Custom Exporter

As of today only the following exporters are implemented: [`SpectreExporter`][nimphel.exporters.SpectreExporter].

A custom exporter can be created by implementing the following interface.

!!! Info
    When writing an exporter, it is advised to check if a component implements the ``fmt()`` method and use it instead.

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

## Exporting models

Models can be exported to a YAML file by using the function [`models_to_yaml`][nimphel.exporters.models_to_yaml]. These models can be read back by using the yaml parser (see [parsers](parsers.md)).

```{.py3}
models_to_yaml(models, "/path/to/models.yml")
```

!!! Info
    In the future, custom exporters will be added to resemble the functionality of the parsers.
