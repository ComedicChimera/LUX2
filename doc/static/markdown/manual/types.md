# Data Types

 - [What is a Data Type](#types)
 - [Printing to the Console](#console)
 - [Basic Types](#basic_types)

## What is a Data Type? <a name="types">

In SyClone, all data has a type.  This type simply specifies what kind of
data, for example, an integer, a character, or a decimal.  SyClone employs
what is called a **unified type system**.  This means that almost all various
sizes of a specific data are condensed into one (the most common size).
The only value to break from this trend are integers as you'll see later on.

## Printing to the Console <a name="console">

Sometimes it is necessary to view to value of item or result of a function call.
To do this, you can **print** its values to the console.  This is done with the
`println` function.

The example syntax for displaying a value to the console would be:

    println(1);

    println(3.14);

Place the value you want display between the parentheses.

## Basic Types <a name="basic_types">

The basic SyClone types can be broken into 4 catagories: numbers, characters, booleans, and bytes.
Each data type is designated by its corresponding keyword along with a set of **literals** that go with it.

### Numbers

There are 3 kinds of numbers in SyClone: integers, floats, and unreal numbers.  Each has its own set of literals associated with it.

    // integers
    int, long // <- keyword  
    0 123 10456 // <- literals
    
    // floats
    float // <- keyword
    0.2 3.14 1.002 // <- literals
    
    // unreal
    complex // <- keyword
    2i 45i 0.5i // <- literals
    
Each literal is an example of the syntax used ie. all floats have a decimal, complexes end in `i` etc.
The keyword represents the word used as each literal's **type designator**.  These will become important once we start
talking about variables.

### Characters

There are only 2 kinds of character based types in SyClone: chars and strings.

    // chars
    char // <- keyword
    'c' '\n' 'ч' ''
    
    // strings
    str // <- keyword
    "hello there" "朋友" ""
    
A string represents a set of chars, whereas a char is merely a single character.  Notice that both strings and chars can contain
special symbols as they are encoded in UTF-8.  In addition to this, there a number of **escape sequences** that designate
certain special characters such as `\n` (newline), `\t` (tab), and `\b` (backspace).
