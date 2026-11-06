# Adversarial Markdown Rendering
Paragraph touching a heading.
## Heading Without a Blank Line
Paragraph touching an unordered list.
- first item
- second item
    - nested item with inline math $a_i + b_i \leq c_i$
    - nested item containing a verylongunbrokenidentifier_that_must_not_escape_the_column_012345678901234567890123456789
Paragraph after bullets must not become part of the last item.
1. ordered item one
2. ordered item two
Paragraph after numbers must not become part of the last item.
> Blockquote without a preceding blank line.
Paragraph touching a pipe table.
| Name | Formula | Mixed notes |
| --- | --- | --- |
| Binomial | $\displaystyle\binom{n}{k}=\frac{n!}{k!(n-k)!}$ | 中文、English、`inline code` |
| Long recurrence | $T(n)=2T(n/2)+n=\Theta(n\log n)$ | https://example.com/a/very/long/path/that/must/wrap/inside/a/narrow/column |
Paragraph after the table must remain a paragraph.

### Unordered List Marker and Indentation Matrix
Paragraph touches all three unordered markers.
- dash parent
  - dash child at two spaces
    * star grandchild at four spaces
      + plus great-grandchild at six spaces
* star parent at root
   + plus child at three spaces
      - dash grandchild at six spaces
+ plus parent at root
    * star child at four spaces
        - dash grandchild at eight spaces
Paragraph after the marker matrix.

### Mixed Unordered and Ordered Nesting
- outer unordered A
  1. ordered child A1 at two spaces
     - unordered grandchild A1a
       1. ordered great-grandchild A1a-i
       2. ordered great-grandchild A1a-ii
  2. ordered child A2
- outer unordered B
   1. ordered child B1 at three spaces
      - unordered grandchild B1a
         1. ordered great-grandchild B1a-i
1. outer ordered C
   - unordered child C1
     1. ordered grandchild C1a
        * unordered great-grandchild C1a-i
2. outer ordered D
	- tab-indented unordered child D1
	  1. tab-and-spaces ordered grandchild D1a

### List Continuations and Attached Blocks
- **S:** Sprint summary
  Sprint 1 needed a focused one-week scope.
  This second continuation line must stay in the same item.
- **T:** Team role
  As PO and CLI developer, I needed to prioritise and integrate a usable release.
- **A:** Actions
  We selected registration, persistence, upload/preview, and CLI/session stories.
  We tracked ownership and status in Issues and Project #367.
- **R:** Result
  v0.1.0 delivered 34 SP, including the two-point CLI test follow-up.

- [ ] unchecked task item
- [x] checked task item

### Alternating Blank-Line Styles
Paragraph immediately before a list without a blank line.
- no-blank list item one
- no-blank list item two
Paragraph immediately after that list without a blank line.

Paragraph before a list with a blank line.

* blank-separated list item one
* blank-separated list item two

Paragraph after that list with a blank line.
Paragraph immediately before a heading without a blank line.
#### Heading Reached Without a Blank Line
Paragraph immediately after the heading without a blank line.

### Long Complex Bilingual Sentences
This deliberately long English sentence combines an algorithmic claim, the recurrence $T(n)=2T(n/2)+n$, an inline identifier `resolve_dependency_graph`, a URL https://example.com/research/algorithms/complexity/with/a/very/long/path/component/that/has/no/convenient/breakpoint, several parenthetical qualifications (including a caveat about amortised analysis), and the unbroken token SupercalifragilisticLongIdentifier_ABCDEFGHIJKLMNOPQRSTUVWXYZ_0123456789_abcdefghijklmnopqrstuvwxyz so that ordinary prose, code, links, and mathematics must all remain inside one narrow column without corrupting the next column.
这是一个故意写得很长且同时包含Englishtechnicalterms、中文标点、inline公式$P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}$、代码`git pull --rebase`以及连续无空格标识符超长变量名称VeryLongMixedLanguageIdentifier_这是中文连续文本_01234567890123456789的复杂句子，用来验证中英文混排时浏览器能够正常换行，并且不会把公式前后的文字拆成错误的Markdown块。
English中文mixed-without-spaces-before-or-after-math:$a_n=\sum_{i=1}^{n}i$继续中文thenEnglish resumes immediately, while a second formula with surrounding spaces $\bar{x}=\frac{1}{n}\sum_{i=1}^{n}x_i$ should remain part of the same paragraph.

### Fenced Code Without Surrounding Blank Lines
Text immediately before a top-level fence.
```python
print("top-level fence; - and 1. stay literal")
```
Text immediately after a top-level fence.
Text immediately before a tilde fence.
~~~json
{"literal": "- bullet-looking text", "step": "1. number-looking text"}
~~~
Text immediately after a tilde fence.

3. If you need an administrator
    Exit the program and run these commands:
    ```zsh
    export VSAS_ADMIN_USERNAME=admin
    read -s VSAS_ADMIN_PASSWORD
    export VSAS_ADMIN_PASSWORD
    ```
    Then restart the program.
4. Continue with the next ordered step.

- Parent with a nested fence
  Text immediately before the nested fence.
  ```bash
  printf '%s\n' '- literal bullet' '1. literal number'
  ```
  Text immediately after the nested fence.
- Parent after the nested fence

