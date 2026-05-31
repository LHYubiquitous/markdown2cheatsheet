# Python Essentials

### Variables & Types
**Python is dynamically typed** — no declaration needed.
- Primitives: `int` `float` `str` `bool` `None`
- Use `isinstance(x, int)` for type checks
- `type(x)` returns the runtime type

```python
x, pi, ok  = 42, 3.14, True
items      = [1, 2, 3]      # list  — mutable
coords     = (10, 20)       # tuple — immutable
lookup     = {"a": 1}       # dict
unique     = {1, 2, 3}      # set
```

### String Methods

| Method | Result |
| --- | --- |
| `"hi".upper()` | `"HI"` |
| `"a,b".split(",")` | `["a","b"]` |
| `" x ".strip()` | `"x"` |
| `"ab".replace("a","x")` | `"xb"` |
| `f"val={x}"` | f-string |

### List Comprehensions

```python
squares = [x**2 for x in range(10)]
evens   = [x for x in range(20) if x % 2 == 0]
inv     = {v: k for k, v in d.items()}   # dict comp
flat    = [x for row in matrix for x in row]
```

### Functions

```python
def greet(name, greeting="Hello"):
    """Return a greeting string."""
    return f"{greeting}, {name}!"

add = lambda x, y: x + y

def log(*args, **kwargs):   # variadic
    print(args, kwargs)
```

## Data Structures

### Dict Operations

```python
d = {"a": 1, "b": 2}
d["c"] = 3              # insert / update
val = d.get("z", 0)     # safe get with default
d.pop("a")              # remove key
merged = d1 | d2        # merge (Python 3.9+)
for k, v in d.items():
    pass
```

### collections Module

| Class | Use case |
| --- | --- |
| `Counter(it)` | Frequency count |
| `defaultdict(T)` | Dict with default value |
| `deque` | O(1) both-end ops |
| `namedtuple` | Immutable record |

### Sorting

```python
nums.sort(reverse=True)
sorted(items, key=lambda x: x[1])
sorted(words, key=str.lower)
```

## Error Handling

```python
try:
    result = 10 / x
except ZeroDivisionError:
    print("div by zero")
except (TypeError, ValueError) as e:
    print(f"Error: {e}")
else:
    print("success")    # runs only if no exception
finally:
    cleanup()
```

**Custom exception:**
```python
class AppError(Exception):
    def __init__(self, msg, code=400):
        super().__init__(msg)
        self.code = code
```

## File & JSON I/O

```python
with open("f.txt", "r", encoding="utf-8") as f:
    text  = f.read()
    lines = f.readlines()

with open("out.txt", "w") as f:
    f.write("Hello\n")

import json
data = json.loads(text)
out  = json.dumps(data, indent=2)
```

## Classes & OOP

```python
class Animal:
    species = "Unknown"          # class variable

    def __init__(self, name):
        self.name = name         # instance variable

    def speak(self):
        return f"{self.name} ..."

    def __repr__(self):
        return f"Animal({self.name!r})"

class Dog(Animal):
    def speak(self):             # override
        return f"{self.name}: Woof!"

isinstance(Dog("Rex"), Animal)   # True
```

# SQL

### SELECT & Filter

```sql
SELECT name, age, dept
FROM   employees
WHERE  dept = 'Eng' AND age > 25
ORDER  BY name ASC
LIMIT  10;
```

### Joins

```sql
-- INNER: matching rows only
SELECT e.name, d.dept_name
FROM   employees e
JOIN   departments d ON e.dept_id = d.id;

-- LEFT: all employees, nullable dept
SELECT e.name,
       COALESCE(d.name, 'None') AS dept
FROM   employees e
LEFT JOIN departments d ON e.dept_id = d.id;
```

### Aggregation

```sql
SELECT   dept,
         COUNT(*)    AS headcount,
         AVG(salary) AS avg_sal,
         MAX(salary) AS max_sal
FROM     employees
GROUP BY dept
HAVING   COUNT(*) > 5
ORDER BY avg_sal DESC;
```

### Window Functions

```sql
SELECT name, salary,
  RANK() OVER (
    PARTITION BY dept ORDER BY salary DESC
  ) AS rnk,
  LAG(salary) OVER (ORDER BY hire_date) AS prev
FROM employees;
```

### Common Clauses

