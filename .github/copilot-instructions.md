## Docstrings

We always write Python docstrings following NumPy-style conventions, be sure to follow them when writing code documentation for Python.

## Typing

All Python code should be type-annotated, using type hints for function parameters and return types, as well as for class attributes; variables should also be annotated when the type is ambiguous.

When annotating types we follow modern Python typing conventions by using built-in types and latest syntax. Use built-in types like `list[str]` instead of `List[str]` importing from the `typing` module, and use the `|` operator for union and optional types like `str | None` instead of `Union[str, None]` or `Optional[str]`.
