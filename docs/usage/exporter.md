# Exporter

```python
class Exporter:
    """Interface for a Exporter."""

    def fmt_component(self, comp) -> str:
        """Format a component instance."""
        raise NotImplementedError

    def fmt_subckt(self, subckt) -> str:
        """Format a subcircuit definition."""
        raise NotImplementedError

    def fmt_net(self, net) -> str:
        """Format a net."""
        raise NotImplementedError
```