| Clause | Purpose |
| --- | --- |
| `DISTINCT` | Remove duplicates |
| `LIKE 'A%'` | Pattern match |
| `IN (1,2,3)` | Match a list |
| `BETWEEN a AND b` | Range check |
| `IS NULL` | Null test |
| `CASE WHEN ... END` | Conditional value |

# Git & Shell

## Git

### Core Commands

```bash
git init / git clone <url>
git status / git log --oneline --graph
git add <file> / git add .
git commit -m "type: message"
git push origin main / git pull
git checkout -b feature/x
git merge feature/x / git rebase main
```

### Undo Operations

```bash
git restore <file>        # discard working changes
git restore --staged <f>  # unstage a file
git reset HEAD~1          # undo last commit (keep changes)
git revert <hash>         # safe undo via new commit
git stash / git stash pop
```

### Reference

| Goal | Command |
| --- | --- |
| Amend last commit | `git commit --amend` |
| Cherry-pick | `git cherry-pick <hash>` |
| Compare branches | `git diff main..feature` |
| Tag release | `git tag -a v1.0 -m "msg"` |
| Clean untracked | `git clean -fd` |

## Bash

```bash
# Navigation & search
ls -lah
find . -name "*.py" -type f

# Text processing
grep -rn "TODO" ./src
sed 's/old/new/g' file.txt
awk '{print $1, $3}' data.csv

# Processes & ports
ps aux | grep node
kill -9 <pid>
lsof -i :3000
```

# Algorithms & Complexity

## Big-O Reference

| Operation | Array | Linked List | Hash Map | BST avg |
| --- | --- | --- | --- | --- |
| Access | O(1) | O(n) | O(1) | O(log n) |
| Search | O(n) | O(n) | O(1) | O(log n) |
| Insert | O(n) | O(1) | O(1) | O(log n) |
| Delete | O(n) | O(1) | O(1) | O(log n) |

## Sorting Algorithms

| Algorithm | Average | Worst | Space | Stable |
| --- | --- | --- | --- | --- |
| Bubble Sort | O(n²) | O(n²) | O(1) | Yes |
| Merge Sort | O(n log n) | O(n log n) | O(n) | Yes |
| Quick Sort | O(n log n) | O(n²) | O(log n) | No |
| Heap Sort | O(n log n) | O(n log n) | O(1) | No |
| Tim Sort | O(n log n) | O(n log n) | O(n) | Yes |

### Binary Search

```python
def binary_search(arr, target):
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if   arr[mid] == target: return mid
        elif arr[mid] <  target: lo = mid + 1
        else:                    hi = mid - 1
    return -1
```

### Graph Traversal

```python
from collections import deque

def bfs(graph, start):
    visited = {start}
    queue   = deque([start])
    while queue:
        node = queue.popleft()
        for nb in graph[node]:
            if nb not in visited:
                visited.add(nb)
                queue.append(nb)
    return visited

def dfs(graph, node, visited=None):
    visited = visited or set()
    visited.add(node)
    for nb in graph[node]:
        if nb not in visited:
            dfs(graph, nb, visited)
    return visited
```

### Dynamic Programming

```python
# 0/1 Knapsack — bottom-up DP
def knapsack(weights, values, W):
    n  = len(weights)
    dp = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            dp[i][w] = dp[i-1][w]
            if weights[i-1] <= w:
                dp[i][w] = max(
                    dp[i][w],
                    dp[i-1][w - weights[i-1]] + values[i-1]
                )
    return dp[n][W]
```

## Regex Quick Reference

| Pattern | Matches |
| --- | --- |
| `.` | Any char (except newline) |
| `\d` / `\D` | Digit / non-digit |
| `\w` / `\W` | Word char / non-word |
| `\s` / `\S` | Whitespace / non-ws |
| `^` / `$` | Line start / end |
| `*` `+` `?` | 0+ / 1+ / optional |
| `{n,m}` | n to m repetitions |
| `[abc]` | Character class |
| `(a\|b)` | Alternation |
| `(?=...)` | Lookahead |

```python
import re
pattern = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
dates   = pattern.findall(text)
cleaned = re.sub(r'\s+', ' ', text).strip()
m       = re.match(r'(\w+)@(\w+)\.(\w+)', email)
if m:
    user, domain, tld = m.groups()
```
