# Interactive Tutorial Builder

一个用于构建和重构浏览器交互式技术教程的 Codex Skill。

它把教程当成一套可验证的学习系统：先修关系、单课教学合同、可运行练习、渐进反馈、连续交互、真实过关证据，以及内容/runtime/浏览器/教学法四层验收。

## 适合什么

- 把技术文档、课程草稿或现有代码整理成连贯的互动教程。
- 重构“内容很多，但学起来断层、跳转混乱、练习无反馈”的课程。
- 为代码、SQL、Agent、API 或其他技术实验设计可运行练习和完成证明。
- 审核课程实际证明了什么，以及哪些结论仍缺少证据。

不适用于纯静态文档、仅 PDF 的书籍、单独的 UI 视觉稿，也不会替代目标项目自己的安全设计和领域专家审查。

## 核心原则

- 先定义学习者起点和可观察终点，再排章节。
- 示例、机制、修改任务、反馈和完成证据围绕同一个技术对象。
- UI 可以是三步、五步或其他形式；学习动作语义不能被某一版界面绑死。
- starter 必须暴露目标问题，reference solution 必须通过可信测试。
- 点击、访问页面和可伪造的本地状态不是运行证明。
- 内容、runtime、浏览器和教学法分别验收，不能互相替代。
- 自动化测试不能证明真人保持率和迁移效果。

## 安装

推荐安装固定版本：

```sh
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo cristi1965/interactive-tutorial-builder \
  --path skills/interactive-tutorial-builder \
  --ref v0.1.0
```

试用主分支最新版时，把 `--ref v0.1.0` 改成 `--ref main`。安装完成后的下一轮对话即可使用新 Skill。

安装器不会覆盖已存在的目录。升级时先把原来的 `${CODEX_HOME:-$HOME/.codex}/skills/interactive-tutorial-builder` 移走或删除，再安装目标版本。

## 使用示例

```text
Use $interactive-tutorial-builder to turn these Go notes into a coherent course with runnable exercises.
```

```text
Use $interactive-tutorial-builder to audit this SQL tutorial for prerequisite gaps, weak feedback, and fake completion evidence.
```

```text
Use $interactive-tutorial-builder to refactor this AI Agent course so each lesson has one clear task and a verified learner loop.
```

## 目录

```text
skills/interactive-tutorial-builder/
  SKILL.md
  agents/openai.yaml
  references/learning-design.md
  references/acceptance-and-evidence.md
  scripts/verify_tutorial_evidence.py
tests/
```

`SKILL.md` 是入口；详细学习设计和验收合同按需加载。证据校验器只检查报告完整性、文件摘要和候选版本绑定，不会自行判断教学质量。

## 验证

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
python3 scripts/check_repository.py
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-creator/scripts/quick_validate.py" \
  skills/interactive-tutorial-builder
```

CI 使用 Python 3.11。Skill 与证据校验器没有第三方运行依赖；只有仓库开发校验使用 PyYAML。

公开发布只使用 Git tracked tree，不直接压缩包含缓存或本地产物的工作目录。

## 安全与隐私

不要把凭证、浏览器 profile、真实学习者数据、完整模型日志、内部 URL、未脱敏截图或运行证明提交到公开仓库。对学习者代码提供执行能力时，必须在目标项目中明确输入、输出、超时、并发、文件、网络、依赖和进程清理边界。

## 版本

当前版本为 `v0.1.0` 公共预览。触发描述、学习合同或证据语义的不兼容修改使用 major 版本；新增可选能力使用 minor；文档和校验器兼容修正使用 patch。

## License

Apache-2.0。该许可证只覆盖本仓库 clean-room 编写的 Skill、参考文档和脚本。
