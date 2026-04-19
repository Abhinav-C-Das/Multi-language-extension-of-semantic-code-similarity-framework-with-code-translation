import os
import re
import json

c_dir = r"c:\Users\abhis\OneDrive\Desktop\msths\ckg-multiview-code-similarity\docs\unw1\data\c"

for root, dirs, files in os.walk(c_dir):
    for filename in files:
        if filename.endswith(".cpp"):
            old_path = os.path.join(root, filename)
            new_path = os.path.join(root, filename[:-4] + ".c")
            
            with open(old_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Syntax substitutions to downgrade from C++ to C
            content = content.replace("#include <iostream>", "#include <stdio.h>\n#include <stdlib.h>")
            content = content.replace("using namespace std;", "")
            
            # Very aggressive cout to printf (e.g. cout << "Is 17 prime? " << isPrime(17) << endl;)
            # I will use a simple regex replacing patterns
            def repl_cout(m):
                # m.group(1) is the string e.g. "Is 17 prime? " or "Sum = "
                # m.group(2) is the var e.g. isPrime(17)
                s1 = m.group(1).replace('"', '')
                if s1.endswith("= "): s1 = s1[:-2] + "=%d"
                elif s1.endswith(" "): s1 = s1[:-1] + "%d"
                else: s1 += "%d"
                return f'printf("{s1}\\n", {m.group(2)});'
                
            content = re.sub(r'cout\s*<<\s*("[^"]*")\s*<<\s*([a-zA-Z0-9_\(\)\[\]\.\-\>\+\*]+)\s*<<\s*endl\s*;', repl_cout, content)
            
            # For couts that are just string
            content = re.sub(r'cout\s*<<\s*("[^"]*")\s*<<\s*endl\s*;', r'printf(\1);\nprintf("\\n");', content)
                             
            with open(new_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            os.remove(old_path)

print("Downgraded C dir back to .c files.")
