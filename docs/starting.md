## Rationale 

This framework was originally conceived from a set of utility functions designed to generate a SPICE netlist while altering the parameters of the different components as a way to bypass the limitations of some simulators when running process variability simulations at large scale. From these tools, this framework was conceived to provide an interface to SPICE that was as frictionless and simple as possible for other people to adapt and use while being powerful enough to generate modular and reusable circuits with ease. 

Traditionally, scripts or custom software have been used to generate complicated SPICE netlists. However, most of these solutions are not available to the public are ad-hoc and thus serve no other purpose for other circuits. This framework provides tools to create subcircuits or certain instances from another tool (e.g. Cadence), parse the netlist and modify it (for example to perform process variability simulations) or extend it by creating the circuit depending on a user defined configuration (aka a macro compiler for SRAM, MACs, chains, ...). As such, it was not designed to substitute the commercially available CAD tools, rather boost the design, simulation cycle.


## Road map

This framework was conceived originall from a set of functions and scripts. While it has been extended to supply most of the creator's needs, there are some objectives to extend this project. The following list provides some of the objectives that may (or not) be implemented.

Issues, ideas and contributions are more than welcome.

- Support for more standards and formats.
- Support for working with SPICE libraries (Corners, parameters and component definitions)
- Automatic layout generation (Perhaps infeasible)

## Installation

Nimphel can be installed by running the following commands.

```sh title="Installation instructions"
$ git clone https://github.com/servinagrero/nimphel && cd nimphel
$ poetry install && poetry build
$ pip install .
```