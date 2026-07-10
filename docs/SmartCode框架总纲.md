# SmartCode 框架总纲

> 44K 行 Python · 103 源文件 · 零运行时依赖
> AI 编码 Agent · think/act/verify 循环引擎

---

## 一、宏观架构

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SmartCode 框架                               │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    入口层 (Entry)                            │    │
│  │  main.py / headless.py / __main__.py / web/server.py        │    │
│  └─────────────────────┬───────────────────────────────────────┘    │
│                        │                                           │
│                        ▼                                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                  编排层 (Orchestration)                       │    │
│  │                                                              │    │
│  │  agent_loop.py（2 行入口）→ loop_orchestrator.py（编排引擎）  │    │
│  │  ┌──────────────────────────────────────────────────────┐    │    │
│  │  │  run_agent_turn()                                     │    │    │
│  │  │    ├── Prelude（初始化状态/上下文/审查系统）            │    │    │
│  │  │    ├── Recurrent Kernel（四步循环）                    │    │    │
│  │  │    └── Coda（收尾/注入/沉淀）                           │    │    │
│  │  └──────────────────────────────────────────────────────┘    │    │
│  └──────┬──────────┬──────────┬──────────┬───────────────────────┘    │
│         │          │          │          │                          │
│         ▼          ▼          ▼          ▼                          │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐            │
│  │ 决策引擎 │ │ 模型调用  │ │ 工具执行  │ │  审查系统    │            │
│  │ turn_   │ │ model_   │ │ tool_    │ │  review/    │            │
│  │ kernel  │ │ caller   │ │ executor │ │ (6 files)   │            │
│  └─────────┘ └──────────┘ └────┬─────┘ └──────────────┘            │
│                                │                                    │
│                     ┌──────────┴──────────┐                         │
│                     ▼                     ▼                         │
│           ┌──────────────┐     ┌──────────────────┐                │
│           │ 18 个工具    │     │ 支撑子系统        │                │
│           │ tools/      │     │ session/memory/   │                │
│           │ import_map  │     │ context/config/   │                │
│           │ sandbox_test│     │ cost_tracker/    │                │
│           │ task/...    │     │ report/...       │                │
│           └──────────────┘     └──────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 二、六层架构

### 第 1 层：入口层（Entry）

| 文件 | 职责 | 启动方式 |
|:-----|:------|:---------|
| `main.py` | CLI 入口，TUI/管道/参数解析 | `minicode "写代码"` / `minicode --tui` |
| `headless.py` | 无头模式，CI/CD 集成 | `python -m minicode.headless` |
| `__main__.py` | 支持 `python -m smartcode` | `python -m smartcode` |
| `web/server.py` | Web UI 后端，FastAPI + WebSocket | `python -m web.server` → `:8341` |

### 第 2 层：编排层（Orchestration）

```
agent_loop.py（2 行）
  └── loop_orchestrator.py（878 行）
        └── run_agent_turn()
              ├── Prelude
              │   ├── TurnRecurrentState 初始化
              │   ├── 意图解析 → TaskObject
              │   ├── 上下文预检 + 微压缩
              │   └── init_review_hooks()
              │
              ├── Recurrent Kernel（while）
              │   ├── Step A: derive_turn_step_policy()
              │   ├── Step B: _model_next()
              │   ├── Step C: decide_assistant_turn()
              │   └── Step D: _execute_single_tool()
              │
              └── Coda（finally）
                  ├── on_turn_end() 注入审查发现
                  ├── metrics_collector.end_turn()
                  └── finalize_work_chain_task()
```

### 第 3 层：决策引擎（Decision Engine）

**`turn_kernel.py`（1700 行）** — 核心状态机，不做任何 LLM 调用或工具执行。

```
TurnRecurrentState        → 回合状态：步数/错误/widening/策略
TurnBudgetSignals         → 预算信号：剩余步数/是否超限
TurnStepPolicy            → 步骤策略：explore/execute/verify
TurnVerificationState     → 验证状态

核心函数：
  derive_turn_step_policy()     → 推导当前策略
  decide_assistant_turn()       → 4 类响应判断
  decide_tool_turn()            → 工具决策
  build_turn_coda_summary()     → Coda 摘要
  build_widening_transition_nudge() → 拓宽提示
```

