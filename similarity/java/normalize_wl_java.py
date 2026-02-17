#!/usr/bin/env python3
"""
L2 normalize WL vectors
"""
import json
import math
import sys
from pathlib import Path

def l2_normalize(vec):
    """L2 normalization"""
    norm = math.sqrt(sum(x*x for x in vec))
    if norm == 0:
        return vec
    return [x/norm for x in vec]

if len(sys.argv) == 3:
    # Single file mode (called with input and output paths)
    input_file = Path(sys.argv[1])
    output_file = Path(sys.argv[2])
    
    with open(input_file) as f:
        vec = json.load(f)
    
    normed = l2_normalize(vec)
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, "w") as f:
        json.dump(normed, f)
    
    print(f"[WL Normalize] ✓ {output_file.name}")
else:
    # Batch mode (normalize all vectors in directory)
    VEC_DIR = Path("vectors/java/wl")
    NORM_DIR = Path("vectors/java/wl_norm")
    
    NORM_DIR.mkdir(parents=True, exist_ok=True)
    
    norm_count = 0
    for vec_file in VEC_DIR.glob("*.vec"):
        with open(vec_file) as f:
            vec = json.load(f)
        
        normed = l2_normalize(vec)
        
        norm_file = NORM_DIR / f"{vec_file.stem}.norm.vec"
        with open(norm_file, "w") as f:
            json.dump(normed, f)
        
        norm_count += 1
    
    print(f"[WL Normalize] ✓ Normalized {norm_count} vectors")
    print(f"[WL Normalize] Saved to {NORM_DIR}")
