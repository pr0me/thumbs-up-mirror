import re

def parse_syms_txt(filename):
    symbols = {}
    with open(filename, 'r') as f:
        for line in f:
            match = re.match(r'Symbol: (.+), Address: 0x([0-9a-fA-F]+)', line.strip())
            if match:
                symbol, address = match.groups()
                addr = int(address, 16)
                symbols[addr] = symbol
    return symbols

def parse_syms_binarly_txt(filename):
    symbols = {}
    current_symbol = None
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('symbol:'):
                current_symbol = line.split(':')[1].strip()
            elif line.startswith('ref:'):
                address = line.split('(')[1].rstrip(')')
                addr = int(address, 16)
                symbols[addr] = current_symbol
    return symbols

def parse_syms_readelf(filename):
    symbols = {}
    with open(filename, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 8:
                address = int(parts[1], 16) & ~1
                symbol = parts[7].split('@@')[0]
                symbols[address] = symbol
    return symbols

def compare_symbols(ground_truth, binarly, third_tool):
    all_symbols = set(ground_truth.keys()) | set(binarly.keys() | set(third_tool.keys()))
    readelf_gt_mismatch = 0
    binja_mismatch = 0

    for addr in all_symbols:
        if addr not in ground_truth:
            pass

        if addr in third_tool and addr not in binarly:
            binja_mismatch += 1

        if addr in ground_truth and addr not in binarly:
            readelf_gt_mismatch += 1
        if addr in ground_truth and addr in binarly:
            if ground_truth[addr] != binarly[addr]:
                print(f"mismatch in naming @ {hex(addr)}:")
                print(f"    ground truth -> {ground_truth[addr]}")
                print(f"    binarly      -> {binarly[addr]}")

    print("[*] Statistics")
    print(f"    mismatches with ground truth: {readelf_gt_mismatch}")
    print(f"    mismatches with binary ninja: {binja_mismatch}")

syms_binja = parse_syms_txt('binja_syms.txt')
syms_binarly = parse_syms_binarly_txt('syms_binarly.txt')
syms_readelf = parse_syms_readelf('readelf_output.txt')

compare_symbols(syms_readelf, syms_binarly, syms_binja)