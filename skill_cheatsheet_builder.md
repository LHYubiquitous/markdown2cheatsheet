# Skill: Exam Cheatsheet Builder

## 使用方式

可在任意项目中通过`/cheatsheet-builder` 调用（传入课程描述作为参数）。

也可将下方"Skill Prompt"段落直接粘贴到任意 AI 对话框中作为 system prompt 使用。

---

## Skill Prompt（直接复制给 AI 使用）

````
You are helping me build a high-density, print-ready A4 double-sided exam cheatsheet
for the course described below.

## Your job

1. Read all the resources I have provided.
2. Create `CLAUDE.md` in the project root — this is the persistent contract that keeps
   future conversations coherent. Follow the CLAUDE.md template in this skill exactly.
3. Then build `cheatsheet.md` in phases, one section per response.
   Announce which phase you are writing at the start of each response.
4. Do NOT generate HTML until I confirm the MD content is complete.

## Cheatsheet structure

The cheatsheet has TWO parts:
- **Part 1 — Code/Answer Templates**: directly reusable in the exam with minimal editing.
  Prioritise correctness over brevity. A template with a subtle bug is worse than none.
- **Part 2 — Short-Answer Knowledge**: concise bullet points and answer phrasing for
  explanatory questions. Focus on vocabulary the examiner expects.

## Formatting conventions (MD source)

- `==text==`       yellow highlight — critical rules, must-know signatures, exam traps
- `**text**`       bold — terms and labels
- `★`              topic appears in 2+ past papers / guaranteed exam content
- `> blockquote`   short-answer template, copy nearly verbatim in exam
- Fenced code      all code templates (include headers, error checks, memory safety)
- Tables           comparison tables, complexity tables
- No emoji. English primary; Chinese allowed only for short section labels and warnings.

## Build phases (suggested)

Announce the phase number at the start of each response and append only that phase
to `cheatsheet.md`. Do not regenerate previously written sections.

{{PHASE_LIST}}

## Rendering pipeline

The markdown2cheatsheet tool converts cheatsheet.md → self-contained HTML for printing.

**Setup (first time only):**
```bash
git clone https://github.com/LHYubiquitous/markdown2cheatsheet
```

**Convert:**
```bash
# Linux / macOS / Git Bash
bash markdown2cheatsheet/md2cheatsheet.sh cheatsheet.md cheatsheet.html

# Windows Git Bash (from project root)
cd "{{PROJECT_PATH}}"
bash markdown2cheatsheet/md2cheatsheet.sh cheatsheet.md cheatsheet.html
```

**Layout defaults** (`markdown2cheatsheet/cheatsheet.css`):

| Setting | Default | Adjust when |
|---|---|---|
| `column-count` | 4 | content overflows → reduce; too sparse → increase |
| `font-size` | 6.5pt | content overflows → reduce |
| Code `font-size` | 5.3pt | code unreadable → increase |
| `margin` | 5mm | need more space → reduce |

## CLAUDE.md template

When creating CLAUDE.md, fill in the sections below with course-specific content.
The file must be self-contained so a new conversation can pick up exactly where this
one left off.

---

# {{COURSE_CODE}} {{COURSE_NAME}} Cheatsheet Project

## Project Goal

Produce a high-density, print-ready A4 double-sided cheatsheet for the
{{COURSE_CODE}} final exam ({{UNIVERSITY}}, {{SEMESTER}}). Must cover every
examinable topic with emphasis on {{EMPHASIS}}. Must fit on one A4 sheet front + back.

## Exam Structure

- **Duration:** {{DURATION}}
- **Total:** {{TOTAL_MARKS}} marks
- **Conditions:** {{EXAM_CONDITIONS}}
- **Formula/reference sheet:** {{FORMULA_SHEET_NOTE}}

### Question Breakdown

| Q | Topic | Marks | Style |
|---|-------|-------|-------|
{{QUESTION_TABLE_ROWS}}

### Observed exam patterns

{{EXAM_PATTERNS}}

### Critical exam hints

{{CRITICAL_HINTS}}

## Workflow

### Step 1 — Write the MD cheatsheet

Create and iterate on `cheatsheet.md` in the project root.

### Step 2 — Convert to HTML

```bash
# Clone tool once (skip if already cloned)
git clone https://github.com/LHYubiquitous/markdown2cheatsheet

# Convert
bash markdown2cheatsheet/md2cheatsheet.sh cheatsheet.md cheatsheet.html
```

On Windows with Git Bash:
```bash
cd "{{PROJECT_PATH}}"
bash markdown2cheatsheet/md2cheatsheet.sh cheatsheet.md cheatsheet.html
```

### Layout defaults (`markdown2cheatsheet/cheatsheet.css`)

| Setting | Default |
|---|---|
| Columns | 4 |
| Font size | 6.5pt |
| Code font | 5.3pt |
| Page margin | 5mm |

## Resources Map

| Resource | Path | Purpose |
|---|---|---|
{{RESOURCES_TABLE_ROWS}}

### Reading large PDFs

All large PDFs require the `pages` parameter (max 20 pages per call).

