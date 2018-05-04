# TODO
This is a file annotating all the current tasks that are unable to be completed until another component is finished.
This file exists to prevent potential debug hell and to ensure that all features get implemented properly and are not forgotten.

 - Add Identifier based data type checking *(syc/icg/types.py)*
 
 - Add Function body parsing/merge return type checking with block parser *(syc/icg/functions.py)*
 
 - Add GetMember trailer checking *(syc/icg/generators/atom.py)*
 
 - Remove to_str methods once testing is complete *(everywhere)*
 
 - Comment expr.py *(syc/icg/generators/expr.py)* 
 
 - Add value cast to function call *(syc/icg/generators/atom.py)*

## Tests
This is a special section of TODO.md devoted specifically to tests that need to be run on certain components of the compiler.

 - Test: expr.py, atom.py (thoroughly) *TEST THE EXPRESSION PARSER*
