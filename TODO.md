# TODO
This is a file annotating all the current tasks that are unable to be completed until another component is finished.
This file exists to prevent potential debug hell and to ensure that all features get implemented properly and are not forgotten.

 - Add Identifier based data type checking *(syc/icg/types.py)*
 - Add Function body parsing/merge return type checking with block parser *(syc/icg/functions.py)*
 - Pass body into literal for inline functions *(syc/icg/atom.py)*
 - Fix Array initialization grammar and ICG for expression based length initialization *(everywhere)*
   **Notes**
   
     * Fix grammatical expression `[types, INTEGER_LITERAL]` to `[types, expr]`.
     * Remove count parameter entirely?  Array bound checking likely will be runtime 
     task and not handled at compile time.  *_Unsure_*   