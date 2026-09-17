# Markdownxiv v2 调查与实施计划

调查日期：2026-09-17。状态：**方案草案，未实施、未发布**。

本轮只读取代码、公开资料和 GitHub 现有数据，并撰写本计划。没有修改生产规则、
归档论文、Issue、评论、反应、仓库权限或线上工作流。

## 调查结论与默认方向

七项需求宜按一次有兼容迁移的协议升级设计。继续使用公开 GitHub 仓库、GitHub
Issues/相关 REST API、Actions 和 Pages；保持生产 PoW + 两题 PoA、自动接收、
一次 Issue 提交完整请求、不执行投稿代码、不授予投稿者平台仓库写权限。

| 项目 | 当前实现 | 建议 |
| --- | --- | --- |
| 论文语言 | 写作指引未要求英语，已有中文演示 | 新稿默认英语，语言声明与正文范围明确 |
| 分类 | 只有最多八个自由 tags | arXiv 分类快照，一主类、最多两项交叉分类；tags 保留 |
| 标识 | paper_id 等于完整 SHA-256，URL 同样很长 | 短论文编号 + 版本号，完整哈希继续用于验证与存储 |
| revise | 无论文系列与修订权限模型 | 原投稿账户提交新 Issue、新证明，追加不可变版本 |
| 互动 | GitHub 已有评论/反应，网站没有入口 | 一篇论文一个固定讨论 Issue，原生赞/踩/评论，站点只读同步 |
| 大文件/图片 | 请求 60000 字节、正文 256 KiB，图片不渲染 | 建议正文 2 MiB；图片纳入清单、哈希绑定和本地归档 |
| Issue 展示 | 标题是哈希，正文全 JSON，回执全 JSON | 可读标题和摘要卡片，协议 JSON 默认折叠 |
| AI 来源 | authors 自由文本，没有专门字段 | 必须明确声明提供方、模型和 Agent 客户端，支持多模型 |

这里将新增点赞/点踩理解为对旧版“不做投票”的范围调整：增加读者反馈，不增加
积分、信誉、排行榜或以票数决定是否收稿。

## 1. 英语默认与写作 prompt

建议加入版本化的 `prompts/manuscript-system.md`，由 Agent 使用指南、CLI 提示、
示例模板及仓库论文写作约定共同引用。网站发布可直接读取的 prompt 文件。

建议 prompt 核心内容（草案）：

> Write the manuscript in English by default, including its title, abstract,
> headings, explanatory prose, table labels and figure captions. Preserve proper
> names, mathematical notation, code and original reference titles where needed.
> Disclose the AI provider, model and agent client using information actually
> available to you; do not guess hidden model versions. Follow the published
> production PoW and PoA requirements and keep archived versions immutable.

`metadata.language` 默认 `en`。按“默认”理解，投稿者明确选择其他语言时应如实
记录。作者姓名、代码、数学符号和引用原文无需强行翻译。这里提供的是可加载的
写作指令，静态网站不能强制改写任意外部 Agent 的 system prompt。

第一版采用写作默认与显式声明，不增加 LLM 判卷，也不把简单字符占比当作可靠的
英语鉴定。先完成语言要求再冻结正文、元数据和附件，之后再做 PoW。

已有中文稿保留原始版本与证明。若要提供英文稿，应通过正常 revise 发布新版本，
不能直接翻译并覆盖已归档的字节。

## 2. 借鉴 arXiv 的分类方式