### 第 4 层：模型调用层（Model Calling）

**`model_caller.py`（215 行）** — LLM 适配器统一调用。

```
_model_next()               → 调 LLM，动态适配签名
_is_at_blocking_limit()     → 上下文超限预判
_summarize_model_api_failure() → API 错误人性化摘要
_infer_active_model_id()    → 推断当前模型 ID

适配器（Adapter 模式）：
  anthropic_adapter.py       → Anthropic Messages API
  openai_adapter.py          → OpenAI 兼容 API（DeepSeek/Qwen）
  mock_model.py              → 测试用 Mock
  model_switcher.py          → 运行时切换模型
```

### 第 5 层：工具执行层（Tool Execution）

**`tool_executor.py`（193 行）** — 工具调度 + 审查钩子。

```
_execute_single_tool()
  ├── 钩子 1：on_before_write（宽松+严格审查，阻断写入）
  ├── ThreadPoolExecutor 超时执行
  ├── 串行/并行分类调度（只读并行，写入串行）
  └── 钩子 2：on_file_written（import map 更新 + test agent）
```

**18 个工具（`tools/`）：**

| 分类 | 工具 | 执行方式 |
|:-----|:------|:--------:|
| 文件操作 | write_file/edit_file/patch_file/read_file/list_files | needs_review=True |
| 搜索 | grep_files/find_symbols/find_references | 并行 |
| 命令 | run_command/git | 串行 |
| 代码 | code_review/diff_viewer/file_tree | 并行 |
| 审查系统 | import_map/sandbox_test/task | 按需 |
| 子 Agent | task（review/test/explore/plan/general） | 独立循环 |

### 第 6 层：审查系统（Review System）

**`review/` 目录（6 个文件）** — 插拔式，存在即启用。

```
review/
├── __init__.py              包入口
├── config.py                配置（三级模式）
├── hooks.py                 4 个类：编排 + 宽松 + 严格 + 沙箱
├── mode_engine.py           严格触发判断
├── memory.py                审查发现持久化
└── promotion.py             发现→skill 沉淀
```

**4 个职责分离的类：**

| 类 | 职责 | 行数 |
|:----|:------|:----:|
| `LooseReviewEngine` | 正则+AST 审查（毫秒级） | 60 |
| `StrictReviewEngine` | 上下文收集 + 1 次 LLM + 熔断器 | 70 |
| `SandboxTestRunner` | Docker 沙箱测试（零 LLM） | 35 |
| `ReviewOrchestrator` | 3 个钩子 + 模式切换 + import map | 180 |

---

## 三、六大子系统

### 3.1 会话系统（session.py）

```
核心：
  SessionData          → 完整会话状态（消息/检查点/权限/技能）
  SessionMetadata      → 会话元数据（ID/时间/统计）
  FileCheckpoint       → 写文前自动创建文件快照

增量 delta 保存：
  每次保存只追加新消息（比全量快 10x）
  每 10 次增量后全量合并
  字段级脏标记

文件级回退：
  支持按步数或 checkpoint_id 回退
  回退前生成反向安全快照
```

### 3.2 记忆系统（memory.py）

```
三层作用域：
  USER    → ~/.mini-code/memory/      跨项目永久
  PROJECT → .mini-code-memory/        团队 Git 共享
  LOCAL   → .mini-code-memory-local/  本地私有

四级层级：
  WORKING → SHORT_TERM → LONG_TERM → ARCHIVAL

六维搜索评分：
  score = (bm25 + substring + tag) × 0.7
        + domain_jaccard × 0.3
        + log1p(usage_count) × 0.3
        + 1/(1+age_hours/24) × 0.5

自动分类器（8 类关键词，零 LLM）：
  architecture / code-pattern / testing / configuration
  workflow / security / performance / convention

工作记忆层（纯内存，15 条）：
  保护 active_task/user_intent/key_decision/error_context
```

### 3.3 上下文管理系统（context_manager.py + context_compactor.py）

