# Variable
Includes variables and constants.  Constants have the internal `CONSTANT` modifier.

| Field | Value |
| ----- | ----- |
| Name | Variable Name |
| DataType | Variable's Data Type |
| Modifiers | Viable Modifiers + CONSTANT |
| Members | `[ initialized_value ]` |


# Function
Includes all normal functions, asynchronous functions and methods.

| Field | Value |
| ----- | ----- |
| Name | Function Name |
| DataType | Function |
| Modifiers | Viable Modifiers |
| Members | `[ parameters, body ]` |


Notes
-----

 - Instance behaves the same for all members that can be instance.  Default static members include: `structs, type, interfaces,
  and sub-modules`