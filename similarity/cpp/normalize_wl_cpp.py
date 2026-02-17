#!/usr/bin/env python3
"""
L2 normalize WL vectors for C++ programs
"""
import sys
import math

if len(sys.argv) != 3:
    print("Usage: python normalize_wl_cpp.py <input.vec> <output.vec>")
    sys.exit(1)

inp, out = sys.argv[1], sys.argv[2]

with open(inp) as f:
    vec = [float(x) for x in f.read().strip().split(",")]

norm = math.sqrt(sum(x * x for x in vec))

if norm == 0:
    normed = vec
else:
    normed = [x / norm for x in vec]

with open(out, "w") as f:
    f.write(",".join(map(str, normed)) + "\n")

print(f"[WL CPP] Normalized: {out}")
