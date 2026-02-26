#!/usr/bin/env python3
"""
generate_cpp.py — APM JSON → C++ source code.

Usage:
  python3 generate_cpp.py apm.json --output generated.cpp
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codegen_base import CodeGenerator


class CppCodeGenerator(CodeGenerator):

    def __init__(self):
        super().__init__("cpp")
        self._size_injected_funcs = {}
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
    # C++ specific overrides
    # -------------------------------------------------------
    def format_declaration(self, resolved_type, name, canonical_type):
        if self.is_array_type(canonical_type):
            base = self.resolve_type(self.base_element_type(canonical_type))
            return f"{base} {name}[]"
        if canonical_type == "BOOL":
            return f"bool {name}"
        return f"{resolved_type} {name}"

    def emit_member_access(self, expr):
        """Replace arr.length with 'n' (C++ uses explicit size param like C)."""
        member = expr.get("member", "")
        if member == "length":
            return "n"
        obj = self.emit_expr(expr.get("object"))
        return f"{obj}.{member}"

    def emit_print(self, stmt, level):
        I = self.indent(level)
        args = stmt.get("arguments", [])
        fmt = stmt.get("format", "")

        if not args and not fmt:
            return [f"{I}std::cout << std::endl;"]

        # Filter out stream tokens that may leak from APM
        filtered = []
        for a in args:
            e = self.emit_expr(a)
            if e in ("System.out", "std::cout", "cout", "std::endl", "endl",
                      "std.cout", "std.endl", "std"):
                continue
            filtered.append(a)
        args = filtered

        # The APM extractor duplicates the printf format string as arguments[0]
        # (a STRING literal). Skip it — the format is already in stmt["format"].
        if args and fmt:
            a0 = args[0]
            if a0.get("kind") == "LITERAL" and a0.get("type") == "STRING":
                lit = a0.get("value", "")
                # Strip surrounding quotes from the literal value
                raw = lit.strip('"')
                if raw == fmt or raw == fmt.replace("\\n", "\n"):
                    args = args[1:]

        # Determine newline from APM format
        use_endl = fmt.endswith("\\n")
        display_fmt = fmt[:-2] if use_endl else fmt

        # No real args after filtering → just endl
        if not args:
            if use_endl:
                return [f"{I}std::cout << std::endl;"]
            return []

        parts = []
        if "%" in display_fmt:
            import re
            tokens = re.split(r'(%[dflsc])', display_fmt)
            arg_idx = 0  # args already has format string stripped
            for tk in tokens:
                if tk in ("%d", "%f", "%l", "%s", "%c"):
                    if arg_idx < len(args):
                        parts.append(self.emit_expr(args[arg_idx]))
                        arg_idx += 1
                elif tk:
                    parts.append(f'"{tk}"')
        elif display_fmt in ("{}", ""):
            # Flatten any Java concat trees in the args
            flat_parts = []
            for a in args:
                flat_parts.extend(self._flatten_concat(a))
            for a in flat_parts:
                parts.append(self.emit_expr(a))
        else:
            parts.append(f'"{display_fmt}"')

        if not parts:
            parts = ['""']

        chain = " << ".join(parts)
        endl_suffix = " << std::endl" if use_endl else ""
        return [f"{I}std::cout << {chain}{endl_suffix};"]

    def emit_cast(self, target_type, inner):
        return f"static_cast<{target_type}>({inner})"

    # -------------------------------------------------------
    # Function signature (same as C — explicit size param)
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

        if needs_size and not any(p.get("role") == "ARRAY_SIZE" for p in params):
            param_strs.append("int n")
            self._size_injected_funcs[name] = True

        return f"{ret} {name}({', '.join(param_strs)})"

    # -------------------------------------------------------
    # Call-args override: inject array size for Java-sourced calls
    # -------------------------------------------------------
    def emit_call_args(self, func_name, args):
        arg_strs = [self.emit_expr(a) for a in args]
        if func_name in self._size_injected_funcs:
            for a in args:
                aname = a.get("name", "")
                if aname in self._array_sizes:
                    arg_strs.append(self._array_sizes[aname])
                    break
            else:
                if arg_strs:
                    arr_name = arg_strs[0]
                    arg_strs.append(f"sizeof({arr_name})/sizeof({arr_name}[0])")
        return ", ".join(arg_strs)

    # -------------------------------------------------------
    # Track array sizes from declarations and assignments
    # -------------------------------------------------------
    def emit_stmt(self, stmt, level):
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

        lines.append("// Auto-generated from CPG Abstract Program Model")
        lines.append("#include <iostream>")
        lines.append("")

        # Functions
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
    parser = argparse.ArgumentParser(description="Generate C++ code from APM JSON")
    parser.add_argument("apm_file", help="Path to APM JSON file")
    parser.add_argument("--output", "-o", help="Output C++ file path")
    args = parser.parse_args()

    gen = CppCodeGenerator()
    gen.generate_from_file(args.apm_file, args.output)


if __name__ == "__main__":
    main()