**Recommended reading order:**
{{READING_ORDER}}

## Cheatsheet Content Requirements

### Required content — Part 1: {{PART1_LABEL}}

{{PART1_CONTENT_LIST}}

### Required content — Part 2: {{PART2_LABEL}}

{{PART2_CONTENT_LIST}}

## How to Build the Cheatsheet (AI instructions)

1. **Read key resources first.** Before writing any section, read the resources
   listed above in the recommended order.
2. **Output in phases.** Announce the phase at the start of each response.
   Append only that phase to `cheatsheet.md` — never regenerate prior sections.
3. **Content first, trimming later.** Write complete, detailed content even if
   it exceeds A4. The user decides what to trim.
4. **No information gaps.** Every exam topic must appear. Every question type
   seen in any past paper must have a corresponding template.
5. **Templates must be correct.** All code/answer templates must be verified
   for correctness before writing.
6. **Do not generate HTML** until user confirms MD is complete and satisfactory.
7. **Formula sheet overlap.** Do not reproduce content that the exam provides —
   use that space for templates not on the formula sheet.

---
````

## Placeholders reference

| Placeholder | What to fill in |
|---|---|
| `{{COURSE_CODE}}` | e.g. `COMP2017` |
| `{{COURSE_NAME}}` | e.g. `Systems Programming` |
| `{{UNIVERSITY}}` | e.g. `University of Sydney` |
| `{{SEMESTER}}` | e.g. `S1 2026` |
| `{{EMPHASIS}}` | e.g. `directly reusable C code templates` |
| `{{DURATION}}` | e.g. `2 hours writing + 10 minutes reading` |
| `{{TOTAL_MARKS}}` | e.g. `100` |
| `{{EXAM_CONDITIONS}}` | e.g. `RESTRICTED OPEN BOOK — 1 A4 double-sided cheatsheet` |
| `{{FORMULA_SHEET_NOTE}}` | e.g. `Yes — covers C syntax; do NOT duplicate` or `None` |
| `{{QUESTION_TABLE_ROWS}}` | One `\| Q \| Topic \| Marks \| Style \|` row per question |
| `{{EXAM_PATTERNS}}` | Bullet list of recurring question types across past papers |
| `{{CRITICAL_HINTS}}` | Bullet list of exam strategy notes |
| `{{PROJECT_PATH}}` | Absolute path to project root (Windows: `d:/Users/...`) |
| `{{RESOURCES_TABLE_ROWS}}` | One `\| Name \| Path \| Purpose \|` row per resource |
| `{{READING_ORDER}}` | Numbered list, most important first |
| `{{PART1_LABEL}}` | e.g. `Code Templates` or `Algorithm Answer Templates` |
| `{{PART1_CONTENT_LIST}}` | Numbered list of required code/answer templates |
| `{{PART2_LABEL}}` | e.g. `Short-Answer Knowledge` |
| `{{PART2_CONTENT_LIST}}` | Numbered list of required knowledge points |
| `{{PHASE_LIST}}` | Numbered list of build phases with scope of each |

---

## 使用说明

### 适用场景

任何"限带一张 A4 纸"形式的受限开卷考试，包括但不限于：
- 计算机科学（算法、系统编程、数据库、网络）
- 数学、物理、工程类考试
- 任何有固定题型规律的课程

### 快速开始步骤

**Step 1 — 准备项目目录**

```
MyCheatsheet/
├── Resources/               ← 放入所有课程资料
│   ├── exam_2024.pdf
│   ├── mock_exam.pdf
│   ├── slides.pdf
│   └── tutorial_notes/
├── CLAUDE.md                ← 由 AI 生成（本 skill 的产物）
└── cheatsheet.md            ← 由 AI 分阶段构建
# markdown2cheatsheet/ 无需手动准备 — AI 会 git clone
```

**Step 2 — 启动新对话**

- **Claude Code CLI:** `/cheatsheet-builder [课程描述]`
- **其他平台:** 复制"Skill Prompt"段落，替换 `{{PLACEHOLDER}}`，发送

**Step 3 — 分阶段构建**

每次新对话只需说：`Phase 1` / `Phase 2` / `Phase 3` ...  
CLAUDE.md 保证上下文连贯，AI 不会重复已写内容。

**Step 4 — 渲染为 HTML**

```bash
git clone https://github.com/LHYubiquitous/markdown2cheatsheet  # 仅首次
bash markdown2cheatsheet/md2cheatsheet.sh cheatsheet.md cheatsheet.html
```

用浏览器打开 `cheatsheet.html`，调整 CSS 后打印为 A4（双面）。

### 跨平台使用

| 平台 | 使用方式 |
|---|---|
| Claude Code CLI | `~/.claude/commands/cheatsheet-builder.md` → `/cheatsheet-builder` |
| Claude.ai 网页 Project | 将 Skill Prompt 存入 Project Instructions，所有对话自动生效 |
| 任意 AI 对话框 | 复制 Skill Prompt 段落作为第一条消息 |
| API / 自建应用 | 将 Skill Prompt 作为 system prompt 注入 |


