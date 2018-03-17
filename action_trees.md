# Action Tree Documentation
This table documents all the names of the action tree nodes, their functions and their parameters.

| Name | Parameters | Function |
| ---- | -----------| -------- |
| Iterator | Base Atom, Iterator Variable | Generate a list / lambda iterator |
| LambdaIf | Conditional Expression | If part of lambda |
| LambdaExpr | Iterator, Expression, \[Lambda If\] | Generate a lambda expression |
| Await | Incomplete Type (result of function call) | Await an async function |
| Malloc | Size | Dynamically allocate a block of memory |
| CreateObjectInstance | Object | Create an instance of an object |
