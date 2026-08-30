# 易购商城测试

易购商城（Yigou Mall）的自动化测试仓库，包含**接口测试**与 **UI 测试**，并支持 Allure 测试报告。

## 技术栈

- Python 3.11 + pytest
- requests —— 接口自动化测试
- Selenium + Edge —— UI 自动化测试
- allure-pytest —— Allure 测试报告
- pytest-html —— 单文件 HTML 报告（双击即开）

## 目录结构

```text
易购商城测试/
├── tests/
│   ├── conftest.py          # 全局 fixture、命令行参数、接口客户端
│   ├── config.py            # 环境配置（地址、账号、测试商品）
│   ├── pytest.ini           # pytest 标记配置
│   ├── api/                 # 接口测试
│   │   ├── test_auth.py         # 用户认证
│   │   ├── test_products.py     # 商品
│   │   ├── test_cart.py         # 购物车
│   │   ├── test_orders.py       # 订单
│   │   ├── test_after_sale.py   # 售后
│   │   ├── test_knowledge.py    # 知识库
│   │   └── test_ai.py           # AI 导购
│   └── ui/                  # UI 测试（Selenium）
│       ├── conftest.py          # Edge 驱动、click fixture、失败截图
│       ├── test_login.py        # 登录
│       ├── test_products.py     # 搜索 / 分类筛选
│       ├── test_cart.py         # 加购 / 减购 / 全选 / 删除
│       └── test_ai.py           # AI 问答
├── run_tests.ps1            # 一键跑测试 + 生成报告
├── export_report.py         # 把 allure 结果导出为自包含 index.html
├── 查看报告.bat             # 双击打开完整 Allure 报告
└── requirements.txt         # Python 依赖
```

## 文档

| 文档 | 说明 |
| --- | --- |
| [docs/功能测试用例.md](docs/功能测试用例.md) | 功能测试用例（登录/商品/购物车/订单/售后/AI/卖家/管理） |
| [docs/接口文档.md](docs/接口文档.md) | 接口文档（请求参数、响应结构、枚举约定） |
| [docs/接口测试用例.md](docs/接口测试用例.md) | 接口测试用例（含异常参数与缺陷用例） |

## 前置条件

1. 后端已启动：`http://localhost:8080`（MySQL 已按 `sql/init.sql` 初始化）
2. 前端已启动：`http://localhost:5173`（仅 UI 测试需要）
3. UI 测试需本机安装 **Edge 浏览器**（驱动由 Selenium Manager 自动下载）
4. 生成 Allure 报告需安装 [Allure CLI](https://github.com/allure-framework/allure2/releases) 并加入 PATH（`allure --version` 可执行）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行测试

```bash
# 接口测试
python -m pytest tests/api -m api

# UI 测试（弹出 Edge 浏览器，可见页面变化）
python -m pytest tests/ui -m ui

# UI 测试（放慢节奏，每步停 1 秒，便于观察）
python -m pytest tests/ui -m ui --slow

# UI 测试（无头模式，后台运行）
python -m pytest tests/ui -m ui --headless

# 全部测试
python -m pytest tests
```

可选参数：

| 参数 | 说明 |
| --- | --- |
| `--api-url` | 接口基础地址，默认 `http://localhost:8080/api` |
| `--web-url` | 前端地址，默认 `http://localhost:5173` |
| `--slow` | 有界面并放慢操作（每步停 1 秒） |
| `--headless` | 无界面后台运行（不弹浏览器） |

## 生成测试报告

一键运行（跑测试 → 生成 Allure 报告 + 单文件报告）：

```powershell
.\run_tests.ps1            # 默认跑接口测试
.\run_tests.ps1 -Target ui # 跑 UI 测试
.\run_tests.ps1 -Target all
```

或手动：

```bash
# 收集结果
python -m pytest tests/api -m api --alluredir=allure-results --clean-alluredir

# 生成报告
allure generate allure-results -o allure-report --clean

# 打开报告（Allure 报告必须用服务打开，不能双击 index.html）
allure open allure-report
```

## 报告查看方式

| 文件 | 打开方式 |
| --- | --- |
| `report.html` | 双击直接打开（pytest-html 单文件，自包含） |
| `allure-report/index.html` | 双击直接打开（export_report.py 导出的自包含版本） |
| 完整 Allure 报告（图表/趋势） | 双击 `查看报告.bat`，或 `allure open allure-report` |

> 注意：完整的 Allure `index.html` 本质是 JS 单页应用，必须通过 HTTP 服务加载，直接双击会空白。如需双击即开，请使用 `report.html` 或 `export_report.py` 导出的自包含版本。

## 测试覆盖

| 模块 | 接口测试 | UI 测试 |
| --- | --- | --- |
| 用户认证 | 登录成功/密码错误/演示账号 | 登录成功跳转/密码错误提示 |
| 商品 | 列表/搜索/分类/详情/CRUD | 关键词搜索/分类筛选 |
| 购物车 | 增删改查/清空/勾选/全选 | 加购/减购/全选/删除 |
| 订单 | 列表/详情/下单/状态/分析 | — |
| 售后 | 申请/处理/申诉/分析 | — |
| 知识库 | 列表/搜索/CRUD | — |
| AI 导购 | 导购/售后/历史/流式 | AI 问答 |

## 已知缺陷（用例以 `xfail` 标记，期望失败）

1. 购物车数量未校验：`quantity<=0` 仍被接受
2. 空购物车下单会生成金额为 0 的空订单
3. 缺少防重复提交：连续两次下单会生成两条订单
