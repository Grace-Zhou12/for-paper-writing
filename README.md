# for-paper-writing

LaTeX 论文写作模板与示例合集，包含三线表、伪代码、数学公式排版等常用模板，以及全国大学生数学建模竞赛论文模板。

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `00三线表.tex` | 三线表基础示例（使用 `booktabs` 宏包） |
| `01big title.tex` | 标题居中排版示例（使用 `titlesec` 宏包） |
| `02gougu.tex` | 勾股定理小论文示例，含图片插入、目录、参考文献等完整结构 |
| `03table.tex` | 多种表格排版示例：基础表格、数学数组、小数点对齐等 |
| `04终极三线表.tex` | 带符号说明的三线表示例（使用 `makecell` 宏包） |
| `05伪代码.tex` | 伪代码排版示例（使用 `algorithm` + `algpseudocode` 宏包） |
| `exam.tex` | **全国大学生数学建模竞赛论文模板**，含完整论文结构 |
| `cumcmthesis.cls` | 数学建模竞赛论文文档类文件 |

### 其他目录

| 目录 | 说明 |
|------|------|
| `photo_tagger/` | 摄影师文件标签整理工具（Python），详见其中的 [README](photo_tagger/README.md) |

## 编译方式

### 环境要求

- TeX 发行版：[TeX Live](https://tug.org/texlive/)（推荐）或 [MiKTeX](https://miktex.org/)
- 中文支持需要安装 `ctex` 宏包（TeX Live 完整安装自带）
- 编辑器推荐：[TeXstudio](https://www.texstudio.org/)、[VS Code](https://code.visualstudio.com/) + LaTeX Workshop 插件、或 [Overleaf](https://www.overleaf.com/)（在线）

### 编译命令

大部分文件包含中文，需要使用 `xelatex` 编译：

```bash
# 编译单个文件（如三线表示例）
xelatex 00三线表.tex

# 编译带目录和参考文献的文件（如勾股定理论文），需要多次编译
xelatex 02gougu.tex
xelatex 02gougu.tex

# 编译数学建模竞赛论文模板
xelatex exam.tex
xelatex exam.tex
```

> **提示：** 含 `\tableofcontents`（目录）或 `\bibliography`（参考文献）的文件需要编译 **两次** 才能正确生成交叉引用。

### 在编辑器中编译

- **TeXstudio**：打开 `.tex` 文件，将编译器设置为 `XeLaTeX`，按 `F5` 编译运行
- **VS Code**：安装 LaTeX Workshop 插件，在设置中将默认编译工具改为 `xelatex`，保存文件时自动编译
- **Overleaf**：将文件上传后，在菜单中将编译器设置为 `XeLaTeX`