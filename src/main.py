import sys

def myers_diff(a, b):
    start = 0
    while start < len(a) and start < len(b) and a[start] == b[start]:
        start += 1
        
    end_a = len(a)
    end_b = len(b)
    while end_a > start and end_b > start and a[end_a - 1] == b[end_b - 1]:
        end_a -= 1
        end_b -= 1
        
    prefix = [(' ', a[i], b[i]) for i in range(start)]
    suffix = [(' ', a[i], b[i - end_a + end_b]) for i in range(end_a, len(a))]
    
    mid_a = a[start:end_a]
    mid_b = b[start:end_b]
    
    n, m = len(mid_a), len(mid_b)
    max_d = n + m
    if max_d == 0:
        return prefix + suffix
        
    v = [0] * (2 * max_d + 1)
    offset = max_d
    trace = []
    
    for d in range(max_d + 1):
        choices = 0
        for k in range(-d, d + 1, 2):
            idx = k + offset
            
            bit_idx = (k + d) // 2
            
            if k == -d:
                x = v[idx + 1]
                # choices is 0, so bit is 0, no-op
            elif k == d:
                x = v[idx - 1] + 1
                choices |= (1 << bit_idx)
            else:
                if v[idx - 1] < v[idx + 1]:
                    x = v[idx + 1]
                    # choices bit is 0
                else:
                    x = v[idx - 1] + 1
                    choices |= (1 << bit_idx)
                    
            y = x - k
            
            while x < n and y < m and mid_a[x] == mid_b[y]:
                x += 1
                y += 1
                
            v[idx] = x
            
            if x >= n and y >= m:
                trace.append(choices)
                return prefix + backtrack(trace, mid_a, mid_b, d, k) + suffix
                
        trace.append(choices)
    return prefix + suffix

def backtrack(trace, a, b, final_d, final_k):
    x, y = len(a), len(b)
    edits = []
    k = final_k
    
    for d in range(final_d, 0, -1):
        while x > 0 and y > 0 and a[x-1] == b[y-1]:
            edits.append((' ', a[x-1], b[y-1]))
            x -= 1
            y -= 1
            
        bit_idx = (k + d) // 2
        choice = (trace[d] >> bit_idx) & 1
        
        if choice == 1:
            edits.append(('-', a[x-1], None))
            x -= 1
            k -= 1
        else:
            edits.append(('+', None, b[y-1]))
            y -= 1
            k += 1
            
    while x > 0 and y > 0 and a[x-1] == b[y-1]:
        edits.append((' ', a[x-1], b[y-1]))
        x -= 1
        y -= 1
        
    edits.reverse()
    return edits

def get_ranges(indices):
    if not indices:
        return "."
    ranges = []
    start = indices[0]
    end = start + 1
    for i in range(1, len(indices)):
        if indices[i] == end:
            end += 1
        else:
            ranges.append(f"{start}-{end}")
            start = indices[i]
            end = start + 1
    ranges.append(f"{start}-{end}")
    return ",".join(ranges)

def group_and_print(edits, highlight=False):
    change_block = []

    def flush():
        if not change_block: return
        
        deletions = []
        insertions = []
        for op, item_a, item_b in change_block:
            if op == '-':
                deletions.append(item_a)
                sys.stdout.buffer.write(b"-" + item_a + b"\n")
            elif op == '+':
                insertions.append(item_b)
                
        p = min(len(deletions), len(insertions))
        
        for i, item_b in enumerate(insertions):
            sys.stdout.buffer.write(b"+" + item_b + b"\n")
            
            if highlight and i < p:
                a_str = deletions[i].decode('utf-8')
                b_str = item_b.decode('utf-8')
                
                char_edits = myers_diff(a_str, b_str)
                
                changed_a = []
                changed_b = []
                idx_a = 0
                idx_b = 0
                for cop, ca, cb in char_edits:
                    if cop == '-':
                        changed_a.append(idx_a)
                        idx_a += 1
                    elif cop == '+':
                        changed_b.append(idx_b)
                        idx_b += 1
                    else:
                        idx_a += 1
                        idx_b += 1
                        
                range_a = get_ranges(changed_a)
                range_b = get_ranges(changed_b)
                out_str = f"? {range_a} | {range_b}\n"
                sys.stdout.buffer.write(out_str.encode('utf-8'))
                
        change_block.clear()

    for op, item_a, item_b in edits:
        if op == ' ':
            flush()
            sys.stdout.buffer.write(b" " + item_a + b"\n")
        else:
            change_block.append((op, item_a, item_b))
    flush()

def read_lines(path):
    try:
        with open(path, "rb") as f:
            content = f.read()
    except OSError as e:
        sys.stderr.write(f"Error reading {path}: {e}\n")
        sys.exit(2)
        
    if not content:
        return []
        
    lines = content.split(b"\n")
    if lines[-1] == b"":
        lines.pop()
        
    return lines

def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    command, a_path, b_path = sys.argv[1:]
    
    lines_a = read_lines(a_path)
    lines_b = read_lines(b_path)
    
    edits = myers_diff(lines_a, lines_b)
    
    group_and_print(edits, highlight=(command == "highlight"))
    return 0

if __name__ == "__main__":
    sys.exit(main())
