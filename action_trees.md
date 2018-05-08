# Action Tree Documentation
This table documents all the names of the action tree nodes, their functions and their parameters.

| Name | Parameters | Function | SyClone Syntax |
| ---- | -----------| -------- | -------------- |
| Iterator | Base Atom, Iterator Variable | Generate a list / lambda iterator | collection\[x\] |
| ForIf | Conditional Expression | If part of lambda | if boolean |
| ForExpr | Iterator, Expression, \[Lambda If\] | Generate a lambda expression | *No direct example, expr of lambda* |
| Await | Incomplete Type (result of function call) | Await an async function | await |
| Malloc | Integer/Data Type | Dynamically allocate a block of memory | new *size/data_type*|
| CreateObjectInstance | Object | Create an instance of an object | new Constructor() |
| Call | Function, Parameters | Call a function | () |
| Constructor | Constructor, Parameters | Call a constructor for a struct | *constructor*() |
| Subscript | Index, Collection | Get a value from a collection | \[ndx\] |
| Dereference | Object | Dereference an Object | * |
| ChangeSine | Numeric Object | Change the sine of a numeric object | - |
| Reference | Object | Create a pointer to an object | & |
| + | ~Object | Add / Concat | + |
| - | ~Object | Subtract | - |
| * | ~Object | Multiply / Multiconcat | * |
| / | ~Object | Divide | / |
| % | ~Object | Modulus | % |
| ^ | ~Object | Exponent | ^ |
| ARshift | Object, Integer | Arithmetic Right Shift | >> |
| LRshift | Object, Integer | Logical Right Shift | >>> |
| Lshift | Object, Integer | Logical Left Shift | << |
| Not | Object | Not Operator (invert) | ! |
| > | Numeric, Numeric | Greater Than | > |
| < | Numeric, Numeric | Less Than | < |
| >= | Numeric, Numeric | Greater Than / Equal To | >= |
| <= | Numeric, Numeric | Greater Than / Equal To | <= |
| == | Object, Object | Equal To | == |
| != | Object, Object | Not Equal To | != |
| === | Object, Object | Strict Equal To | === |
| !== | Object, Object | Strict Unequal To | !== |
| Or | Boolean, Boolean | Perform Boolean Or Operation | \|\| |
| And | Boolean, Boolean | Perform Boolean And Operation | && |
| Xor | Boolean, Boolean | Perform Boolean Xor Operation | ^^ |
| BitwiseOr | Simple, Simple | Perform Bitwise Or Operation | \|\| |
| BitwiseAnd | Simple, Simple | Perform Bitwise And Operation | && |
| BitwiseXor | Simple, Simple | Perform Bitwise Xor Operation | ^^ |
| NullCoalesce | Object, Object | Perform a null coalescence on an object | ?? |
| InlineCompare | Object, Object, Object | Perform an inline comparison between 2 objects | ? : |
| StaticCast | Object | Perform a static cast on an object to the return type of the Action Node | *typename*() |
| DynamicCast | Type, Object | Perform a dynamic cast on an object (warning) | *type yielding expr*() |
| Return | ~Object | Return a value from a function | return *expr \[, expr\]* |
| Aggregate | Object, Function | Apply an aggregator | *expr*\|>*lambda/inline function*\| |
| SliceBegin | Collection, Integer | Perform a slice from beginning to arbitrary index | \[:*integer*\] |
| SliceEnd | Collection, Integer | Perform a slice from an arbitrary index to the end | \[*integer*:\] |
| Slice | Collection, Integer, Integer | Slice a collection between 2 arbitrary points | \[*integer*:*integer*\] |
