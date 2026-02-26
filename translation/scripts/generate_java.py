#!/usr/bin/env python3
"""
generate_java.py — APM JSON → Java source code.

Usage:
  python3 generate_java.py apm.json --output Generated.java
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from codegen_base import CodeGenerator


class JavaCodeGenerator(CodeGenerator):

    def __init__(self):
        super().__init__("java")
        self.class_name = "Generated"

    # -------------------------------------------------------
    # Java-specific overrides
    # -------------------------------------------------------
    def format_declaration(self, resolved_type, name, canonical_type):
        if self.is_array_type(canonical_type):
            base = self.resolve_type(self.base_element_type(canonical_type))
            return f"{base}[] {name}"
        if canonical_type == "BOOL":
            return f"boolean {name}"
        return f"{resolved_type} {name}"

    def emit_member_access(self, expr):
        """In Java, arr.length is valid — emit directly."""
        obj = self.emit_expr(expr.get("object"))
        member = expr.get("member", "")
        return f"{obj}.{member}"

    def emit_print(self, stmt, level):
        I = self.indent(level)
        args = stmt.get("arguments", [])
        fmt = stmt.get("format", "")

        if not args and not fmt:
            return [f"{I}System.out.println();"]

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
        use_println = fmt.endswith("\\n")
        display_fmt = fmt[:-2] if use_println else fmt

        # No real args after filtering
        if not args:
            if use_println:
                return [f"{I}System.out.println();"]
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
            for a in args:
                parts.append(self.emit_expr(a))
        else:
            parts.append(f'"{display_fmt}"')

        if not parts:
            parts = ['""']

        # Ensure string concatenation does not falsely evaluate earlier integer math
        concat = " + ".join(parts)
        if not parts[0].startswith('"'):
            concat = '"" + ' + concat

        print_func = "System.out.println" if use_println else "System.out.print"
        return [f"{I}{print_func}({concat});"]

    # -------------------------------------------------------
    # Java: C-style int-as-boolean coercion
    # In C, `if (func())` is valid. In Java, int cannot be boolean.
    # Detect non-boolean conditions and add `!= 0`.
    # -------------------------------------------------------
    COMPARISON_OPS = {"<", ">", "<=", ">=", "==", "!=", "&&", "||"}

    def emit_if(self, stmt, level):
        I = self.indent(level)
        cond_node = stmt.get("condition", {})
        cond = self.emit_expr(cond_node)

        # Check if condition is already a boolean expression
        kind = cond_node.get("kind", "")
        is_boolean = False
        if kind == "BINARY_OP" and cond_node.get("operator", "") in self.COMPARISON_OPS:
            is_boolean = True
        elif kind == "UNARY_OP" and cond_node.get("operator", "") == "!":
            is_boolean = True
        elif kind == "LITERAL" and cond_node.get("type") == "BOOL":
            is_boolean = True

        if not is_boolean:
            cond = f"{cond} != 0"

        lines = [f"{I}if ({cond}) {{"]
        for s in stmt.get("then", stmt.get("body", [])):
            lines.extend(self.emit_stmt(s, level + 1))
        lines.append(f"{I}}}")
        else_body = stmt.get("else_body", [])
        if else_body:
            lines[-1] = f"{I}}} else {{"
            for s in else_body:
                lines.extend(self.emit_stmt(s, level + 1))
            lines.append(f"{I}}}")
        return lines

    def emit_cast(self, target_type, inner):
        return f"({target_type}) ({inner})"

    # -------------------------------------------------------
    # Java function signature: remove ARRAY_SIZE, use arr.length
    # -------------------------------------------------------
    def _build_func_sig(self, func):
        ret = self.resolve_type(func["return_type"])
        name = func["name"]
        params = func.get("parameters", [])

        param_strs = []
        for p in params:
            ptype = p["type"]
            pname = p["name"]
            # Skip ARRAY_SIZE parameters — Java uses arr.length
            if p.get("role") == "ARRAY_SIZE":
                continue
            if self.is_array_type(ptype):
                base = self.resolve_type(self.base_element_type(ptype))
                param_strs.append(f"{base}[] {pname}")
            else:
                resolved = self.resolve_type(ptype)
                param_strs.append(f"{resolved} {pname}")

        return f"public static {ret} {name}({', '.join(param_strs)})"

    # -------------------------------------------------------
    # Expression override: replace size param references with arr.length
    # -------------------------------------------------------
    def emit_expr(self, expr):
        """Override to handle Java-specific expression transformations."""
        if expr is None:
            return ""
        kind = expr.get("kind", "")

        # For IDENTIFIER: check if it's a size parameter that should become arr.length
        if kind == "IDENTIFIER":
            name = expr.get("name", "")
            
            if hasattr(self, "current_func") and self.current_func is not None:
                params = self.current_func.get("parameters", [])
                is_size_param = any(p.get("name") == name and p.get("role") == "ARRAY_SIZE" for p in params)
                if is_size_param:
                    # Find the array it refers to (assume the first DATA param, CS-1 standard)
                    data_param = next((p for p in params if p.get("role") == "DATA"), None)
                    if data_param:
                        return f"{data_param.get('name')}.length"
            
            return name

        # For MEMBER_ACCESS: arr.length is valid in Java
        if kind == "MEMBER_ACCESS":
            return self.emit_member_access(expr)

        return super().emit_expr(expr)

    def emit_array_initializer(self, expr):
        args = [self.emit_expr(a) for a in expr.get("arguments", [])]
        return "new int[]{" + ", ".join(args) + "}"

    def emit_call_args(self, func_name, args):
        # Drop arguments that map to an ARRAY_SIZE parameter
        if not hasattr(self, "apm"):
            return super().emit_call_args(func_name, args)
            
        target_func = next((f for f in self.apm.get("functions", []) if f.get("name") == func_name), None)
        if not target_func:
            return super().emit_call_args(func_name, args)
            
        params = target_func.get("parameters", [])
        if len(params) != len(args):
            return super().emit_call_args(func_name, args)
            
        filtered_args = []
        for p, a in zip(params, args):
            if p.get("role") != "ARRAY_SIZE":
                filtered_args.append(self.emit_expr(a))
        return ", ".join(filtered_args)

    # -------------------------------------------------------
    # Full program generation
    # -------------------------------------------------------
    def generate(self, apm):
        self.apm = apm
        self.optimize_apm(self.apm)
        lines = []

        # Determine class name from source file or function name
        src = apm.get("source_file", "Generated")
        base_name = os.path.splitext(os.path.basename(src))[0] if src else "Generated"
        # Clean up: remove language suffixes
        for suffix in ["_c", "_cpp", "_java"]:
            if base_name.endswith(suffix):
                base_name = base_name[:-len(suffix)]
                break
        # Capitalize first letter for Java class name
        self.class_name = base_name[0].upper() + base_name[1:] if base_name else "Generated"

        lines.append("// Auto-generated from CPG Abstract Program Model")
        lines.append(f"class {self.class_name} {{")
        lines.append("")

        # Functions
        for func in apm.get("functions", []):
            self.current_func = func
            sig = self._build_func_sig(func)
            lines.append(f"    {sig} {{")
            for stmt in func.get("body", []):
                lines.extend(self.emit_stmt(stmt, 2))
            lines.append("    }")
            lines.append("")

        # Main / entry point
        self.current_func = None  # reset so main body has no function context
        entry = apm.get("entry_point")
        if entry:
            lines.append("    public static void main(String[] args) {")
            for stmt in entry.get("declarations", []):
                lines.extend(self.emit_stmt(stmt, 2))
            for stmt in entry.get("statements", []):
                # Don't emit return 0 for void main in Java
                if stmt.get("kind") == "RETURN":
                    continue
                lines.extend(self.emit_stmt(stmt, 2))
            lines.append("    }")
        else:
            lines.append("    public static void main(String[] args) {")
            lines.append("    }")

        lines.append("}")
        return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate Java code from APM JSON")
    parser.add_argument("apm_file", help="Path to APM JSON file")
    parser.add_argument("--output", "-o", help="Output Java file path")
    args = parser.parse_args()

    gen = JavaCodeGenerator()
    gen.generate_from_file(args.apm_file, args.output)


if __name__ == "__main__":
    main()
