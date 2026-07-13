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

## Correctness Proof Templates 正确性证明模板

### 1.6 Exchange Argument 交换论证 ★ (贪心正确性)

设 $G=$ 贪心解，$O=$ 最优解。若不同，在第一个不同处把 $O$ 换成 $G$，代价不增，重复直到 $O=G$。

> Let G be the greedy solution and O be any optimal solution. Suppose G != O.
>
> Let i be the first position where G and O differ. In O, swap [O's choice at i] with [G's choice at i].
>
> This swap [does not decrease the objective / keeps the solution feasible] because [brief argument].
>
> Repeating this exchange transforms O into G without worsening the objective.
>
> Therefore G is optimal. ✓

- **区间调度**: 换 $o \to g$ (更早结束): 仍可行，后续选择不受影响，大小不变。
- **Kruskal**: 取 $x \in OPT \setminus KRUS$。加 $x$ 形成环 $C$，某 $y \in C \cap (KRUS \setminus OPT)$，$w(y) \leq w(x)$。换 $y \to x$ 不增代价。矛盾 → $KRUS=MST$。
- **加权完成时间**: ==排序依据 $w_j/t_j$ 降序== (Smith 法则)。

### Counterexample 反例 ★

构造小实例 (3-5 元素)，贪心给出次优解，手动给出更优解。

> Consider the following instance: [describe small instance concisely].
>
> The greedy algorithm [describe what it does] and outputs [X] with [objective value A].
>
> However, the solution [Y] is also valid and achieves [objective value B < A / B > A].
>
> Therefore the greedy algorithm is not optimal (correct). ✓

### 1.7 D&C Correctness 分治正确性 ★

基情形直接验证，归纳步骤证每种情形覆盖 + 合并正确。

> **Claim:** The algorithm is correct for all inputs of size n.
>
> **Base case:** For $n \leq$ [threshold], the algorithm [directly computes the correct answer]. ✓
>
> **Inductive hypothesis (IH):** Assume the algorithm is correct for all inputs of size < n.
>
> **Inductive step:** The DIVIDE step produces subproblems of size < n. By IH, each recursive call returns the correct result. Every input of size n falls into exactly one of the cases [list cases] (exhaustive and mutually exclusive). The COMBINE step correctly merges the recursive results because [brief argument]. Therefore the algorithm is correct for size n. ✓

### Loop Invariant 循环不变式

适合证明排序、扫描线、双指针、栈队列算法。

1. **Initialization 初始化:** 循环开始前，不变式成立。
2. **Maintenance 保持:** 若某轮开始时成立，执行循环体后下一轮仍成立。
3. **Termination 终止:** 循环结束时，不变式推出目标结论。

| Algorithm | Invariant | Termination gives |
| --- | --- | --- |
| Insertion sort | 左侧前缀始终有序 | 整个数组有序 |
| Two pointers | 被排除区间不含更优解 | 当前答案最优 |
| BFS | 队列按距离非降序出队 | 最短路层次正确 |
| Dijkstra | 已出堆点距离已确定 | 单源最短路 |

### Master Theorem 主定理

若 $T(n)=aT(n/b)+f(n)$，比较 $f(n)$ 与 $n^{\log_b a}$。

| Case | Condition | Result |
| --- | --- | --- |
| Case 1 | $f(n)=O(n^{\log_b a-\epsilon})$ | $T(n)=\Theta(n^{\log_b a})$ |
| Case 2 | $f(n)=\Theta(n^{\log_b a}\log^k n)$ | $T(n)=\Theta(n^{\log_b a}\log^{k+1} n)$ |
| Case 3 | $f(n)=\Omega(n^{\log_b a+\epsilon})$ and regularity | $T(n)=\Theta(f(n))$ |

**Examples:** Merge sort $T(n)=2T(n/2)+n=\Theta(n\log n)$; binary search $T(n)=T(n/2)+1=\Theta(\log n)$.

## Markdown Stress Tests 混合格式测试

### CJK, Emphasis, and Inline Math 中文混排

这段用于测试中文、English words、`inline code`、**bold 粗体**、*italic 斜体*、==mark 高亮==、以及 $a_i + b_i \leq c_i$ 的行内数学在多栏中的换行表现。

- 复杂度记号: $O(n\log n)$, $\Theta(V+E)$, $\Omega(n^2)$。
- 常见证明词: 因为 / therefore / hence / contradiction / WLOG。
- 边界条件: 空数组、单元素、重复元素、负权边、断开图。

### Mixed Lists 多层列表

1. Greedy 贪心
   - choose locally optimal item
   - prove with exchange argument
   - disprove with counterexample
2. DP 动态规划
   - state: `dp[i][j]`
   - transition: $dp[i]=\min(dp[i], dp[j]+cost)$
   - order: topological / increasing length / increasing capacity
3. Graph 图论
   - BFS: unweighted shortest path
   - DFS: components, cycle detection, topo sort
   - MST: Kruskal / Prim

### Dense Formula Table 公式表

| Topic | Formula | Notes |
| --- | --- | --- |
| Arithmetic series | $\sum_{i=1}^{n} i = n(n+1)/2$ | 常用于双重循环 |
| Geometric series | $\sum_{i=0}^{k} 2^i = 2^{k+1}-1$ | 分治树节点数 |
| Harmonic | $H_n=\Theta(\log n)$ | randomized analysis |
| Binomial | $\binom{n}{k}=\frac{n!}{k!(n-k)!}$ | combinations |

### Long Quote 长引用

> A proof is useful only when every step can be checked locally. In an exam setting, prefer a short invariant, a clear exchange, or a tiny counterexample over a long narrative.
>
> 证明不是把直觉写长，而是把关键约束写清楚：状态是什么、保持了什么、结束时推出什么。

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
