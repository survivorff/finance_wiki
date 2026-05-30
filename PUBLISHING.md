# 发布到 GitHub 指南

这个知识库是纯 Markdown，可以直接发布到 GitHub 浏览，也可以生成文档站。

## 方式一：直接作为 GitHub 仓库（最简单，推荐先用这个）

每个目录都有 `README.md` 作为导航，GitHub 会自动渲染，直接浏览即可。

```bash
# 在 finance_wiki 目录下初始化（如果还没有 git 仓库）
git init
git add .
git commit -m "init: finance wiki with crypto/cex"

# 关联到 GitHub 仓库，然后推送：
git remote add origin https://github.com/survivorff/finance_wiki.git
git branch -M main
git push -u origin main
```

> 注意：本知识库目前位于 `economy_wiki/finance_wiki/`。
> 如果想让 `finance_wiki` 成为 GitHub 仓库根目录，在 `finance_wiki/` 目录里执行上面的命令即可。

## 方式二：生成文档站（内容多了之后再考虑）

适合内容变多、想要搜索/侧边栏/美观导航时。常见三选一：

- **MkDocs + Material 主题**（Python 系，最省心，适合纯文档）
- **Docusaurus**（React 系，功能强，适合带博客/版本）
- **VitePress**（Vue 系，轻快，Markdown 友好）

以 MkDocs Material 为例：

```bash
pip install mkdocs-material
# 在 finance_wiki 目录创建 mkdocs.yml，把 docs_dir 指向当前内容
mkdocs serve   # 本地预览
mkdocs gh-deploy  # 一键发布到 GitHub Pages
```

> 建议：内容还在快速积累期，先用「方式一」直接看 Markdown；等结构稳定、篇幅变大，再上文档站。

## 提交规范建议（可选）

用语义化前缀，方便回顾学习历程：

- `add: <赛道>/<主题>` 新增内容
- `update: ...` 更新/补充
- `fix: ...` 修订错误

例：`add: crypto/cex 完成五章初版`
