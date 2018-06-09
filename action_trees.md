# Action Tree Documentation
This table documents all the names of the action tree nodes, their functions and their parameters.

## Expression Nodes

| Name | Parameters | Function | SyClone Syntax |
| ---- | -----------| -------- | -------------- |
| ForIf | Conditional Expression | If part of lambda | if boolean |
| ForComprehension | Iterator, Expression, \[ForIf\] | Generate a for comprehension expression | for(lst\|i\| => *expr*); |
| Await | Incomplete Type (result of function call) | Await an async function | await |
| Malloc | Integer/Data Type | Dynamically allocate a block of memory | new *size/data_type*|
| CreateObjectInstance | Object, \[*init_list*\] | Create an instance of an object | new Constructor() |
| Call | Function, Parameters | Call a function | () |
| Constructor | Constructor, Parameters | Call a constructor for a struct | *constructor*() |
| Subscript | Index, Collection | Get a value from a collection | \[ndx\] |
| Dereference | Count, Object | Dereference an Object | * |
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
| TypeCast | Object | Perform a type cast on an object | *typename*() |
| Aggregate | Object, Function | Apply an aggregator | *expr*\|>*lambda/inline function*\| |
| SliceBegin | Collection, Integer | Perform a slice from beginning to arbitrary index | \[:*integer*\] |
| SliceEnd | Collection, Integer | Perform a slice from an arbitrary index to the end | \[*integer*:\] |
| Slice | Collection, Integer, Integer | Slice a collection between 2 arbitrary points | \[*integer*:*integer*\] |
| GetMember | Object, Property | Get member of a module or structure | obj.prop |

## Statement Nodes

| Name | Parameters | Statement | SyClone Syntax |
| ---- | -----------| -------- | -------------- |
| Return | Object | Return an object | return *value* |
| Yield | Object | Return an object and yield function back to spawn process, but retain state | yield *value* |
| Break | - | Break statement | break |
| Continue | - | Continue statement | continue |
| Throw | Error | Throw an error | throw *error* |
| DeclareVariable | Type, Name, Initializer, Modifiers | Declare a single variable | $*var* = *initializer* |
| DeclareConstant | Type, Name, Initializer, Modifiers | Declare a single constant | @*var* = *initializer* |
| DeclareVariables | Overall Type, Variables, Modifiers, [\Initializer\] | Declare multiple variables | $(*var*, *var2*): *type* |
| DeclareConstants | Overall Type, Constants, Modifiers, [\Initializer\] | Declare multiple constants | @(*var*, *var2*): *type* |
| Increment | Numeric | Increment a value | *var*++ |
| Decrement | Numeric | Decrement a value | *var*-- |
| Expr | Expr | Invoke an expression as a statement | *expr* |
| Assign | Operator, Variable-Initializer Dict | Perform an assignment | *var*= *expr* |
| Delete | Identifiers | Delete an identifier or multiple identifiers | delete *identifier* |
| Return | ~Object | Return a value from a function | return *expr \[, expr\]* |
