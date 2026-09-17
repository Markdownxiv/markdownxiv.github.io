# 本次验证记录

本地环境：2026-09-17，Linux/WSL2，Python 3.12.3，AMD Ryzen 7 8845H。
初次实现先完成本地验证；随后经用户授权，已推送到目标仓库并成功部署 GitHub Pages。
真实 GitHub CI 使用 Python 3.12.14。没有创建真实投稿 Issue 或公开发布演示论文，
也没有修改仓库可见性、分支保护或用户已配置好的部署环境规则。

## 已实际运行

* 使用 `requirements.lock` 的固定版本和 wheel SHA-256 强制重新安装全部 Python
  依赖；随后 `pip check` 返回 `No broken requirements found`。项目使用本地可编辑安装。
* `python -m unittest discover -s tests -v`：发布前补充 Git 原始字节保留配置和
  CRLF 回归用例后，**67 项全部通过，本地完整运行耗时 26.495 秒**。
  覆盖协议、PoW、数学证书、生产配置、
  原始事件、回执、并发、API mock、本地 Git 事务、HTML 安全、公式和建站测试。
  没有在 CI 测试中挖生产 PoW 或求生产规模题。
* `python examples/local_demo.py --out .demo`：所有实际 CLI 阶段跑通，包含
  有效开发 PoW、两个实际题目及证书、完整验证、归档、静态构建；同一期再次运行，
  保持一个 paper ID，没有重复收录。本地回执如实保持 `published: false`。
* `preprints build --out _site`：根目录暂停配置下成功生成空站；静态生成器测试
  覆盖 `/repo-name/` 子路径。另用只绑定 loopback 的本地 HTTP 服务挂载
  `/Markdownxiv/`，首页、CSS、JS、挑战 JSON、索引 JSON、Agent 指南、协议页及
  submission schema 均实际返回 HTTP 200。
* PoW 基准真正完成 38,215,680 次尝试，耗时 10,000,762,354 ns，速率约
  3,821,276.68 次/秒。CPU/线程/条件/实现/target 的原始记录见
  [local-pow.json](measurements/local-pow.json)。这只是本机测量，没有发布到根目录
  的生产标定注册表，也没有把运行环境描述成所有矿工的统一速度。
* 使用这个实测 target，另在隔离目录真实挖出一个生产 PoW，整个挖矿及随后验证
  实验耗时约 **109.810 秒**。已用两题生产参数的真实证书通过完整生产校验路径。
  `tests/fixtures/production/` 保存完整可复核输入；其中发布状态**明确是本地模拟**，
  仓库/用户测试 ID 分别为 `1` / `2`。CI 只验算固定 nonce 和证书，不重新挖矿。
* 两个生产参数题族各五个公开固定 seed，实际测了采样、参考求解、独立验证的
  纳秒耗时。最后一次测量包含对输入矩阵形状/数字范围的额外检查。中位数见
  [POA_DESIGN.md](POA_DESIGN.md)，原始数据见 [local-poa.json](measurements/local-poa.json)。
  没有做 Agent 身份/水平区分实验；两种参考求解器都很快。
* 用临时的**本地裸 Git 仓库**测试了真实 commit/push、两个并发写入者和真实
  non-fast-forward 冲突。冲突后的第二次回调读到了更新后的状态，成功存档与
  回执处在同一 commit。模拟 push 拒绝时，没有伪称远端归档成功。这些临时
  本地 push 与向 `github.com:kzoacn/Markdownxiv` 推送不是同一件事。
* `compileall`、`node --check site/search.js`、`git diff --check` 均通过。

## 工作流静态核对及工具限制

已通过官方 GitHub Git refs API 核对所用 Action release tag 对应的完整 commit SHA，
读取了相关 pinned `action.yml`，并对照官方 Pages、权限、事件和并发文档。
YAML 本地解析得到 accept/maintain 各 5 个 job、CI 1 个 job。

