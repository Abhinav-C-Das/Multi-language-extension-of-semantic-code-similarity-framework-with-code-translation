#!/usr/bin/env python3
"""
generate_c.py — APM JSON → C source code.

Usage:
  python3 generate_c.py apm.json --output generated.c
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codegen_base import CodeGenerator


class CCodeGenerator(CodeGenerator):

    def __init__(self):
        super().__init__("c")
        # Track functions that had an array-size parameter injected
        # Maps: function_name -> True
        self._size_injected_funcs = {}
        # Track declared array variables and their sizes (for call-site injection)
        # Maps: var_name -> size_expr
        self._array_sizes = {}

    # -------------------------------------------------------
    # Concat flattening — decompose BINARY_OP(+) trees from Java
    # -------------------------------------------------------
    def _flatten_concat(self, node):
        """Recursively flatten BINARY_OP(+) trees into a flat list of parts."""
        if node.get("kind") == "BINARY_OP" and node.get("operator") == "+":
            left = self._flatten_concat(node.get("left", {}))
            right = self._flatten_concat(node.get("right", {}))
            return left + right
        return [node]

    # -------------------------------------------------------
    # C-specific overrides
    # -------------------------------------------------------
    def format_declaration(self, resolved_type, name, canonical_type):
        if self.is_array_type(canonical_type):
            base = self.resolve_type(self.base_element_type(canonical_type))
            return f"{base} {name}[]"
        return f"{resolved_type} {name}"

    def emit_member_access(self, expr):
        """Replace arr.length with size parameter 'n'."""
        member = expr.get("member", "")
        if member == "length":
            return "n"
        obj = self.emit_expr(expr.get("object"))
        return f"{obj}.{member}"

    def emit_print(self, stmt, level):
        I = self.indent(level)
        fmt = stmt.get("format", "")
        raw_args = stmt.get("arguments", [])

        # Filter out stream/namespace identifiers that leak from C++/Java
        STREAM_TOKENS = {"System.out", "std::cout", "cout", "std::endl",
                         "endl", "std.cout", "std.endl", "std"}
        args = []
        for a in raw_args:
            expr_str = self.emit_expr(a)
            if expr_str in STREAM_TOKENS:
                continue
            args.append(a)

        # Determine if a trailing newline is required from the APM format
        has_newline = fmt.endswith("\\n")

        # The APM extractor duplicates the printf format string as arguments[0]
        # (a STRING literal). Skip it — the format is already in stmt["format"].
        if args and fmt:
            a0 = args[0]
            if a0.get("kind") == "LITERAL" and a0.get("type") == "STRING":
                lit = a0.get("value", "")
                raw = lit.strip('"')
                if raw == fmt or raw == fmt.replace("\\n", "\n"):
                    args = args[1:]

        # ---- C-originated printf with % specifiers: pass through as-is ----
        if "%" in fmt:
            arg_strs = [self.emit_expr(a) for a in args]
            if arg_strs:
                return [f'{I}printf({self._c_string(fmt)}, {", ".join(arg_strs)});']
            return [f'{I}printf({self._c_string(fmt)});']

        # ---- No real arguments: emit bare newline if needed ----
        if not args:
            if has_newline:
                return [f'{I}printf("\\n");']
            return []  # nothing to print at all

        # ---- Flatten all args (handles Java string concatenation trees) ----
        flat_parts = []
        for a in args:
            flat_parts.extend(self._flatten_concat(a))

        # ---- Build format string dynamically from flattened parts ----
        fmt_parts = []
        val_exprs = []

        for a in flat_parts:
            expr_str = self.emit_expr(a)
            val = a.get("value", "")
            # A LITERAL whose value is wrapped in double-quotes is a string
            if a.get("kind") == "LITERAL" and isinstance(val, str) and val.startswith('"'):
                fmt_parts.append(val.strip('"'))
            elif a.get("kind") == "LITERAL" and isinstance(val, str) and val.startswith("'"):
                fmt_parts.append("%c")
                val_exprs.append(expr_str)
            elif a.get("type") in ("LONG",):
                fmt_parts.append("%ld")
                val_exprs.append(expr_str)
            elif a.get("type") in ("DOUBLE", "FLOAT"):
                fmt_parts.append("%f")
                val_exprs.append(expr_str)
            elif a.get("type") == "STRING":
                fmt_parts.append("%s")
                val_exprs.append(expr_str)
            else:
                fmt_parts.append("%d")
                val_exprs.append(expr_str)

        fmt_string = "".join(fmt_parts)
        if has_newline:
            fmt_string += "\\n"

        if val_exprs:
            return [f'{I}printf("{fmt_string}", {", ".join(val_exprs)});']
        return [f'{I}printf("{fmt_string}");']

    def _c_string(self, s):
        """Ensure proper C string quoting."""
        if s.startswith('"') and s.endswith('"'):
            return s
        return f'"{s}"'

    def emit_cast(self, target_type, inner):
        return f"({target_type}) ({inner})"

    # -------------------------------------------------------
    # Call-args override: inject array size for Java-sourced calls
    # -------------------------------------------------------
    def emit_call_args(self, func_name, args):
        """If the function had a size param injected, add the array's size."""
        arg_strs = [self.emit_expr(a) for a in args]
        if func_name in self._size_injected_funcs:
            # Find the array argument and compute its size
            for a in args:
                aname = a.get("name", "")
                if aname in self._array_sizes:
                    arg_strs.append(self._array_sizes[aname])
                    break
            else:
                # Fallback: use sizeof if array name not tracked
                if arg_strs:
                    arr_name = arg_strs[0]
                    arg_strs.append(f"sizeof({arr_name})/sizeof({arr_name}[0])")
        return ", ".join(arg_strs)

    # -------------------------------------------------------
    # Function signature with array-size injection
    # -------------------------------------------------------
    def _build_func_sig(self, func):
        ret = self.resolve_type(func["return_type"])
        name = func["name"]
        params = func.get("parameters", [])

        param_strs = []
        needs_size = False

        for p in params:
            ptype = p["type"]
            pname = p["name"]
            if self.is_array_type(ptype):
                base = self.resolve_type(self.base_element_type(ptype))
                param_strs.append(f"{base} {pname}[]")
                needs_size = True
            elif p.get("role") == "ARRAY_SIZE":
                param_strs.append(f"int {pname}")
            else:
                resolved = self.resolve_type(ptype)
                param_strs.append(f"{resolved} {pname}")

        # If source was Java (no explicit size param) and we have an array, inject 'int n'
        if needs_size and not any(p.get("role") == "ARRAY_SIZE" for p in params):
            param_strs.append("int n")
            self._size_injected_funcs[name] = True

        return f"{ret} {name}({', '.join(param_strs)})"

    # -------------------------------------------------------
    # Track array variable sizes from initializers
    # -------------------------------------------------------
    def emit_stmt(self, stmt, level):
        """Override to track array declarations for size injection."""
        if stmt and stmt.get("kind") == "DECLARE":
            name = stmt.get("name", "")
            ctype = stmt.get("type", "")
            if self.is_array_type(ctype):
                init = stmt.get("init")
                if init and init.get("function") == "arrayInitializer":
                    count = len(init.get("arguments", []))
                    self._array_sizes[name] = str(count)
        elif stmt and stmt.get("kind") == "ASSIGN":
            val = stmt.get("value", {})
            if val.get("kind") == "CALL_EXPR" and val.get("function") == "arrayInitializer":
                target = stmt.get("target", {})
                aname = target.get("name", "")
                count = len(val.get("arguments", []))
                self._array_sizes[aname] = str(count)
        return super().emit_stmt(stmt, level)

    # -------------------------------------------------------
    # Full program generation
    # -------------------------------------------------------
    def generate(self, apm):
        self.apm = apm
        self._size_injected_funcs = {}
        self._array_sizes = {}
        self.optimize_apm(self.apm)
        lines = []

        # Headers
        lines.append("// Auto-generated from CPG Abstract Program Model")
        lines.append("#include <stdio.h>")
        lines.append("")

        # Functions (non-main) — process signatures first to track injected params
        for func in apm.get("functions", []):
            sig = self._build_func_sig(func)
            lines.append(f"{sig} {{")
            for stmt in func.get("body", []):
                lines.extend(self.emit_stmt(stmt, 1))
            lines.append("}")
            lines.append("")

        # Main / entry point
        entry = apm.get("entry_point")
        if entry:
            lines.append("int main() {")
            for stmt in entry.get("declarations", []):
                lines.extend(self.emit_stmt(stmt, 1))
            for stmt in entry.get("statements", []):
                lines.extend(self.emit_stmt(stmt, 1))
            # Only add return 0 if the last statement isn't already a return
            stmts = entry.get("statements", [])
            if not stmts or stmts[-1].get("kind") != "RETURN":
                lines.append("    return 0;")
            lines.append("}")
        else:
            lines.append("int main() {")
            lines.append("    return 0;")
            lines.append("}")

        return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate C code from APM JSON")
    parser.add_argument("apm_file", help="Path to APM JSON file")
    parser.add_argument("--output", "-o", help="Output C file path")
    args = parser.parse_args()

    gen = CCodeGenerator()
    gen.generate_from_file(args.apm_file, args.output)


if __name__ == "__main__":
    main()
