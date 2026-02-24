#!/usr/bin/env python3
"""
codegen_base.py — Shared logic for APM → target language code generation.

All three generators (C, C++, Java) inherit from CodeGenerator and override
language-specific methods.
"""

import json
import sys
import os

class CodeGenerator:
    """Base class for APM → source code generation."""

    def __init__(self, target_lang):
        self.target_lang = target_lang
        self.indent_str = "    "
        self.type_map = {}
        self.io_map = {}
        self._load_maps()

    def _load_maps(self):
        """Load type_map.json and io_map.json from the same directory."""
        base = os.path.dirname(os.path.abspath(__file__))
        type_map_path = os.path.join(base, "type_map.json")
        io_map_path = os.path.join(base, "io_map.json")
        if os.path.exists(type_map_path):
            with open(type_map_path, "r") as f:
                self.type_map = json.load(f)
        if os.path.exists(io_map_path):
            with open(io_map_path, "r") as f:
                self.io_map = json.load(f)

    def indent(self, level):
        return self.indent_str * level

    # -------------------------------------------------------
    # Type resolution
    # -------------------------------------------------------
    def resolve_type(self, canonical_type):
        """Convert canonical type to target language type."""
        types = self.type_map.get("canonical_types", {})
        mapping = types.get(canonical_type, {})
        return mapping.get(self.target_lang, canonical_type.lower())

    def is_array_type(self, canonical_type):
        return canonical_type and canonical_type.endswith("_ARRAY")

    def base_element_type(self, array_type):
        """INT_ARRAY → INT, LONG_ARRAY → LONG, etc."""
        return array_type.replace("_ARRAY", "") if array_type else "INT"

    # -------------------------------------------------------
    # Expression emission (override in subclasses as needed)
    # -------------------------------------------------------
    def emit_expr(self, expr):
        """Convert an APM expression node to source code string."""
        if expr is None:
            return ""
        kind = expr.get("kind", "")

        if kind == "IDENTIFIER":
            return expr.get("name", "")

        elif kind == "LITERAL":
            return str(expr.get("value", "0"))

        elif kind == "BINARY_OP":
            left = self.emit_expr(expr.get("left"))
            right = self.emit_expr(expr.get("right"))
            op = expr.get("operator", "+")
            return f"({left} {op} {right})"

        elif kind == "UNARY_OP":
            operand = self.emit_expr(expr.get("operand"))
            op = expr.get("operator", "!")
            if expr.get("prefix", True):
                return f"{op}{operand}"
            else:
                return f"{operand}{op}"

        elif kind == "ARRAY_ACCESS":
            array = self.emit_expr(expr.get("array"))
            index = self.emit_expr(expr.get("index"))
            return f"{array}[{index}]"

        elif kind == "MEMBER_ACCESS":
            return self.emit_member_access(expr)

        elif kind == "CALL_EXPR":
            func = expr.get("function", "")
            if func == "arrayInitializer":
                return self.emit_array_initializer(expr)
            args = expr.get("arguments", [])
            args_str = self.emit_call_args(func, args)
            return f"{func}({args_str})"

        elif kind == "CAST":
            target_type = self.resolve_type(expr.get("target_type", "INT"))
            inner = self.emit_expr(expr.get("expression"))
            return self.emit_cast(target_type, inner)

        else:
            # Fallback: use name or value if present
            return expr.get("name", expr.get("value", "/* unknown */"))

    def emit_member_access(self, expr):
        """Override in subclasses for language-specific member access."""
        obj = self.emit_expr(expr.get("object"))
        member = expr.get("member", "")
        return f"{obj}.{member}"

    def emit_array_initializer(self, expr):
        """Override in subclasses. Default C-style."""
        args = [self.emit_expr(a) for a in expr.get("arguments", [])]
        return "{" + ", ".join(args) + "}"

    def emit_call_args(self, func_name, args):
        """Override in subclasses to drop arguments if needed."""
        return ", ".join([self.emit_expr(a) for a in args])

    def emit_cast(self, target_type, inner):
        return f"({target_type}) {inner}"

    # -------------------------------------------------------
    # Statement emission
    # -------------------------------------------------------
    def emit_stmt(self, stmt, level):
        """Convert an APM statement node to source code lines."""
        if stmt is None:
            return []
        kind = stmt.get("kind", "")
        I = self.indent(level)

        if kind == "DECLARE":
            return self.emit_declare(stmt, level)
        elif kind == "FOR_LOOP":
            return self.emit_for_loop(stmt, level)
        elif kind == "WHILE_LOOP":
            return self.emit_while_loop(stmt, level)
        elif kind == "DO_WHILE":
            return self.emit_do_while(stmt, level)
        elif kind == "IF":
            return self.emit_if(stmt, level)
        elif kind == "ASSIGN":
            return self.emit_assign(stmt, level)
        elif kind == "COMPOUND_ASSIGN":
            return self.emit_compound_assign(stmt, level)
        elif kind == "RETURN":
            return self.emit_return(stmt, level)
        elif kind == "CALL":
            return self.emit_call(stmt, level)
        elif kind == "PRINT":
            return self.emit_print(stmt, level)
        elif kind == "BREAK":
            return [f"{I}break;"]
        elif kind == "CONTINUE":
            return [f"{I}continue;"]
        elif kind == "BLOCK":
            lines = []
            for s in stmt.get("body", []):
                lines.extend(self.emit_stmt(s, level))
            return lines
        elif kind == "EXPR_STMT":
            expr_code = self.emit_expr(stmt.get("expression"))
            return [f"{I}{expr_code};"]
        else:
            return [f"{I}/* unsupported: {kind} */"]

    def emit_declare(self, stmt, level):
        I = self.indent(level)
        name = stmt.get("name", "var")
        ctype = stmt.get("type", "INT")
        resolved = self.resolve_type(ctype)
        init = stmt.get("init")
        if init:
            init_code = self.emit_expr(init)
            return [f"{I}{self.format_declaration(resolved, name, ctype)} = {init_code};"]
        else:
            return [f"{I}{self.format_declaration(resolved, name, ctype)};"]

    def format_declaration(self, resolved_type, name, canonical_type):
        """Override for language-specific declaration format."""
        return f"{resolved_type} {name}"

    def emit_for_loop(self, stmt, level):
        I = self.indent(level)
        lines = []

        # Init
        var_init = stmt.get("var_init")
        init_str = ""
        if var_init:
            if var_init.get("kind") == "DECLARE":
                vtype = self.resolve_type(var_init.get("type", "INT"))
                vname = var_init.get("name", "i")
                vinit = self.emit_expr(var_init.get("init"))
                init_str = f"{vtype} {vname} = {vinit}"
            elif var_init.get("kind") == "EXPR_STMT":
                init_str = self.emit_expr(var_init.get("expression"))
            else:
                init_str = self.emit_expr(var_init.get("init", var_init))

        # Condition
        cond = self.emit_expr(stmt.get("condition"))

        # Update
        update = self.emit_expr(stmt.get("update"))

        lines.append(f"{I}for ({init_str}; {cond}; {update}) {{")
        for s in stmt.get("body", []):
            lines.extend(self.emit_stmt(s, level + 1))
        lines.append(f"{I}}}")
        return lines

    def emit_while_loop(self, stmt, level):
        I = self.indent(level)
        cond = self.emit_expr(stmt.get("condition"))
        lines = [f"{I}while ({cond}) {{"]
        for s in stmt.get("body", []):
            lines.extend(self.emit_stmt(s, level + 1))
        lines.append(f"{I}}}")
        return lines

    def emit_do_while(self, stmt, level):
        I = self.indent(level)
        cond = self.emit_expr(stmt.get("condition"))
        lines = [f"{I}do {{"]
        for s in stmt.get("body", []):
            lines.extend(self.emit_stmt(s, level + 1))
        lines.append(f"{I}}} while ({cond});")
        return lines

    def emit_if(self, stmt, level):
        I = self.indent(level)
        cond = self.emit_expr(stmt.get("condition"))
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

    def emit_assign(self, stmt, level):
        I = self.indent(level)
        target = self.emit_expr(stmt.get("target"))
        value = self.emit_expr(stmt.get("value"))
        return [f"{I}{target} = {value};"]

    def emit_compound_assign(self, stmt, level):
        I = self.indent(level)
        target = self.emit_expr(stmt.get("target"))
        value = self.emit_expr(stmt.get("value"))
        op_map = {"ADD": "+=", "SUB": "-=", "MUL": "*=", "DIV": "/=", "MOD": "%="}
        op = op_map.get(stmt.get("operator", "ADD"), "+=")
        return [f"{I}{target} {op} {value};"]

    def emit_return(self, stmt, level):
        I = self.indent(level)
        value = stmt.get("value")
        if value:
            return [f"{I}return {self.emit_expr(value)};"]
        return [f"{I}return;"]

    def emit_call(self, stmt, level):
        I = self.indent(level)
        func = stmt.get("function", "")
        args_str = self.emit_call_args(func, stmt.get("arguments", []))
        return [f"{I}{func}({args_str});"]

    def emit_print(self, stmt, level):
        """Override in subclasses for language-specific print."""
        I = self.indent(level)
        return [f'{I}/* print: {stmt.get("format", "")} */']

    # -------------------------------------------------------
    # Full program generation
    # -------------------------------------------------------
    def optimize_apm(self, apm):
        """Clean up the APM tree before emission, e.g. merging split declarations."""
        def merge_decls(stmt_list):
            if not stmt_list: return []
            merged = []
            skip_next = False
            for i in range(len(stmt_list)):
                if skip_next:
                    skip_next = False
                    continue
                s1 = stmt_list[i]
                if i < len(stmt_list) - 1:
                    s2 = stmt_list[i+1]
                    if s1.get("kind") == "DECLARE" and s2.get("kind") == "ASSIGN":
                        decl_name = s1.get("name")
                        target = s2.get("target", {})
                        if target.get("kind") == "IDENTIFIER" and target.get("name") == decl_name:
                            # Merge s2 into s1
                            s1["init"] = s2.get("value")
                            merged.append(s1)
                            skip_next = True
                            continue
                
                # Recursively optimize inner blocks
                if "body" in s1:
                    s1["body"] = merge_decls(s1["body"])
                if "else_body" in s1:
                    s1["else_body"] = merge_decls(s1["else_body"])
                merged.append(s1)
            return merged

        for f in apm.get("functions", []):
            if "body" in f:
                f["body"] = merge_decls(f["body"])
        
        entry = apm.get("entry_point")
        if entry:
            # Entry point statements might contain the splits
            if "statements" in entry:
                entry["statements"] = merge_decls(entry.get("declarations", []) + entry["statements"])
                entry["declarations"] = []

    def generate(self, apm):
        """Generate complete source code from APM JSON."""
        raise NotImplementedError("Subclasses must implement generate()")

    def generate_from_file(self, apm_path, output_path=None):
        """Load APM from file and generate code."""
        with open(apm_path, "r") as f:
            apm = json.load(f)
        code = self.generate(apm)
        if output_path:
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
            with open(output_path, "w") as f:
                f.write(code)
            print(f"[✓] Generated {output_path}")
        else:
            print(code)
        return code


def load_apm(path):
    """Load and return APM JSON from a file."""
    with open(path, "r") as f:
        return json.load(f)