```
四级压缩：
  Level 1 微压缩（0.1ms）→ 清除 >60s 旧 tool_result
  Level 2 轻压缩          → 使用率 >70% 时合并历史
  Level 3 激进压缩         → LLM 总结对话历史
  Level 4 反应式压缩       → API 返回 prompt too long 时

熔断器保护：
  连续失败 3 次 → 跳过压缩
  任意成功 → 重置
```

### 3.4 配置系统（config.py + settings）

```
配置优先级（从高到低）：
  1. 环境变量（MINICODE_REVIEW_MODE 等）
  2. .claude/settings.json
  3. ~/.mini-code/settings.json
  4. 代码默认值
```

### 3.5 成本控制（cost_tracker.py + report.py）

```
成本上限：
  export MINICODE_API_COST_LIMIT=0.50
  每次 API 调用前检查，超限抛 RuntimeError

/report 命令聚合 4 个数据源：
  AppState          → 会话时长 / API 次数 / 错误
  CostTracker       → 每个模型 token 明细 / 成本
  CompactionBreaker → 压缩熔断器状态
  ReviewBreaker     → 审查熔断器状态
```

### 3.6 权限系统（permissions.py）

```
非交互模式自动放行 workspace 内编辑
危险命令分类（rm -rf / git push --force / chmod 777 等）
LRU 缓存路径标准化
```

---

## 四、数据流全景

```
用户输入
  │
  ▼
main.py / headless.py / Web UI
  │
  ├── load_runtime_config() → 加载模型配置
  ├── create_model_adapter() → 创建适配器
  ├── create_default_tool_registry() → 注册工具
  └── run_agent_turn()
        │
        ├── Prelude
        │   ├── TurnRecurrentState(profile)
        │   ├── _build_work_chain_task() → TaskObject
        │   ├── MicroCompactor.compact()
        │   └── init_review_hooks()
        │
        ├── Recurrent Loop（while）
        │   │
        │   ├── Step A: derive_turn_step_policy()
        │   │   → explore/execute/verify + widening
        │   │
        │   ├── Step B: _model_next()
        │   │   → _is_at_blocking_limit()? 阻止 or 放行
        │   │   → model.next(messages)
        │   │   → ConnectionError/TimeoutError/其他异常
        │   │
        │   ├── Step C: decide_assistant_turn()
        │   │   → progress → 追加消息, continue
        │   │   → retry → nudge 提示, continue
        │   │   → fallback → widen 或终止
        │   │   → final → 返回结果
        │   │
        │   └── Step D: _execute_single_tool()
        │       → 钩子 1: on_before_write()
        │       │   ├── LooseReviewEngine.review()（0.7ms）
        │       │   └── StrictReviewEngine.review()（~5s，strict 模式）
        │       │
        │       → tools.execute(tool_name, input, context)
        │       │   ├── ThreadPoolExecutor 超时
        │       │   ├── 只读并行 / 写入串行
        │       │   └── 分类调度
        │       │
        │       → 钩子 2: on_file_written()
        │           ├── _async_update_import_map()（后台）
        │           └── should_trigger_strict()? → SandboxTestRunner（后台）
        │
        └── Coda（finally）
            ├── 等待 import map + 后台线程完成
            ├── ReviewOrchestrator.on_turn_end()
            │   ├── 注入 _coda_findings → current_messages
            │   └── promote_findings() → skill/记忆
            ├── metrics_collector.end_turn()
            └── finalize_work_chain_task()
```

---

## 五、文件清单

### 核心引擎（55 文件）

| 文件 | 行数 | 职责 |
|:-----|:----:|:------|
| `agent_loop.py` | 2 | 入口重新导出 |
| `loop_orchestrator.py` | 878 | 三阶段编排 |
| `model_caller.py` | 215 | LLM 调用 |
| `tool_executor.py` | 193 | 工具执行 + 审查钩子 |
| `turn_kernel.py` | ~1700 | 决策状态机 |
| `main.py` | ~800 | CLI 入口 |
| `state.py` | ~200 | AppState 全局状态 |
| `session.py` | ~600 | 会话持久化 |
| `memory.py` | ~2500 | 记忆系统 |
| `config.py` | ~900 | 配置系统 |
| `permissions.py` | ~600 | 权限系统 |
| `cost_tracker.py` | ~480 | 成本追踪 |
| `report.py` | ~200 | 运行报告 |
| `cli_commands.py` | ~1000 | CLI 命令 |
| `tooling.py` | ~600 | 工具注册/定义 |