实际下载了官方 actionlint **v1.7.12** 并核验其 release SHA-256 checksum。
原样运行时仅报两项错误：它不识别 accept/maintain 的 `concurrency.queue`。
当前[官方 GitHub 工作流语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
明确支持 `queue: max`，最多 100 个 pending run；因此没有为迁就旧 linter
删除可靠性配置。只忽略这个精确的已知兼容错误后，其余检查通过：

```bash
actionlint -shellcheck= \
  -ignore '^unexpected key "queue" for "concurrency" section\.' \
  .github/workflows/accept.yml .github/workflows/maintain.yml .github/workflows/ci.yml
```

没有宣称原样 actionlint 全部通过。ShellCheck 未运行；工作流 run 段仅为固定
安装/平台命令，不包含 Issue 文本插值。页面使用原生 MathML，已检查生成内容，
没有进行真实浏览器截图、移动设备或跨浏览器视觉回归。

## 仍未完成的线上验证

1. 一次真实生产投稿的 `issues: opened` 快照、正式归档和机器人 Issue 回执。
2. 队列容量/丢失事件、失败 job 重跑、限流、网络故障和部署失败恢复的真实故障演练。
3. 跨浏览器与移动设备视觉检查，以及 PoA 的 Agent 能力区分度实验。

这些内容的可执行 smoke test 步骤位于 [DEPLOYMENT.md](DEPLOYMENT.md)。本地
mock、模拟发布上下文、静态 YAML 检查都不能代替这些线上验收。上述初次交付时，
根目录为 `enabled: false`、`calibration_id: null` 和 `calibration_required`。

## 随后的本地部署准备（2026-09-17）

用户提出部署后，通过公开 GitHub API 确认 `kzoacn/Markdownxiv` 是公开仓库，
Issues 已启用，默认分支为 `main`，仓库 ID 为 `1374075838`。官方 GitHub CLI
2.101.0 校验 release checksum 后放入 `.work/tools/gh`；该准备阶段尚未登录。

在同一 CPU、Python 实现和单线程条件下，为部署重新完成 15 秒真实标定：
57,458,688 次尝试、15,000,341,114 ns。生产标定 ID 为
`bda1d4f84171e5860d5878b1bd3cc997ee6a452ed64a636d8043684eff7cffc4`，
原始字节位于 `challenges/calibrations/`。已在本地绑定实际仓库 ID、启用生产配置并
生成 `2026-09-17` epoch。当时 registry 中 `published_at` 为 null，正式验证会返回
`epoch_unpublished`。没有改成测试难度，也没有伪造 Pages 成功记录。

该准备阶段未提交到项目远端、修改远端设置或公开发布；用户随后完成 GitHub 登录
和 Pages source 设置，才进行了下面记录的实际部署。

## 实际首次部署（2026-09-17）

* 实现提交：`ac4e144744d7b0da53e634b19d563fca7e96a3d4`。
* [真实 CI 运行](https://github.com/kzoacn/Markdownxiv/actions/runs/35201763330)：
  Python 3.12.14，67 项测试在 2.786 秒内通过，CLI 完整演示及静态构建也通过。
* [真实部署运行](https://github.com/kzoacn/Markdownxiv/actions/runs/35201761005)：
  validate、archive、build、deploy、receipt 五个 job 全部成功。GitHub 实际接受了
  `queue: max` 配置，官方 Action 的 artifact 上传、下载及 Pages 部署组合已跑通。
* `GITHUB_TOKEN` 在 main 写入发布登记提交
  `9b31487d3d700a20bea2282bd847fb03fe0a4d95`；环境只允许 main，无人工审核。
  本次没有 Issue 回执需要发送，因此不能据此声称已验证真实评论 API 写入。
* 首期 epoch 的 `published_at` 为 `2026-09-17T08:50:08Z`，发布完成登记时间为
  `2026-09-17T08:50:42Z`。挑战 ID、盐、target 及原始文件哈希保持不变。
* [公网站点](https://kzoacn.github.io/Markdownxiv/)及其 CSS、JS、挑战页、指南、协议、
  索引、生产配置、latest、registry、schema 和 manifest 共 12 个入口实际返回 HTTP 200。
  原始 epoch SHA-256 与 latest/registry 一致，生产 profile 和实际仓库 ID 也已核对。
* `preprints challenge --site https://kzoacn.github.io/Markdownxiv/ --root .work/live-challenge`
  实际下载并校验了生产挑战及标定。论文索引为空，未收录或发布示例论文。

以上是真实部署记录；前文的生产证明 fixture 仍然只是离线测试数据。
