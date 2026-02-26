# Translation Pipeline — Complete Explanation

This document explains everything about the translation system: how it works,
what each component does, and detailed examples of the full process.

---

## Table of Contents

1. [Big Picture](#1-big-picture)
2. [Stage 1 — CPG Generation](#2-stage-1--cpg-generation)
3. [Stage 2 — APM Extraction](#3-stage-2--apm-extraction)
4. [The APM JSON Format](#4-the-apm-json-format)
5. [Stage 3 — Code Generation](#5-stage-3--code-generation)
6. [How `emit` Works Step by Step](#6-how-emit-works-step-by-step)
7. [Where Languages Differ](#7-where-languages-differ)
8. [The Array Size Problem](#8-the-array-size-problem)
9. [The PRINT Reconstruction](#9-the-print-reconstruction)
10. [Stage 4 — Verification](#10-stage-4--verification)
11. [Resource Files](#11-resource-files)

---

## 1. Big Picture

The system translates code between C, C++, and Java — **not** by directly converting
syntax, but by first converting to a **language-neutral intermediate representation**
called the APM (Abstract Program Model), then generating syntax from that.

```
Source (.c / .cpp / .java)
        │
        ▼  joern-parse
   CPG Binary (.bin)         ← Code Property Graph (Joern's internal graph)
        │
        ▼  extract_apm.sc
   APM JSON (.json)          ← Language-neutral description of the program
        │
        ▼  generate_{c|cpp|java}.py
   Generated Source Code
        │
        ▼  gcc / g++ / javac
   Compiled Binary → Output Comparison
```

**Analogy:** Like translating French → Spanish via a universal recipe card.
You don't translate French → Spanish directly. You write down the recipe in
neutral terms (ingredients, quantities, steps), then someone rewrites it in Spanish.
The APM is that universal recipe card.

---

## 2. Stage 1 — CPG Generation

```bash
joern-parse source.c --output source_cpg.bin
```

Joern parses the source file and builds a **Code Property Graph** — a binary graph that
merges three classic program representations:

| Graph | What it captures |
|---|---|
| AST | Syntactic structure (expressions, statements) |
| CFG | Execution order (loops, branches, returns) |
| PDG | Data and control dependencies |

**Key insight**: A `for` loop from C and a `for` loop from Java produce the same
CPG node types. The CPG is language-aware at parse time but language-neutral by structure.

**Caching**: `run_translation.sh` skips this step if `_cpg.bin` already exists.

---

## 3. Stage 2 — APM Extraction (`extract_apm.sc`)

```bash
CPG_FILE=source_cpg.bin joern --script extract_apm.sc
```

This 782-line Joern Scala script traverses the CPG and serializes it into APM JSON.

### The 5 core transformations

**1. Type Canonicalization**

Raw language types get normalized to canonical types:
```
"long long int"      → LONG
"int *"              → INT_ARRAY
"bool"               → BOOL
"java.lang.String[]" → STRING
```
This makes the APM truly language-neutral.

**2. Parameter Role Detection**

The script analyzes parameters to determine their role:
```c
int sumArray(int arr[], int n)
```
It checks: does `n` appear in a loop bound (`i < n`) alongside `arr`?
If yes → tagged as `"role": "ARRAY_SIZE"`.

This is critical: C needs `int n` explicitly, Java uses `arr.length`.
The role tag lets generators add or remove the parameter automatically.

**3. I/O Normalization**

All print idioms collapse to one APM `PRINT` node:
```
printf("Sum: %d\n", total)        →  PRINT {format: "Sum: %d\n", args: [total]}
std::cout << "Sum: " << x << endl →  PRINT {format: "{}\\n",     args: ["Sum: ", x]}
System.out.println("Sum: " + x)   →  PRINT {format: "{}\\n",     args: ["Sum: ", x]}
```

**4. Operator Mapping**

Joern's internal operator names → source symbols:
```
<operator>.addition       → +
<operator>.shiftLeft      → <<  (also detected as cout chaining)
<operator>.assignmentPlus → +=
```

**5. Expression Tree Serialization**

Every expression becomes a typed JSON tree:
```json
{ "kind": "BINARY_OP", "operator": "+",
  "left":  { "kind": "IDENTIFIER", "name": "i" },
  "right": { "kind": "LITERAL",    "value": "1" } }
```

---

## 4. The APM JSON Format

A complete APM JSON for a real function:

**Source (C):**
```c
int factorial(int n) {
    int result = 1;
    for (int i = 1; i <= n; i++) {
        result = result * i;
    }
    return result;
}
```

**APM JSON:**
```json
{
  "source_file": "factorial.c",
  "source_lang": "c",
  "functions": [
    {
      "name": "factorial",
      "return_type": "INT",
      "parameters": [
        { "name": "n", "type": "INT", "role": "DATA" }
      ],
      "body": [
        {
          "kind": "DECLARE",
          "name": "result",
          "type": "INT",
          "init": { "kind": "LITERAL", "value": "1" }
        },
        {
          "kind": "FOR",
          "init": { "kind": "DECLARE", "name": "i", "type": "INT",
                    "init": { "kind": "LITERAL", "value": "1" } },
          "condition": { "kind": "BINARY_OP", "operator": "<=",
                         "left":  { "kind": "IDENTIFIER", "name": "i" },
                         "right": { "kind": "IDENTIFIER", "name": "n" } },
          "update": { "kind": "UNARY_OP", "operator": "++",
                      "operand": { "kind": "IDENTIFIER", "name": "i" } },
          "body": [
            { "kind": "ASSIGN",
              "target": { "kind": "IDENTIFIER", "name": "result" },
              "value":  { "kind": "BINARY_OP", "operator": "*",
                          "left":  { "kind": "IDENTIFIER", "name": "result" },
                          "right": { "kind": "IDENTIFIER", "name": "i" } } }
          ]
        },
        {
          "kind": "RETURN",
          "value": { "kind": "IDENTIFIER", "name": "result" }
        }
      ]
    }
  ],
  "entry_point": {
    "declarations": [],
    "statements": [ ... ]
  }
}
```

### All APM node kinds

| Kind | What it represents |
|---|---|
| `DECLARE` | Variable declaration: `int x = 5` |
| `ASSIGN` | Assignment: `x = y + 1` |
| `FOR` | For loop with init/condition/update/body |
| `WHILE` | While loop with condition/body |
| `DO_WHILE` | Do-while with body/condition |
| `IF` | If/else with condition/then/else_body |
| `RETURN` | Return statement |
| `PRINT` | Any print (printf/cout/println) normalized |
| `SCAN` | Any input (scanf) — not translatable |
| `BREAK` | break statement |
| `CONTINUE` | continue statement |
| `EXPR_STMT` | Bare expression as statement |
| `BINARY_OP` | a + b, a < b, a && b, etc. |
| `UNARY_OP` | !x, -y, i++, i-- |
| `IDENTIFIER` | A variable name |
| `LITERAL` | A constant value: 5, "hello", true |
| `CALL` | Function call: f(a, b) |
| `ARRAY_ACCESS` | arr[i] |
| `MEMBER_ACCESS` | arr.length |
| `CAST` | (int)x, static_cast\<int\>(x) |

---

## 5. Stage 3 — Code Generation

### File structure

```
codegen_base.py       ← Base class: all shared logic
generate_c.py         ← Inherits base, overrides C-specific parts
generate_cpp.py       ← Inherits base, overrides C++-specific parts
generate_java.py      ← Inherits base, overrides Java-specific parts
```

### Entry point

```bash
python3 generate_java.py apm.json --output generated.java
```

Calls `generate(apm)`:
1. `optimize_apm(apm)` — pre-pass, merges split DECLARE+ASSIGN pairs
2. Emit each function in `apm["functions"]`
3. Emit the `apm["entry_point"]` (main method)

---

## 6. How `emit` Works Step by Step

`emit` functions read fields from the APM JSON and wrap them in syntax.
Every value comes *directly* from the JSON — nothing is invented.

### `emit_stmt` — the statement dispatcher

```python
def emit_stmt(self, stmt, level):
    kind = stmt["kind"]         # read the "kind" field

    if   kind == "DECLARE":   return self.emit_declare(stmt, level)
    elif kind == "ASSIGN":    return self.emit_assign(stmt, level)
    elif kind == "FOR":       return self.emit_for(stmt, level)
    elif kind == "WHILE":     return self.emit_while(stmt, level)
    elif kind == "IF":        return self.emit_if(stmt, level)
    elif kind == "RETURN":    return self.emit_return(stmt, level)
    elif kind == "PRINT":     return self.emit_print(stmt, level)  # language-specific
    elif kind == "BREAK":     return ["break;"]
    elif kind == "CONTINUE":  return ["continue;"]
```

Just a big `if/elif`. When it sees `"kind": "FOR"`, it calls `emit_for`. No magic.

### `emit_expr` — the expression tree walker

```python
def emit_expr(self, expr):
    kind = expr["kind"]

    if kind == "LITERAL":
        return expr["value"]                         # "5", "true", "\"hello\""

    elif kind == "IDENTIFIER":
        return expr["name"]                          # "result", "i", "n"

    elif kind == "BINARY_OP":
        left  = self.emit_expr(expr["left"])         # recurse
        right = self.emit_expr(expr["right"])        # recurse
        op    = expr["operator"]
        return f"({left} {op} {right})"             # "(i <= n)"

    elif kind == "UNARY_OP":
        operand = self.emit_expr(expr["operand"])
        return f"{expr['operator']}{operand}"        # "i++"

    elif kind == "CALL":
        func = expr["function"]
        args = self.emit_call_args(func, expr.get("arguments", []))
        return f"{func}({args})"

    elif kind == "ARRAY_ACCESS":
        arr = self.emit_expr(expr["array"])
        idx = self.emit_expr(expr["index"])
        return f"{arr}[{idx}]"
```

### Full example: walking the factorial APM

**DECLARE result:**
```
emit_stmt sees kind="DECLARE"
  → emit_declare reads:
       name = "result"
       type = "INT"  → resolve_type("INT","java") → "int"
       init = LITERAL "1"  → emit_expr → "1"
  → writes: int result = 1;
```

**FOR loop:**
```
emit_stmt sees kind="FOR"
  → emit_for reads:
       init      = DECLARE "i", INT, init=LITERAL "1" → "int i = 1"
       condition = BINARY_OP "<=" left=IDENTIFIER "i" right=IDENTIFIER "n"
                    → emit_expr called:
                         left  = emit_expr(IDENTIFIER "i") → "i"
                         right = emit_expr(IDENTIFIER "n") → "n"
                         op    = "<="
                    → returns "(i <= n)"
       update    = UNARY_OP "++" operand=IDENTIFIER "i"
                    → emit_expr → "i++"
       body      = [ ASSIGN result = result * i ]
                    → emit_stmt → emit_assign:
                         target = emit_expr(IDENTIFIER "result") → "result"
                         value  = emit_expr(BINARY_OP "*")
                                     left  = "result"
                                     right = "i"
                                  → "(result * i)"
                    → writes: result = (result * i);
  → writes:
       for (int i = 1; (i <= n); i++) {
           result = (result * i);
       }
```

**RETURN:**
```
emit_stmt sees kind="RETURN"
  → emit_return reads:
       value = IDENTIFIER "result" → emit_expr → "result"
  → writes: return result;
```

**Final Java output assembled:**
```java
public static int factorial(int n) {
    int result = 1;
    for (int i = 1; (i <= n); i++) {
        result = (result * i);
    }
    return result;
}
```

Every value (`result`, `i`, `n`, `1`, `*`, `<=`) came **directly from the APM JSON**.
The emit functions only added: `public static`, `int`, `=`, `;`, `for (`, `) {`, `}`.

---

## 7. Where Languages Differ

`emit_print` is *not* in the base class — each language must implement it.

### Same APM PRINT node:
```json
{ "kind": "PRINT", "format": "Sum: %d\\n",
  "arguments": [ { "kind": "IDENTIFIER", "name": "total" } ] }
```

### C generates:
```c
printf("Sum: %d\n", total);
```
How: keeps format string + adds args positionally.

### Java generates:
```java
System.out.println("Sum: " + total);
```
How: splits `"Sum: %d\n"` on `%d` → `"Sum: "` + `total`. Strips `\n` (println auto-adds).

### C++ generates:
```cpp
std::cout << "Sum: " << total << std::endl;
```
How: each piece becomes a `<<` chain. `std::endl` replaces `\n`.

**All three read the exact same JSON. Only the surrounding syntax changes.**

---

## 8. The Array Size Problem

C requires explicit array size. Java arrays know their own size.

**C source:**
```c
int sum(int arr[], int n) {   // n is explicit size parameter
    int total = 0;
    for (int i = 0; i < n; i++) {
        total += arr[i];
    }
    return total;
}
int main() {
    int nums[] = {1, 2, 3};
    int result = sum(nums, 3);   // pass 3 explicitly
}
```

**APM tags `n` with role: ARRAY_SIZE** (detected because `n` appears in `i < n` alongside `arr`)

**Java generator reads this and:**

1. **Signature**: skips `n` → `public static int sum(int[] arr)`
2. **Body**: wherever IDENTIFIER `"n"` appears → writes `arr.length` instead
3. **Call site**: drops the `3` arg → `sum(nums)`

**Java output:**
```java
public static int sum(int[] arr) {
    int total = 0;
    for (int i = 0; (i < arr.length); i++) {
        total += arr[i];
    }
    return total;
}
public static void main(String[] args) {
    int[] nums = new int[]{1, 2, 3};
    int result = sum(nums);         // 3 dropped, arr.length used inside
}
```

Going the other way (Java → C): the C generator *injects* `int n` and replaces
`arr.length` with `n`.

---

## 9. The PRINT Reconstruction

The hardest part — going between printf format strings and Java/C++ concatenation.

### C → Java (format string to concatenation)

**APM stores:**
```json
{ "format": "GCD of %d and %d is %d\n",
  "arguments": [num1, num2, gcd] }
```

Java generator:
1. Split format string on `%d`/`%f`/`%s` tokens:
   `["GCD of ", "%d", " and ", "%d", " is ", "%d", "\n"]`
2. String segments → wrap in `"..."`: `"GCD of "`, `" and "`, `" is "`
3. `%d` tokens → pull next arg: `num1`, `num2`, `gcd`
4. Join with ` + `: `"GCD of " + num1 + " and " + num2 + " is " + gcd`
5. Strip the trailing `\n` → use `println` (auto-adds newline)

**Output:** `System.out.println("GCD of " + num1 + " and " + num2 + " is " + gcd);`

### Java → C (concatenation to format string)

**APM stores:**
```json
{ "format": "{}\\n",
  "arguments": ["\"Sum of digits of \"", number, "\" is \"", result] }
```

C generator:
1. For each arg: is it a string literal → put in format string; is it a variable → add `%d`
2. Builds: `"Sum of digits of %d is %d\n"`
3. Collects variables: `number, result`

**Output:** `printf("Sum of digits of %d is %d\n", number, result);`

---

## 10. Stage 4 — Verification (`verify_translation.py`)

```bash
python3 verify_translation.py \
  --source original.c \
  --generated generated.java \
  --target-lang java
```

**Level 1 — Compilation:**
```
gcc original.c -o orig_bin          # compile original
javac generated.java -d outdir       # compile generated
```

**Level 2 — Output comparison:**
```
Run orig_bin → capture stdout:  "Factorial of 5 is 120"
Run generated → capture stdout: "Factorial of 5 is 120"
Compare → MATCH ✓
```

A MATCH means the translation is **semantically correct** — same output for same logic.

---

## 11. Resource Files

### `resources/type_map.json`

Maps canonical types to language-specific types. Used by `resolve_type()`.

```json
{
  "canonical_types": {
    "INT":      { "c": "int",  "cpp": "int",       "java": "int"      },
    "LONG":     { "c": "long", "cpp": "long long",  "java": "long"     },
    "BOOL":     { "c": "int",  "cpp": "bool",       "java": "boolean"  },
    "INT_ARRAY":{ "c": "int",  "cpp": "int",        "java": "int[]"    }
  },
  "print_format_specifiers": {
    "INT": "%d", "LONG": "%ld", "DOUBLE": "%f", "STRING": "%s"
  }
}
```

### `resources/io_map.json`

Maps I/O function names and styles per language. Used by print generators.

```json
{
  "io_functions": {
    "print": {
      "c":    { "function": "printf",             "format_string": true  },
      "cpp":  { "function": "std::cout",           "format_string": false },
      "java": { "function": "System.out.println",  "auto_newline": true   }
    }
  }
}
```

### `resources/apm_schema.json`

JSON Schema validating the APM structure. Used to catch malformed APM before
the generator runs.

---

## Quick Reference: Translation Direction Transformations

| Direction | Key changes |
|---|---|
| C → Java | Remove `int n` param, `n` → `arr.length`, `printf` → `println`, add class wrapper |
| Java → C | Inject `int n` param, `arr.length` → `n`, `println` → `printf` |
| C → C++ | `printf` → `cout`, `<stdio.h>` → `<iostream>`, `long` → `long long` |
| C++ → C | `cout` → `printf`, reconstruct format string |
| Java → C++ | Remove size param, `println` → `cout`, add `std::` prefix |
| C++ → Java | Remove size param, `cout` → `println`, add class wrapper |
