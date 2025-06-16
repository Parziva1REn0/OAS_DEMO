import os
import re
from collections import defaultdict

def remove_internal_imports(code, module_names):
    """移除对本地其他模块的 import 语句"""
    lines = code.splitlines()
    cleaned = []
    imports = []

    for line in lines:
        stripped = line.strip()
        if any(
            stripped.startswith(f"import {mod}") or
            stripped.startswith(f"from {mod} import")
            for mod in module_names
        ):
            continue
        if stripped.startswith("import ") or stripped.startswith("from "):
            imports.append(stripped)
            continue
        cleaned.append(line)

    return "\n".join(cleaned), imports

def find_global_vars(code):
    """提取全局变量（简化：函数和类外部的 xxx = ...）"""
    lines = code.splitlines()
    globals_found = []
    inside_func_or_class = False

    for line in lines:
        if re.match(r'^\s*def\s+', line) or re.match(r'^\s*class\s+', line):
            inside_func_or_class = True
        elif re.match(r'^\s*$', line):  # 空行保持状态
            continue
        elif not line.startswith((' ', '\t')):  # 无缩进
            inside_func_or_class = False

        if not inside_func_or_class:
            match = re.match(r'^([a-zA-Z_][a-zA-Z0-9_]*)\s*=', line.strip())
            if match:
                globals_found.append(match.group(1))
    return globals_found

def merge_py_files(source_dir, output_file='main.py'):
    py_files = sorted([
        f for f in os.listdir(source_dir)
        if f.endswith(".py") and f != output_file
    ])

    module_names = [os.path.splitext(f)[0] for f in py_files]

    all_imports = set()
    global_vars = defaultdict(list)
    merged_code = []
    code_blocks = []
    main_function_found = False

    for py_file in py_files:
        file_path = os.path.join(source_dir, py_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()

        cleaned_code, imports = remove_internal_imports(code, module_names)
        all_imports.update(imports)

        # 检查 main 函数
        if re.search(r"^\s*def\s+main\s*\(", cleaned_code, re.MULTILINE):
            main_function_found = True

        # 检查全局变量
        globals_in_file = find_global_vars(cleaned_code)
        for var in globals_in_file:
            global_vars[var].append(py_file)

        code_blocks.append((py_file, cleaned_code))

    # 报告冲突变量
    conflict_vars = {k: v for k, v in global_vars.items() if len(v) > 1}
    if conflict_vars:
        print("⚠️ 检测到重复定义的全局变量：")
        for var, files in conflict_vars.items():
            print(f"  - `{var}` 出现在多个文件: {', '.join(files)}")

    # 合并代码
    merged_code.append("# === 自动合并的 import（去重） ===")
    for imp in sorted(all_imports):
        merged_code.append(imp)

    for filename, code in code_blocks:
        merged_code.append(f"\n\n# === {filename} ===\n{code.strip()}\n")

    if main_function_found:
        merged_code.append("\nif __name__ == '__main__':\n    main()\n")

    output_path = os.path.join(source_dir, output_file)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(merged_code))

    print(f"\n✅ 合并完成，输出文件：{output_path}")

# 示例使用
if __name__ == "__main__":
    default_path = r"C:\Users\A\Desktop\Projects\OASIS\test"

    import argparse
    parser = argparse.ArgumentParser(description="合并项目至PB版本")
    parser.add_argument("folder", nargs="?", default=default_path,
                        help="合并目录的位置")

    args = parser.parse_args()
    merge_py_files(args.folder)
