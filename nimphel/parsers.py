#!/usr/bin/env python3

from __future__ import annotations

import re
from os import PathLike
from typing import Any, Callable, Dict, List, TextIO, Union

import yaml

from nimphel.component import Model, ParamValue

#: Interface for a model file parser
Parser = Callable[[TextIO], Dict[str, Model]]


def cast_value(val: str) -> ParamValue:
    """Cast a string to an int, or float or string.

    The value is casted to int. If it fails it is casted to float and if that fails, the value is returned without modification.

    Args:
        val: Value we want to cast

    Returns:
        The value casted to the type.
    """
    for t in [int, float]:
        try:
            value = t(val)
            return value
        except ValueError:
            pass
    return val


def veriloga_parser(lib: TextIO) -> Dict[str, Model]:
    """Parser for verilogA files.

    Args:
        lib: Path to the lib file.

    Returns:
        Dictionary containing the models in the file.
    """
    models: Dict[str, Model] = {}
    lines = iter([l.strip() for l in lib.readlines()])
    param_re = re.compile(r".*parameter \w+ (\w+) = (.*);")
    module_re = re.compile(r".*module (\w+) .*;")

    line = next(lines)
    while lines:
        while not module_re.search(line):
            try:
                line = next(lines)
            except StopIteration:
                return models

        module_name = module_re.search(line).group(1)
        params = {}
        while not line.startswith("analog begin"):
            line = next(lines)
            if param_re.search(line):
                name, value = param_re.search(line).groups()
                params[name] = cast_value(value.replace('"', ""))
        models[module_name] = Model(module_name, params)
    return models


def eldo_parser(lib: TextIO) -> Dict[str, Model]:
    """Parser for eldo technology files.

    Args:
        lib: Path to the lib file.

    Returns:
        Dictionary containing the models in the file.
    """
    re_subckt = re.compile(r"\.subckt (\w+) .*")
    models: Dict[str, Model] = {}

    lines = iter([l.strip() for l in lib.readlines()])

    line = next(lines)
    while lines:
        while not re_subckt.search(line):
            try:
                line = next(lines)
            except StopIteration:
                return models

        subckt_name = re_subckt.search(line).group(1)
        while not line.startswith("+"):
            line = next(lines)

        param_lines = []
        while line.startswith("+"):
            param_lines.append(line[1:].strip())
            line = next(lines)

        params = {}
        parameters = " ".join(param_lines)
        for param in parameters[6:].split(" "):
            name, value = param.split("=")
            params[name] = cast_value(value)
        models[subckt_name] = Model(subckt_name, params)

    return models


def spectre_parser(lib: TextIO) -> Dict[str, Model]:
    """Parser for spectre technology files.

    Args:
        lib: Path to the lib file.

    Returns:
        Dictionary containing the models in the file.
    """
    re_subckt = re.compile(r"subckt (\w+) .*")
    re_param = re.compile(r"\+ (\w+) = (.*)")
    models: Dict[str, Model] = {}

    lines = iter([l.strip() for l in lib.readlines()])

    line = next(lines)
    while lines:
        while not re_subckt.search(line):
            try:
                line = next(lines)
            except StopIteration:
                return models

        subckt_name = re_subckt.search(line).group(1)
        while not re_param.search(line):
            line = next(lines)

        params = {}
        while not re_param.search(line):
            line = next(lines)

        while re_param.search(line):
            name, value = re_param.search(line).groups()
            params[name] = cast_value(value)
            line = next(lines)

        models[subckt_name] = Model(subckt_name, params)

    return models


def yaml_parser(lib: str) -> Dict[str, Model]:
    """Parser for YAML files.

    Args:
        lib: Path to the lib file.

    Returns:
        Dictionary containing the models in the file.
    """
    models: Dict[str, Model] = {}
    for config in yaml.load_all(lib, Loader=yaml.Loader):
        if config["params"].get("from", False):
            name = config["params"]["from"]
            new_vals = {k: v for k, v in config.items() if k != "from"}
            params = {**models[name].params, **new_vals}
            params = {k: v for k, v in params.items() if v}
            models[config["name"]] = Model(name, params)
        else:
            models[config["name"]] = Model(**config)
    return models


def parse_model_file(file_path: PathLike, parser: Parser) -> Dict[str, Model]:
    """Parse a technology file using the given parser
    Args:
        file_path: Path to the technology file.
        parser: Parser to use in the file.

    Returns:
        Dictionary containing the models in the file.
    """
    with open(file_path, "r") as f:
        return parser(f)
