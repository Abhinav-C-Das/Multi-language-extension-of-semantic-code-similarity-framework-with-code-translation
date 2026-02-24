# Java APM Extraction — Design Notes

## Why Java Test Files Have No `package` Declaration

The Java source files in `data/cpg_t1/` intentionally omit `package` declarations:

1. **Joern CPG behavior** — When a `.java` file has `package data.cpg_t1;`, Joern qualifies the class internally (e.g., `data.cpg_t1.MaxElement`), altering how `method.filename` is stored. This caused the filename filter in `extract_apm.sc` to return zero methods, producing empty APMs.

2. **Standalone CS1 programs** — These are simple, self-contained algorithm demonstrations (find max, sum digits, count vowels). They have no inter-file dependencies, so a package declaration adds no value.

3. **Compilation/verification** — Our `verify_translation.py` uses simple `javac File.java && java ClassName`. A package declaration requires the classpath root to be set correctly and the class invoked as `java data.cpg_t1.ClassName`, which the verifier doesn't handle.

## Filename Filter Design

The `extract_apm.sc` method filter (line ~740) uses a **tiered matching strategy**:

```
1. m.filename.endsWith(tf)                              — exact suffix
2. m.filename.contains(tf)                              — substring
3. m.filename.endsWith(baseName)                        — without extension
4. m.filename.toLowerCase.contains(baseName.toLowerCase) — case-insensitive
5. FALLBACK: use ALL non-external methods                — safe for single-file CPGs
```

The fallback (step 5) is safe because `joern-parse` is always invoked on a single source file, so all non-external methods belong to that file.

## Java-Specific Handling in extract_apm.sc

| Feature | How it's handled |
|---------|-----------------|
| `this` parameter | Filtered by `_.index > 0` (line 678) |
| `main(String[] args)` | `args` param filtered out (line 679) |
| `System.out.println` | Detected by `isIOCall` via `call.code.contains("System.out")` |
| `<init>` / `<clinit>` | Excluded from method list (line 736) |
| `std` namespace leaks | Filtered from Local declarations (line 307) |