### Inline Math Spacing and Punctuation Matrix
English with spaces before and after $E=mc^2$ remains ordinary prose.
English-no-space-before:$x^2+y^2=z^2$followed-immediately-by-English.
中文前后都无空格：集合$A\cap B=\varnothing$继续中文，且标点紧邻公式$\Pr(X\geq k)\leq\frac{\mathbb{E}[X]}{k}$，后面继续说明。
中文前后有空格：期望值 $\mathbb{E}[X]=\sum_x x\Pr(X=x)$ 用于离散随机变量。
Punctuation adjacency works for ($\alpha+\beta=\gamma$), [$\lVert v\rVert_2=1$], and {$f\colon A\to B$}.
Several formulas touch operators: $a$+$b$=$c$, while escaped currency \$5 and code `$not_math$` must remain literal.
超长inline公式前后无空格：前$P(A_1\cap A_2\cap A_3\cap A_4\cap A_5)=P(A_1)P(A_2\mid A_1)P(A_3\mid A_1\cap A_2)P(A_4\mid A_1\cap A_2\cap A_3)P(A_5\mid A_1\cap A_2\cap A_3\cap A_4)$后，English resumes after the same formula.

Paragraph immediately before display math without a blank line.
$$\nabla\cdot\mathbf{E}=\frac{\rho}{\varepsilon_0}$$
Paragraph immediately after display math without a blank line.

### Display Math Environments
Inline symbols: $A\cup B$, $x\in\mathbb{R}$, $\neg(p\leftrightarrow q)$.

$$\begin{aligned}
f(n) &= \sum_{i=1}^{n} i \\
     &= \frac{n(n+1)}{2}
\end{aligned}$$

$$f(x)=\begin{cases}
x^2, & x\ge 0 \\
-x, & x<0
\end{cases}$$

$$\begin{pmatrix}
1 & 2 \\
3 & 4
\end{pmatrix}$$

$$\begin{array}{|l|l|}\hline
A\cup B=B\cup A & \text{Commutation law} \\
\overline{A\cap B}=\overline A\cup\overline B & \text{De Morgan's law} \\
\hline\end{array}$$

$$P(A_1\cap A_2\cap A_3\cap A_4\cap A_5)=P(A_1)P(A_2\mid A_1)P(A_3\mid A_1\cap A_2)P(A_4\mid A_1\cap A_2\cap A_3)$$

### Extended LaTeX Notation Matrix

$$\frac{\sqrt{x^2+1}}{\sqrt[3]{y+2}}+\binom{n}{k}+\frac{\frac{a}{b}}{\frac{c}{d}}$$

$$\lim_{n\to\infty}\sum_{i=1}^{n}\frac{1}{i^2}=\frac{\pi^2}{6},\qquad \prod_{j=1}^{m}j=m!$$

$$\int_{-\infty}^{\infty}e^{-x^2}\,dx=\sqrt{\pi},\qquad \oint_{\partial\Omega}\mathbf{F}\cdot d\mathbf{r}$$

$$\begin{bmatrix}a&b\\c&d\end{bmatrix}\begin{pmatrix}x\\y\end{pmatrix}=\begin{pmatrix}ax+by\\cx+dy\end{pmatrix},\qquad \det(A)\neq0$$

$$\left\lVert\vec{v}\right\rVert_2=\sqrt{\sum_{i=1}^{n}v_i^2},\qquad \hat{\theta}=\operatorname*{arg\,min}_{\theta\in\Theta}L(\theta)$$

$$\underbrace{a+b+\cdots+z}_{\text{English label}}+\overbrace{\alpha+\beta}^{\text{中文说明}}$$

$$\begin{aligned}
\Pr(A\cup B)&=\Pr(A)+\Pr(B)-\Pr(A\cap B)\\
H(X)&=-\sum_x p(x)\log_2p(x) && \text{信息熵 / entropy}
\end{aligned}$$

### Collapsed LaTeX Row Commands From Dense Notes

$$\begin{array}{|c|c|}\hline
\text{\textbf{Symbol}} & \text{\textbf{Meaning}} \\\forall & \text{for all} \\\exists & \text{there exists} \\\to & \text{implies} \\\emptyset & \text{empty set} \\\left[0,1\right] & \text{closed interval} \\\overline{A} & \text{complement} \\ \hline
\end{array}$$

Divisibility notation with a Pandoc-incompatible negation: $d\not\mid n$, while inline code `d\not\mid n` must stay unchanged.

### Markdown-looking Text Inside Code Must Stay Literal
```markdown
Paragraph
- this is literal code
| not | a table |
| --- | --- |
$$not math$$
```

### Tall Table Near a Column Boundary

| Case | Condition | Result |
| --- | --- | --- |
| 1 | $f(n)=O(n^{\log_b a-\epsilon})$ | $T(n)=\Theta(n^{\log_b a})$ |
| 2 | $f(n)=\Theta(n^{\log_b a}\log^k n)$ | $T(n)=\Theta(n^{\log_b a}\log^{k+1}n)$ |
| 3 | $f(n)=\Omega(n^{\log_b a+\epsilon})$ | $T(n)=\Theta(f(n))$ |

### Bilingual Table With Inline Math and Long Prose

| Topic 主题 | Definition / 定义 | Edge case 边界情况 |
| --- | --- | --- |
| Bayes 贝叶斯 | 后验概率$P(A\mid B)=\frac{P(B\mid A)P(A)}{P(B)}$combines prior and likelihood | 当$P(B)=0$时未定义 / undefined |
| Complexity 复杂度 | $T(n)=aT(n/b)+f(n)$，需要比较$f(n)$与$n^{\log_ba}$ | ALongUnbrokenCellValue_ABCDEFGHIJKLMNOPQRSTUVWXYZ_01234567890123456789 |