### 审查系统（6 文件）

| 文件 | 行数 | 职责 |
|:-----|:----:|:------|
| `review/__init__.py` | 1 | 包入口 |
| `review/config.py` | 40 | 三级模式配置 |
| `review/hooks.py` | ~500 | 4 个类：编排/宽松/严格/沙箱 |
| `review/mode_engine.py` | ~100 | 4 层触发判断 |
| `review/memory.py` | ~130 | 审查发现持久化 |
| `review/promotion.py` | ~300 | 发现→skill 沉淀 |

### 工具系统（23 文件）

| 文件 | 职责 |
|:-----|:------|
| `tools/__init__.py` | 工具注册中心 |
| `tools/write_file.py` | 写文件（needs_review=True） |
| `tools/edit_file.py` | 编辑文件（needs_review=True） |
| `tools/patch_file.py` | 补丁文件（needs_review=True） |
| `tools/read_file.py` | 读文件 |
| `tools/list_files.py` | 列出目录 |
| `tools/grep_files.py` | 搜索文件内容 |
| `tools/run_command.py` | 运行命令 |
| `tools/git.py` | Git 操作 |
| `tools/code_review.py` | 代码质量审查 |
| `tools/import_map.py` | AST 建表 + 增量更新 |
| `tools/sandbox_test.py` | Docker 沙箱测试 |
| `tools/task.py` | 子 Agent 调度（5 种类型） |
| `tools/test_runner.py` | 测试运行器 |
| `tools/code_nav.py` | 符号查找/引用 |
| `tools/diff_viewer.py` | Diff 查看 |
| `tools/file_tree.py` | 文件树 |
| `tools/web_fetch.py` | Web 抓取 |
| `tools/web_search.py` | Web 搜索 |
| `tools/ask_user.py` | 询问用户 |
| `tools/todo_write.py` | 任务列表 |
| `tools/load_skill.py` | Skill 加载 |
| `tools/batch_ops.py` | 批量操作 |

### TUI 子系统（19 文件）

`tui/chrome.py` / `input_handler.py` / `input_parser.py` / `renderer.py` / `screen.py` / `markdown.py` / `transcript.py` / `theme.py` / `state.py` / `event_flow.py` / `navigation.py` / `session_flow.py` / `runtime_control.py` / `tool_helpers.py` / `tool_lifecycle.py` / `ui_hints.py` / `types.py` / `__init__.py` / `input.py`

### Web UI（2 文件）

| 文件 | 职责 |
|:-----|:------|
| `web/server.py` | FastAPI + WebSocket 后端 |
| `web/index.html` | 单页应用：终端 + 编辑器 + 文件浏览 + 设置 |

---

## 六、设计决策记录

| 决策 | 选择 | 理由 |
|:-----|:------|:------|
| 决策/执行分离 | turn_kernel vs loop_orchestrator | 独立测试，互不耦合 |
| 审查写前同步 | on_before_write 阻断 | 代码不落地，安全 |
| 审查 4 类分离 | 4 个类 vs 1 个巨类 | 独立测试，职责清晰 |
| test agent 零 LLM | 直接截取 pytest 输出 | 0 token，信息不丢失 |
| Docker 沙箱 | 容器全部隔离 | 彻底隔离，删容器回滚 |
| 环境变量传参 | runtime dict 代替 os.environ | 线程安全 |
| needs_review 声明 | ToolDefinition 字段 | 加新工具自动获审查 |
| 记忆软混合 | 不硬过滤 | 不因领域不匹配漏记忆 |
| 会话增量保存 | delta + 全量合并 | IO 减少 10x |
| 零运行时依赖 | 纯标准库 | 即装即用 |
