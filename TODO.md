# TODO
This is a file annotating all the current tasks that are unable to be completed until another component is finished.
This file exists to prevent potential debug hell and to ensure that all features get implemented properly and are not forgotten.
 
 - Remove to_str methods once testing is complete *(everywhere)*
 
 - Comment expr.py *(syc/icg/generators/expr.py)*

 - Add static cast checking *(syc/icg/casting.py)*
 
 - Add value cast checking *(syc/icg/casting.py)*
 
 - Redo function checking to check for code paths and allow for type coercion *(syc/icg/generators/functions.py)*
 
 - Add constexpr checker *(syc/icg/constexpr)*
 
 - Add packages to get members checking *(syc/icg/generators/atom.py)*
 
 - Add interface, struct and module based type coercion *(syc/icg/types.py, syc/icg/casting.py)*
 
 - Add validity cast *(syc/icg/casting.py)*
 
 - Consider removing operator overloading from initial generation *(syc/icg/generators/...)*

## Tests
This is a special section of TODO.md devoted specifically to tests that need to be run on certain components of the compiler.

 - Test: expr.py, atom.py
 
 - Test: stmt.py 
 
 - Test: tuple-based declaration
 
## Notes
This is a separate section regarding notes for things that need to be taken into account in future components of the compiler.

 - Statement parser should ignore `return` and `yield`.  They will be parsed by the return type parser.  However, ensure that
 they are checked for context. (along with break and continue)
 
 - Functions that return multiple values actually return tuples