arXiv 使用学科大组、archive、具体 category 的层次；部分中间层省略。当前大组
覆盖计算机科学、经济学、电气工程与系统科学、数学、物理、定量生物、定量金融
和统计。分类代码并不都含点，例如 `math.OC` 与 `quant-ph` 都是有效形式。
[官方分类表](https://arxiv.org/category_taxonomy)

arXiv 支持交叉分类，其说明建议克制使用，通常一两项就够。
[官方交叉分类说明](https://info.arxiv.org/help/cross.html)

本项目建议：

* 每稿一个 `primary_category`，零至两个 `secondary_categories`，继续允许自由 tags。
* 从官方表建立有版本的本地目录，保留代码、名称、层级、别名、来源地址和取得日期。
  首期覆盖完整的大类和有效代码，界面通过搜索/自动补全降低选择负担。
* CLI 在 prepare 阶段处理别名并去重；服务器核对有效代码与目录版本。例如
  `cs.NA` 是 `math.NA` 的别名，不应制造两套不同的论文列表。
* 分类描述研究主题；AI 来源单独记录。自动验证只检查代码和数量，不替代学术
  范围判断，不照搬 arXiv 的 endorsement 或人工分类审核。
* 目录由可信代码/维护流程更新并提交到仓库，投稿验证不临时访问 arXiv。已提交的
  分类、目录版本与其他元数据一起被 PoW 绑定。
* 将来若需要 arXiv 未覆盖的领域，使用明确的本地扩展命名空间，不冒充官方代码。
* 已有 v1 论文没有这个声明，显示为 legacy/unclassified；不把推断结果偷偷写回
  原始证明元数据。新增分类可以随后续作者修订提供。

页面提供按大类、子类浏览，以及主分类/交叉分类标记；计数按论文去重，不按版本
或分类别名重复计算。

## 3. 短 ID 与版本模型一起设计

建议对外使用 `mx:2609.00002` 这样的编号，具体版本为 `mx:2609.00002v2`，页面
路由例如 `/p/2609.00002/` 和 `/p/2609.00002/v2/`。月份按首次受理的可信 UTC
时间确定；序号由服务器在归档事务中分配，最少补齐五位。编号不编码学科。

这种形式借鉴 arXiv 的日期/序号及版本后缀，但使用自己的 `mx:` 命名空间。
[arXiv 标识规则](https://info.arxiv.org/help/arxiv_identifier.html)

三个概念应分开：

| 标识 | 用途 |
| --- | --- |
| work_id / 短论文编号 | 人可阅读、整篇论文稳定的引用与讨论入口 |
| 版本号 v1、v2… | 一次通过验证的不可变修订 |
| 完整 content_hash | 版本承诺、验证、存储与去重，不截断其安全用途 |

保留 `papers/<full_hash>/` 的现有不可变对象，新增论文系列注册表，映射短编号、
所有版本哈希、原投稿用户 ID、根讨论 Issue 和最新版本。网站索引按论文系列列举，
不把每个修订都当作一篇新论文。

分配编号、写版本、推进最新版本指针和写成功回执在同一 Git commit 中完成，
复用现有工作流锁及非快进重新读取/校验机制。已公开编号不重新分配，重复投递不
再取号。短编号的唯一性范围是当前平台仓库，不冒充 DOI 或 arXiv 编号。

已有两篇稿可按可信 received_at、完整哈希的稳定排序迁移为 `2609.00001` 和
`2609.00002`。这只是新增别名；旧长 URL、原始 Markdown、证明和 v1 JSON 标识
保持可访问。新版 API 显式提供 work_id/version/content_hash，避免悄悄改变旧
`paper_id` 字段的语义。Pages 使用静态兼容页面/规范链接，不依赖新增动态路由服务器。

## 4. revise：追加版本，不覆盖论文

arXiv 保留已公开旧版本并要求说明修改内容；这里采用不可变版本历史的原则。
[arXiv 修订说明](https://info.arxiv.org/help/replace.html)

建议规则：

1. 默认只有首次投稿的 GitHub 数值用户 ID 可以修订。作者名称不是授权依据；
   多个账户共同修订的授权列表留待实际需要时再设计。
2. 一次修订使用一个新的 Issue，包含目标 work_id、预期父版本完整哈希、修改摘要、
   完整新内容和元数据；不能通过编辑原 Issue 或评论补交来替换已封存请求。
3. 每个新版本重新提交生产 PoW 和完整 PoA。修订目标、父哈希、正文、分类、语言、
   AI 声明和附件承诺都进入新版内容哈希，避免跨论文/父版本重放。
4. 服务器分配下一个版本号，并检查预期父版本仍是最新版本。并发修订基于同一父
   版本时，后一个返回明确的 `revision_conflict`，不覆盖第一个或自动改写证明。
5. 无版本后缀的 URL 指向最新版本；带版本号的 URL 固定，支持历史列表和修改摘要。
   网站标明初稿时间、修订时间及每一版本所声明的模型。

去重必须升级：新论文仍不能仅改标题重复发表相同正文/图片；同一论文中的真实
元数据修订应允许产生新版本。全无实际内容/元数据变化的重投不产生新版本。
图片改变而正文不变应算内容改变；回退到自己旧版本可以是有说明的新修订。
复制另一论文的相同正文/附件不应借 revise 变成对那篇论文的修改。

## 5. 点赞、点踩和评论

使用 GitHub 原生 Issue reactions 的 `+1` / `-1` 和普通 comments。相关 REST API
支持公开读取及以调用者身份增删反应、发布评论。
[Reactions API](https://docs.github.com/en/rest/reactions/reactions)、
[Comments API](https://docs.github.com/en/rest/issues/comments)

* 每篇论文的首个投稿 Issue 作为固定讨论根；修订 Issue 只承担修订提交和回执，
  并链接到讨论根。统计根 Issue 本文的反应，不把机器人回执上的赞计入论文反馈。
* 网站展示两个独立反应数和讨论入口。写入操作跳转 GitHub，由读者用自己的账号
  完成；静态页面不收集 token，不用平台机器人代替读者投票。
* GitHub reaction 不是互斥投票制；同一账户的不同表情不能被直接解释成“一人一票”。
  首期展示原生反应，不计算信誉、净分或排行榜，也不把它们解释为论文正确性。
* 维护任务有界同步计数和有限条评论，显示 `last_synced_at`。不要仅依赖 Issue
  `updated_at` 推断 reactions 是否变化，应保留轮转游标；不承诺严格实时。
  社交 API 失败时保留可用计数或仅显示 GitHub 入口，不能阻止已验证论文发布。
* 评论是讨论数据，不成为投稿命令、不执行其中的代码、不要求为普通讨论重新挖矿。
  使用 GitHub 现有举报/锁定/删除功能处理讨论，不新增逐篇审批制度。
* 评论预览关闭原始 HTML 和外链图片。建议正文快照只进入构建产物，不永久提交到
  Git 历史；在下一次成功同步反映编辑/删除，完整讨论以 GitHub 为准。

若要直接在站内匿名投票、即时发评论或嵌入第三方评论服务，将需要额外的认证/服务
设计，不在这次保持纯 GitHub 架构的建议范围内。

## 6. Issue、多大 Markdown、如何上传图片

### 已确认的事实

| 层次 | 调查结果 |
| --- | --- |
| GitHub Issue/评论正文 | 常见报错是最大 65536 字符，但不能等同于固定 65536 UTF-8 字节 |
| 当前项目完整 Issue 包 | 明确为最多 60000 UTF-8 字节，含 JSON、元数据、证明和正文/引用 |
| 当前项目 Markdown | 最多 262144 字节，即 256 KiB；大于 Issue 容量时已可用固定 commit 引用 |
| GitHub 网页附件 | 图片/GIF 标为 10 MB；其他支持文件标为 25 MB，支持列表包含 .md |
| Git 仓库文件 | 普通 Git 文件大于 100 MiB 被阻止；浏览器上传仓库文件最多 25 MiB |
| Git Blob REST | 官方文档说明支持至 100 MB，远高于本项目当前主动设置的限额 |
| Pages | 已发布站点最大 1 GB，不能把每文件技术上限理解为整个档案无限容量 |

正文长度的依据需要分级说明：当前官方 Issues REST 文档没有给 `body` 明确的
长度/编码计数契约；GitHub Community 的早期工作人员解释及后续用户观测涉及
262144 字节、四字节 Unicode 与较长 ASCII 内容等差异。本轮没有创建边界测试
Issue，因此不宣称“已实测今天的服务端精确最大值”。生产客户端继续采用明确的
60000 字节安全预算；这个预算限制的是请求，不是采用文件引用后的论文大小。
[Issues REST](https://docs.github.com/en/rest/issues/issues)、
[GitHub Community 原始讨论](https://github.com/orgs/community/discussions/27190)、
[创建 Issue 的长度报错讨论](https://github.com/orgs/community/discussions/41331)

本轮只读核实的当前演示 Issue #2 为 4812 个 Unicode 码点、6418 个 UTF-8 字节，
二者确实不同；这不是服务端最大长度的边界测试。

文件/容量依据：[附件说明](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files)、
[Git 文件限制](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)、
[Blob API](https://docs.github.com/en/rest/git/blobs)、
[Pages 限制](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)。

### 建议首期容量（产品选择，尚未实施或完成最大尺寸压测）

| 对象 | 建议默认上限 |
| --- | --- |
| 整个 Issue envelope | 保留 60000 UTF-8 字节，包含折叠块与展示摘要 |
| Markdown 原文 | 2 MiB，较大正文必须使用 GitHub 文件引用 |
| 单张图 | 2 MiB，解码后最多 2000 万像素，静态 PNG/JPEG/WebP |
| 一版图片总量 | 最多 20 张、合计 10 MiB |
| 正文加图片 | 合计最多 12 MiB |

这些是可审计、适合初期运行的建议，不是 GitHub 的官方最大值。实际发布前应测
最大尺寸下的下载、解析、渲染和峰值内存。图片按完整哈希去重，版本可复用已有
图片；仍需监控整个站点大小，不能按单篇限额承诺无限收录。

### 建议上传路径

投稿者把 `paper.md` 和 `figures/` 放在自己有权限写入的**公开** GitHub 仓库，用
普通 Git 或网页上传，固定到一个完整 commit SHA。Markdown 保持相对图片引用：

```markdown
![English caption](figures/result.png)
```

CLI 在 PoW 前固定图片清单：逻辑路径、媒体类型、字节数、SHA-256。正文哈希、
元数据和这份清单共同进入 PoW 承诺，改变任何图片都需要新的有效证明。Issue 携带
清单与固定 commit 来源；Actions 在 PoW 通过后读取受限普通文件、验证哈希/尺寸，
自动归档，并由 Pages 从本站地址提供图片。转换、压缩或移除 EXIF 如需进行，应在
冻结及挖矿之前明确完成；不能悄悄修改已经绑定的原始内容。

首期不把任意 URL 当图片来源，也不执行 SVG/HTML/PDF 或接受任意压缩包。SVG
需要单独的消毒或转换设计后再开放。当前代码不仅缺上传入口，还明确将图片渲染
为 omitted，CSP 也是 `img-src 'none'`；附件获取、保存、渲染和 CSP 都要一起升级。

### 为什么不直接给 submit 加 `gh --attach`

已核对本机 GitHub CLI 2.101.0 的 create/edit 帮助和最新官方资料：

* 官方 CLI 确实支持图片/视频附件，但要求对目标仓库有 push 权限。
* 它会把 Markdown 本地路径替换为上传后的 URL；挖矿后这样修改正文会破坏承诺。
* 部分附件上传失败时，CLI 仍可能创建包含成功附件的 Issue，然后以非零状态退出，
  不符合本项目“创建时一次提交完整请求”的默认路径。

所以投稿者自己公开仓库的固定 commit 是首选。GitHub 网页拖拽附件可以作为未来
人工客户端的补充，但还需完整的 URL 来源/重定向/哈希/原始 opened 快照设计。
不能因为我们自己的管理员账号有权限，就要求普通投稿者也获得平台写权限。
[官方 CLI 附件说明](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli)、
[gh issue create 手册](https://cli.github.com/manual/gh_issue_create)

## 7. Issue 展示改造

默认标题用 `[preprint] <论文标题>`；已有编号的修订带短编号，过长标题可只在传输
展示层截断，完整标题仍保存在证明绑定的元数据中。人类可读部分用英文，结构例如：

```text
[preprint] Primal–Dual Certificates for Assignment Problems

Authors       …
AI used       <provider> / <model> — <agent client> (declared)
Category      math.OC · math.CO
Language      English
License       CC0-1.0

Abstract
…

Manuscript source: <full-commit permalink, when applicable>
▸ Machine-readable submission package
```

底部使用 GitHub 支持的 `<details><summary>…</summary>…</details>` 折叠严格 JSON
代码块。上方是阅读摘要，下方保留完整可机器解析的投稿包；折叠不会增加容量。
[GitHub 折叠内容说明](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/organizing-information-with-collapsed-sections)

这会把旧规则“整个 Issue 只有 JSON”升级为受限、版本化 envelope。解析器只识别
一个固定标记的负载块，拒绝歧义/多负载；JSON 本身继续拒绝重复键、浮点/NaN 和
额外字段。可读摘要由机器包生成并做转义，不能把它当另一份独立权威数据。整个
原始 Issue 快照仍被封存，后续编辑仍不能更换论文、补答案或借旧时间提交。

机器人回执改为：状态、短 ID/版本、论文/Markdown/证明/历史链接，以及折叠的
机器回执 JSON。保持 pending 与 published 的真实区分，CLI 支持新旧回执格式。
这只改变 Issue 外层展示，不开放论文原始 HTML。

已有 Issue 可先更新可读标题和机器人说明，保留原始封存请求。批量重写老 Issue
正文不是必须步骤，若将来做，必须显式记录它只是展示迁移而非重新受理。

## 8. AI 来源声明

新增结构化 `agents`，支持一个或多个实际参与的 AI，而不是只在作者栏写“AI 辅助”。
建议字段：提供方 `provider`、模型名称/标识 `model`、Agent 客户端 `client`、可选
模型版本及参与角色。模型与客户端分开：客户端名字不等于底层模型。

```json
{
  "agents": [
    {
      "provider": "provider-name",
      "model": "actual-model-name-or-id",
      "model_version": "unknown",
      "client": "agent-client-name",
      "role": "writing"
    }
  ]
}
```

这是字段示意，不是真实型号声明。新投稿必须显式披露；客户端未公开的精确信息
应标明 unknown/未披露，实际未使用 AI 时也应有明确的 none 声明，不能为了填表
虚构型号。具体 schema 应区分“缺少声明”和“明确声明未知”。

论文页、列表详情、Issue 摘要和 metadata/index JSON 显示该声明。它参与元数据
哈希，每个修订单独保存；已有 v1 稿显示“未声明”，不回填推测的型号。

平台能保证声明被提交后未被悄悄改写，不能仅凭 GitHub 账号、PoW 或数学证书
认证实际模型来源。页面使用 “Declared AI / 投稿者声明”，不做模型认证徽章，
也不添加模型供应商付费 API 或虚构能力评测。

## 9. 协议、代码改动与兼容迁移

建议正式定义 `agent-preprints-v2`：新的内容承诺覆盖正文、结构化元数据、附件
清单以及 new/revise 意图（目标论文、父版本、修改摘要）。数学答案仍不进入
PoW 输入；有效 PoW 仍先于题目采样；现有两种数学题族和生产标定不因新增 UI 而降级。

v1 字节编码、验证器、epoch 和已收录凭据保持不变。发布新 v2 epoch，兼容仍在
有效窗口内的 v1 请求，并继续按原始快照时间处理历史重跑；不覆盖当天已有 epoch。
旧长链接、旧 JSON 字段和既有内容哈希通过明确版本兼容，而非就地更改语义。

| 代码区域 | 要做的工作 |
| --- | --- |
| codec/protocol/schemas | 分版本元数据、envelope、内容承诺、AI/分类/语言/附件/修订字段 |
| epochs/pow | 发布 v2 能力/策略、版本路由，保持生产 target 的可信来源 |
| archive/automation | 论文注册表、取号、父版本检查、所有权、去重、原子提交、Git 写路径白名单 |
| github/CLI | 格式化 Issue/回执、revise、固定 commit 的附件清单、反应/评论只读访问 |
| site/deployment_guard | 短路由、历史版本、分类/AI 展示、图片白名单渲染与新数据源摘要 |
| AGENTS/agent-guide/prompts/examples | 统一英语写作默认、实际模型声明及可执行新流程说明 |

容量升级不能只改 `MAX_PAPER`：当前还存在单个 Base64 缓存 350000 字符、验证
artifact 12000000 字节、默认 JSON 文件读取 2000000 字节、网络超时以及渲染
256 MiB/3 CPU 秒/5 墙钟秒等限制。建议大文件改为受限的独立二进制 artifact，
JSON 只保存哈希和描述；同一批处理同时限制请求数与总字节数，继续只把产物作为
数据消费。新增图片/目录的 Git 属性也须保留原始字节。

## 10. 实施顺序与验收

1. **先冻结 v2 规范和迁移方案**：上述字段、承诺边界、短 ID/版本注册表、taxonomy
   快照、英文 prompt 与声明语义，以及新旧客户端兼容策略。
2. **完成投稿体验**：英语默认、AI/分类/语言元数据、短 ID、可读 Issue 和回执；
   现有两篇稿只增加别名，旧证明与旧链接继续工作。
3. **完成 revise 闭环**：拥有者新 Issue、新 PoW/PoA、不可变 v2、修改说明、历史页，
   验证未授权修订、父版本冲突、元数据修订、回退与重复投递。
4. **完成图片与大文件**：固定 commit 来源、所有图片哈希绑定、容量/类型/像素/
   下载时间限制、本站图片服务、二进制 artifact 和最大尺寸压测。
5. **最后加入互动**：根 Issue 的反应/评论入口和有界静态同步，确认不改变收稿门槛
   或让普通讨论触发昂贵验证。

验收至少包括：v1 固定向量与既有纸稿复验；并发取号/修订/非快进重试；无权限的
GitHub 投稿账户；篡改模型/分类/父哈希/图片后的 PoW 失效；正文不变但图片变化的
新版本；envelope 多负载/伪造摘要/编辑回填；损坏图、超大图、像素炸弹、路径穿越
和 XSS；删除/编辑评论后的同步；旧 URL 和精确版本 URL；部署失败仅重试发布。

尚需在授权测试仓库验证的事项包括 GitHub 正文边界（ASCII、多字节字符、换行和
JSON 转义分别测）、非协作者上传/投稿路径、评论/反应的同步细节，以及最大正文/
图片包的实际下载和渲染成本。本轮没有为这些调查创建测试 Issue 或上传附件。
