# Action Tree Documentation
This table documents all the names of the action tree nodes, their functions and their parameters.

| Name | Parameters | Function | SyClone Syntax |
| ---- | -----------| -------- | -------------- |
| Iterator | Base Atom, Iterator Variable | Generate a list / lambda iterator | collection\[x\] |
| LambdaIf | Conditional Expression | If part of lambda | if boolean |
| LambdaExpr | Iterator, Expression, \[Lambda If\] | Generate a lambda expression | *No direct example, expr of lambda* |
| Await | Incomplete Type (result of function call) | Await an async function | await |
| Malloc | Size | Dynamically allocate a block of memory | new *data_type/size*|
| CreateObjectInstance | Object | Create an instance of an object | new Constructor() |
| Call | Function, Parameters | Call a function | () |
| Constructor | Constructor, Parameters | Call a constructor | *constructor*() |
| Subscript | Index, Collection | Get a value from a collection | \[ndx\] |
| Dereference | Object | Dereference an Object | * |
| ChangeSine | Numeric Object | Change the sine of a numeric object | - |
