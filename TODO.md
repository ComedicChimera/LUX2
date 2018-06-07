# TODO
This is a file annotating all the current tasks that are unable to be completed until another component is finished.
This file exists to prevent potential debug hell and to ensure that all features get implemented properly and are not forgotten.
 
 - Remove to_str methods once testing is complete *(syc/...)*
 
 - Comment expr.py *(syc/icg/generators/expr.py)*
 
 - Add value cast checking *(syc/icg/casting.py)*
 
 - Redo function checking to check for code paths and allow for type coercion *(syc/icg/generators/functions.py)*
 
 - Add char* casting *(syc/icg/casting.py)*
 
 **General**
 
 - Apply Raymond's optimization rules *(syc/...)*
 
 - Add detupling *(syc/...)*
 
 - Add operator aggregators *(syc/...)*
 
 - Add static templates *(syc/icg/...)*


## Tests
This is a special section of TODO.md devoted specifically to tests that need to be run on certain components of the compiler.

 - Test: expr.py, atom.py
 
 - Test: stmt.py 
 
 - Test: tuple-based declaration
 
 - Test: get member in constexpr and in general
 
## Notes
This is a separate section regarding notes for things that need to be taken into account in future components of the compiler.

 - Statement parser should ignore `return` and `yield`.  They will be parsed by the return type parser.  However, ensure that
 they are checked for context. (along with break and continue)
 
 - Functions that return multiple values actually return tuples
 
 - Data types can be obtained from a value cast through the use of the `DataType` function; the raw property is ignored to allow for
 template-aware type accessing.
