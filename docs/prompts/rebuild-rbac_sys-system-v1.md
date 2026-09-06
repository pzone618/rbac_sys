# rbac_sys：RBAC Phase 1 完整基础系统重建提示词 v1.17

> 本文件由 `docs/prompts/rebuild-rbac-system-v1.md` 实例化；第 1 节唯一输入块已填写，不重复询问已有参数，不擅自改名或改端口。

### v1.17 变更记录

- 测试服务及专用资源仅在测试 Compose 文件声明，消除生产合并配置夹带测试服务的矛盾。
- 区分生产内部服务与禁止公开的端口，补齐后端测试依赖、迁移、初始化及清理入口。
- 明确模板独立使用边界，实例运行资料不作为模板提交或重新生成的前置依赖。

### v1.16 变更记录

- 将宿主机 CA 信任列为首次开发启动的必需步骤，区分签发证书、安装信任和浏览器验证。
- 补齐跨平台安装/撤销、CA 身份核对及 Certificate Error 排障，增加未信任与轮换验收。

### v1.15 变更记录

- 固定各场景服务白名单、用途、数量与生命周期；开发默认 7 个服务，测试与调试按需启动。
- 明确 Compose 分组、临时任务、测试隔离和生产服务边界，禁止通过改名或反复试建规避冲突。
- 增加拓扑清单、重复启动和失败恢复验收；修正默认启动命令及 maintenance 描述。

### v1.14 变更记录

- 修正备份目录/文件权限与秘密传递示例；Compose 验证默认静默，只保留脱敏摘要。
- 将 E2E 明确为独立测试服务、数据、限流和 fixture，不依赖开发管理员初始密码。
- 补齐真实 provider 健康探针、上游容器重建、数据库故障恢复和证书重复初始化验收。
- 明确代理信任来源与 Uvicorn hostname 边界；统一根 workspace 命令和 smoke URL 语义。
- 增加实施状态/验证证据矩阵，区分已实现与实际通过；不降低完整 Phase 1 完成条件。

### v1.13 变更记录

- 明确特权账户保护与角色授予边界，禁止通过用户创建、改密或角色管理间接提权。
- 统一改密后全部退出，定义稳定 session family、即时撤销及多标签页刷新协调。
- 补齐 E2E 容器网络与 Chromium/Firefox CA 验证，修正 Quadlet 开机启动命令。
- 区分重复启动与外部端口冲突，明确模板输入、实例展开和扫描器边界，增加对应验收用例。

### v1.12 变更记录

- 将 RedisInsight 完整纳入开发 Compose、端口、持久卷、健康检查、README 和验收契约；宿主机登记端口数量由八个修正为九个。
- 增加 `.gitignore`、`.containerignore`、秘密扫描和 build-context 自动验收要求。
- 明确 README 只能记录连接方法、账户名和凭据来源，不得写入真实密码；补充 uv、npm 与 Podman 的环境职责矩阵。
- 固定所有 Compose 命令显式使用同一个 `.env`，增加实际 provider 的最小构建兼容测试。
- 增加版本严格匹配且预装浏览器的 Playwright E2E 容器契约，并明确单机生产的 Podman/Quadlet 生命周期。

> 将本文件全文交给编码 Agent 执行。本阶段只建设认证、RBAC、会话和安全审计底座，不实现任何学习业务。交付物必须可运行、可迁移、可测试、可部署；禁止只生成脚手架、伪代码或静态页面。

## 1. 执行原则

你是一名资深全栈架构师、安全工程师、数据库工程师和 UI 设计师。直接在当前 monorepo 中实现本提示词，不要擅自扩大范围。

开始编码前必须使用 Context7 核对当前稳定版的 React、React Router、TanStack Query、FastAPI、Pydantic v2、SQLAlchemy 2.x asyncio、Alembic、asyncpg、PyJWT、pwdlib、Redis 和 Playwright 用法。若 Context7 不可用，必须明确记录并改查官方文档，不得假称已查询。

发生歧义时按以下优先级处理：

1. 本文件中的表结构、API 契约和测试用例。
2. 安全性与数据不丢失。
3. 当前仓库中仍适用于 RBAC 的行为。
4. 框架官方最佳实践。

不得自行增加业务模块，也不得以“以后可能需要”为理由实现一套庞大平台。

本次重建使用由本节模板参数派生的全新数据库和全新 Alembic baseline。旧数据库、旧 migration 和 `storage/` 仅作为只读参考，禁止 drop、truncate 或原地改造成新 schema。只迁移既有用户、角色和权限时，先生成可审计的数据映射与 dry-run 报告，再由用户单独授权执行；Phase 1 的完成不依赖旧业务数据迁移。

### 模板输入、项目标识与同机隔离契约

本文件是可重复使用的工程生成模板。使用通用模板时调用者必须提供完整输入块；使用已实例化文件时直接读取其唯一 `template_inputs` 块，不重复索取已提供的值。缺少必填值、格式非法或与同机已登记工程冲突时，在写业务文件前一次性列出问题，不得猜测或静默改值。模板源文件不是运行时输入；占位符扫描只允许按精确路径排除 `docs/prompts/rebuild-rbac-system-v1.md`，不得排除实例文件或整个目录。实例化只替换参数值，保留参数名称、配置变量与派生规则。

| 输入 | 必填 | 格式与用途 |
|---|---:|---|
| `PROJECT_DISPLAY_NAME` | 是 | 面向用户的产品名称；1–80 个可显示 Unicode 字符 |
| `PROJECT_SLUG` | 是 | 全局资源 namespace；`^[a-z0-9][a-z0-9-]{1,38}[a-z0-9]$`，同机唯一 |
| `PROJECT_DB_PREFIX` | 是 | PostgreSQL/identifier 安全前缀；`^[a-z][a-z0-9_]{1,39}$`，通常由 slug 的 `-` 转 `_` 后显式确认 |
| `CONTAINER_REGISTRY` | 是 | 镜像 registry/namespace，不含尾随 `/` |
| `DEV_HOSTNAME` | 是 | 本地证书 SAN、浏览器 URL、CORS/CSRF/E2E 共用 hostname；不得含 scheme/port/path |
| `WEB_DEV_TLS_HOST_PORT` 等端口输入 | 是 | 见第 15 节；每个值在 30000–39999 内且同机唯一 |

通用模板填写以下完整输入块，不能只提供显示名；实例文件仅保留这一处已填写的输入块，文件标题不是第二个配置来源：

```yaml
template_inputs:
  project_display_name: "rbac_sys"
  project_slug: "rbac-sys"
  project_db_prefix: "rbac_sys"
  container_registry: "localhost/rbac-sys"
  dev_hostname: "rbac-sys.localhost"
  ports:
    web_dev_tls: 31443
    web_redirect: 31080
    web_tls: 31444
    postgres: 35432
    postgres_test: 35433
    redis: 36379
    mailpit_smtp: 31025
    mailpit_ui: 38025
    redisinsight: 35540
```

派生值只有一套权威规则，执行时写入 `docs/project-identity.md`，不得在不同文件自行拼接：

```text
COMPOSE_PROJECT_NAME = rbac-sys
DEV_DATABASE_NAME    = rbac_sys_dev
TEST_DATABASE_NAME   = rbac_sys_test
DATABASE_OWNER       = rbac_sys_app
RESOURCE_PREFIX      = rbac-sys-
REDIS_KEY_PREFIX     = rbac-sys:
COOKIE_NAME_PREFIX   = rbac_sys_
REFRESH_COOKIE_NAME  = rbac_sys_refresh
CSRF_COOKIE_NAME     = rbac_sys_csrf
BROWSER_KEY_PREFIX   = rbac-sys:
IMAGE_PREFIX         = localhost/rbac-sys/rbac-sys-
BACKUP_EXTENSION     = .rbac-sys.backup
DEV_PUBLIC_ORIGIN    = https://rbac-sys.localhost:31443
```

- 根目录 `.env.example` 必须声明所有上述输入/派生变量；实际 `.env` 是每个生成工程在 development/test 的唯一配置入口且不入 Git。staging/production 只允许从受控部署配置与 secret manager/Podman secret 注入同一 typed Settings 所需值，不得把生产秘密保存为仓库或服务器工作目录中的 `.env`。`compose.yml` 顶层使用 `name: ${COMPOSE_PROJECT_NAME:?COMPOSE_PROJECT_NAME is required}`，资源引用使用 `${VARIABLE:?message}`，禁止把本次实例的名称或端口复制成 YAML/string literal。
- Context7/Compose 官方规则确认 project name 优先级为命令行 `-p`、`COMPOSE_PROJECT_NAME`、顶层 `name`、目录名。启动脚本和 CI 必须使用 `podman compose config`（默认 `config --quiet`；需要最终插值时在进程内读取 `config`/`config --environment`，只输出 allowlist 脱敏摘要，禁止原文进入终端、CI artifact 或 diagnostics）验证最终插值值，并拒绝 `-p`/shell/`--env-file` 把 project name 覆盖为非 `rbac-sys` 的值。
- Compose 禁止设置固定 `container_name`；network、volume、container、image、database、object-storage bucket/path 和日志标签全部读取已验证的派生变量，不能与同机其他工程共享。
- Cookie 即使端口不同也可能互相覆盖，因此 Cookie 名必须来自派生变量；不得使用通用 `refresh_token`、`csrf_token`。localStorage/sessionStorage key 同样必须读取 `BROWSER_KEY_PREFIX`，不能在 TypeScript 中重复拼 slug。
- 应用启动时校验 slug、数据库名、Redis prefix、Cookie 名、public origin 和端口非空、格式正确、彼此一致；生产错误 fail fast。生成 `scripts/check_template_values.py`，扫描受控源码/配置/项目文档，除通用模板源文件 `docs/prompts/rebuild-rbac-system-v1.md` 的精确路径外，若发现未解析模板参数、未登记 literal host port 或运行配置资源名绕过集中配置，CI 失败。模板参数检测使用明确参数名集合，不把合法 GitHub Actions/Jinja 表达式误判为占位符；身份输入块、派生说明、端口注册表和 `.env.example` 中与权威输入相符的值合法，错误示例词通过显式规则检查，不能禁止当前工程名称出现在全部文档中。
- 后端只通过一个 typed Settings 模块读取环境变量，domain/use-case 不直接访问 `os.environ`；前端只通过一个经过 Zod 校验的 public runtime/build config 模块读取 `PROJECT_DISPLAY_NAME`、`BROWSER_KEY_PREFIX`、public origin 等非秘密值，组件不得直接访问散落的 `import.meta.env`。Nginx、Compose、maintenance、脚本和测试分别只有一个 config adapter，所有文档命令引用变量而非复制实际值；秘密绝不进入前端 public config。
- “禁止硬编码”针对工程身份、资源 namespace、hostname、origin、宿主机端口、外部 URL、路径和环境差异；权限码、状态机、数据库约束、安全上限和协议版本等明确写入本契约的领域常量仍应由代码集中定义并测试，不能为了形式上的可配置而变成任意字符串。

## 2. 固定技术栈

以下主版本是约束，不得擅自替换框架。直接依赖在 manifest 中使用兼容范围，`uv.lock`/`package-lock.json` 锁定完整传递依赖；容器镜像在生产配置中锁定 digest。

- Python 3.12.x；仓库提交 `.python-version`。
- uv：使用实现当日经官方文档确认的稳定版，仓库记录到 `docs/toolchain.md`；CI 使用 `uv lock --check` 与 `uv sync --locked`，禁止手改 `uv.lock`。
- 前端：Node.js 24 LTS、npm 11.x、React 19.x、TypeScript 6.x strict、Vite 8.x、React Router 7.x、TanStack Query 5.x、Tailwind CSS 4.x。
- 前端表单与校验：React Hook Form 7.x + Zod 4.x；基础交互使用 Radix UI primitives，图标只使用 Lucide React；禁止再引入第二套组件库或图标库。
- 前端测试：Vitest + React Testing Library + MSW 2.x；浏览器和黑盒 E2E 使用 Playwright Test。不得用 Enzyme、Cypress 或 Jest 建立第二套测试栈。
- Playwright 的 npm package、lockfile 与 E2E 容器镜像版本必须严格相同；镜像使用实现当日核对的 `mcr.microsoft.com/playwright:v<exact-version>-noble@sha256:<digest>`，禁止 `latest`。浏览器及系统依赖在镜像构建/CI 准备阶段安装，应用容器启动时不得运行 `playwright install` 或访问公网。提供独立 `e2e` service/profile，按第 14 节共享 web-test 网络命名空间、只读挂载测试 CA、不得发布宿主机端口；Linux Chromium 按官方建议提供足够共享内存（优先 `ipc: host`，受限环境使用经压测的 `shm_size`），CI 至少真实运行 Chromium 和 Firefox。若 package 与镜像版本不一致或浏览器 executable 缺失，测试必须在准备阶段失败并给出修复命令。
- API 类型：`openapi-typescript` + `openapi-fetch` 生成/消费契约；生成文件只输出到 `packages/api-client`，禁止手改。
- 后端：FastAPI `>=0.115,<1`、Pydantic `>=2,<3`、SQLAlchemy `>=2,<3` asyncio、Alembic `>=1.13,<2`、asyncpg。
- 后端基础依赖限定为 redis-py asyncio、HTTPX、PyJWT、pwdlib[argon2]、email-validator、`cryptography`（仅用于 Ed25519 备份签名/验证）；Phase 1 禁止引入 Celery、RQ、Kafka、RabbitMQ 或另一套 ORM。
- 迁移：Alembic；禁止在应用启动时调用 `create_all()`。
- 数据库：PostgreSQL 16.x 的最新安全 minor；不自动跨 major 升级。
- Redis：Redis Open Source 8.2.x，用于限流、短期权限缓存和跨副本协调；Redis 故障不能导致权限错误放行。
- RedisInsight：仅允许用于 development 环境，Compose 使用 `debug` profile，使用官方 `redis/redisinsight` 镜像并锁定实现当日稳定 tag 与 digest，容器端口固定 5540，命名 volume 只挂载 `/data`，健康检查调用 `/api/health/`。它与 Redis 加入同一个内部网络，README 使用 service host `redis:6379` 说明首次连接；宿主机 UI 只能通过 `${DEV_BIND_ADDRESS}:${REDISINSIGHT_HOST_PORT}:5540` 访问。production/staging 禁止启用、发布或携带 RedisInsight 数据卷。
- 密码：Argon2id，固定使用 `pwdlib[argon2]`；Context7 若无法解析 pwdlib，不得卡住实施或改用不相关库，直接查阅 pwdlib 官方文档/官方源码与发布元数据，把链接、版本和关键 API 记录到 `docs/toolchain.md` 后继续。
- Token：PyJWT；access JWT + rotation refresh session。
- 测试：Pytest 8.x + AnyIO pytest plugin（统一使用 `@pytest.mark.anyio`，不再并装 pytest-asyncio）、HTTPX AsyncClient、前端组件测试、Playwright Test、OpenAPI schema/coverage 检查。
- 容器：Podman 5.7+、`podman compose`；必须检测并记录实际 compose provider/version，不能假设所有机器使用同一个外部 provider。
- 入口与静态资源：本地/单机生产使用 Nginx；云环境允许由云 Load Balancer/Ingress/CDN 替代部分职责。
- 本地开发 CA：mkcert，使用实现当日官方发布的稳定版并把版本记录到 `docs/toolchain.md`；只负责开发证书，不进入生产镜像或生产证书流程。禁止用 Vite basic-ssl 的临时自签名证书替代受信本地 CA。
- 日志管道：应用/Nginx 只输出结构化 stdout/stderr；单机部署固定使用实现当日稳定版的 OpenTelemetry Collector Contrib 镜像并锁定 digest，云部署可使用等价托管 agent，负责采集、allowlist/redaction、batch、retry、持久化有界队列和集中导出。应用业务代码不得绑定某个日志厂商 SDK，实际版本记录到 `docs/toolchain.md`。

若某个固定组合在实现时被官方标记为不兼容或 EOL，必须先给出 Context7/官方资料证据和最小升级建议，不得静默换栈。升级依赖必须显式执行并提交 lockfile diff；CI 和容器构建只消费锁文件，不自动升级。

## 3. Phase 1 范围

### 必须实现

- 自助注册、邮箱验证、重发验证邮件、管理员审批/拒绝注册、注册状态展示。
- 管理员登录、普通用户登录、刷新 token、当前用户、退出当前会话、退出全部会话。
- 忘记密码、一次性密码重置、登录后修改密码、管理员强制重置密码、首次登录强制改密。
- 用户 CRUD 的安全子集：创建、查询、修改资料、启用/停用、分配角色、管理员重置密码。
- 角色 CRUD、权限目录只读、角色权限分配。
- 多角色权限取并集、后端权限校验、对象级“本人”规则。
- 当前用户查看自己的会话、撤销自己的会话、修改自己的密码、查看自己的登录历史。
- 管理员查看和筛选全部会话、登录历史、操作历史。
- 管理员创建、下载、导入、校验和删除完整数据库逻辑备份；super-admin 可从受信任备份恢复到新数据库并验证。
- 独立的普通用户账户区和 Administrator 管理控制台。
- Alembic、幂等 seed、OpenAPI、结构化日志、request id、健康检查。
- 后端/Nginx 集中日志、受控前端错误遥测、敏感字段双层脱敏、生产日志 UTC 日次归档/保留/恢复演练。
- 完整自动化测试以及单机容器部署配置。

### 明确不实现

- 课程、科目、报名、学习、进度、听力、拼写、IELTS、词典、文件库、协同编辑。
- LLM、端侧模型、远程模型、TTS、PDF、Vocab 生成和任务队列的具体业务实现。
- 第三方登录、MFA、组织/多租户。
- Kubernetes、服务网格、微服务和微前端。

上述非 RBAC 功能只允许写一份未来接入 ADR，不允许在 Phase 1 创建空页面、空表或假 API。数据库备份/恢复所需的 maintenance worker 是本阶段唯一允许的后台任务进程，不得借机实现通用业务队列。

## 4. Monorepo 与代码边界

保留务实的 polyglot monorepo：

```text
rbac-sys/
  .gitignore
  .containerignore
  .env.example
  pyproject.toml
  uv.lock
  package.json
  package-lock.json
  frontend/                  # React SPA
  backend/                   # FastAPI API
  packages/
    api-client/              # 根据 OpenAPI 自动生成的 TS client/types
  deploy/
    compose.yml
    compose.dev.yml
    compose.test.yml
    compose.prod.yml
    quadlet/                  # Linux 单机生产 systemd/Quadlet units 与 drift test 输入
    nginx/
    otel-collector/           # 日志采集、脱敏、批处理、持久化队列和导出配置
  docs/
    adr/
    observability/
    runbooks/
  scripts/
  storage/                   # 既有运行数据，本阶段禁止改动
  Makefile
  README.md
```

规则：

- 本契约采用根 workspace：根目录提交 `pyproject.toml`、唯一 `uv.lock`、`package.json` 和唯一 `package-lock.json`；npm workspaces 包含 `frontend` 与 `packages/api-client`。Python 源码仍位于 `backend/app`，测试/类型检查通过根配置定位。所有固定命令从仓库根目录执行，不在子目录创建第二套 lockfile。
- 前端不能 import Python 源码，后端不能读取前端源码；共享契约只能来自 OpenAPI 生成物。
- API schema 改变但 `packages/api-client` 未更新时 CI 必须失败。
- 根命令至少包含 `make dev/test/lint/typecheck/build/migrate/seed/ci`，CI 调用相同底层命令。
- `storage/` 不参与源码扫描、容器 build context 或前端打包。
- 禁止创建包含任意业务逻辑的全局 `shared` 垃圾目录。

### 后端分层

```text
backend/app/
  main.py
  core/                      # config、security primitives、errors、logging
  db/                        # engine、session、base、transaction helpers
  shared/                    # pagination、request id 等无业务语义能力
  modules/
    auth/
    identity/                # users、roles、permissions
    sessions/
    audit/                   # login_history、action_history、retention
    backup/                  # backup metadata、archive validation、restore orchestration
  middleware/
  seed/
backend/alembic/
backend/tests/
  unit/
  integration/
  contract/
  concurrency/
backend/app/workers/
  maintenance.py            # 只处理备份、恢复和保留期任务
```

每个业务模块内部按需要放置 `router.py`、`schemas.py`、`service.py`、`repository.py`、`models.py`。依赖方向固定如下：

- Router：HTTP 解析、响应和依赖注入；禁止复杂 SQL、业务判断和自行 commit。
- Service：use case、领域不变量、事务边界；禁止依赖 FastAPI Request/Response。
- Repository：查询和持久化；禁止权限决策和 HTTP exception。
- ORM model 与 Pydantic schema 分离。
- 入口依赖检查 permission；service/repository 强制数据范围和本人规则。
- Middleware 只做 request id、访问日志和上下文，不通过“记录全部请求”代替业务审计。

### 前端分层

```text
frontend/src/
  app/                       # providers、router、route metadata
  layouts/                   # PublicLayout、AccountLayout、AdminLayout
  features/
    auth/
    account/
    users/
    roles/
    sessions/
    login-history/
    action-history/
  components/ui/             # 无业务含义的基础组件
  components/common/
  services/api/
  lib/
  styles/
```

- Feature 内部可包含 page、component、query、mutation、schema 和 test；其他 feature 只能从其公开入口引用。
- TanStack Query 管理服务器状态；不得复制到全局 store。
- `components/ui` 不读取权限，也不调用业务 API。
- 路由、导航、面包屑和权限要求来自唯一 `routeConfig`。

## 5. PostgreSQL 权威表结构

以下结构是实现契约。Alembic migration 必须表达等价表、约束、外键和索引；ORM 名称、类型与约束必须一致。所有时间使用 `TIMESTAMPTZ` 和 UTC。UUID 由应用生成 UUIDv4，测试不得依赖自增顺序。

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(64) NOT NULL,
    username_normalized VARCHAR(64) NOT NULL,
    email VARCHAR(320) NOT NULL,
    email_normalized VARCHAR(320) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    status VARCHAR(24) NOT NULL DEFAULT 'pending_verification',
    must_change_password BOOLEAN NOT NULL DEFAULT false,
    email_verified_at TIMESTAMPTZ,
    approved_at TIMESTAMPTZ,
    approved_by UUID REFERENCES users(id) ON DELETE SET NULL,
    auth_version INTEGER NOT NULL DEFAULT 1,
    row_version INTEGER NOT NULL DEFAULT 1,
    failed_login_count INTEGER NOT NULL DEFAULT 0,
    locked_until TIMESTAMPTZ,
    last_login_at TIMESTAMPTZ,
    password_changed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    deleted_at TIMESTAMPTZ,
    CONSTRAINT uq_users_username_normalized UNIQUE (username_normalized),
    CONSTRAINT uq_users_email_normalized UNIQUE (email_normalized),
    CONSTRAINT ck_users_status CHECK (status IN (
      'pending_verification','pending_approval','active','suspended','rejected','deleted'
    )),
    CONSTRAINT ck_users_auth_version CHECK (auth_version >= 1),
    CONSTRAINT ck_users_row_version CHECK (row_version >= 1),
    CONSTRAINT ck_users_failed_login_count CHECK (failed_login_count >= 0)
);

CREATE INDEX ix_users_status_created_at ON users (status, created_at DESC);
CREATE INDEX ix_users_last_login_at ON users (last_login_at DESC);

CREATE TABLE user_profiles (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    display_name VARCHAR(120),
    row_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_user_profiles_row_version CHECK (row_version >= 1)
);

CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    theme_mode VARCHAR(16) NOT NULL DEFAULT 'system',
    theme_palette VARCHAR(24) NOT NULL DEFAULT 'default',
    contrast_mode VARCHAR(16) NOT NULL DEFAULT 'system',
    density VARCHAR(16) NOT NULL DEFAULT 'comfortable',
    motion_mode VARCHAR(16) NOT NULL DEFAULT 'system',
    time_zone VARCHAR(64) NOT NULL DEFAULT 'UTC',
    page_size INTEGER NOT NULL DEFAULT 20,
    row_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_user_preferences_theme CHECK (theme_mode IN ('system','light','dark')),
    CONSTRAINT ck_user_preferences_palette CHECK (theme_palette IN ('default','eye_care','sepia','forest')),
    CONSTRAINT ck_user_preferences_contrast CHECK (contrast_mode IN ('system','standard','high')),
    CONSTRAINT ck_user_preferences_density CHECK (density IN ('comfortable','compact')),
    CONSTRAINT ck_user_preferences_motion CHECK (motion_mode IN ('system','reduced')),
    CONSTRAINT ck_user_preferences_page_size CHECK (page_size IN (20,50,100)),
    CONSTRAINT ck_user_preferences_row_version CHECK (row_version >= 1)
);

CREATE TABLE roles (
    id UUID PRIMARY KEY,
    code VARCHAR(80) NOT NULL,
    name VARCHAR(120) NOT NULL,
    description VARCHAR(500),
    is_system BOOLEAN NOT NULL DEFAULT false,
    is_active BOOLEAN NOT NULL DEFAULT true,
    row_version INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_roles_code UNIQUE (code),
    CONSTRAINT ck_roles_code CHECK (code ~ '^[a-z][a-z0-9_]{1,79}$'),
    CONSTRAINT ck_roles_row_version CHECK (row_version >= 1)
);

CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    code VARCHAR(120) NOT NULL,
    resource VARCHAR(80) NOT NULL,
    action VARCHAR(40) NOT NULL,
    category VARCHAR(80) NOT NULL,
    description VARCHAR(500) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_permissions_code UNIQUE (code),
    CONSTRAINT uq_permissions_resource_action UNIQUE (resource, action),
    CONSTRAINT ck_permissions_code CHECK (code ~ '^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$')
);

CREATE TABLE user_roles (
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    assigned_by UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, role_id)
);

CREATE INDEX ix_user_roles_role_id ON user_roles (role_id);

CREATE TABLE role_permissions (
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID NOT NULL REFERENCES permissions(id) ON DELETE RESTRICT,
    granted_by UUID REFERENCES users(id) ON DELETE SET NULL,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (role_id, permission_id)
);

CREATE INDEX ix_role_permissions_permission_id ON role_permissions (permission_id);

CREATE TABLE refresh_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    family_id UUID NOT NULL,
    parent_session_id UUID REFERENCES refresh_sessions(id) ON DELETE SET NULL,
    replaced_by_session_id UUID REFERENCES refresh_sessions(id) ON DELETE SET NULL,
    token_hash CHAR(64) NOT NULL,
    csrf_token_hash CHAR(64) NOT NULL,
    auth_version_at_issue INTEGER NOT NULL,
    ip_address INET,
    user_agent VARCHAR(1000),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    last_used_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ NOT NULL,
    used_at TIMESTAMPTZ,
    revoked_at TIMESTAMPTZ,
    revoke_reason VARCHAR(80),
    CONSTRAINT uq_refresh_sessions_token_hash UNIQUE (token_hash),
    CONSTRAINT ck_refresh_sessions_expiry CHECK (expires_at > created_at)
);

CREATE INDEX ix_refresh_sessions_user_active
    ON refresh_sessions (user_id, expires_at DESC)
    WHERE revoked_at IS NULL;
CREATE INDEX ix_refresh_sessions_family_id ON refresh_sessions (family_id);

CREATE TABLE one_time_tokens (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    purpose VARCHAR(32) NOT NULL,
    token_hash CHAR(64) NOT NULL,
    requested_ip INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    consumed_at TIMESTAMPTZ,
    invalidated_at TIMESTAMPTZ,
    CONSTRAINT uq_one_time_tokens_token_hash UNIQUE (token_hash),
    CONSTRAINT ck_one_time_tokens_purpose CHECK (purpose IN ('email_verification','password_reset','registration_status')),
    CONSTRAINT ck_one_time_tokens_user_required CHECK (
      user_id IS NOT NULL OR purpose = 'registration_status'
    ),
    CONSTRAINT ck_one_time_tokens_expiry CHECK (expires_at > created_at)
);

CREATE INDEX ix_one_time_tokens_user_purpose_created
    ON one_time_tokens (user_id, purpose, created_at DESC);
CREATE INDEX ix_one_time_tokens_expires_at ON one_time_tokens (expires_at);

CREATE TABLE email_change_requests (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    new_email VARCHAR(320) NOT NULL,
    new_email_normalized VARCHAR(320) NOT NULL,
    token_hash CHAR(64) NOT NULL,
    requested_ip INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    consumed_at TIMESTAMPTZ,
    invalidated_at TIMESTAMPTZ,
    CONSTRAINT uq_email_change_requests_token_hash UNIQUE (token_hash),
    CONSTRAINT ck_email_change_requests_expiry CHECK (expires_at > created_at)
);

CREATE INDEX ix_email_change_requests_user_created
    ON email_change_requests (user_id, created_at DESC);
CREATE INDEX ix_email_change_requests_expires_at ON email_change_requests (expires_at);

CREATE TABLE password_history (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX ix_password_history_user_created
    ON password_history (user_id, created_at DESC);

CREATE TABLE login_history (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(40) NOT NULL,
    result VARCHAR(16) NOT NULL,
    failure_reason_code VARCHAR(80),
    identifier_masked VARCHAR(320),
    ip_address INET,
    user_agent VARCHAR(1000),
    device_summary VARCHAR(255),
    request_id UUID NOT NULL,
    session_id UUID REFERENCES refresh_sessions(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_login_history_event CHECK (event_type IN (
      'login_succeeded','login_failed','logout','refresh_succeeded',
      'refresh_failed','refresh_reuse_detected','registration_submitted',
      'email_verified','password_reset_requested','password_reset_completed',
      'password_changed'
    )),
    CONSTRAINT ck_login_history_result CHECK (result IN ('success','failure'))
);

CREATE INDEX ix_login_history_created_at ON login_history (created_at DESC);
CREATE INDEX ix_login_history_user_created ON login_history (user_id, created_at DESC);
CREATE INDEX ix_login_history_result_created ON login_history (result, created_at DESC);
CREATE INDEX ix_login_history_request_id ON login_history (request_id);
CREATE INDEX ix_login_history_ip_created ON login_history (ip_address, created_at DESC);

CREATE TABLE action_history (
    id UUID PRIMARY KEY,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    actor_type VARCHAR(16) NOT NULL,
    action VARCHAR(120) NOT NULL,
    target_type VARCHAR(80) NOT NULL,
    target_id VARCHAR(120),
    result VARCHAR(16) NOT NULL,
    http_method VARCHAR(10),
    path VARCHAR(500),
    status_code INTEGER,
    request_id UUID NOT NULL,
    ip_address INET,
    user_agent VARCHAR(1000),
    changes JSONB,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT ck_action_history_actor_type CHECK (actor_type IN ('user','system','worker')),
    CONSTRAINT ck_action_history_result CHECK (result IN ('success','failure')),
    CONSTRAINT ck_action_history_status CHECK (status_code IS NULL OR status_code BETWEEN 100 AND 599)
);

CREATE INDEX ix_action_history_created_at ON action_history (created_at DESC);
CREATE INDEX ix_action_history_actor_created ON action_history (actor_user_id, created_at DESC);
CREATE INDEX ix_action_history_action_created ON action_history (action, created_at DESC);
CREATE INDEX ix_action_history_target ON action_history (target_type, target_id, created_at DESC);
CREATE INDEX ix_action_history_request_id ON action_history (request_id);

CREATE TABLE idempotency_keys (
    id UUID PRIMARY KEY,
    actor_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    endpoint VARCHAR(200) NOT NULL,
    idempotency_key VARCHAR(128) NOT NULL,
    request_hash CHAR(64) NOT NULL,
    state VARCHAR(16) NOT NULL,
    response_status INTEGER,
    response_body JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    expires_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_idempotency_actor_endpoint_key UNIQUE
      (actor_user_id, endpoint, idempotency_key),
    CONSTRAINT ck_idempotency_state CHECK (state IN ('processing','completed','failed')),
    CONSTRAINT ck_idempotency_expiry CHECK (expires_at > created_at)
);

CREATE INDEX ix_idempotency_expires_at ON idempotency_keys (expires_at);

CREATE TABLE backup_artifacts (
    id UUID PRIMARY KEY,
    created_by UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    format VARCHAR(40) NOT NULL DEFAULT 'pg_dump_custom_v1',
    storage_key VARCHAR(1000),
    original_filename VARCHAR(255),
    source_database VARCHAR(120) NOT NULL,
    source_postgres_version VARCHAR(40) NOT NULL,
    application_version VARCHAR(80) NOT NULL,
    alembic_revision VARCHAR(80) NOT NULL,
    size_bytes BIGINT,
    sha256 CHAR(64),
    object_count INTEGER,
    encrypted BOOLEAN NOT NULL DEFAULT false,
    encryption_key_id VARCHAR(255),
    manifest JSONB,
    error_code VARCHAR(80),
    error_message VARCHAR(1000),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    retention_until TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_backup_artifacts_storage_key UNIQUE (storage_key),
    CONSTRAINT ck_backup_artifacts_status CHECK (status IN (
      'pending','running','validating','completed','failed','deleted'
    )),
    CONSTRAINT ck_backup_artifacts_size CHECK (size_bytes IS NULL OR size_bytes >= 0),
    CONSTRAINT ck_backup_artifacts_object_count CHECK (object_count IS NULL OR object_count >= 0)
);

CREATE INDEX ix_backup_artifacts_status_created
    ON backup_artifacts (status, created_at DESC);
CREATE INDEX ix_backup_artifacts_retention
    ON backup_artifacts (retention_until)
    WHERE status = 'completed';

CREATE TABLE restore_runs (
    id UUID PRIMARY KEY,
    backup_id UUID NOT NULL REFERENCES backup_artifacts(id) ON DELETE RESTRICT,
    requested_by UUID REFERENCES users(id) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    strategy VARCHAR(32) NOT NULL DEFAULT 'restore_to_new_database',
    target_database VARCHAR(120) NOT NULL,
    safety_backup_id UUID REFERENCES backup_artifacts(id) ON DELETE SET NULL,
    verification JSONB,
    error_code VARCHAR(80),
    error_message VARCHAR(1000),
    requested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    CONSTRAINT ck_restore_runs_status CHECK (status IN (
      'pending','running','verifying','ready_for_cutover','succeeded','failed','rolled_back'
    )),
    CONSTRAINT ck_restore_runs_strategy CHECK (strategy IN ('restore_to_new_database'))
);

CREATE INDEX ix_restore_runs_status_requested
    ON restore_runs (status, requested_at DESC);
CREATE INDEX ix_restore_runs_backup_id ON restore_runs (backup_id);
```

### 表结构行为约束

- username 使用 Unicode trim 后的明确规范化策略；登录时查询 `username_normalized`。email 至少 trim + lowercase。把规则写成单元测试。
- 自助注册创建 `pending_verification` 用户并分配系统 `user` 角色；验证邮箱后进入 `pending_approval`；管理员审批后才进入 `active`。拒绝进入 `rejected`，不能登录。
- 每个注册、管理员创建、seed 或导入的用户都必须在同一事务创建且仅创建一行 `user_profiles` 和 `user_preferences`；migration 为既有行回填默认值。`users` 只保存登录身份、安全状态和生命周期，`user_profiles` 保存可编辑展示资料，`user_preferences` 保存非安全性 UI/区域偏好，三者不能合并成无约束 JSONB。
- `time_zone` 必须是 Python `zoneinfo` 可解析的 IANA 时区名称；不得接受任意缩写。`theme_mode/theme_palette/contrast_mode/density/motion_mode/page_size` 必须在服务端校验，且每个字段在 Phase 1 UI 中真实生效；不得预埋没有行为的 language、notification 或 marketing preference。强制安全邮件（改密、邮箱变更、停用、角色/权限变化）不可由偏好关闭。
- 一次性 token 至少 256-bit 随机值，数据库只存 SHA-256 hash；同一用户同一 purpose 重新签发时使旧 token 失效。消费 token 必须使用行锁并保持一次性。
- `password_history` 保留最近 5 个历史 hash；改密、找回密码和管理员重置均禁止复用最近 5 个密码，并按保留策略删除更旧记录。
- 用户采用不可逆软删除：同一事务内设置 `status='deleted'`、`deleted_at`、递增 `auth_version`、撤销全部会话，并把 `username/username_normalized` 改为 `deleted_<user_uuid_hex>`，把 `email/email_normalized` 改为 `deleted+<user_uuid_hex>@invalid.local`，把 `user_profiles.display_name=NULL`、`user_preferences` 重置为默认值，并删除该用户全部 `email_change_requests`（其中含目标邮箱 PII）。上述 tombstone 值必须满足列长度、格式和唯一约束；原 username/email 不得出现在 action history diff 或日志中。
- 软删除完成后，原 username 和 email 必须可被新 UUID 的账户重新注册；deleted 用户永远不能 reactivate，恢复身份只能创建新账户。审计历史保留原 user_id 关联及当时已脱敏的展示信息，不恢复被匿名化的 PII。软删除与同标识并发注册依赖数据库唯一约束串行化，结果不得产生两个 active/pending 账户。
- `permissions` 只由代码目录和幂等 seed 管理，UI 只读。
- `user_roles`、`role_permissions` 使用 association object 映射，不同时提供冲突的可写 secondary relationship。
- `login_history` 与 `action_history` append-only；常规 API 不提供 update/delete。
- 用户本人和管理员对 display name 的修改、username 变更、email change 的发起/确认/失败必须写 action history；diff 只记录脱敏值。主题等个人偏好切换不写安全审计，避免每次切换污染 action history；其当前状态由 `updated_at/row_version` 追踪，运行日志只记录字段名集合而不记录值。
- `changes` 只保存 allowlist 字段的 before/after，禁止密码哈希、token、Cookie、密钥和请求正文。
- 普通 GET、健康检查和页面访问不写 `action_history`；HTTP access log、登录历史、操作历史三者分离。
- migration 为所有约束显式命名；复杂数据迁移和 schema 迁移分开。
- 备份文件不存入 PostgreSQL bytea；`backup_artifacts` 只存状态与元数据。开发环境文件写入专用只读/读写分离 volume，云环境写入私有 S3-compatible object storage。
- maintenance worker 使用 `SELECT ... FOR UPDATE SKIP LOCKED` 领取 pending backup/restore，使用 lease/heartbeat 或等效防重复机制；同一数据库同一时间最多一个 restore。

## 6. 固定权限与角色

权限清单必须由 seed 幂等创建：

```text
admin.access
users.read
users.create
users.update
users.activate
users.suspend
users.delete
users.approve
users.reject
users.reset_password
users.manage_roles
roles.read
roles.create
roles.update
roles.delete
roles.manage_permissions
permissions.read
sessions.read_own
sessions.revoke_own
sessions.read
sessions.revoke
login_history.read_own
login_history.read
login_history.export
action_history.read
action_history.export
system.backup
system.restore
```

固定系统角色：

- `super_admin`：全部权限，`is_system=true`。
- `administrator`：除系统角色破坏性管理外的日常管理权限，`is_system=true`。
- `user`：`sessions.read_own`、`sessions.revoke_own`、`login_history.read_own`，`is_system=true`。

`administrator` 的初始权限固定为：`admin.access`、`users.read/create/update/activate/suspend/approve/reject/reset_password/manage_roles`、`roles.read`、`permissions.read`、`sessions.read/revoke`、`login_history.read/export`、`action_history.read`、`system.backup`。它默认不能恢复数据库、删除用户、创建/修改/删除角色、修改角色权限或导出 action history；`system.restore` 等高风险权限只能由 super-admin 显式授予。

规则：

- 权限按多角色并集计算，默认拒绝；禁止根据 `role.name == "admin"` 放行。
- 始终至少存在一个 active 的 super-admin 用户。
- 特权身份判断基于不可修改的系统角色 `code=super_admin` 及数据库关联，不依赖显示名。非 active super-admin 调用者不得授予/撤销该角色，也不得通过管理员接口修改任何持有该角色的账户（包括非 active 账户）的资料、登录标识、密码、状态、角色或会话；统一返回 403 `PRIVILEGED_ACCOUNT_PROTECTED`。本人安全接口仍允许其修改自身密码/资料，最后管理员保护仍适用。
- 非 super-admin 为用户创建或替换角色时必须拥有 `users.manage_roles`，目标角色的有效权限必须是调用者当前有效权限的子集；创建/修改角色权限也遵守该子集规则，且禁止修改调用者自身持有角色的权限或启用状态。停用角色重新启用时检查其完整权限集合，防止通过先分配后启用绕过检查。只有 `users.create` 不能携带任意角色：无 `users.manage_roles` 时仅允许系统 `user` 角色。越界统一 403 `ROLE_GRANT_FORBIDDEN`。
- 上述判断与写入在同一事务校验数据库当前状态；角色权限、状态和成员变更必须遵循统一锁顺序，避免检查后并发变更绕过边界。super-admin 操作仍须具备 endpoint permission，且授予/撤销 super_admin、管理其他 super-admin 账户必须提交 `reauth_password` 进行本次密码验证（沿用认证限流），不能仅凭 UI 隐藏或长期 JWT 放行。
- 用户不能停用或删除自己，不能撤销自己的最后一个 super-admin 身份。
- 系统角色不能删除，code 不能修改。
- `super_admin` 的启用状态和权限集合是核心不变量：该角色不能被停用或重命名，并且在任意时刻必须恰好包含权限目录中的全部权限。通用 `PUT /admin/roles/{id}/permissions` 命中 `super_admin` 时固定返回 409 `SYSTEM_ROLE_PERMISSIONS_IMMUTABLE`，即使调用者拥有 `roles.manage_permissions` 也不能删减或手工改写。
- 幂等 permission seed 每次新增权限时，必须在同一事务内把该权限补到 `super_admin` 后再提交；删除权限前先处理全部引用。启动/ready check 和备份恢复验证都断言 `super_admin permissions == permission catalog`，不满足时 readiness 失败且报警。
- 权限目录不能由普通 CRUD 创建、修改或删除。
- 本项目权限码唯一规范是点号形式 `resource.action`，并由 `ck_permissions_code` 强制；这是新项目的有意约定，不兼容或自动转换旧项目的 `resource:action`。迁移旧授权时必须使用显式 mapping 并对未知 code fail closed，禁止同时支持两种分隔符。
- 角色/权限变化后，在同一数据库事务中递增所有受影响用户的 `auth_version`；事务提交后 best-effort 清理 Redis cache。
- Access JWT 带 `sub`、`jti`、`iss`、`aud`、`iat`、`exp`、`auth_version`、`sid`，其中 `sid=refresh_sessions.family_id`，rotation 不改变 sid。每次已认证请求从 PostgreSQL 验证用户状态、auth_version 和该 family 的当前有效后继（未使用、未撤销、未过期且版本匹配）；Redis 仅缓存权限集合，不能用过期缓存替代这些即时撤销检查。已经开始的请求不追溯取消，撤销提交后开始的请求必须拒绝。

## 7. 认证与并发正确性

### Token 存储

- Access JWT 有效期默认 10 分钟，仅存浏览器内存，不写 localStorage/sessionStorage。
- Refresh token 为至少 256-bit 随机值，只通过配置 `REFRESH_COOKIE_NAME`（派生值 `rbac_sys_refresh`）、属性为 `HttpOnly; Secure; SameSite=Lax; Path=/api/v1/auth` 的 Cookie 传输，数据库只存 SHA-256 hash。
- CSRF Cookie 固定 `Secure; SameSite=Lax; Path=/`，不设 Domain，供 SPA 读取；refresh Cookie 同样不设 Domain，清理时使用与签发一致的 Path。
- 登录同时设置配置 `CSRF_COOKIE_NAME`（派生值 `rbac_sys_csrf`）的非 HttpOnly CSRF Cookie；`refresh/logout` 必须校验精确 Origin/Referer allowlist 和 double-submit CSRF header，并与 session 中的 CSRF hash 比对。不得仅依赖 CORS。
- 生产和本地浏览器开发均使用 HTTPS，refresh Cookie 始终 `Secure=true`。只有不启动真实网络监听的后端 unit/integration test transport 可通过 test-only setting 构造 Cookie，任何 Compose、Playwright、smoke 或人工浏览器 profile 都不得关闭 Secure。
- 登录、刷新、修改密码、管理员重置密码、停用用户都生成 login/action history，且不泄露敏感字段。

### 注册、邮件与密码生命周期

- `SELF_REGISTRATION_ENABLED=true`、`REQUIRE_EMAIL_VERIFICATION=true`、`REQUIRE_ADMIN_APPROVAL=true` 为默认生产策略，均通过环境变量配置并在 `/health/ready` 的非敏感 capability 中体现。
- 自助注册对已存在和不存在的 username/email 返回不可枚举的通用结果；数据库唯一冲突（包括并发竞争）也必须转换为相同 202 响应。管理员创建用户 API 才返回稳定的 409 唯一冲突错误。
- `POST /auth/register` 无论创建新用户还是命中既有 username/email，都返回形状和时序策略一致的 `RegisterResponse`。其中 `status_token` 是至少 256-bit 的随机 opaque bearer token，原值只返回一次，数据库只存 SHA-256 hash，默认 7 天过期；它不是 access JWT，不放进 URL、日志、Cookie 或浏览器持久化存储。
- 新注册成功时创建关联该用户的 `purpose='registration_status'` token；命中既有账户时也创建 `user_id=NULL` 的 decoy status token。`GET /auth/registration-status` 只从 `X-Registration-Status-Token` header 读取 token：关联真实注册时返回有限状态，decoy 始终返回 `submitted`，无效/过期统一返回 410 `REGISTRATION_STATUS_EXPIRED`，不得通过该流程枚举既有账户。
- 定义 `MailSender` port；生产 adapter 使用配置的事务邮件服务或 SMTP，开发/测试使用 Mailpit/fake adapter。测试不得发送真实邮件。
- 验证与重置邮件只包含一次性原始 token 的链接；日志、数据库和 action history 不保存原始 token。发送失败时用户可通过 resend 重试，不能激活账户。
- 邮件验证 token 默认 24 小时，密码重置 token 默认 30 分钟；消费后立即失效。密码重置成功后递增 auth_version 并撤销全部 refresh sessions。
- maintenance retention job 定期删除已过期且超过审计保留窗口的 verification/reset/registration-status token 与 email-change request 行，包括 decoy status token；删除只按 expiry/purpose 批处理，不读取或导出敏感原值或目标邮箱。
- 密码策略固定为 12–128 Unicode 字符，允许空格和 password manager 生成值；禁止与规范化 username/email 相同，检查最近 5 个历史密码。不得强制“必须含大小写数字符号”式组合规则。
- 管理员创建用户时可设置角色并生成临时密码，用户标记 `must_change_password=true`；该用户登录后只能访问 `/me/change-password`、`/auth/logout` 和 `/auth/me`，完成改密前不能使用其他 API。
- 管理员审批、拒绝、激活、停用、角色授权和密码重置必须写 action history，并向用户发送不含敏感信息的通知；邮件失败不回滚已提交的安全状态，但必须记录可重试的运维错误。

### Profile、身份标识与偏好边界

- 用户可直接修改 `display_name`，但 username、email 属于登录身份而不是普通 Profile 字段，禁止由通用 PATCH 静默修改。Phase 1 不实现头像文件上传、bio、地址、生日等非 RBAC 必需 PII；头像统一由 display name/username 首字母生成，后续若引入对象存储必须另做 threat model、内容校验、配额、删除和备份契约。
- 本人修改 username 必须提交 current password 与旧 `row_version`；服务端重新认证、规范化并在事务中检查唯一约束，成功后递增 `auth_version/row_version`、撤销全部 refresh session、发送安全通知、写脱敏 action history，并要求重新登录。管理员修改 username 使用独立 endpoint、`users.update`、最近重新认证与相同行为，不能绕过唯一性、通知或会话撤销。
- 本人请求修改 email 必须提交 current password；服务端生成 256-bit opaque token，数据库只在 `email_change_requests` 保存 SHA-256 hash 和目标邮箱，默认 30 分钟过期，同一用户新请求使旧请求失效。新邮箱收到确认链接，旧邮箱收到不可取消的安全通知；请求响应固定 202，不能泄露目标邮箱是否已占用。
- 确认 email change 时锁定 request 与 user，校验未消费/未过期，并在提交前重新检查 `users.email_normalized` 唯一性；并发争用只能有一个成功。成功后更新 email、`email_verified_at=now()`、递增 `auth_version/row_version`、消费 token、撤销全部 session、通知新旧邮箱并要求重新登录。失败响应不可用于枚举现有邮箱。管理员只能发起同一验证流程，不能直接覆盖 email。
- username/email 变更按 user id 与受信 client IP 分布式限流；current password 连续失败沿用认证安全事件与告警规则，不能成为绕过 login 限流的离线猜密入口。确认接口按 token fingerprint/IP 限流，原始 token、完整新旧邮箱不进入日志、URL query 或 action diff。
- 管理员治理范围是账号状态、角色、权限、安全动作和审计；管理员可查看 Profile，但不得修改用户的主题、密度、动态效果、时区等个人偏好。若未来因合规需要强制外观/无障碍策略，必须新增显式 policy 优先级和审计，不能复用个人 preference 字段。
- Profile 与 Preferences PATCH 均使用各自 `row_version` 乐观并发；偏好更新是字段级部分更新，未知字段返回 422。客户端不得把其他账户的偏好写入 localStorage，也不得让最后写入者静默覆盖另一设备的新版本。

### 登录限流与账户临时锁定

这是两层独立机制，顺序和状态必须固定：

1. 先执行 Redis 分布式限流，按规范化 identifier + client IP 两个维度分别计数；默认任一维度 5 次/5 分钟后返回 429 与准确 `Retry-After`。只信任受信代理解析出的 client IP。Redis 故障时，login/register/resend/forgot/reset 等公共认证入口固定 fail closed 为 503 + `Retry-After` 并使 readiness degraded；不得绕过限流、临时查询日志计数或退化成单进程内存计数。已认证请求的权限缓存故障仍按 RBAC 规则回查 PostgreSQL。
2. 未被限流时执行固定成本的账户查找与 Argon2 验证；不存在账户也执行 dummy hash。真实 active 账户每次密码错误原子递增 `failed_login_count`；达到 10 次连续错误时设置 `locked_until=now()+15 minutes`，并在 `login_failed` 事件中记录内部 `failure_reason_code=account_locked`，外部仍返回与普通错误一致的 401，避免泄露账户存在性。
3. `locked_until > now()` 时不签发 token，记录内部 reason `account_temporarily_locked`；到期后的下一次请求在同一事务中清零 count/lock 后再正常验证。一次成功登录立即把 `failed_login_count=0, locked_until=NULL`。
4. suspended/rejected/deleted 状态不使用临时锁定语义。管理员 activate 只处理 suspended 用户，不绕过或清除尚未到期的凭据锁；Phase 1 不提供远程管理员强制解锁接口，break-glass 解锁只能通过受审计 CLI。

所有阈值可通过有上下界的配置覆盖，但上述默认值写入 `.env.example`，API 副本共享同一 Redis/PostgreSQL 状态。限流 429 优先于账户验证；账户锁定 401 不是 429 的替代品。

### Refresh rotation

刷新必须在短事务中：

1. 对 token hash 对应的 `refresh_sessions` 行执行 `SELECT ... FOR UPDATE`。
2. 验证未过期、未撤销、`used_at IS NULL`、用户 active、auth_version 一致。
3. 若旧 token 已使用或已被替换，判定 reuse，撤销同一 `family_id` 全部 session、递增用户 `auth_version` 并记录事件。
4. 创建同 family 的新 session，旧行设置 `used_at` 和 `replaced_by_session_id`。
5. 提交后才返回新的 access token 和 refresh cookie。

两个并发 refresh 使用同一 token 时只能有一个成功；另一个必须触发 reuse 策略，不能产生两个有效后继 token。reuse 分支必须提交撤销和事件后再返回 401，不能因抛出异常而回滚；步骤 2 的 used/replaced 检查进入步骤 3，而不是提前返回普通失败。

会话列表按 `family_id` 聚合，一个浏览器登录只展示一条会话；响应 `id` 与 DELETE `/me/sessions/{id}`、`/admin/sessions/{id}` 的 id 均为 family UUID，`current` 由 access JWT 的 sid 判断。撤销 family 必须撤销其全部行并使对应 access token 立即失效，其他 family 不受影响；logout 使用 refresh cookie 定位 family，并校验 CSRF/Origin，不要求尚未过期的 access JWT。

前端刷新协调必须覆盖同源多个标签页：使用由 `BROWSER_KEY_PREFIX` 派生名称的 Web Locks 独占锁；锁内重新读取最新 CSRF Cookie 后才发送 refresh，禁止排队前缓存 Cookie/header。各标签页可依次 rotation 获取仅存本标签页内存的 access token，旧 access 的 sid 在正常 rotation 后仍有效。BroadcastChannel 仅发送退出/身份切换通知，不广播 token；登录、退出与刷新共用锁，并用内存 generation 防止迟到响应恢复旧身份。网络超时造成 rotation 结果未知时不自动重试旧凭据，清理本地状态并要求重新登录。缺少跨标签页协调能力时显示明确的不受支持提示，不静默退回仅单标签页锁。

本人改密固定采用全部退出：在同一事务更新密码历史、清除 `must_change_password`、递增 `auth_version/row_version` 并撤销全部 family；提交后返回 204、清理 refresh/CSRF Cookie。前端清空内存 token、账户查询缓存并通知其他标签页退出，转到登录页；改密接口不签发新 token。

### 数据库与请求并发

- 使用 `AsyncEngine`、asyncpg 和 request/task scoped `AsyncSession`；一个 AsyncSession 绝不能被两个 asyncio task 共享。
- Argon2 hash/verify 属于 CPU 密集工作，必须放入容量受限的线程池或等效隔离执行，并设置登录并发上限；不得阻塞主 event loop，也不得创建无限线程。
- 每个请求最多一个主事务；调用 Redis、邮件、远程 HTTP、LLM 或文件处理时不得保持数据库事务或行锁。
- 使用数据库唯一约束处理并发重复创建；捕获 `IntegrityError` 后回滚并返回稳定 409。
- 修改 users/roles 时使用 `row_version` 乐观并发控制；API 通过 `version` 字段或 `If-Match` 提交旧版本，不匹配返回 409 `VERSION_CONFLICT`。
- 乐观锁必须使用单条 `UPDATE ... WHERE id=:id AND row_version=:expected` 并检查 affected row count，不能先读取再无条件 update。
- 最后一个 super-admin 检查必须在同一事务中锁定相关用户/角色关联行，避免两个管理员并发撤权同时通过。
- 管理写接口接受 `Idempotency-Key`。同用户、同 endpoint、同 key 且 request hash 相同，返回已保存结果；hash 不同返回 409；处理中返回 409/425 和 `Retry-After`。
- API 必须无状态，可运行多个副本；禁止用进程内 dict、Lock 或全局变量保证正确性。
- 数据库连接池大小通过环境变量配置。文档给出预算公式：`API_REPLICAS × (POOL_SIZE + MAX_OVERFLOW) + migration/worker reserve < PostgreSQL max_connections`。
- 云上副本较多时支持 PgBouncer；不得同时把应用池和 PgBouncer 池配置得无限大。

## 8. 整库备份与恢复

### 备份层级决策

本系统的管理员备份固定采用“单个应用数据库的完整逻辑备份”，不是 schema-only、table list 或手写导出：

- 使用 PostgreSQL 16 客户端 `pg_dump --format=custom`，不传 `--schema`、`--table`、`--exclude-schema` 或 `--exclude-table`。
- 默认包含该数据库内全部用户 schema 的数据和 database-scoped 对象：表、分区、序列及当前值、约束、索引定义、视图、物化视图、函数、触发器、规则、类型、domain、row-level security policy、extension 声明和 large objects。
- 索引在逻辑备份中保存的是定义，恢复时重建，不复制索引物理页。这是期望行为。
- 对象发现完全由 PostgreSQL catalog/`pg_dump` 完成；代码、配置和 UI 中禁止维护“要备份的表/schema 清单”。以后新增任意数量的表、索引、视图或函数，不需要修改备份逻辑。
- schema-only 只允许用于开发诊断，不能标记为可恢复备份；按表/按 schema 导出只属于未来的数据迁移工具，不属于灾难恢复。

`pg_dump` 只覆盖一个数据库，不包含 cluster 级 PostgreSQL role、tablespace 和其他数据库。为了让备份在新环境可移植，本系统使用 `--no-owner --no-privileges`，目标环境通过 IaC/secret manager 先创建 PostgreSQL 实例、目标 database owner 和必要 extension binaries，再把全部应用对象恢复给目标 owner。不得把数据库账号密码或 cluster superuser 凭据塞进备份包。

### 单文件格式

对用户交付一个扩展名来自配置 `BACKUP_EXTENSION`（派生值 `.rbac-sys.backup`）的单文件 bundle，内部固定包含：

```text
manifest.json       # 格式版本、应用版本、Alembic revision、PG 版本、时间、对象数等
database.dump       # pg_dump custom archive
checksums.sha256    # bundle 各成员 SHA-256
signature.ed25519   # Ed25519 私钥对两个成员的精确字节签名
```

- bundle 只是容器，不再次高压缩 `database.dump`；避免无意义双重压缩。
- `manifest.json` 至少记录 `format_version/source_database/source_pg_version/pg_dump_version/application_version/git_sha/alembic_revision/created_at/object_count/archive_sha256/required_extensions/signature_algorithm/signing_key_id`。
- 私有对象存储必须使用 SSE-KMS 或云平台等效加密，传输必须 HTTPS。签名私钥来自 secret manager，不进入 bundle、数据库、日志或 Git。
- `${BACKUP_EXTENSION}` 文件是唯一需要搬运的业务备份 bundle，但重建仍需要兼容的 PostgreSQL、受信任签名密钥/公钥策略和目标数据库凭据；文档不得宣称一个文件能凭空包含数据库服务器与秘密。
- Phase 1 固定使用 Ed25519 非对称签名，不使用共享 HMAC。只有 maintenance backup worker 可读取 `BACKUP_SIGNING_PRIVATE_KEY`；API、管理员 UI 和目标恢复实例只配置按 `signing_key_id` 索引的受信 Ed25519 公钥 keyring。跨实例迁移必须由目标运维域显式信任源公钥，验证方不能因此伪造备份。
- 签名输入固定为 bundle 内 `manifest.json` 的精确 UTF-8 字节、单个 LF 分隔符和 `checksums.sha256` 的精确 ASCII 字节；验证方不得先解析再重新序列化。先验证 key id、算法和签名，再按严格 schema 解析 manifest 并验证成员 checksum。定义公钥轮换、旧 key 验证保留期和撤销 runbook；私钥泄漏时撤销对应 key id，并把受影响备份标记 untrusted。

### 创建流程

API 只创建 `backup_artifacts(status='pending')` 并返回 202；maintenance worker 执行：

1. 获取互斥 lease，检查目标空间/对象存储可写，创建权限为 0700 的临时目录，其中 `.partial`、临时 passfile 和其他秘密文件权限为 0600；目录必须具备 owner 的搜索/执行权限。Windows 宿主机辅助文件使用仅当前用户可访问的 ACL，不能把 POSIX mode 当作 Windows ACL 验证。
2. worker 从 typed Settings/secret adapter 配置 libpq 的非秘密连接项 `PGHOST/PGPORT/PGDATABASE/PGUSER`，通过 `PGPASSFILE` 指向上述 0600 临时 passfile；生产同时传递受信 TLS 参数。密码由进程内安全写入 passfile，正确转义 `:` 与反斜线，不能经 shell 插值写入或打印。使用与服务器相同 major 的 PostgreSQL client 执行等价命令：

```bash
pg_dump \
  --format=custom \
  --compress=6 \
  --no-owner \
  --no-privileges \
  --file=database.dump \
  --no-password
```

3. 必须检查进程 exit code；不得使用 `--no-sync`。失败删除 partial，记录脱敏错误，不生成 completed artifact。
4. 执行 `pg_restore --list database.dump`，生成对象数和 archive TOC 摘要；任何 schema/table filter 痕迹视为失败。
5. 生成 manifest、checksum 和 Ed25519 signature，打包后再次校验，再原子 rename/upload，最后把数据库状态改为 completed。
6. 备份过程中 `pg_dump` 的一致性快照允许应用继续读写；不得为了备份长时间全站停机。

数据库 URL、密码不能进入 argv、shell trace、日志或进程错误详情；不得把含密码 URI 传给 `pg_dump/pg_restore/psql`。优先临时 passfile，不以 `PGPASSWORD` 作为默认替代；退出、异常和取消都关闭连接并删除 passfile/partial，保留范围受控的失败状态。maintenance image 固定安装 PostgreSQL 16 client，不依赖宿主机碰巧存在的 `pg_dump`。

### 导入与恢复流程

恢复是高危、异步、两阶段操作，只允许 `system.restore` + active super-admin + 最近 5 分钟重新认证。上传备份还必须通过 CSRF、内容长度、文件名、magic bytes、bundle 结构、checksum、可信 `signing_key_id` 和 Ed25519 signature 校验。

PostgreSQL 官方警告 restore 会执行 dump 中包含的 SQL/函数代码，因此 UI/API 禁止恢复来源不可信或签名无效的 archive。`pg_restore --list` 只能检查结构，不能把恶意 dump 变安全；unsigned legacy dump 只能由运维人员离线审查后通过受控 CLI 处理。

默认且唯一的 Phase 1 策略是 restore-to-new-database，禁止直接覆盖正在使用的数据库：

1. 校验 bundle、PG major compatibility、所需 extension、可用磁盘、目标数据库名和没有其他 active restore。
2. 自动创建当前数据库的 safety backup；失败则禁止继续。
3. 从 `template0` 创建全新的、不可与现有库重名的 target database，由配置的 target owner 拥有。
4. 执行等价命令：

```bash
createdb --template=template0 --owner="$TARGET_OWNER" "$TARGET_DATABASE"
pg_restore \
  --exit-on-error \
  --no-owner \
  --no-privileges \
  --jobs="$RESTORE_JOBS" \
  --dbname="$TARGET_DATABASE" \
  database.dump
```

5. 恢复失败立即把 run 标记 failed，保留旧数据库，不允许切换；目标失败库按保留策略隔离，不能误删名称不匹配的库。
6. 成功后运行 `ANALYZE`、Alembic revision 检查、catalog 对象/TOC 检查、关键 RBAC 完整性查询、API 只读 smoke 和可选 `pg_amcheck`。在目标库执行受审计的安全收尾：撤销备份中恢复出的全部 refresh session、递增用户 auth_version，并把快照中的 pending/running maintenance/idempotency 状态标记为恢复时失效，防止切换后重放旧任务。
7. 状态进入 `ready_for_cutover`，UI 展示验证报告、源/目标版本、checksum 和 safety backup。
8. 第二次明确确认后，由部署层切换 DATABASE_URL/secret 并滚动重启 API、maintenance worker；应用请求本身不得修改自己的环境变量或重启容器。
9. 切换后执行 `/health/ready` 和完整只读 smoke；失败时把连接切回旧数据库并标记 rolled_back。

同一数据库任何时刻只允许一个 restore。备份可以排队，但 restore 运行时暂停新的 backup/restore job。不能在持有业务数据库事务时调用 `pg_dump`/`pg_restore`。

必须同时提供不依赖 Web UI 和原业务数据库的灾难恢复 CLI。它从只读挂载的 `${BACKUP_EXTENSION}` bundle 和环境变量中的目标连接/签名配置执行相同 preflight、restore 和 verification，例如：

```bash
podman compose run --rm \
  -v /absolute/backup-dir:/restore:ro \
  -e RESTORE_BUNDLE="/restore/backup${BACKUP_EXTENSION:?required}" \
  maintenance \
  python -m app.cli.restore_backup --target-database "${RESTORE_TARGET_DATABASE:?required}"
```

README 必须注明 Windows PowerShell 的绝对路径写法。archive 固定不包含 `CREATE DATABASE`，任何路径都不得使用 `pg_restore --create/-C`，数据库名称永远以经过校验的 `TARGET_DATABASE` 为准。CLI 默认禁止覆盖既有数据库；单独的离线 break-glass 原名重建必须要求输入目标数据库全名和固定确认短语、检查/终止连接、成功创建 safety backup，把旧库 rename 到带时间戳的 quarantine 名称，再从 `template0` 创建明确命名的新空库并用不带 `--create`/`--clean` 的 `pg_restore --dbname="$TARGET_DATABASE"` 恢复。任一步失败都保留 quarantine/safety backup，绝不根据 archive 内的 source database 名执行 drop/create。

### 双层灾备策略

- 管理员 `${BACKUP_EXTENSION}` bundle：用于下载归档、跨实例迁移、在空 PostgreSQL 上重建整个应用数据库，RPO 等于最近一次成功备份时间。
- 云 PostgreSQL 自动备份 + WAL/PITR：用于生产环境分钟级/秒级时间点恢复、整实例灾难恢复和较低 RPO。
- 两者必须同时存在。应用整库逻辑备份不能替代 PITR，PITR 也不能替代管理员可下载、可跨实例验证的逻辑 archive。
- 明确保留策略，例如每日 7 份、每周 4 份、每月 12 份；实际删除由 maintenance worker 执行并写 action history。
- 每月至少自动做一次“恢复到隔离数据库并验证”的演练。只有可恢复并通过验证的备份才算有效。

## 9. 为未来 LLM/Vocab 并发预留的边界

本阶段不实现任务队列和任何模型调用，只新增一份 ADR，固定未来业务遵守以下边界：

- HTTP API 不直接执行长时间 LLM、端侧模型、PDF 或 Vocab 任务；提交后返回 `202 + job_id`，由独立 worker 执行。
- API、通用 worker、CPU 文档 worker、GPU/端侧模型 worker 独立进程和独立扩缩容。
- 每用户并发配额、每 provider/model 并发上限、全局队列上限均使用跨副本协调，不能使用单进程 semaphore。
- 相同 `job_type + resource_id + resource_version + normalized_params_hash` 支持去重；“Vocab”重复点击不能启动多个相同任务。
- 队列满时明确返回 429/503 和 Retry-After，实施背压，不能无限积压。
- worker 使用 lease/heartbeat、超时、取消、幂等提交和有限重试；只对可安全重试错误使用指数退避和 jitter。
- 模型输出先写临时对象，再通过原子状态更新发布；失败不能覆盖上一次成功结果。
- GPU 模型不能随 API worker 数量重复加载。模型 worker 数按 GPU/内存预算部署。
- SSE/WebSocket 只传递状态和增量结果，任务真相存于持久层；断线重连不能丢任务。
- 未来对象文件进入 S3-compatible object storage，本地容器磁盘不作为持久存储。

ADR 只定义接口、状态机和约束，不创建 job 表、worker 空壳或未使用依赖。

## 10. 固定 API 契约

统一前缀 `/api/v1`。列表响应：`{items,total,page,size,pages}`。错误响应：

```json
{"error":{"code":"PERMISSION_DENIED","message":"...","details":null,"request_id":"uuid"}}
```

所有响应不得返回 `password_hash`、token hash 或内部敏感 metadata。

固定公共 DTO；字段不得由执行者随意改名。涉及 super-admin 保护动作时，请求额外接受 `reauth_password`（string[1..128]，仅验证调用者密码，不写入幂等响应、日志或审计）；DELETE 使用 JSON body。OpenAPI 必须表达该字段及条件必填规则：

```text
LoginRequest      = {identifier: string[1..320], password: string[1..128]}
RegisterRequest   = {username: string[3..64], email: EmailStr, display_name?: string[1..120], password: string[12..128]}
RegisterResponse  = {message: "If registration can proceed, check your email", status_token: string, status_token_expires_in: 604800}
RegistrationStatusResponse = {status: "submitted"|"email_verified"|"pending_approval"|"approved"|"rejected", updated_at?: datetime}
TokenOnlyRequest  = {token: string}
ResendVerificationRequest = {email: EmailStr}
ForgotPasswordRequest = {email: EmailStr}
ResetPasswordRequest = {token: string, new_password: string[12..128]}
TokenResponse     = {access_token: string, token_type: "bearer", expires_in: 600, user: UserMe}
UserMe            = {id, username, email, status, must_change_password, profile: UserProfile, preferences: UserPreferences, roles: RoleSummary[], permissions: string[], auth_version, row_version}
UserProfile       = {user_id, display_name, row_version}
UserProfilePatch  = {display_name?: string[1..120]|null, row_version: integer}
UsernameChange    = {new_username: string[3..64], current_password: string[1..128], row_version: integer}
AdminUsernameChange = {new_username: string[3..64], reauth_password: string[1..128], row_version: integer}
EmailChangeRequest = {new_email: EmailStr, current_password: string[1..128]}
AdminEmailChangeRequest = {new_email: EmailStr, reauth_password: string[1..128]}
EmailChangeConfirm = {token: string}
UserPreferences  = {theme_mode: "system"|"light"|"dark", theme_palette: "default"|"eye_care"|"sepia"|"forest", contrast_mode: "system"|"standard"|"high", density: "comfortable"|"compact", motion_mode: "system"|"reduced", time_zone: string, page_size: 20|50|100, row_version: integer}
UserPreferencesPatch = {theme_mode?, theme_palette?, contrast_mode?, density?, motion_mode?, time_zone?, page_size?, row_version: integer}
RoleSummary       = {id, code, name}
UserCreate        = {username, email, display_name?, password, role_ids: UUID[]}
AdminUserProfilePatch = {display_name?: string[1..120]|null, row_version: integer}
UserRoleReplace   = {role_ids: UUID[], row_version: integer}
PasswordReset     = {new_password, row_version: integer}
ChangePassword    = {current_password, new_password}
RoleCreate        = {code, name, description?}
RolePatch         = {name?, description?, is_active?, row_version: integer}
RolePermissionReplace = {permission_ids: UUID[], row_version: integer}
BackupCreate      = {label?: string[1..120], retention_days: integer[1..3650]}
RestoreCreate     = {backup_id: UUID, target_database: string[1..120], reauth_password: string, confirmation: "RESTORE TO NEW DATABASE"}
ClientErrorEvent  = {event_id: UUID, occurred_at: datetime, level: "warning"|"error", event_type: "react_error_boundary"|"unhandled_error"|"unhandled_rejection"|"api_failure", route_name: string[1..120], client_release: string[1..80], error_name: string[1..120], sanitized_message?: string[1..500], sanitized_stack?: string[1..8000], request_id?: UUID}
ClientErrorBatch  = {events: ClientErrorEvent[1..20]}
```

- 密码长度、泄露密码检查等完整规则集中在一个 policy 模块；API schema 只做基本边界校验。
- 默认 `page=1,size=20`，最大 `size=100`；未知 sort/filter 返回 422，禁止把客户端字符串直接拼入 SQL。
- 日期筛选使用 ISO 8601 UTC；列表默认按 `created_at DESC, id DESC` 稳定排序。
- Admin user/role 响应必须包含 `row_version`，更新成功后返回新版本。
- CSV 导出默认最多 10,000 行；更大导出属于未来异步任务，本阶段返回明确 422/413，不在请求中无限流式查询。

### Auth 与本人接口

| Method | Path | 权限 | 成功状态 | 说明 |
|---|---|---|---:|---|
| POST | `/auth/register` | Public | 202 | 返回固定 `RegisterResponse`；新注册和既有标识均签发不可枚举的 status token |
| POST | `/auth/verify-email` | Public | 200 | 消费 token，进入 pending_approval 或 active |
| POST | `/auth/resend-verification` | Public | 202 | 通用响应、限流、旧 token 失效 |
| GET | `/auth/registration-status` | Public + opaque status token header | 200 | 从 `X-Registration-Status-Token` 读取；只返回本次注册的有限状态 |
| POST | `/auth/forgot-password` | Public | 202 | 无论 email 是否存在均通用响应 |
| POST | `/auth/reset-password` | Public + one-time token | 204 | 修改密码、撤销会话、token 单次消费 |
| POST | `/auth/login` | Public | 200 | body: identifier/password；返回 access token + user，设置 refresh cookie |
| POST | `/auth/refresh` | Refresh cookie | 200 | rotation |
| POST | `/auth/logout` | Refresh cookie + CSRF/Origin | 204 | 撤销当前 refresh family/session 并清 cookie |
| POST | `/auth/logout-all` | Authenticated | 204 | 撤销用户全部 session，auth_version +1 |
| GET | `/auth/me` | Authenticated | 200 | 身份、Profile、Preferences、角色、权限、版本；登录后的偏好权威来源 |
| POST | `/auth/confirm-email-change` | Public + one-time token | 204 | 确认目标邮箱、撤销全部会话；不可枚举 |
| GET/PATCH | `/me/profile` | Authenticated | 200 | 读取/更新本人 display name；带 profile row_version |
| POST | `/me/change-username` | Authenticated + current password | 204 | 修改 username、撤销全部会话、要求重新登录 |
| POST | `/me/change-email/request` | Authenticated + current password | 202 | 向新邮箱发确认、向旧邮箱发安全通知 |
| GET/PATCH | `/me/preferences` | Authenticated | 200 | 读取/部分更新本人偏好；带 preference row_version |
| POST | `/me/change-password` | Authenticated | 204 | current/new password；撤销全部 session、清 Cookie，重新登录 |
| GET | `/me/sessions` | `sessions.read_own` | 200 | 当前用户会话，标明 current |
| DELETE | `/me/sessions/{id}` | `sessions.revoke_own` | 204 | 只能撤销本人 session |
| GET | `/me/login-history` | `login_history.read_own` | 200 | 只能读取本人记录 |
| POST | `/telemetry/client-errors` | Public + exact Origin + rate limit | 202 | 严格 allowlist 的前端错误批次；可选 access token 只由后端附加 actor id，不写业务表 |

### 管理接口

| Method | Path | 权限 | 说明 |
|---|---|---|---|
| GET/POST | `/admin/users` | `users.read/create` | 分页筛选 / 创建 |
| GET | `/admin/users/pending` | `users.read` | pending_approval 分页列表 |
| GET/PATCH | `/admin/users/{id}` | `users.read/update` | 详情 / 仅更新 Profile；返回 user/profile 两个 row_version |
| POST | `/admin/users/{id}/change-username` | `users.update` + recent reauth | 修改登录名、撤销会话、通知与审计 |
| POST | `/admin/users/{id}/request-email-change` | `users.update` + recent reauth | 只能发起目标邮箱验证，不能直接改 email |
| POST | `/admin/users/{id}/approve` | `users.approve` | 仅 pending_approval；进入 active |
| POST | `/admin/users/{id}/reject` | `users.reject` | 仅 pending_approval；进入 rejected |
| POST | `/admin/users/{id}/suspend` | `users.suspend` | 停用并撤销会话 |
| POST | `/admin/users/{id}/activate` | `users.activate` | 仅 suspended → active；不用于 deleted/rejected/locked |
| DELETE | `/admin/users/{id}` | `users.delete` | 软删除 |
| POST | `/admin/users/{id}/reset-password` | `users.reset_password` | 重置并撤销会话 |
| PUT | `/admin/users/{id}/roles` | `users.manage_roles` | body: role_ids + row_version，集合替换 |
| GET/POST | `/admin/roles` | `roles.read/create` | 列表 / 创建 |
| GET/PATCH/DELETE | `/admin/roles/{id}` | 对应 roles 权限 | 系统角色受保护 |
| PUT | `/admin/roles/{id}/permissions` | `roles.manage_permissions` | permission_ids + row_version，集合替换 |
| GET | `/admin/permissions` | `permissions.read` | 分组只读目录 |
| GET | `/admin/sessions` | `sessions.read` | 分页筛选 |
| DELETE | `/admin/sessions/{id}` | `sessions.revoke` | 撤销任意会话 |
| GET | `/admin/login-history` | `login_history.read` | 分页筛选 |
| GET | `/admin/login-history/export` | `login_history.export` | 流式 CSV，限制范围和行数 |
| GET | `/admin/action-history` | `action_history.read` | 分页筛选 |
| GET | `/admin/action-history/export` | `action_history.export` | 流式 CSV，限制范围和行数 |
| GET/POST | `/admin/backups` | `system.backup` | 分页列表 / 创建完整整库备份，POST 返回 202 |
| GET | `/admin/backups/{id}` | `system.backup` | 状态、manifest、checksum、脱敏错误 |
| GET | `/admin/backups/{id}/download` | `system.backup` | 下载 completed `${BACKUP_EXTENSION}` bundle；禁止代理缓存 |
| DELETE | `/admin/backups/{id}` | `system.backup` | 删除 artifact；active restore 引用时 409 |
| POST | `/admin/backups/import` | `system.restore` | multipart 导入 `${BACKUP_EXTENSION}` bundle，流式限量写入并校验，返回 202 |
| POST | `/admin/backups/{id}/validate` | `system.restore` | checksum/Ed25519/TOC/compatibility 校验，返回报告 |
| POST | `/admin/restores` | `system.restore` | 最近重新认证 + 固定确认短语；创建 restore-to-new-db，返回 202 |
| GET | `/admin/restores` | `system.restore` | restore run 分页列表 |
| GET | `/admin/restores/{id}` | `system.restore` | 状态、验证报告与 cutover runbook |
| GET | `/health/live` | Public | 只表示进程存活 |
| GET | `/health/ready` | Internal/Public by deploy | 检查 PostgreSQL；Redis 状态单独展示 |

认证失败 401；已认证但无权限 403；资源不存在 404；唯一冲突或版本冲突 409；校验错误 422；限流 429。不要把这些状态混用。

## 11. UI 信息架构

### 公共界面

- `/login`：登录与 pending/suspended 等安全状态提示。
- `/register`：注册；提交后进入“检查邮箱”状态，不泄露既有账户信息。
- `/verify-email`：验证处理中、成功、过期、已使用等明确状态。
- `/registration-status`：显示邮箱已验证、待管理员审批、已批准或已拒绝。
- `/forgot-password` 与 `/reset-password`：不可枚举的找回流程和一次性 token 重置。
- `/403`、`/404`：可访问且提供安全返回入口。

### 普通用户 `/app/*`

普通用户区域只做账户和安全，不伪造学习首页：

- `/app`：账户概览，显示姓名、用户名、角色摘要、最近登录和安全状态。
- `/app/profile`：展示资料；username/email 变更使用独立重新认证与邮件确认流程，不混入普通保存按钮。
- `/app/preferences`：外观（主题、对比度、密度、动态效果）与区域（IANA 时区、默认分页大小），每项都有即时预览、保存状态和恢复默认值。
- `/app/security`：修改密码、当前会话、其他会话、退出全部设备以及近期安全动作。
- `/app/login-history`：本人登录历史。

使用 `AccountLayout`。导航只包含“账户概览”“个人资料”“偏好设置”“安全与会话”“登录历史”。个人菜单包含亮度模式和当前 palette 的快捷切换与退出，快捷切换与 Preferences 页使用同一状态源。普通用户不看到任何管理员入口、ADMIN 标记或管理数据。

### 管理员 `/admin/*`

- `/admin`：用户数量、active/suspended 数量、24h 登录成功/失败、活跃会话、近期高风险操作。
- `/admin/users` 与 `/admin/users/:id`。
- `/admin/users/pending`：待审批注册，支持审批/拒绝与审计。
- `/admin/roles` 与 `/admin/roles/:id`。
- `/admin/permissions`。
- `/admin/sessions`。
- `/admin/login-history`。
- `/admin/action-history`。
- `/admin/backups`：创建、下载、导入、校验、保留期和删除备份。
- `/admin/restores` 与 `/admin/restores/:id`：高危恢复向导、实时状态、验证报告和 cutover runbook。

`AdminLayout` 在 light/dark/high-contrast 各模式下均使用与账户区不同的 Slate/Navy 管理侧栏，固定显示盾牌图标、`Administrator Console` 与琥珀色 `ADMIN` 徽标，不能因切换主题失去管理员身份提示。用户详情把 Account governance、Profile、Roles、Security、Activity 分区展示；管理员不能编辑 Preferences。顶栏提供“返回账户区”。只有拥有 `admin.access` 才能进入管理根路由；子路由继续检查细粒度权限。

### Theme 与 Preferences 执行契约

- 主题采用正交的两层模型：`theme_mode=system|light|dark` 只决定亮度；`theme_palette=default|eye_care|sepia|forest` 决定配色。每个 palette 都必须同时提供 light/dark token，因而支持“护眼浅色”“护眼深色”和“护眼跟随系统”，不得把 palette 硬编码为某一种亮度。
- 固定 palette 含义：`default` 为 Slate/Zinc + Indigo；`eye_care` 为低饱和暖中性色配柔和 Green/Teal；`sepia` 为暖纸色/暖暗色；`forest` 为低饱和自然绿色。名称“护眼”只表示减少刺眼感的视觉舒适预设，不得作预防近视、过滤有害蓝光或改善视力等医疗功效宣称。任何 palette 都不能以降低文字对比度换取“柔和”。
- Tailwind CSS 4 使用语义 design token，不允许业务组件散落 `bg-white/text-black` 等原始明暗色。至少定义 background、surface、surface-raised、text、text-muted、border、primary、danger、admin-accent、focus-ring、selection，并为 `data-theme × data-palette × data-contrast` 的受支持组合提供完整值；缺 token 时构建测试失败，禁止静默回退成半套默认主题。
- dark variant 固定采用 Tailwind 4 selector：`@custom-variant dark (&:where([data-theme=dark], [data-theme=dark] *));`。DOM 的 `data-theme` 只放解析后的 `light|dark`，`data-palette` 放已校验 palette code；`system` 使用 `window.matchMedia('(prefers-color-scheme: dark)')` 并仅在该模式监听系统变化。同步设置 `color-scheme`，保证原生控件、滚动条和浏览器 UI 与实际主题一致。
- Preferences 页把“亮度模式”和“配色方案”显示为两个独立且带说明的控件：模式是“跟随系统 / 浅色 / 深色”键盘可操作 segmented control，palette 是带真实色板预览的 Default / Eye Care / Sepia / Forest 卡片网格；都有准确 accessible name、selected state、文字标签和可见焦点，不能只靠图标或颜色传意。快捷组件复用于公共页 header、Account 个人菜单和 Admin 顶栏。
- 未登录页面只允许把经过固定枚举/大小校验的 `{theme_mode, theme_palette}` 存入由配置生成的 `${BROWSER_KEY_PREFIX}anonymous-theme`；禁止把 localStorage 值直接拼入 selector/style，也禁止持久化任何用户 id、Profile 或已认证 Preferences。登录后服务端 `user_preferences` 是权威来源并覆盖匿名选择；退出时清除内存中的账户偏好并回到匿名/系统主题，确保共享浏览器切换账号不会串用上一个用户的设置。
- 在 React 首次绘制前由 CSP-compatible 的极小 bootstrap script 解析并严格校验匿名 mode/palette、解析系统亮度，再一次性设置 DOM attributes，避免默认色或错误 palette 闪烁；`/auth/me` 返回后再无闪屏地 reconcile 服务端偏好。不得为此放宽 production CSP 到任意 `unsafe-inline`，应使用外部同源脚本或 nonce/hash。
- 已认证亮度或 palette 变更通过 TanStack Query mutation 写入 `/me/preferences`；可乐观预览，但 409/网络失败必须原子回滚 mode + palette 并提示，成功后更新 query cache 与 row_version。偏好需跨刷新、跨设备生效，不以 localStorage 作为用户状态真相。
- `contrast_mode=system` 跟随 `prefers-contrast`（浏览器不支持时回退 standard）；high 模式必须实际提高 token 对比度和边界辨识度。`density` 必须实际改变表格行高、表单间距与导航密度。`motion_mode=reduced` 禁用非必要过渡；OS `prefers-reduced-motion: reduce` 始终优先，用户不能强制恢复动画。
- PublicLayout、AccountLayout、AdminLayout、Dialog、toast、表格、表单、loading/empty/error 状态在每个 palette 的 light/dark/high contrast 下都满足 WCAG 2.2 AA，并支持 `forced-colors`。程序化 token contrast 测试覆盖全部组合；自动化 visual regression 至少覆盖三个 layout 的 default light/dark、eye_care light/dark、其他 palette 的代表页面、Preferences high contrast 以及窄屏，不允许只测设置控件本身。

### 导航与视觉规范

- 不把账户和管理功能混在同一侧栏。
- 桌面侧栏 256px/折叠 72px；移动端 Drawer，Esc 关闭并恢复焦点。
- 折叠图标有 tooltip 和 accessible name；当前页、父组、hover、focus 状态可区分。
- 管理侧栏分为 Identity、Security、Audit、System 四组，没有可见子项的组不渲染；Backups/Restore 只出现在 System。
- 使用 route metadata 同时生成 Router、导航和面包屑。
- 使用 Inter + Noto Sans SC、Slate/Zinc 中性色、Indigo 普通强调色、Amber 管理身份提示、Red 危险操作。
- 卡片以 1px border 为主，避免大面积绿色、过度渐变、玻璃拟态、厚阴影和无意义动画。
- 满足 WCAG 2.2 AA；支持键盘、可见焦点、语义 label、Dialog 焦点圈定和 `prefers-reduced-motion`。
- 列表页固定包含标题说明、主操作、服务端筛选、表格、分页、loading skeleton、空状态和错误重试。
- 角色权限使用按资源分组的矩阵，保存前展示权限 diff；危险操作确认框必须写明对象和影响。
- 不展示假的搜索框、统计值或按钮。

## 12. Login history 与 Action history 规则

### Login history

- 认证 use case 显式写入；失败登录在用户不存在时也可写入，`user_id=NULL`，identifier 只存脱敏值。
- failure reason 内部可精确，外部登录错误保持泛化，避免枚举账号。
- 普通用户看到自己的时间、事件、结果、设备摘要和脱敏 IP；管理员可按用户、事件、结果、原因、IP、日期筛选。
- 绝不记录 attempted password、完整 token、Cookie 或认证请求体。

### Action history

- 记录用户创建、Profile 修改、username/email 身份变更、停用/软删除、密码重置、角色分配、角色变更、权限分配、会话撤销、导出、备份创建/下载/导入/删除、恢复请求/验证/失败/完成和 cutover；主题等非安全个人偏好按第 5 节规则不写入 action history。
- `actor_type=system/worker` 时不得伪造 actor user。
- 业务事务成功提交后记录 success；若需要与业务变更原子一致，audit insert 与业务写入同一事务。失败记录必须明确 failure，不能因 rollback 留下 success。
- `changes` 只包含 allowlist 字段 diff；角色/权限只记录 ID/code 集合变化，不保存整个 ORM 对象。
- access log 通过 request id 与 action history 关联，但不复制完整日志内容。

## 13. 明确测试用例

所有测试使用独立测试数据库/transaction fixture，不能依赖执行顺序。以下编号全部必须实现；Given/When/Then 是验收契约，不得只以截图或手工说明代替。

### Endpoint 全覆盖策略

`curl` 不是主测试框架。必须同时实现以下四层：

1. 后端 API 集成测试：使用 Pytest + HTTPX `AsyncClient` + ASGI transport/lifespan，对真实测试 PostgreSQL 与 Redis 执行，断言 HTTP 响应、数据库副作用、Cookie、审计和缓存失效。
2. OpenAPI 契约覆盖：生成并提交 `backend/tests/contract/endpoint_matrix.yaml`，每行包含 `operationId/method/path/happy_case/unauthenticated/forbidden/validation/not_found_or_conflict` 对应测试 ID。测试自动读取 `/openapi.json` 比较 operation 集合；新增 endpoint 没有矩阵记录或测试 ID 时 CI 失败。
3. Playwright E2E：通过真实浏览器访问 Nginx，验证注册、验证邮件（Mailpit/fake inbox）、审批、登录、改密、Cookie/CSRF、导航和权限界面。
4. 部署后黑盒 smoke：`scripts/smoke_api.py` 使用 HTTPX 请求 `BASE_URL`，从注册或受控 fixture 开始串起完整流程。另提供 `scripts/smoke-api.sh` 和 `scripts/smoke-api.ps1` 的 curl 示例用于人工排障，但不得让 curl 脚本成为唯一验收。

每个 API operation 至少必须有：一个成功路径、一个 schema/业务校验失败路径；受保护接口还必须有 401 和 403；按 ID 查询必须有 404；并发/幂等接口必须有竞争测试。测试必须校验响应 schema 和关键副作用，不能只断言 status code。

集成测试禁止用 SQLite 或 fakeredis 替代 PostgreSQL/Redis。完整的 staging 黑盒套件必须通过 Nginx 对 endpoint matrix 中每个 operation 至少发出一次请求并核对预期响应；具有破坏性的场景使用专用测试用户和可清理 fixture。生产部署后的 smoke 只执行只读和专门设计的安全探针，不在生产创建/删除真实用户。

### Migration 与 seed

- `DB-001` Given 空 PostgreSQL，When `alembic upgrade head`，Then 所有表、约束和索引与第 5 节一致。
- `DB-002` Given 已到 head，When downgrade 到 base 再 upgrade head，Then 成功且无残留对象；若某迁移明确不可逆，必须测试其清晰失败信息。
- `DB-003` Given seed 连续运行两次，Then permission/role/user 不重复，既有安全自定义不被覆盖。
- `DB-004` Given 管理员 API 并发创建相同 normalized username/email，Then 仅一个成功，另一个稳定返回 409；自助 `/auth/register` 的同类竞争转换为不可枚举的相同 202 `RegisterResponse`。

### Auth

- `REG-001` Given 可注册的新 username/email，When register，Then 202、创建 pending_verification 用户和 user 角色、仅存 token hash、fake inbox 收到验证链接。
- `REG-002` Given 相同 email/username 已存在或两个并发注册，When register，Then 响应形状一致且不泄露账户状态，不产生重复用户或多个有效 email-verification token；每次请求仍得到独立可查询的 real/decoy status token。
- `REG-003` Given 有效验证 token，When verify，Then token consumed、email_verified_at 设置、状态进入 pending_approval。
- `REG-004` Given token 过期/已消费/被新 token 替代，When verify，Then 稳定失败且账户状态不变。
- `REG-005` Given resend 请求，Then 旧验证 token invalidated、新 token 可用、响应不可枚举且受限流。
- `REG-006` Given pending_approval 用户，When 管理员 approve，Then active、approved_by/at 正确、action history 正确、可登录。
- `REG-007` Given pending_approval 用户，When reject，Then rejected、不可登录、重复审批/拒绝返回 409。
- `REG-008` Given real、decoy、invalid 和 expired status token，When 通过 header 查询，Then real 仅返回允许状态、decoy 固定 submitted、invalid/expired 返回相同 410，响应和日志均不泄露 email/user id/token。
- `AUTH-001` Given active user，When 正确密码登录，Then 200、返回短时 access token、设置 HttpOnly refresh cookie、写 success login history。
- `AUTH-002` Given 不存在用户或错误密码，When 登录，Then 两者返回相同 401 外部消息，内部 reason 正确且不记录密码。
- `AUTH-003` Given suspended/deleted user，When 登录，Then 401 且不签发 token。
- `AUTH-004` Given access token 的 iss/aud/alg/exp 任一无效，When 调用 `/auth/me`，Then 401。
- `AUTH-005` Given 合法 refresh，When refresh，Then 旧 session used、新 session 同 family、cookie 被轮换。
- `AUTH-006` Given 同一 refresh token 两个并发请求，Then 最多一个正常 rotation，另一个触发 reuse，family 被撤销，不存在两个可继续刷新的后继 token。
- `AUTH-007` Given 已 logout session，When 再 refresh，Then 401，cookie 清理。
- `AUTH-008` Given 修改密码，Then 密码 hash 改变、auth_version +1、全部 session 撤销、旧 access token 失效、Cookie 清理、重新登录。
- `AUTH-009` Given 登录频率超过阈值，Then 返回 429 + Retry-After；Redis 故障时执行文档规定的安全降级。
- `AUTH-010` Given 缺失/错误 CSRF header 或不受信任 Origin，When refresh/logout，Then 403 且 session 状态不改变。
- `AUTH-011` Given 同一 active 用户连续 10 次密码错误且未先触发外层限流，Then 原子设置 15 分钟锁、内部记录 account_locked、外部保持通用 401；到期后自动清零，成功登录也清零。
- `AUTH-012` Given Redis 限流已命中，When 登录，Then 先返回 429 + Retry-After 且不继续账户验证；Given Redis 故障，Then 公共认证入口统一返回 503 + Retry-After、readiness degraded，多 API replica 下不得 fail-open 或使用进程内计数。
- `PWD-001` Given 已登录用户，When current password 正确且新密码符合策略，Then 改密成功、旧密码失败、新密码成功、历史 hash 记录、全部 session 撤销、返回 204 并重新登录。
- `PWD-002` Given current password 错误、弱密码或复用最近 5 个密码，When change，Then 拒绝且 hash/session 不改变。
- `PWD-003` Given 存在或不存在 email，When forgot-password，Then 均返回相同 202；存在账户只保存 token hash 并由 fake inbox 收到链接。
- `PWD-004` Given 有效 reset token，When reset，Then token consumed、密码改变、auth_version +1、全部 session 撤销；再次使用失败。
- `PWD-005` Given 管理员 reset password，Then 临时密码被 hash、must_change_password=true、全部 session 撤销并写 action history。
- `PWD-006` Given must_change_password 用户已登录，When 访问非 allowlist API，Then 403 `PASSWORD_CHANGE_REQUIRED`；完成改密后全部退出，重新登录后恢复其 RBAC 权限。

### Profile 与 Preferences

- `PRO-001` Given 注册、管理员创建、seed 和 migration backfill 的用户，Then 每人恰有一行 profile/preferences，默认值符合表契约；任一步失败时用户与关联行整体回滚。
- `PRO-002` Given 用户以正确 profile row_version PATCH 本人 display name，Then 仅本人 profile 改变并写脱敏 action history；过期版本返回 409，未知字段返回 422，其他用户资料不可写。
- `PRO-003` Given 本人以正确 current password 修改为可用 username，Then 唯一性/规范化正确、auth_version 与 user row_version 增加、全部 session 撤销、收到通知并需重新登录；错误密码、重复 username 或并发争用不产生部分更新。
- `PRO-004` Given email-change request，Then 响应固定 202、只存 token hash、新邮箱收到确认且旧邮箱收到通知；重复请求使旧 token 失效，按 user/IP 限流，错误 current password 不产生 request，日志/审计不出现 token 或完整邮箱。
- `PRO-005` Given 有效 email-change token，When 确认，Then 在锁内重新检查唯一性、更新已验证邮箱、消费 token、递增版本并撤销全部 session；过期/已用/冲突/两个并发确认均不可枚举且至多一次成功。
- `PRO-006` Given 管理员变更 username 或发起 email change，Then 需要 `users.update` 与最近重新认证，并执行同一唯一性、确认、通知、会话撤销和审计规则；管理员不能直接 PATCH email。
- `PRO-007` Given 用户被软删除，Then profile PII 清空、preferences 重置、全部 email-change request 删除，原 username/email 可复用且备份/日志/action diff 不泄露旧值或目标新邮箱。
- `PREF-001` Given 用户 GET/PATCH preferences，Then 枚举、IANA time zone、page size 和 row_version 校验正确；更新一个字段不覆盖其他字段，过期版本返回 409。
- `PREF-002` Given 用户 A、用户 B 和管理员，Then A/B 偏好严格隔离；管理员可因用户详情读取必要的 Profile，但任何管理 API 都不能修改个人 Preferences。
- `PREF-003` Given page_size/time_zone/density/motion/contrast/theme mode/theme palette 任一值改变，Then 对应列表分页、日期显示、布局、动画或色彩真实改变；不存在已保存但 UI 未使用的 Phase 1 preference。
- `PREF-004` Given 任意 mode × palette × contrast 组合，Then 完整 token 均存在、服务端与客户端枚举一致、文字/控件/焦点满足 WCAG 2.2 AA；非法或未来未知 palette 返回 422 而不是部分应用。

### RBAC

- `RBAC-001` Given user 拥有两个角色，Then effective permissions 是去重并集。
- `RBAC-002` Given 无 `admin.access`，When 请求 `/admin/*`，Then 后端 403，前端不闪现 AdminLayout。
- `RBAC-003` Given 有 `admin.access` 但无 `users.read`，When 访问用户列表，Then 403 且导航不显示用户项。
- `RBAC-004` Given 角色权限变化，Then 受影响用户 auth_version 增加，旧 access token 失效，Redis cache 被清理或自然按新版本隔离。
- `RBAC-005` Given 恰有两个 active 用户拥有 `super_admin` 角色，When 两个管理员并发提交请求、各自移除其中一个用户的该角色，Then 两个事务至多一个成功，另一个返回 409 `LAST_SUPER_ADMIN_REQUIRED`，提交后仍至少有一个 active super-admin。
- `RBAC-006` Given 系统角色，When 删除或修改 code，Then 409/422。
- `RBAC-007` Given 管理员以过期 row_version 更新用户/角色，Then 409 `VERSION_CONFLICT`，不覆盖新数据。
- `RBAC-008` Given Redis 不可用，When 检查权限，Then 回查数据库，不能 fail-open。
- `RBAC-009` Given 普通用户，When 请求他人 session/login history，Then 403 或受所有权过滤而不可见。
- `RBAC-010` Given 管理员为用户替换角色集合，Then user_roles 与请求完全一致、assigned_by/at 正确、auth_version/row_version 增加、旧 token 失效、action diff 正确。
- `RBAC-011` Given 无 `users.manage_roles`，When 尝试授权，即使拥有 `users.update`，Then 403；普通资料修改权限不能隐式授予角色管理权。
- `RBAC-012` Given 角色被停用或删除，Then 不再贡献 effective permissions；仍有关联用户的角色删除按契约返回 409。
- `RBAC-013` Given 任意调用者（包括 super-admin）对 `super_admin` 调用权限集合替换、停用或重命名，Then 409 且角色不变；Given seed 新增权限，Then 同一事务自动加入 `super_admin`，ready check 验证其等于完整 permission catalog。
- `RBAC-014` Given 只有 `users.update` 而无 `users.activate`，When activate suspended 用户，Then 403；拥有 `users.activate` 时只能执行 suspended → active，不能恢复 deleted/rejected 用户或清除临时凭据锁。
- `RBAC-015` Given 用户被软删除，Then 原 username/email 已被唯一 tombstone 替换、敏感值不进入审计；When 使用原标识重新注册，Then 创建新 UUID 的账户。并发删除/注册不得留下重复 active/pending 标识。

- `RBAC-016` Given 非 super-admin 拥有 users.create/manage_roles/reset_password/update，When 自授 super_admin、创建携带 super_admin 的用户或修改任意 super_admin 账户，Then 403 且无状态变更；授权集合超过自身权限、编辑自身角色、分配后启用越权角色也被拒绝。
- `RBAC-017` Given active super-admin，When 管理特权账户但 reauth_password 缺失/错误，Then 拒绝；有效重新认证仍不能破坏最后管理员不变量。并发角色权限变更与授予不能绕过子集检查。

### 幂等、会话和历史

- `CON-001` Given 相同 actor/endpoint/key/hash 的两个并发管理写请求，Then 业务副作用只发生一次，重放得到相同结果或 processing 响应。
- `CON-002` Given 相同 key 但不同 request hash，Then 409，原结果不被覆盖。
- `SES-001` Given 用户撤销自己的其他 family，Then 204，该 family 的 access/refresh 均不可用，本 family 仍有效；旧 rotation 行 id 不能作为另一条可绕过的会话。
- `SES-002` Given 用户撤销他人 session，Then 403。
- `HIS-001` 每种登录事件字段符合表约束，未知用户失败登录允许 user_id NULL。
- `HIS-002` 关键管理动作产生一条 action history，actor/target/result/request_id 正确。
- `HIS-003` 事务失败不产生 success action；敏感字段不出现在 changes/metadata。
- `HIS-004` 普通 GET、health 和页面访问不生成 action history。
- `HIS-005` 普通用户只能查本人 login history；导出接口需要独立 export 权限。

### 运行日志与前端遥测

- `LOG-001` Given 一个带 W3C trace context 的 HTTPS 请求经过 Nginx/API，Then 两侧 JSON log schema 合法、request_id/trace_id 一致、route template/status/duration 可关联，且每条记录恰为一个 JSON object。
- `LOG-002` Given request body/header/query/exception 中放入 password、access/refresh/status token、Cookie、email、完整 IP、DATABASE_URL 等 canary secret，When 产生 access/application/error log 和 Collector export，Then 所有阶段均不存在 canary 原值，redaction 测试失败时 CI 阻断。
- `LOG-003` Given URL query、encoded/rewritten path、path parameter 和恶意引号/换行中含敏感 canary，When Nginx access log，Then `escape=json` 后每行仍是合法 JSON，只输出预期低基数 route_group/脱敏 path；不出现原始 `$request_uri`、raw `$uri`、query/hash/path canary，并能区分 rewrite 前后的受控 route group。
- `LOG-004` Given 合法、跨 Origin、超 64 KiB、超过 20 条、未知字段和超限流的 `ClientErrorBatch`，When `/telemetry/client-errors`，Then 分别得到 202/403/413/422/429；accepted event 只输出 allowlist 字段、不写业务表，并由后端附加 actor/environment/service version，client release 不能覆盖可信属性。
- `LOG-005` Given production frontend，Then ESLint/build 不允许散落 console，source map 不公开；React boundary/unhandled rejection/API failure 可关联 request id 上报，telemetry 超时/失败不会阻塞 UI 且不会持久化敏感队列。
- `LOG-006` Given 日志 exporter 暂时不可用，When Collector 重启，Then bounded persistent queue 恢复并继续发送；队列满时按规定 drop 优先级执行、产生 dropped-record metric/alert，不撑爆磁盘或阻塞 API。
- `LOG-007` Given 某 UTC 日多服务日志，When 日次归档首次执行、失败重试和重复执行，Then 只有一个 completed logical partition，partial 不可见，manifest 的时间范围/record count/checksum 正确，archive 与数据库备份隔离。
- `LOG-008` Given 已归档日志，When 在隔离查询空间执行季度恢复演练，Then checksum/schema/record count 通过，并能用 request id 串联 Nginx→API→client error；演练结果可审计。
- `LOG-009` Given hot/archive/audit 数据超过各自 retention，When lifecycle 执行，Then 只删除到期目标并留下平台审计证据；legal hold/object lock 中的数据不得被提前删除。
- `LOG-010` Given PostgreSQL 整库备份与日志日次归档，Then `${BACKUP_EXTENSION}` bundle 不包含运行日志 archive，login/action history 随数据库恢复，运行日志由独立日志归档恢复，两条流程互不覆盖。
- `LOG-011` Given 测试专用 endpoint/fixture 注入一个已知未处理异常，When 从页面 Support ID 排查，Then 能唯一关联 client event→Nginx→API failed event→exception type/fingerprint/source frame/cause，且响应和日志不泄露内部 stack 给用户。
- `LOG-012` Given PostgreSQL/Redis/邮件/外部 HTTP 分别出现慢调用、timeout、retry 和失败，Then dependency event 包含 operation/duration/outcome/retry/error.type 并能定位瓶颈，但不含 SQL/query text、参数、Redis key/value、URL query/header/body。
- `LOG-013` Given production frontend 发生 React error，Then 上报最多 20 条允许的内存 breadcrumb、正确 Support ID 和 client release；刷新后 breadcrumb 消失，source map 版本不匹配被明确检测，DOM/输入/cookie/storage canary 均不存在。
- `LOG-014` Given 多 service 混合日志、坏行和已轮转边界，When 在 Windows 与 Linux 运行 logs/request/trace 命令，Then 筛选与 follow 结果一致、坏行可见、截断提示明确，并能在无 `grep/jq` 时工作。
- `LOG-015` Given logs/settings/health 中植入敏感 canary，When 生成 diagnostics，Then 包大小/时间窗受限、manifest/checksum 正确、允许诊断信息齐全且所有禁入文件/字段/canary 缺失；目录不会进入 Git 或自动上传。
- `LOG-016` Given development/test/production profile，Then 默认 level 与第三方噪声限制正确、每个 event 只输出一次；logger override 生效时 handler 不截断 DEBUG。production DEBUG 缺原因/expiry、超过 30 分钟或 namespace 不在 allowlist 时启动失败，合法窗口在每个 replica 到期自动恢复并告警，redaction 始终不变。
- `LOG-017` Given 高并发成功请求与重复异常，Then health/static 采样、fingerprint 抑制和 rotation 生效，error/critical 不被常规采样或指纹抑制，日志量/磁盘/CPU 保持在预算内；极端队列耗尽时 drop/backlog 指标准确并立即告警。

### 备份与恢复

- `BKP-001` Given 测试数据库包含表、数据、PK/FK/check、普通/唯一/表达式索引、序列、enum/domain、view、materialized view、function、trigger、RLS policy 和 large object，When 创建备份并恢复到空数据库，Then catalog 对象集合与关键数据一致且应用 smoke 通过。
- `BKP-002` Given 自动创建 150 个额外表、索引和视图，When 备份/恢复，Then 全部自动出现；备份代码和配置中没有表/schema allowlist。
- `BKP-003` Given completed backup，Then `${BACKUP_EXTENSION}` 文件名与实例配置一致且恰含固定 bundle 成员，manifest/TOC/object_count/sha256/Ed25519 signature 正确，数据库密码和私钥不存在于文件或日志。
- `BKP-004` Given pg_dump 非零退出、磁盘不足或上传失败，Then artifact=failed、partial 不可下载、旧 completed backups 不受影响。
- `BKP-005` Given 无 `system.backup`，When list/create/download/delete，Then 403；有权限成功且每个动作写正确 action history。
- `BKP-006` Given bundle 任一字节被修改、key id 未受信/已撤销、Ed25519 签名无效、magic/结构错误或 archive unsigned，When UI/API import，Then 拒绝且绝不调用 pg_restore；仅持有公钥不能伪造有效 bundle。
- `BKP-007` Given compatible trusted bundle，When restore，Then 先成功创建 safety backup，再恢复到新的 template0 database，原数据库仍在线且未修改。
- `BKP-008` Given source/target PG major 不兼容、extension 缺失、目标名冲突或空间不足，Then preflight 失败，不创建/覆盖目标数据库。
- `BKP-009` Given pg_restore 或验证失败，Then restore=failed、不会进入 ready_for_cutover，当前 DATABASE_URL 不改变。
- `BKP-010` Given 两个并发 restore 和并发 backup，Then lease 保证同一时刻最多一个 restore，重复请求不产生两个目标库。
- `BKP-011` Given restore 完成，Then ANALYZE、Alembic revision、TOC/catalog、RBAC 完整性和只读 smoke 结果写入 verification。
- `BKP-012` Given 仅有可信 `${BACKUP_EXTENSION}` bundle、空 PostgreSQL 16、目标 owner 凭据和受信 signing public key，When 按 disaster-recovery CLI/runbook 执行，Then 无需原仓库数据库或签名私钥即可重建全部应用数据库对象和数据。
- `BKP-013` Given backup 正被 restore 引用或 safety backup 仍在保护期，When 删除/retention job，Then 409/跳过；过期且无引用时才删除对象文件并保留脱敏审计。
- `BKP-014` 每月 restore drill 使用隔离数据库真实恢复最近备份；只运行 `pg_restore --list` 不算恢复演练成功。
- `BKP-015` Given source database 名为 A、请求 target database 名为 B，When 常规或 break-glass 恢复，Then archive 不含 CREATE DATABASE、实际只创建/写入 B、从不创建/drop A，所有 pg_restore 命令均不使用 `--create/-C`。

### API 契约

- `API-001` 每个受保护 endpoint 分别测试未登录 401、缺权限 403、正确权限成功。
- `API-002` pagination、最大 page size、排序和筛选稳定，响应形状固定。
- `API-003` 404、409、422、429 使用统一错误 envelope 并包含 request_id。
- `API-004` OpenAPI schema snapshot 变化会触发 api-client 重新生成检查。
- `API-005` 所有用户/session/history 响应均不含 hash、token、Cookie 和敏感 metadata。
- `API-006` OpenAPI 中每个 operationId 在 endpoint matrix 中恰好出现一次且引用的测试 ID 存在；反向也不能有已删除 endpoint 的孤儿记录。
- `API-007` 对每个 endpoint 运行参数化 happy/401/403/422/404-or-409 用例，并校验响应 JSON 符合 OpenAPI schema。

### 前端与 E2E

- `FE-001` 普通用户登录进入 `/app`，只见五个账户导航项，不见任何管理员文字或链接。
- `FE-002` 管理员可进入 `/admin` 并返回 `/app`，两个 layout 的导航和视觉身份明确不同。
- `FE-003` 普通用户手输 `/admin` 显示 403，不发生管理内容闪烁。
- `FE-004` 导航根据 permission 过滤，空分组隐藏，routeConfig 同时生成 breadcrumb。
- `FE-005` 桌面折叠、360px Drawer、Esc、焦点恢复和键盘导航通过测试。
- `FE-006` 用户列表 loading/empty/error/data/pagination 五种状态都有组件测试。
- `FE-007` 角色权限矩阵显示分组、diff、版本冲突和保存结果。
- `FE-008` 多请求同时收到 401 时只发出一次 refresh；失败后统一清理并回登录页，无循环。
- `FE-009` 删除、停用、重置密码、撤销会话均显示包含目标和影响的确认框。
- `FE-010` 浏览器完成注册→Mailpit 获取验证链接→验证→管理员审批→登录的真实流程。
- `FE-011` 浏览器完成忘记密码→Mailpit 链接→重置→旧密码失败→新密码成功。
- `FE-012` 亮度三态 selector 与四种 palette selector 均通过鼠标和键盘切换；任意有效组合跨刷新/设备保持，system 仅在系统媒体查询变化时跟随，首屏无默认色、错误亮度或错误 palette 闪烁。
- `FE-013` Given 共享浏览器依次登录 A、退出、登录 B，Then B 从服务端得到自己的 preference，不短暂显示或继承 A 的主题；未登录页只使用 namespaced anonymous theme。
- `FE-014` Public/Account/Admin 三个 layout 在全部 palette 的 light/dark/high contrast/forced-colors 下通过 axe、程序化 contrast 和关键视觉回归；Admin 在所有组合持续显示明确侧栏和 ADMIN 标识。
- `FE-015` high contrast、comfortable/compact、reduced motion 都改变真实 UI；OS reduced-motion 始终胜出，Preferences 保存 409/网络失败时预览回滚并可重试。

- `FE-016` Given 同一 browser context 中两个标签页 access 过期，When 同时请求 API，Then refresh 串行完成、无误判 reuse、两页均可继续访问；一页退出/改密后另一页清空身份，迟到响应不得恢复登录。rotation 响应丢失时不得自动重放旧 token。
- `SES-003` Given 正常 rotation，Then sid 不变、会话列表仍只有一条；Given family 撤销或到期，Then 旧 access 立即被拒绝，即使 Redis 中仍有权限缓存。

### 部署与并发烟雾测试

- `CFG-001` Given 任一必填模板输入缺失、格式非法、派生值超 PostgreSQL/Cookie/Compose 长度限制或端口重复/越界，When 开始生成或启动，Then 在写业务文件/启动容器前 fail fast，并一次性列出全部错误。
- `CFG-002` Given 一组合法输入完成生成，When 运行 `check_template_values.py`，Then 除通用模板源文件 `docs/prompts/rebuild-rbac-system-v1.md` 精确路径外，受控文件中不存在未解析模板参数、错误模板示例工程名、未登记 literal host port、通用 Cookie 名或绕过集中配置自行拼接的 namespace/origin；删除/移动模板文件后检查范围不会意外变化。
- `CFG-003` Given 同一模板分别使用 A/B 两组 project identity、数据库、Cookie、Redis、镜像、备份扩展名和端口，When 渲染并检查 Compose/config，Then 两组资源完全隔离、应用行为与 OpenAPI 相同，且任何一组都不包含另一组标识。
- `CFG-004` Given shell、`--env-file` 或 `-p` 尝试覆盖本次 `COMPOSE_PROJECT_NAME`，When 启动/config check，Then 一致值可运行，非本次 `PROJECT_SLUG` 的值被明确拒绝；CI 保存脱敏的最终插值摘要作为证据。

- `DEP-001` 容器以非 root 用户运行，启动后 liveness/readiness 正确。
- `DEP-002` migration 作为单独一次性任务执行，两个 API replica 不会同时迁移。
- `DEP-003` 两个 API replica 后无 sticky session 仍可 login/refresh/logout。
- `DEP-004` Nginx 正确传递 request id、Host、X-Forwarded-For/Proto，应用只信任已配置代理。
- `DEP-005` SIGTERM 后停止接新请求、在 grace period 内完成短请求并关闭 DB/Redis 连接。
- `LOAD-001` 使用明确工具对 `/auth/me` 和用户分页接口做基础并发测试，报告并发数、p50/p95/p99、错误率、DB pool 使用，禁止只写“性能良好”。
- `DEP-006` maintenance container 内的 `pg_dump/pg_restore` major 与 PostgreSQL server 匹配；宿主机未安装 PostgreSQL client 时备份/恢复仍可运行。
- `DEP-007` Given production profile，When 探测公网入口，Then HTTP 重定向 HTTPS、TLS 1.2/1.3 成功、TLS 1.0/1.1 失败、证书链/hostname 有效，认证响应包含 Secure Cookie 和预期安全头。
- `DEP-008` Given 伪造 `X-Forwarded-Proto/For` 的公网请求，Then 应用不信任；Given 受信 proxy，Then scheme/client IP 解析正确。HTTPS upstream 使用错误 CA/hostname 时 Nginx 必须拒绝连接。
- `DEP-009` Given production 配置包含明文 public origin、非 Secure refresh Cookie、PostgreSQL 非 verify-full、非 TLS Redis/object storage/SMTP，Then config validation 或 readiness fail closed，服务不得以降级明文方式启动。
- `DEP-010` staging 执行证书/CA 轮换测试，Then 无镜像重建即可加载新材料、旧连接有界退出、健康检查恢复；到期阈值触发告警且日志不包含私钥/token。
- `DEP-011` Given dev CA 已信任且 dev Compose 启动，When Playwright/smoke 访问配置 `DEV_PUBLIC_ORIGIN`，Then hostname/chain 校验成功、Secure Cookie/CSRF/Origin 正常、Vite HMR 通过 WSS；Vite/API 无宿主机 published port，HTTP 或绕过 Nginx 的浏览器访问失败。

- `DEP-012` Given 专用 e2e 容器，Then Chromium/Firefox 均通过同一 DEV_PUBLIC_ORIGIN 完成可信 TLS 与登录；错误 CA/SAN 必须失败，新增测试 listener 未发布宿主机且 production 不存在。
- `DEP-013` Given 本工程已运行且配置相同，When 再次 dev-up，Then 成功且数据不变；外部进程/其他工程/错误绑定占用登记端口时明确失败，不杀进程、不改端口。
- `DEP-014` Given 安装 rootless Quadlet 并满足 linger 前置条件，When daemon-reload/start 与主机重启，Then unit 自动启动且 HTTPS smoke 通过；不对生成 service 执行 enable。

- `DEP-015` Given 实际 provider 启动，When 手工运行 API/maintenance healthcheck，Then exit=0 且容器 healthy；注入探针参数错误或依赖超时必须失败，不能只检查 Up。
- `DEP-016` Given 上游 API/frontend 被重建且地址变化，Then 网关在规定 deadline 内恢复页面/API/WSS，无持续旧 IP 502；测试容器不阻塞测试网关受控重建。
- `DEP-017` Given PostgreSQL 暂时不可用，Then readiness 有界失败、worker 安全退避；恢复后可继续领取新任务，不重复执行失去 lease 的恢复任务，取消退出可完成。
- `DEP-018` Given 重复运行 E2E 或轮换测试 CA，Then Chromium/Firefox 的真实 profile 非交互初始化并通过 canary，旧/错误 CA 仍被拒绝。
- `DEP-019` Given 开发库管理员已改密且有开发数据，When 完整 E2E/smoke 写流程，Then 仅访问测试数据库/Redis/邮件，开发数据、密码与限流状态不变；最终目标误指开发/生产时在首次写入前拒绝。
- `DEP-020` Given 配置检查和备份执行中注入 canary secret，Then argv、终端、CI artifact 与异常日志不含 canary；目录 0700、passfile 0600 可用，成功/失败/取消后临时秘密文件被清理。
- `DEP-021` Given 默认开发、调试、数据库测试、完整 E2E、日志专项测试及单机生产配置，Then 服务集合与第 14 节拓扑表精确一致，数量按生命周期计算；默认开发恰好 7 个，默认不启动一次性任务，生产无开发/测试服务。
- `DEP-022` Given 同一配置连续启动两次和一次失败后重试，Then project/service、卷身份保持一致，不增加副本；额外/未知资源只报告、不自动删除。
- `DEP-023` Given E2E 成功、失败或取消，Then 本次执行器/helper 被清理，本次启动的专用测试服务按所有权停止，开发服务及原有数据卷不变；拓扑文档、JSON 清单与真实 provider/Quadlet 无漂移。
- `DEP-024` Given 干净宿主机尚未信任开发 CA，Then 启动诊断准确报告信任未完成；证书签发、容器 healthy 或指定 CA 的请求成功不能使该项通过。使用同一 CA 安装信任并重启目标浏览器后，实际 HTTPS 登录页无证书警告；系统与浏览器结果分别记录。
- `DEP-025` Given CA 安装权限被拒绝、CAROOT 不匹配、旧服务端证书或 CA 轮换，Then 明确报告对应阶段且不绕过验证；重复安装/签发保持幂等，轮换后新链通过、旧链在隔离信任验证中失败。撤销验证在专用测试信任库进行，不删除开发者共享 CA。
- `CFG-005` Given 模板和实例升级，Then 参数展开除明确标题/实例说明外完全一致；两份版本及 README 一致，所有新增编号唯一，验证报告不能把未执行/环境受限项计入通过。

## 14. Nginx 与云部署基线

### Nginx

为单机/Compose 生产提供真实可用配置：

- 统一对外提供 SPA 和 `/api/` 反向代理；SPA fallback 仅用于前端路由，不能吞掉 API 404。
- 生产入口只接受 TLS 1.2/1.3，HTTP 入口永久重定向 HTTPS；禁止 TLS 1.0/1.1、弱 cipher、压缩和不安全 renegotiation。证书链、私钥和受信 CA 通过只读 secret mount/secret manager 注入，不写入镜像、Git、日志或普通 `.env`。
- HTTP→HTTPS redirect 的目标从受信 `PUBLIC_ORIGIN` 配置生成，不能拼接客户端可控的 `Host`。单机生产非标准端口必须从该 origin 得到准确目标；云端标准 443 不附加内部端口。本地开发不发布额外 HTTP redirect 端口，直接使用 `DEV_PUBLIC_ORIGIN`。
- Nginx 终止 TLS 时必须正确设置 `X-Forwarded-Proto=https`；应用只接受来自显式 trusted proxy CIDR 的 forwarded headers。若反向代理到 HTTPS upstream，必须启用 upstream hostname/SNI 和 CA 校验（等价于 `proxy_ssl_server_name on; proxy_ssl_verify on; proxy_ssl_trusted_certificate ...`），禁止“加密但不验身份”。
- 传递并规范化 `Host`、`X-Real-IP`、`X-Forwarded-For`、`X-Forwarded-Proto`、`X-Request-ID`。
- 应用只信任受控部署输入中的显式 proxy IP/CIDR；只包含必要网关 peer/专用代理网络，禁止 `*` 或把混合服务网络整体视为可信。Nginx 在单跳边界覆写客户端传入的 forwarded headers；多跳边界明确每一跳信任与解析顺序。
- Uvicorn 的 `forwarded-allow-ips` 不会把 `web` 等 hostname 自动解析为可信 IP。不能仅填 service name 就宣称配置生效；采用静态 IP/CIDR、部署层生成允许列表或经 ADR 说明的受控解析适配时，都必须验证容器地址变化、DNS 失败、重复/畸形头及非网关 peer 伪造。自定义适配要禁用重复的框架代理头处理，不得扩大上述信任边界。
- 配置合理的 `client_max_body_size`、header/body timeout、upstream connect/read/send timeout。
- RBAC 普通 API 使用短 timeout；未来 SSE/WebSocket/长任务状态接口使用单独 location，不把全站 timeout 调成数小时。
- WebSocket 预留正确的 HTTP/1.1 Upgrade/Connection 配置；SSE location 关闭不合适的 proxy buffering。
- 静态带 hash 资源使用长期 immutable cache；`index.html` 不长期缓存。
- 上游 API/frontend 容器重建后必须能重新解析地址。按锁定 Nginx 版本配置受信 resolver、DNS TTL 与可用的动态 upstream 能力，或由生命周期脚本在上游就绪后受控 reload/recreate 网关；不能只因 service name 相同就假定不会保留旧 IP。不要照搬包含商业模块的示例，实际重建后必须验证页面、API 与 WSS 不持续返回 502。
- 添加 HSTS（仅全站 HTTPS 后）、nosniff、referrer policy、frame ancestors/CSP 等安全头；CSP 按实际资源最小化。
- 登录限流以应用/Redis 为权威，可在 Nginx 加粗粒度防护，但不能因多 Nginx 副本产生错误安全假设。
- 不缓存认证接口、`/auth/me` 或任何管理 API 响应。

如果云 Load Balancer/Ingress 已处理 TLS、HTTP/2/3、WAF、限流和压缩，评估是否仍需要 Nginx。不要为了“标准架构”无意义叠加两层代理；保留 Nginx 时要写清它仍承担 SPA 静态资源和路由等职责。

### TLS 与传输加密契约

- 浏览器到单机 Nginx 或云 Load Balancer/Ingress 的生产流量必须全程 HTTPS。Secure refresh Cookie 是生产硬约束；检测到 `APP_ENV=production` 且 public origin、Cookie 或 proxy scheme 非 HTTPS 时应用 fail fast。
- 单机部署允许 Nginx→API 在同一台主机的专用 `internal: true` Compose network 上使用 HTTP，但 API 不发布宿主机端口，且该信任边界必须写入 ADR。流量跨主机、跨节点、跨不受信网络或云平台要求时，边缘到 API 必须重新 TLS 加密并校验证书；高安全环境可启用 mTLS。
- PostgreSQL 生产连接固定要求 `sslmode=verify-full`（或 asyncpg 等价的 CA + hostname verification），migration、API、maintenance、`pg_dump`、`pg_restore` 使用相同验证策略；禁止 `sslmode=disable/allow/prefer`。证书轮换不得要求重新构建镜像。
- Redis 生产使用 `rediss://`/TLS、校验 CA 与 hostname，禁止跳过证书验证；托管 Redis 若要求 ACL 用户名或客户端证书，通过 secret manager 提供。
- S3-compatible object storage、邮件 provider API 和所有外部 HTTP 回调只允许 HTTPS 并验证证书。生产 SMTP 必须使用经验证的 STARTTLS 或 SMTPS，若服务端不支持 TLS则发送失败，不能静默降级为明文。
- 备份上传、下载和跨实例迁移的网络传输必须走 HTTPS/TLS；Ed25519 负责真实性与完整性，SSE-KMS/磁盘加密负责静态数据，两者都不能替代 TLS。
- 本地完整栈的唯一浏览器入口为配置 `DEV_PUBLIC_ORIGIN=https://rbac-sys.localhost:31443`，由 Nginx 使用本地受信 CA 证书终止 TLS；不再提供浏览器可访问的 HTTP profile 或直连 Vite host port。Nginx→Vite/API、API→本地 PostgreSQL/Redis 可在同机专用 Compose bridge 内使用明文协议，但这些内部端口不得发布到 LAN。staging 必须与 production 使用相同 TLS 强制策略。
- 提供 `scripts/dev-certs.ps1` 与 `scripts/dev-certs.sh`，使用 mkcert 为已校验的 `DEV_HOSTNAME` 创建 SAN 开发证书；只有当配置显式列出额外 `DEV_CERT_SANS` 时才加入其他 hostname/IP，不能在脚本中写死本机名称。脚本必须幂等、显示将修改的 trust store，并提供撤销说明。CA 私钥、leaf 私钥和生成证书全部 Git ignored，Nginx 只读挂载 leaf certificate/key；只允许把测试所需的公开 CA certificate 复制到临时测试环境。

#### 本机 CA 信任与 Certificate Error 应对（首次启动必需）

证书文件存在、容器 healthy、`curl --cacert` 成功或容器 E2E 通过，均不能证明开发者的宿主机浏览器已经信任 CA。生成工程必须把“签发 → 本机信任 → 部署证书 → 实际浏览器验证”作为可观察的独立阶段，不能在只完成签发时输出“HTTPS 已就绪”。

1. **核对 CA 身份**：使用本次签发所用的 mkcert 二进制、用户和 `CAROOT`。`mkcert -CAROOT` 定位 CA；比较项目公开 `rootCA.pem` 与该目录公开根证书的 SHA-256 指纹，验证 leaf 的签名链、有效期与 `DEV_HOSTNAME` SAN。不能只比较 issuer 文本，也不能用另一个用户或默认 CAROOT 中的新 CA 去“修复”旧证书。只读取公开证书作诊断，不输出或复制 `rootCA-key.pem`。
2. **安装本机信任**：dev-certs 入口必须在实际运行浏览器的宿主机调用 `mkcert -install`，显示 CA 指纹、目标信任库及所需系统权限，并检查退出状态。安装到 Podman VM 或测试容器不等于安装到宿主机。需要系统授权时使用系统正常授权流程；已有明确授权不重复询问。权限拒绝、缺少信任库工具或策略禁止时，明确标记“本机 CA 信任未完成”，提供同一 CAROOT 的人工修复步骤，不假报成功。
3. **覆盖实际浏览器**：Windows/macOS/Linux 的 README 分别说明系统信任库和浏览器/NSS 的差异；按实际 mkcert 与浏览器版本列出依赖和操作方法。`TRUST_STORES` 可以限定 `system`、`nss` 等目标，脚本必须记录实际选择，不能静默跳过目标浏览器。安装后完全退出并重新启动目标浏览器；Firefox/NSS 依赖缺失须给出对应平台安装方法。内嵌浏览器或独立 profile 单独验证，不从系统浏览器结果推断其已通过。
4. **验证部署和访问**：将匹配的 leaf/key 同步给 Nginx 后，核对服务端实际返回的证书指纹与本地期望一致。宿主机使用正常信任链访问 `DEV_PUBLIC_ORIGIN`，再用实际浏览器打开登录页，确认无 Certificate Error、安全警告或手工例外。系统 curl、包管理器 curl、Python/Node 可能使用不同 CA 来源，须记录客户端/TLS 后端并分别判定；一次 curl 失败或成功不能替代所有浏览器结果。未能实际验证的浏览器写“未验证”。
5. **重复运行和撤销**：已正确受信的同一 CA 不应每次重新创建；SAN/有效期变化可在同一 CA 下重签 leaf，真正轮换 CA 时更新所有使用方信任并清除旧信任。README 提供 `mkcert -uninstall`，使用安装时相同 CAROOT 与目标信任库；先列明依赖该 CA 的其他本机项目，避免误撤共享信任。卸载信任不等于删除 CA 文件，普通 stop/down 不撤销信任或删除 CA。

README 必须给出以下命令的 Windows PowerShell 与 macOS/Linux 等价用法，并明确 `mkcert` 应替换为已检测的实际路径；若使用自定义 CAROOT，安装、签发与撤销必须显式保持相同配置。以下命令执行前完成上述身份核对，撤销命令只列在独立卸载流程，不串入启动脚本：

```sh
# 在实际运行浏览器的宿主机执行；此命令只显示 CA 目录
mkcert -CAROOT
# 安装签发当前站点证书的 CA；可能触发操作系统授权
mkcert -install
```

| 现象 | 判定与修复 |
|---|---|
| 默认访问报 unknown issuer / authority invalid / NOT_TRUSTED，指定正确公开 CA 后成功 | 排查对应客户端信任库是否缺少该 CA；完成宿主机/目标浏览器安装并重启后复测 |
| 安装后仍报不受信任 | 比较 CA 指纹、用户/CAROOT、浏览器 profile 和服务端证书；确认信任安装退出状态，禁止盲目反复生成 CA |
| hostname mismatch 或证书过期/尚未生效 | 核对 SAN、DEV_HOSTNAME、系统时间与有效期，重签并同步证书，确认 Nginx 已加载新证书 |
| connection refused / DNS 失败 | 先检查解析、端口和 web 服务；这类故障不能归因为 CA 信任 |
| 容器 E2E 通过、人工浏览器失败 | 分别检查容器与宿主机信任库；测试通过不代表人工访问就绪 |

`curl --cacert` 仅用于定位证书链问题或明确使用专用 CA 的测试，不能冒充默认信任验收；禁止把 `curl -k`、`verify=False`、`ignoreHTTPSErrors=true`、关闭浏览器校验或点击继续访问作为修复办法。生成 `docs/runbooks/tls.md` 中的本机 CA 小节，并在启动结果分别记录证书签发、系统信任、目标浏览器验证状态及证据，不记录秘密。

#### 开发代理与隔离测试证书

- Vite 本身保持内部 HTTP，不安装 `@vitejs/plugin-basic-ssl`，避免形成另一条与生产不同的 TLS 终止路径。开发 Nginx 必须代理 Vite 页面和 HMR WebSocket；Vite 的 internal host/port 由集中配置提供，`strictPort=true`，HMR client 从 `DEV_HOSTNAME/WEB_DEV_TLS_HOST_PORT` 生成 `wss` 地址，禁止 WebSocket 失败后绕过 Nginx 直连未发布端口。镜像标准 internal port 可有集中默认值，但不得与宿主机端口或 project namespace 混用。
- `.env.example`、CORS/Origin allowlist、CSRF Origin 校验、邮件链接、Playwright `baseURL` 和 smoke URL 必须统一读取 `DEV_PUBLIC_ORIGIN`，不得各自拼 hostname/port。本地也保持 refresh Cookie `Secure=true`；不得通过 `ignoreHTTPSErrors=true` 掩盖证书问题，开发机/CI 必须显式信任测试 CA 并验证 hostname。
- E2E 使用独立 `web-test/api-test/frontend-test` 服务；会改变数据的维护流程使用 `maintenance-test`。服务、network、volume 名从 `RESOURCE_PREFIX` 派生，测试 API/worker 只连接测试 PostgreSQL、测试 Redis 和测试 Mailpit，不重配或重启开发 API/web 来切换数据库。测试 Redis 使用独立服务/volume，并保留按 environment 派生的 key namespace；测试邮件不得进入开发收件箱。测试应用不发布额外宿主机端口。
- E2E 仍通过 Nginx 并保持 `DEV_PUBLIC_ORIGIN` 的 hostname、port 和 Cookie/Origin 语义：e2e 使用 `network_mode: service:web-test`（不同时声明 networks/ports），web-test 增加仅监听其命名空间 `127.0.0.1:${WEB_DEV_TLS_HOST_PORT}` 的 TLS listener。浏览器将 `DEV_HOSTNAME` 解析到该 loopback，使用测试 CA 签发的匹配 SAN 证书；不得假定 Node CA 配置等同浏览器信任。测试 listener 不发布宿主机，开发 web 的监听与代理目标保持不变；production 不包含上述测试服务。真实 Podman provider 必须验证 service 网络共享和 hostname 解析。
- `scripts/run_e2e.py` 为跨平台编排入口：检查最终测试配置与数据库身份，构建匹配浏览器镜像、启动独立依赖、执行 `migrate-test/seed-test`、创建受控测试账户、等待 HTTPS canary，再以 `run --rm --no-deps` 执行浏览器。fixture 密码随机生成且不进入 argv/日志；不得依赖 `BOOTSTRAP_ADMIN_PASSWORD` 在开发库中仍有效。失败也要收集脱敏报告并清理本次 fixture/临时容器，禁止泛化 prune 或删除开发卷。重建 web-test 前先关闭共享其命名空间的测试容器。
- E2E CA 准备必须分别覆盖容器操作系统信任库、运行浏览器用户所使用的 Chromium 信任库与 Firefox profile 的受信根设置；具体导入命令按锁定浏览器版本验证并记录。首次及重复启动均须非交互；已存在的信任库不能重复执行会索要密码的初始化，测试用户/profile 更换或 CA 轮换时更新对应公开根证书。公开 CA 只读挂载，信任库/profile 在临时可写目录初始化，不挂载 CA 私钥。`NODE_EXTRA_CA_CERTS` 只解决 Node 侧信任，不能当作两个浏览器已信任的证据；两个浏览器必须在 `ignoreHTTPSErrors=false` 下先运行 HTTPS canary，错误 CA/错误 SAN 也必须失败。
- `docs/runbooks/tls.md` 必须包含证书签发/续期/轮换、CA bundle 轮换、到期告警、私钥泄漏处置、HSTS 渐进启用与回滚。HSTS 只有在整个域名确认 HTTPS 后启用，不能未经评估直接加入 preload。

### 后端、Nginx 与前端日志管理

先区分四类数据，禁止混用：

1. `login_history`、`action_history` 是 PostgreSQL 中的安全审计事实，按数据库事务和数据库备份/PITR 保护。
2. FastAPI、maintenance、migrate/seed 是后端运行日志。
3. Nginx access/error 是边缘访问与代理日志。
4. 浏览器只上报受控的前端错误遥测，不上报完整 console、用户行为回放或任意页面内容。

后端和 Nginx 规则：

- 每条日志是单行结构化 JSON，写 stdout/stderr，不写容器内永久文件。字段至少包含 `timestamp`（RFC 3339 UTC）、`severity`、`service.name`、`service.version`、`environment`、`event.name`、`request_id`、`trace_id`、`span_id`、`route_template`、`http.method`、`http.status_code`、`duration_ms`；worker/job 日志改用 `job_id`/`backup_id`/`restore_id` 等对应 correlation id。
- 只记录 route template 和脱敏维度，不记录原始 query string、完整 URL、request/response body、Authorization、Cookie、token、password、secret、数据库 URL、邮件地址、原始 username、完整 IP、文件内容或异常 locals。错误 stack trace 只用于 warning/error，必须经过统一 redaction，不能把 Pydantic 输入或 ORM 对象整体序列化。
- 自动 instrumentation 即使按 OpenTelemetry semantic convention 默认提供 `url.query`、`client.address`、`user_agent.original` 或 `db.query.text`，本项目也必须在 SDK/Collector 层删除或替换为 route、masked/network classification、browser summary 和代码定义的 query fingerprint；不能因为字段是“标准属性”就绕过隐私 allowlist。
- Nginx access log 固定使用 `log_format ... escape=json`，让引号、反斜杠和控制字符按 JSON string 规则转义。`$request_uri` 含原始 query，任何环境都禁止记录；`$uri` 虽不含 query，但它是可能因 rewrite/internal redirect 改变的当前规范化 URI，也可能含用户 ID/文件名，因此只能作为受控 `map`/redaction 的输入。集中日志只输出低基数 `route_group`（如 `/api/v1/admin/users/*`、`/assets/*`）和必要的脱敏 normalized path，不原样输出 `$uri`。同时透传/生成 request id 并记录 upstream status/latency；健康检查成功日志采样或降级，4xx/5xx 不采样。
- 日志 level 语义固定：预期的用户校验失败不写 error；401/403/409/422 默认 info/warning 并聚合指标；未处理异常、依赖不可用和数据不变量失败才写 error/critical。相同异常必须有 fingerprint 和采样/抑制策略，防止日志风暴。
- request id/trace id 必须在前端错误响应、Nginx、API 和 worker 间可关联。接收外部 `traceparent`/request id 时先做格式与长度校验，不接受客户端伪造 privileged resource attributes。

前端规则：

- 前端提供唯一 `logger/telemetry` facade；生产构建通过 ESLint 禁止散落 `console.log/debug`，只允许该 facade 在本地开发输出。React Error Boundary、`window.onerror`、`unhandledrejection` 和统一 API client 只能上报 `ClientErrorBatch` 定义的 allowlist 字段。
- `/telemetry/client-errors` body 上限 64 KiB、单批最多 20 条；默认每 IP 每分钟最多 10 个请求/60 个 event、每 authenticated user 每分钟最多 120 个 event，校验 exact Origin。服务端附加可信 `received_at/environment/service.version/actor_id`；客户端 `client_release` 明确标记为 untrusted display attribute，只接受受限格式，不能覆盖服务端 release。浏览器不能提交 user id、email、IP、任意 metadata key 或 privileged resource attribute；重复 `event_id` 只做 bounded best-effort 去重，不创建业务表。
- `sanitized_message/stack` 在客户端先清理、服务端再次 allowlist/redact；禁止采集表单值、DOM、剪贴板、键盘输入、截图、session replay、localStorage/sessionStorage、Cookie、URL query/hash 和 API body。telemetry 发送失败不能阻塞 UI、登录或导航；使用有界内存批次与退避，刷新页面后不持久化敏感队列。
- 生产 source map 不随静态站点公开；按 release 上传到受限的错误分析/日志系统。日志中只保存 release 和 stack frame，访问 source map 需要运维权限并受审计。

### 可调试性与开发排障工作流

日志必须能真实回答“哪一个请求、在哪个版本、经过哪些组件、在哪一步失败、依赖耗时多少”，不能只有一条模糊的 500：

- 环境 profile 固定：development 对本项目 namespace 默认 DEBUG、第三方库默认 WARNING；test 默认 INFO，测试失败时自动附加相关 request/trace 的 DEBUG capture；staging/production 默认 INFO。error/critical、安全不变量失败和审计事件永不采样，成功 health/static 请求可以采样或抑制。
- Python logging 使用点分层级命名 logger；初始化 `dictConfig` 时固定 `disable_existing_loggers=False`，顶层 handler 配置一次，子 logger 默认 `propagate=True`，禁止重复挂 handler 造成一条事件输出多次。per-logger override 通过 allowlist 后调用等价的 `logging.getLogger(name).setLevel(level)`；handler threshold 必须不高于所有已批准 override，否则 logger 已是 DEBUG 但事件仍会被 handler 丢弃。第三方 namespace 显式保持 WARNING。
- override 例如 `LOG_LEVEL_OVERRIDES=app.auth=DEBUG,app.db=DEBUG`；未知 namespace 启动失败。非 development 开启 DEBUG 必须同时配置工单/原因和不超过 30 分钟的 `DEBUG_LOG_EXPIRES_AT`。每个 replica 的 `DebugWindowController` 在启动时校验 UTC expiry，并用 monotonic timer 到期恢复原 level、产生 `debug_window_started/expired` 告警；不得提供 Python `logging.config.listen()`、公网管理端口或无审计的动态 level API。提升 level 绝不能关闭 redaction 或扩大字段 allowlist。
- 每个请求至少产生 `http.server.request.started`（DEBUG）和 `http.server.request.completed`（INFO）或 `http.server.request.failed`（ERROR），共享 request/trace id。completed/failed 包含 route、method、status、duration、response_size、release 和 replica，但不含原始 URL/query/body。
- 为 PostgreSQL、Redis、邮件、对象存储和外部 HTTP 调用记录结构化 dependency event/span：`dependency.system`、代码定义的低基数 `operation.name`、duration、outcome、retry_count、timeout 和低基数 `error.type`。数据库只记录 `db.operation.name` 与代码定义的 repository operation/query fingerprint，固定禁止 `db.query.text`、SQL 参数和 `SQLALCHEMY_ECHO=true`；Redis 不记录 key/value，HTTP client 不记录 query、认证 header 或 body。
- 未处理异常记录清理后的 `exception.type`、`error.type`、stack trace、代码文件/函数/行号、cause chain 和 fingerprint；`exception.message` 只有经过统一 sanitizer 后才能进入日志，禁止 locals、frame variables 和完整输入模型。预期业务异常记录稳定 error code，不生成噪声 stack。
- 关键状态机记录 before/after 的非敏感状态 code 和 entity id：注册、审批、session rotation/reuse、RBAC cache invalidation、backup/restore step、邮件发送 attempt。运行日志用于排障，不能替代同事务 action history。
- 服务启动只记录安全配置摘要和 fingerprint，例如 environment、release/git sha、Alembic revision、feature/capability 布尔值、pool size、timeout；禁止打印完整 settings、environment variables 或 connection URL。

前端排障能力：

- 前端 logger 在 development 提供带 timestamp/level/event/request id 的可读 console renderer，同时保留结构化对象；生产不输出 debug console。内存中最多维护 50 条脱敏 breadcrumb，仅允许 route name 变化、API operationId/status/duration/request_id、feature boundary 和 error event，错误上报最多携带最近 20 条。
- breadcrumb 禁止按钮输入值、搜索词、URL query/hash、DOM、用户文本和身份信息；刷新/关闭页面即清空，不写任何浏览器持久化存储。它是错误上下文，不得演变成行为分析或 session replay。
- API client 从响应 `X-Request-ID` 与标准 trace header 提取关联信息。所有用户可见的未知错误页/Dialog 显示可复制的 `Support ID`（request_id；无请求时使用 client event_id），管理员与普通用户看到相同的非敏感 ID，不显示 stack 或内部原因。
- 开发 Error Boundary 同时显示 component stack、source-mapped frame 和最近安全 breadcrumb；production 只显示 Support ID。source map 解析必须匹配 `client_release`，不匹配时明确标记，不能错误映射到当前版本。

开发者工具必须跨 Windows PowerShell 与 macOS/Linux 可用，不能要求手工组合 `grep/jq`：

- 提供 `scripts/dev_logs.py`、`scripts/collect_diagnostics.py`，以及根命令 `make logs`、`make logs-api`、`make logs-request REQUEST_ID=...`、`make logs-trace TRACE_ID=...`、`make diagnostics SINCE=30m`。README 还必须给出不依赖 make 的 PowerShell/POSIX 直接 Python 命令。日志脚本从 `podman compose logs --no-color --timestamps` 读取并严格解析 JSON，支持 service/level/event/request_id/trace_id/time range/follow/filter，坏行单独标记而不是导致整个查询失败。
- development runtime log 默认每 service `20 MiB × 10 files`，且最长保留 7 天，取先到者；`.env.example` 可在设定上限内调整。脚本必须显示截断/轮转边界，不能让开发者误以为结果完整，也不能通过无限日志占满 Podman machine 磁盘。
- `make diagnostics` 生成最大 100 MiB、默认最近 30 分钟的 `.local/diagnostics/<UTC timestamp>/` 脱敏诊断包，只包含筛选后的 NDJSON、compose ps/health、版本/git sha/Alembic revision、前后端 release、非敏感配置 fingerprint 和 manifest/checksum。禁止包含 `.env`、secret、证书私钥、数据库 dump、Cookie/token、用户上传文件或原始业务数据；目录 Git ignored，7 天自动清理且绝不自动上传。
- README 必须给出四个真实排障示例：从页面 Support ID 查到 API exception；定位慢 PostgreSQL/Redis dependency；定位 refresh 并发/reuse；定位前端 release/source-map 不匹配。每个示例写明预期事件链和无结果/日志已轮转时的下一步。

采集与故障规则：

- 单机/云部署由 OpenTelemetry Collector 或等价托管 agent 从 stdout/stderr 采集，先执行 attribute allowlist、redaction/filter，再 batch/export。日志记录携带 trace/span id 以支持关联，但 login/action history 仍以 PostgreSQL 为唯一事实来源。
- 本地开发只要求经过大小/文件数限制的 Podman runtime logs 和 `podman compose logs`，不要求常驻 Collector。Linux 单机生产优先让 Podman 使用 journald（或经验证的只读 runtime log source），Collector 只读取本项目标签对应记录；云环境使用平台 DaemonSet/agent。不得为了采集日志把可控制容器的 engine socket 以读写方式挂给 Collector。
- Collector exporter 启用 retry 和有界 persistent sending queue；队列使用独立加密 volume、限制磁盘占用并监控 backlog/dropped records。队列只是短期断路缓冲，不是日志归档；后端请求不能因为普通运行日志 exporter 失败而无限等待。
- Collector 的 OTLP、health 和管理端口只允许 internal network，不发布宿主机或公网。配置、队列容量、drop 优先级和 exporter endpoint 写入 `deploy/otel-collector/`，secret 由 secret manager 注入。
- critical 安全事件在数据库事务提交后可镜像到不可变安全日志流；镜像失败不得伪造业务事务失败，但必须产生告警。禁止从运行日志反向重建 login/action history。

### 日志日次归档、保留与恢复

生产日志必须考虑日次归档，但它不是 `${BACKUP_EXTENSION}` bundle 的成员，也不能由管理员数据库备份/恢复 UI 管理：

- 默认策略：开发日志最多保留 7 天并配置容器 runtime 有界轮转；生产集中日志热查询 30 天，每日按 UTC 封存前一自然日分区到独立私有 log-archive bucket，默认保留 180 天；PostgreSQL 中 login/action history 默认在线保留 365 天并随整库备份/PITR 保护。法规、隐私和成本要求改变这些数值时必须形成 ADR 和删除验证。
- 托管日志平台若已经提供跨可用区冗余、不可变保留和满足上述期限的每日导出/归档，可直接作为实现，不再重复打包；自建日志系统必须把每日 archive 写到与数据库备份、业务对象不同的 bucket/prefix 和 IAM principal。
- 日次归档由日志平台 scheduled export 或独立 observability scheduler/IaC 管理，不由 FastAPI 请求、浏览器或数据库 `maintenance` worker 执行；日志平台故障不能占用业务数据库事务或备份/恢复 lease。
- 每个 UTC 日归档包含分区对象与 manifest，记录环境、服务、起止时间、record count、schema version、对象 checksum 和导出状态。使用 TLS、SSE-KMS、versioning、生命周期规则和最小权限；需要取证/合规时启用 object lock/WORM。日志 archive 密钥和数据库备份签名私钥不得复用。
- 日次任务必须幂等：同一 environment/service/date 重跑不能产生未追踪重复；partial 不可标记完成。监控 latest successful archive age、export lag、失败次数、bucket 写入失败、collector queue 和 drop count；生产归档超过 26 小时未成功必须告警。
- 每季度抽取一个已归档 UTC 日恢复到隔离查询空间，验证 checksum、record count、时间范围、schema 可读性，并用 request id 关联 Nginx→API→错误事件；只验证“对象存在”不算恢复演练成功。
- 日志归档到期删除由对象存储 lifecycle 执行并生成平台审计证据。用户数据删除/隐私请求必须按照 retention ADR 处理日志中的可识别字段；禁止为了方便无限期保留。
- Phase 1 不在 RBAC 管理控制台新增原始运行日志浏览/下载页面，也不允许管理员从应用 API 任意查询 Collector 或 bucket；运维通过受限日志平台/IAM 查询，安全审计页面仍只展示经过业务授权和脱敏的 login/action history。
- 提交 `docs/observability/log-schema.md`、`docs/runbooks/log-pipeline.md` 和 `docs/runbooks/log-archive-restore.md`，分别定义字段/schema version、采集故障/敏感数据处置、日次归档与恢复。`.env.example` 至少给出 `LOG_LEVEL`、`LOG_LEVEL_OVERRIDES`、`DEBUG_LOG_EXPIRES_AT`/原因、本地 rotation size/file count、hot/archive/audit retention days、archive bucket/prefix、export lag alert threshold；真实 endpoint、KMS key 和凭据只来自 secret manager/IaC。

### 服务拓扑、数量与生命周期（强制生成契约）

Compose project 是应用资源分组，不是嵌套容器；不得为了界面分组另加包装容器或 Pod。以下数量按单副本、已完成初始化的运行服务计算，不含镜像、network、volume、Pod infra 容器、已退出任务或瞬时构建步骤。九个宿主机登记端口不等于九个必须常驻的容器。不得擅自增删、合并、改名或复制服务；变更必须先更新本表、ADR、启动脚本和验收预期。

| 固定 service key | 用途及停用影响 | 环境 / Compose profile | 生命周期 |
|---|---|---|---|
| `web` | Nginx HTTPS 入口；停止后浏览器入口不可用 | dev/prod；无 profile | 常驻，1 个 |
| `frontend` | Vite 开发页面与 HMR；停止后开发页面不可用 | dev；无 profile | 常驻，1 个；prod 静态产物由 web 提供 |
| `api` | 认证、RBAC、会话和审计接口 | dev/prod；无 profile | 常驻，1 个 |
| `postgres` | 业务数据库，承载持久业务数据 | dev/prod；无 profile | 常驻，1 个 |
| `redis` | 认证限流等依赖；不是可随意关闭的缓存 | dev/prod；无 profile | 常驻，1 个 |
| `maintenance` | 备份/恢复任务及过期数据清理；停止后相关任务无法正常推进 | dev/prod；无 profile | 常驻，1 个 |
| `mailpit` | 开发邮件收件箱，用于验证、重置密码等流程 | dev；无 profile | 完整开发常驻，1 个；prod 使用真实邮件服务 |
| `postgres-test` | 自动化测试专用数据库，不连接开发数据卷 | dev/test；`test` | 按需，1 个 |
| `redisinsight` | Redis 管理 UI；应用不依赖它 | dev；`debug` | 按需，1 个 |
| `redis-test` | 隔离测试限流和 Redis 数据 | test；`test` | 测试期间，1 个 |
| `mailpit-test` | 隔离测试邮件 | test；`test` | 测试期间，1 个 |
| `api-test` | 连接测试依赖的后端 | test；`test` | E2E 期间，1 个 |
| `frontend-test` | 测试前端，只经 web-test 访问 | test；`test` | E2E 期间，1 个 |
| `web-test` | 测试 HTTPS 入口及浏览器共享网络命名空间 | test；`test` | E2E 期间，1 个 |
| `maintenance-test` | 测试备份/恢复和清理流程，不操作开发资源 | test；`test` | E2E 期间，1 个 |
| `otel-collector` | 本项目日志采集、转发和持久队列 | 单机 prod 无 profile；test 为 `observability` | 单机生产常驻，1 个；日志专项测试按需 |
| `migrate` / `seed` | 开发/生产受控迁移与初始化，凭据与 API 隔离 | dev/prod；`tools` | 两种独立一次性任务，串行 `run --rm` |
| `migrate-test` / `seed-test` | 仅操作测试数据库的迁移与初始化 | test；`test-tools` | 两种独立一次性任务，串行 `run --rm` |
| `e2e` | 预装匹配版本的 Chromium/Firefox 的测试执行器 | test；`e2e` | 一次性 `run --rm --no-deps` |

| 场景 | 精确启动集合 / 预期运行数量 |
|---|---|
| 默认完整开发 | web、frontend、api、postgres、redis、maintenance、mailpit：**7 个** |
| 开发 + Redis 调试 | 默认 7 个 + redisinsight：**8 个** |
| 开发 + 仅数据库测试依赖 | 默认 7 个 + postgres-test：**8 个**；测试进程在宿主机执行，不计入容器 |
| 开发 + 上述两项辅助 | 默认 7 个 + postgres-test + redisinsight：**9 个** |
| 完整后端测试 | postgres-test、redis-test、mailpit-test：**3 个依赖服务**，执行中的 api-test 一次性 pytest 容器使运行总数为 **4 个**；由 run_backend_tests.py 编排 |
| 独立完整 E2E | postgres-test、redis-test、mailpit-test、api-test、frontend-test、web-test、maintenance-test：**7 个测试服务**，加执行中的 e2e 为 **8 个**；迁移和 seed 在浏览器启动前串行结束 |
| E2E 与默认开发并行 | 7 个开发服务 + 7 个测试服务 + 1 个执行器：**15 个**；若 postgres-test 已存在则复用该测试服务，不创建第二个副本 |
| 日志专项测试 | 完整 E2E 集合额外启用 otel-collector：测试服务 **8 个**，执行器运行时 **9 个** |
| Linux 单机生产基线 | web（含前端静态产物）、api、postgres、redis、maintenance、otel-collector：**6 个**；迁移/seed 不计入常驻数；SMTP、对象存储和集中日志后端是外部依赖 |

云环境使用托管数据库/Redis/日志 agent 或增加 API replicas 时，必须另交付显式拓扑与数量公式，不能冒用单机生产的 6 个验收值。production 合并配置不得包含 frontend、Mailpit、RedisInsight 或任何 `*-test`/e2e service，即使被 profile 禁用也不允许夹带。

- profile 固定为 `debug`、`test`、`tools`、`test-tools`、`e2e`、`observability`；不要把环境名与 Compose profile 混为一谈。默认入口拒绝隐式 `COMPOSE_PROFILES` 扩大启动集合；禁止使用 `--profile '*' up` 启动全部服务和一次性任务。显式指定 profiled service 会启动该服务及依赖，不会自动启动同 profile 的全部服务。必须按实际 provider 验证依赖图，默认服务不得依赖可选服务。
- 默认开发使用 base + dev 文件；完整测试使用 base + test 文件且显式指定上述测试服务集合，禁止裸 `up` 顺带启动 base 中的开发依赖。`postgres-test` 及其他测试专用 service、network、volume、secret 声明只放 `compose.test.yml`，不放 base/dev/prod。仅需测试数据库时也使用 base + test 并显式指定 `postgres-test`；所有测试入口使用同一文件顺序和测试资源身份。base 中服务不得依赖测试定义，测试服务网络、数据卷和凭据保持隔离。
- 调试仅显式启动 `redisinsight`；仅数据库测试依赖仅显式启动 `postgres-test`。E2E 脚本显式启动 7 个测试服务，等待健康后执行测试 migration/seed，再运行 e2e。日志专项测试显式增加 collector。任务不配置永久 restart；依赖就绪后任务使用 `--no-deps`，避免启动集合扩大。
- 生成 `docs/container-topology.md` 和机器可读 `deploy/service-topology.json`，逐项记录 service key、用途、配置文件、场景/profile、依赖、镜像来源、端口变量、卷/读写用途、健康检查、数量、任务退出/清理规则。二者与 Compose/Quadlet 进行自动 drift 检查；README 给出默认/测试/调试/生产精确命令和预期数量，不能只写“启动全部容器”。
- 创建前验证最终配置、provider、项目身份、端口和已有资源；使用同一 project/service 身份幂等协调。禁止用随机 project name、数字后缀、新 volume 或手工 `podman run` 反复试建长期服务来绕过错误。因平台文件共享限制需要临时 helper 时，事先登记用途、唯一任务标识和清理策略，在 finally 中只清理本次 helper。
- 重复启动不能增加服务副本或生成新数据卷。失败须保留脱敏阶段日志和资源清单，修复后重试同一服务；不得以“退出”“未打标签”或“当前未挂载”单独判定垃圾。报告额外资源的 ID、归属、来源、状态、挂载和删除影响，经明确授权后才定向删除；普通停止不删卷，不执行全局 prune。
- E2E 结束（成功、失败、取消）清理执行器、fixture 和本次创建的临时 helper，停止本次启动且未被其他任务使用的测试服务，保留运行前已有服务和数据卷；不能在共享 project 上执行会停止开发服务的 `down`。记录运行前后差异，退出容器与持久卷数量单独报告。

### 容器和发布

- 分离 `web`（Nginx）、`api`、`maintenance` 和一次性 `migrate`；Phase 1 已包含 maintenance worker，未来通用任务 worker 不在本期范围。生产容器一个 API 进程，由平台复制；单机 Compose 才可评估单容器多个 worker。
- 镜像多阶段构建、固定基础镜像版本、非 root、最小运行依赖、只读 root filesystem（必要临时目录单独挂载）。
- 配置全部来自环境变量/secret manager；提供无真实值的 `.env.example`。立即轮换仓库历史中暴露过的密钥。
- migration 是部署前单实例 job，失败则阻止新版本上线；API replica 不在 startup 自动迁移。
- 支持 rolling deploy、readiness gate、graceful shutdown、明确 termination grace period。
- CORS 只允许配置的确切 origin；生产禁止 `*` 搭配 credential。

### 云资源

- 优先托管 PostgreSQL 和 Redis；启用加密、私网访问、自动备份、PITR、维护窗口和告警。
- PostgreSQL/Redis 与应用分开扩缩容；对 DB connection 数设置容量预算，必要时使用 PgBouncer。
- 至少区分 dev/staging/prod，使用不同数据库、Redis、密钥和域名；禁止共享生产数据。
- DNS、TLS 证书续期、WAF/DDoS、出站访问策略和安全组写入 runbook。
- API 保持无状态，不依赖本地磁盘和 sticky session；未来文件使用对象存储。
- 备份 bucket/container 与普通业务文件隔离，启用私有访问、SSE-KMS、versioning、object lock（若合规需要）、生命周期和最小权限；下载优先使用短时、一次性受审计 URL 或流式响应，禁止 API 把整个 archive 读入内存。
- API 数据库账号不得拥有 CREATEDB、DROP DATABASE 或 superuser；maintenance 使用单独 secret 和最小化 backup/restore 角色。云厂商不允许在实例内创建目标数据库时，restore adapter 必须恢复到新托管实例/数据库，不能提升 API 权限绕过限制。
- 备份必须定期做恢复演练，不能只验证“备份任务成功”。
- 日志采集、脱敏、热存储、日次归档和保留严格执行本节日志契约；云日志服务不能只开默认无限保留或只依赖容器本地文件。
- 暴露 RED 指标：request rate、error rate、duration；另监控 DB pool、Redis、登录失败率、refresh reuse、403/429、活跃 session。
- 使用 OpenTelemetry 兼容的 logs/traces correlation；敏感认证数据不得进入 log attribute、span 或 resource attribute。
- 为依赖漏洞、镜像扫描、SBOM、secret scanning 和最小权限云 IAM 建立 CI/发布门禁。

## 15. Podman、uv 与本地开发契约

README 必须分别提供 Windows PowerShell 与 macOS/Linux 命令，所有命令从仓库根目录可复制执行。不得只写“安装依赖并启动”。

### 环境职责矩阵

| 环境 | 依赖与质量工具 | 服务运行方式 | 硬约束 |
|---|---|---|---|
| development | 宿主机使用 uv 管理 Python、npm 管理前端；也可在工具容器执行同一锁定命令 | 完整依赖与浏览器入口由 rootless Podman Compose 启动 | uv/npm 不代替 PostgreSQL、Redis、Mailpit、RedisInsight、Nginx；浏览器仍只走 HTTPS Nginx |
| test/CI | `uv sync --locked`、`npm ci`、独立 Playwright E2E 镜像 | 隔离的 `postgres-test`、Redis、Mailpit 和测试 Compose profile | 不复用开发库/volume；不得在应用启动时下载依赖或浏览器 |
| staging/production | 构建流水线消费 lockfile；目标主机不要求安装 uv、npm 或编译器 | 只运行已扫描、签名且锁定 digest 的 Podman 镜像 | 不 bind-mount 源码/`.venv`/`node_modules`，不在容器启动时安装依赖，不启用 Mailpit/RedisInsight |

uv 负责 Python 依赖、虚拟环境和后端命令；npm 负责前端依赖与构建；Podman 负责跨平台基础设施、完整栈和生产镜像运行。三者是分层职责，不得把“开发/测试使用 uv、生产使用 Podman”错误实现为互斥方案。

### 工具检查

首次运行先执行并记录：

```text
podman --version
podman info
podman compose version
uv --version
python --version
node --version
npm --version
mkcert -version
curl --version
```

- 支持 Podman Desktop（Windows/macOS）和原生 Podman（Linux）。Windows/macOS 必须说明 `podman machine init/start`，但在 machine 已存在时不得重复创建。
- `podman compose` 是对外统一命令；启动前验证 compose provider。项目脚本不得直接依赖某个未声明的 `docker-compose` 二进制。
- 开发者只通过 `uv add/remove/sync/lock/run` 管理 Python 环境，不允许 `pip install` 污染项目 `.venv`。
- dev-certs 脚本只检测并调用 mkcert，不自动从网络下载安装二进制；README 必须给出 Windows/macOS/Linux 的官方安装与 trust-store 撤销步骤。CI 使用隔离测试 CA，不修改开发者 trust store。
- `.venv`、Node `node_modules`、测试缓存和本地数据目录不进入 Git 或容器 build context。

### Git 与构建上下文卫生

- 根目录必须提供完整 `.gitignore`，至少忽略实际 `.env` 与 `.env.*` 秘密文件（显式反向保留 `!.env.example`）、`*.key`/CA 私钥/生成的开发 leaf certificate、`.venv`、`node_modules`、Python/TypeScript/Vite 缓存、coverage、Playwright `test-results`/report/trace/screenshot/video、`.local/diagnostics`、运行日志、数据库文件、备份 bundle、编辑器和操作系统临时文件。公开模板、migration、lockfile、测试 fixture 和经批准的公开测试 CA 不得被宽泛规则误伤。
- 根目录以及 backend/frontend 等独立 build context 必须提供 `.containerignore` 或 provider 支持的等价文件，排除 `.git`、`.env*`、私钥/证书生成物、宿主机 `.venv`/`node_modules`、测试报告、coverage、diagnostics、日志、备份和本地数据。Containerfile 只能显式复制构建所需 manifest、lockfile 与源码，禁止 `COPY . .` 把秘密或无关产物带入镜像；必须用镜像层检查证明 `.env`、私钥和测试产物不存在。
- CI 必须运行 `git check-ignore` fixture、build-context 清单检查、secret scanning 和生成镜像内容检查：敏感 fixture 必须被忽略，`.env.example`/lockfile/migration 必须仍受版本控制；发现真实 token、密码、数据库 URL 凭据或私钥立即失败。README 不得建议用 `git add -f` 绕过规则。

### 参数化端口与服务

本工程拥有的所有宿主机 TCP/UDP 监听端口必须位于闭区间 `30000–39999`。这包括 Compose 端口映射、本机开发服务器、测试 webServer、调试器、mock server、metrics/管理端口和未来新增服务；不得使用工具默认的 5173、8000、5432 等宿主机端口。容器内部端口可保留镜像标准值，云 Load Balancer 对公网提供的 80/443 可映射至本工程 30000–39999 范围内的后端端口；操作系统自动分配的客户端临时端口不属于本契约。

| Service | Container port | Host port | 环境变量 | 说明 |
|---|---:|---:|---|---|
| web/nginx dev HTTPS | 443 | `31443` | `WEB_DEV_TLS_HOST_PORT` | 本地完整栈唯一浏览器入口；开发 CA |
| web/nginx production HTTP redirect | 80 | `31080` | `WEB_REDIRECT_HOST_PORT` | 只跳转到 HTTPS |
| web/nginx production HTTPS | 443 | `31444` | `WEB_TLS_HOST_PORT` | 单机生产唯一业务入口 |
| frontend/Vite | 5173 | — | — | 仅 Compose internal network；页面/HMR 均经 dev Nginx/WSS |
| api | 8000 | — | — | 仅 Compose internal network；调试使用 logs/exec，所有黑盒请求走 HTTPS Nginx |
| postgres | 5432 | `35432` | `POSTGRES_HOST_PORT` | 仅开发暴露 |
| postgres-test | 5432 | `35433` | `POSTGRES_TEST_HOST_PORT` | 自动测试专用，不复用开发库 |
| redis | 6379 | `36379` | `REDIS_HOST_PORT` | 仅开发暴露 |
| RedisInsight | 5540 | `35540` | `REDISINSIGHT_HOST_PORT` | dev-only 运维 UI；仅 loopback |
| mailpit SMTP | 1025 | `31025` | `MAILPIT_SMTP_HOST_PORT` | 开发/测试邮件 |
| mailpit UI | 8025 | `38025` | `MAILPIT_UI_HOST_PORT` | 查看验证/重置邮件 |
| otel-collector OTLP/health | 4317/4318/13133 | — | — | 仅 production/test profile internal network，不发布到宿主机 |

- 每次生成时必须由调用者为上表九个宿主机端口提供显式值；模板不提供可被多个工程重复采用的默认端口。`.env.example` 写入本次已经校验的值并注明可按注册表整体调整；Compose 通过 `${DEV_BIND_ADDRESS:?required}:${VARIABLE:?required}:容器端口`（或等价 long syntax）绑定开发基础设施，`DEV_BIND_ADDRESS` 的安全默认值在环境配置中设为 loopback，不能省略 host IP 后监听所有网卡，也不能省略 published port 后随机分配。Vite 等 internal-only 服务不得出现 `ports`，只允许使用 `expose`/容器网络。
- `docs/ports.md` 是唯一端口注册表。任何新增监听端口必须先登记用途、环境变量、协议和冲突检查，再进入配置；禁止在源码、脚本和 CI 中散落未登记 magic port。
- 提供跨平台 `scripts/check_ports.py`，检查 Compose 最终插值配置、`.env.example`、Vite、Uvicorn、Playwright、Nginx 和测试配置：所有项目拥有的宿主机固定监听端口必须在 `30000–39999`、工程内无重复、与 `docs/ports.md` 一致，并可读取同机共享端口登记文件做跨工程冲突检查。CI 和 `make ci` 必须运行该检查；找不到共享登记文件时明确报告“仅完成工程内检查”，不能伪称同机无冲突。
- 启动脚本必须在拉起服务前探测目标端口。只有经 Podman inspect 核实属于当前 project/service、绑定地址和 published port 与本次配置一致的运行容器，才视为本项目重复启动并继续幂等流程；外部进程、其他工程、配置不一致或无法验证归属的占用均列出用途与证据后退出。不能仅按进程名或端口开放认定本项目，不能静默改端口或终止占用者；检查后实际 bind 失败也必须明确报错。
- Pytest 后端集成测试优先使用 HTTPX ASGI transport，不创建宿主机监听端口；确需真实 socket 的测试只能使用注册表中预留的 30000–39999 端口并串行管理生命周期。

`maintenance` 为无端口后台服务，使用与 API 同版本代码但单独入口，并在镜像内安装 PostgreSQL 16 client。otel-collector 同样不得发布宿主机端口。RedisInsight 是 dev-only 运维 UI，必须使用独立 `${RESOURCE_PREFIX}redisinsight-data` 命名 volume、`/api/health/` healthcheck、对 Redis healthy 的依赖和 loopback host binding；不得被 API 或 production 服务依赖。单机生产按拓扑表创建内部 PostgreSQL、Redis、API、maintenance、Collector 及其必要持久卷，但不得向宿主机发布这些服务的数据库、调试或管理端口。Mailpit、RedisInsight 和全部测试专用服务及其资源声明不进入生产合并配置；生产浏览器入口仅由 web 发布。

### Windows 与 Linux 服务启停文档

README 必须把 Windows PowerShell 和 Linux POSIX shell 作为两个同等支持的一等入口，分别给出从全新 checkout 到服务可访问的完整、可复制命令；不得只给一套 Bash 命令后要求 Windows 用户自行翻译，也不得要求 Windows 用户必须安装 WSL。两套说明必须使用相同的 `.env`、Compose 文件、service 名、迁移和 seed 顺序，并至少覆盖：

1. 前置工具安装/版本检查、复制 `.env.example` 为 `.env`、配置秘密和运行 `scripts/check_template_values.py`、`scripts/check_ports.py`。
2. 按第 14 节核对签发 CA 身份并安装宿主机信任，再生成/复用开发证书；Windows 调用 `scripts/dev-certs.ps1`，macOS/Linux 调用 `scripts/dev-certs.sh`。检查实际安装结果；未完成信任时不得继续宣称首次启动成功。
3. 检查 Compose provider、执行 `podman compose ... config --quiet` 与最小实际 build、构建镜像、启动 PostgreSQL/Redis/Mailpit（RedisInsight 与测试数据库按需启动）、运行 Alembic migration、执行幂等 seed，再启动 API/frontend/Nginx/maintenance。
4. 使用 `podman compose ps` 和 health URL 验证服务，列出 `DEV_PUBLIC_ORIGIN`、Mailpit UI、RedisInsight UI、PostgreSQL 与 Redis 的本机和容器网络连接方法。README 使用表格明确 host、container/host port、database、用户名对应的环境变量和密码/secret 来源；必须说明 bootstrap 管理员 username/email/password 分别来自 `BOOTSTRAP_ADMIN_USERNAME`、`BOOTSTRAP_ADMIN_EMAIL`、`BOOTSTRAP_ADMIN_PASSWORD`。只允许写变量名和安全取值方法，不得记录实际密码、完整含凭据 URL、token，命令也不得在参数、输出示例或 shell history 中展开秘密。
5. 查看日志、重启单个服务、停止完整栈，以及明确标为破坏性且不属于日常停止流程的 volume 清理方法。普通停止命令只能执行 `down`，不能带 `-v`。

必须生成并维护 `scripts/dev-up.ps1`、`scripts/dev-down.ps1`、`scripts/dev-up.sh`、`scripts/dev-down.sh`。它们只是上述权威步骤的薄封装，失败立即退出并返回非零状态，不得把配置或端口复制成第二套常量：

- Windows 脚本兼容当前受支持的 PowerShell，路径使用 `Join-Path`/`-LiteralPath` 等安全方式并从脚本位置解析仓库根目录，不能依赖调用者当前目录。先读取 `podman machine list`：没有 machine 时提示并按用户明确操作初始化，已有但未运行时启动，已经运行时不得重复创建；随后确认 `podman info` 可用。
- Linux 脚本使用 POSIX 兼容 shell、`set -eu` 和从脚本位置解析出的绝对仓库根目录；默认支持 rootless Podman，不把 `sudo` 写进常规启动命令，也不执行 `podman machine init/start`。
- 两个平台都必须显式使用 `--env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml`，先校验配置和端口，再按依赖→migration→seed→应用的固定顺序启动。Makefile、CI 和逐条文档命令必须使用同一 env-file 与文件顺序；配置检查必须拒绝 `.env` 中不匹配 `rbac-sys` 的 project identity。任一步失败都输出失败阶段和下一条安全排障命令，不能继续启动一个半配置状态的应用栈。
- README 同时保留不依赖封装脚本的逐条 PowerShell/POSIX 命令，方便审计和故障恢复；脚本、README、Makefile 与 CI 调用的底层命令必须一致。
- Linux CI 至少实际执行 shell 脚本语法检查和完整 Compose smoke；Windows CI 至少执行 PowerShell 解析/静态检查、Compose 配置生成和一个最小实际镜像 build。provider compatibility 测试必须捕获“解析了 `build.dockerfile` 但实际 build 未传递 Containerfile”的实现差异；各 build context 应直接包含默认 `Containerfile`，或由真实 provider 构建测试证明显式路径有效。发布前必须在真实 Windows Podman machine 和 Linux rootless Podman 各完成一次冷启动、重复启动、停止再启动测试并记录结果。

### 固定命令

必须生成跨平台 `scripts/run_backend_tests.py`，作为完整后端 pytest 的标准入口：先用 typed Settings 校验 test 环境、独立数据库/角色及 Redis/邮件目标，拒绝开发或生产连接；显式使用 `--env-file .env -f deploy/compose.yml -f deploy/compose.test.yml` 检查配置、构建测试任务镜像，启动 `postgres-test redis-test mailpit-test` 三个服务并等待真实 healthy；串行执行 `run --rm --no-deps migrate-test` 与 `run --rm --no-deps seed-test`，然后以 `run --rm --no-deps api-test` 在测试镜像中执行 `uv run --locked pytest`，通过已校验的测试配置连接内部依赖。测试镜像在构建时安装锁定的测试依赖并包含测试源码，运行时不下载依赖；秘密不得进入 argv 或日志。无需向宿主机新增 Redis/邮件端口，也不启动长期 api-test 或增加 service key。容器执行期间额外 1 个一次性测试容器不计入常驻数。失败/取消保留脱敏结果并返回非零状态，finally 只清理本次任务和停止本次启动的依赖，保留已有服务/卷；与 E2E 并行时用任务锁串行化共享测试数据库的迁移/重置，或使用已登记的独立测试数据库，禁止互相覆盖 fixture。无外部依赖的纯单元测试可直接运行 `uv run --locked pytest backend/tests/unit`，不能以此替代完整后端验收。

根 `package.json` 的 lint/typecheck/test/build 命令转发至各 workspace。`seed` 是独立一次性服务，只有 seed/测试 fixture 注入 bootstrap 凭据；长期 API/frontend 不注入初始管理员密码。`smoke_api.py --base-url` 固定接收 HTTPS origin，不含 `/api/v1`；脚本内部拼接 API 前缀并检查 `/health/ready`。提供 `--readiness-only` 模式用于重复启动和生产只读检查，不要求初始管理员密码。完整写流程 smoke 只针对已验证的隔离测试目标，使用受控 fixture；禁止把首次 bootstrap 密码作为长期健康探针。


```bash
# 以下为 POSIX 参考命令；README 必须按上一节另给语义等价的 PowerShell 命令
# 核对 CA 身份、安装宿主机信任并生成/复用证书；权限失败须明确退出
./scripts/dev-certs.sh

# 验证合并后的 compose 配置；不把展开后的秘密打印到终端/CI
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml config --quiet

# 构建后先启动依赖，再迁移/seed，最后启动 HTTPS 应用栈
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml build api frontend web
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml build maintenance
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml up -d postgres redis mailpit
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml run --rm migrate
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml run --rm seed
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml up -d api frontend maintenance
# 本参考采用重建网关更新上游地址；测试栈由 run_e2e.py 单独管理
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml up -d --force-recreate --no-deps web
# 浏览器只访问 .env 中的 DEV_PUBLIC_ORIGIN

# 后端本地质量检查；不另启浏览器可访问的 HTTP server
uv sync --locked
uv lock --check
uv run --locked ruff check backend scripts
uv run --locked ruff format --check backend scripts
uv run --locked mypy backend/app
uv run --locked python scripts/run_backend_tests.py

# 前端本地质量检查；`npm run dev` 只由 Compose frontend service 执行
npm ci
npm run lint
npm run typecheck
npm run test
npm run build

# E2E 使用与 lockfile 完全相同版本且预装浏览器的专用容器，不在 frontend 应用容器临时下载浏览器
uv run --locked python scripts/run_e2e.py

# 开发栈仅执行只读 smoke；origin 由 typed Settings 从 .env 读取，不要求 source .env
uv run --locked python scripts/smoke_api.py \
  --readiness-only \
  --ca-file deploy/certs/dev/rootCA.pem

# 开发日志：PowerShell/macOS/Linux 使用相同 Python CLI，不依赖 grep/jq
uv run --locked python scripts/dev_logs.py logs --service api --level DEBUG --since 30m --follow
uv run --locked python scripts/dev_logs.py request --request-id 00000000-0000-0000-0000-000000000000
uv run --locked python scripts/dev_logs.py trace --trace-id 00000000000000000000000000000000
uv run --locked python scripts/collect_diagnostics.py --since 30m

# 验证 maintenance 使用正确 PostgreSQL client
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml exec maintenance pg_dump --version
podman compose --env-file .env -f deploy/compose.yml -f deploy/compose.dev.yml exec maintenance pg_restore --version
```

如果实际 uv 稳定版对某个 flag 的名称有变化，使用 Context7/uv 官方文档确认后同步更新 README、Makefile、CI 和本节生成的实际命令，四处必须一致。

### 单机生产 Podman 生命周期

- `compose.yml + compose.prod.yml` 是服务拓扑、镜像、network、volume、secret、resource limit 与 healthcheck 的权威声明，用于 CI production smoke 和受控发布。Linux 单机长期运行必须另外生成 `deploy/quadlet/`，以当前 Podman 官方推荐的 Quadlet/systemd user units 管理开机启动、依赖顺序、失败重启、stop timeout 与日志来源；不得继续使用已弃用的 `podman generate systemd` 作为新实现。
- Quadlet 的 image、digest、user、network、volume、secret、health、read-only、capability 与 Compose production 定义必须由同一份受类型校验的部署输入生成或由自动 drift test 逐项比较，禁止维护两套手写且会漂移的生产参数。rootless unit 放入 `~/.config/containers/systemd/`，Quadlet 文件使用 `[Install]` 的 `WantedBy=default.target` 管理开机启动，README 分别给出 `systemctl --user daemon-reload`、`systemctl --user start <unit>.service`、status/stop 命令、linger 前置条件、失败恢复和卸载步骤；生成的 service 不能直接 `systemctl enable`，卸载时先 stop，再移除 Quadlet 定义并 daemon-reload；rootful 仅在明确运维批准时使用 `/etc/containers/systemd/`。
- production 主机只拉取已签名且 digest 锁定的镜像，不现场 build；secret 使用 Podman secret/挂载文件或平台 secret manager 注入，不出现在 Quadlet、Compose 展开输出、命令参数、镜像层和 journald。发布流程先 migration job、再应用 unit，失败不得把数据库自动降级；升级、回滚、证书轮换和主机重启后均执行 readiness/HTTPS smoke。
- 自动更新不是默认行为；只有签名验证、兼容 migration、健康门禁和回滚策略全部配置后才允许 Quadlet `AutoUpdate`。开发环境仍以 Podman Compose 为唯一启动方式，Windows 不要求 systemd/Quadlet，云平台可用等价托管编排替代。

### Compose 验收

- `compose.yml` 只放跨环境共同定义；`compose.dev.yml` 放开发端口、Mailpit、RedisInsight、热更新；`compose.test.yml` 独占测试 CA、全部测试服务及专用资源声明（包括 postgres-test、migrate-test、seed-test）和版本匹配的 Playwright E2E service/profile；`compose.prod.yml` 放资源限制、只读文件系统、生产 restart/health 配置，并通过 drift test 与 `deploy/quadlet/` 保持一致。
- README 中 Windows 与 Linux 的冷启动、重复启动、单服务重启、日志查看和普通停止步骤均可直接执行；四个 `dev-up/dev-down` 脚本与文档命令保持一致，普通停止不删除 volume，平台差异不会改变数据库、Cookie、Origin 或资源 namespace。
- `compose.dev.yml` 中 frontend 不发布端口；Nginx 通过集中配置的 internal service endpoint 代理页面、WebSocket HMR 和 API，并只按 `${DEV_BIND_ADDRESS}:${WEB_DEV_TLS_HOST_PORT}:443` 发布。开发证书不存在、不受信或与 `DEV_HOSTNAME` 不匹配时启动/smoke 必须失败并提示运行 dev-certs 脚本。
- PostgreSQL、Redis、Mailpit、RedisInsight、API、Nginx、maintenance，以及启用 production/test profile 时的 otel-collector 都有真实 healthcheck；RedisInsight 必须检查 `/api/health/`，启用调试服务时浏览器 smoke 必须验证其 loopback UI 返回成功且 production config 不存在该 service。`depends_on` 不能被误认为应用级 readiness，API 自身仍要重试有限次并暴露 readiness。
- 健康探针必须在真实 Compose provider 下执行并检查 exit code、health log 和最终 healthy 状态；`Up`、YAML 解析成功和 HTTP 手工成功均不能替代容器探针通过。优先独立模块/脚本（例如 `python -m app.healthcheck api`），避免跨 provider 传递多层 `-c` 内联代码；具体 workaround 记入 toolchain，不断言所有 Podman 版本都存在同一问题。
- liveness 仅反映进程，readiness 有总 deadline、检查 schema/权限不变量和必要依赖；探针 timeout 必须大于内部检查 deadline。数据库暂不可用时 API readiness 降级，维护进程以有限退避/jitter 重新建连且日志脱敏；恢复后重新检查 lease/任务状态，不能盲目重放已有副作用的 restore。heartbeat 不得把已失联或卡死任务伪装为健康，SIGTERM/取消可在 stop timeout 内退出。
- 提供命名 volume，明确哪些可以删除；测试数据 volume 与开发数据 volume 分离。任何清库命令必须标注破坏性并要求明确目标环境。
- `podman compose down` 不带 `-v`；文档不得把删除 volume 写进普通停止流程。
- Containerfile 使用 uv lock 做可复现安装；复制 `.venv` 前考虑平台相关性，默认在 Linux builder 内创建，不复制宿主机 `.venv`。
- `podman compose logs -f api`、`podman compose ps`、health URL、Mailpit UI 和 RedisInsight UI/`redis:6379` 连接步骤写入排障手册。

## 16. 实施顺序

0. 在任何源码写入前收集、规范化并验证全部模板输入，生成 `docs/project-identity.md` 与 `docs/ports.md`；完成 `CFG-*` 的双实例隔离 fixture，确认调用者提供的工程标识和端口不会与同机登记项冲突。
1. 审计当前 RBAC 数据和行为，写出保留/废弃映射，不修改 `storage/`。
2. 建立 monorepo 命令、`.gitignore`/各 context `.containerignore`、后端基础、配置和测试数据库 fixture；先让 secret/build-context 检查通过再构建镜像。
3. 按第 5 节创建第一组 Alembic migration，并完成 `DB-*` 测试。
4. 完成幂等 permission/role/bootstrap-admin seed；bootstrap 密码只能来自环境变量，首次登录要求修改。
5. 完成注册、邮箱验证、审批/拒绝、登录、找回/修改/重置密码、refresh rotation、session、Profile、username/email 安全变更、Preferences 与 `REG-*`/`AUTH-*`/`PWD-*`/`PRO-*`/`PREF-*` 测试。
6. 完成 RBAC、乐观锁、最后 super-admin 保护、幂等写与测试。
7. 完成 login/action history，以及后端/Nginx 结构化日志、dependency event、前端 telemetry/breadcrumb/Support ID、跨平台日志检索/诊断包、双端脱敏和对应 `HIS-*`/`LOG-*` 测试。
8. 完成 backup/restore 元数据、maintenance worker、`${BACKUP_EXTENSION}` bundle、对象存储 adapter、灾难恢复 CLI 与 `BKP-*` round-trip 测试。
9. 生成 OpenAPI client，完成三个 layout、Profile/Preferences、亮度模式 × 多 palette 主题系统及全部 Phase 1 页面，包括 System/Backup/Restore。
10. 完成前端组件测试与 Playwright 用例。
11. 完成 Nginx、TLS/证书校验与轮换、RedisInsight dev-only 服务、版本匹配的 Playwright E2E 容器、Collector/托管 agent、持久化队列、集中日志、UTC 日次归档/retention/恢复演练、Compose/Quadlet drift test、健康检查、graceful shutdown、云部署/备份/PITR/cutover runbook 和未来任务 ADR，并完成其余 `LOG-*`/`DEP-*` 测试。
12. 在 Node 工具环境运行 lint/typecheck/unit/build，在专用 Playwright 容器真实运行 Chromium/Firefox；运行全部后端 unit/integration/contract、migration、backup-restore drill、log-archive restore drill 和 smoke/load checks，并在 Windows Podman machine 与 Linux rootless/Quadlet 环境留下脱敏结果；修复后交付。

不要在每一步停下来等待确认。只有缺少会实质改变表结构或安全模型的信息时才请求用户决策。

## 17. 完成定义

必须提交 `docs/implementation-status.md` 与机器可读的 `docs/verification-result.json`。按需求/测试编号分别记录实现状态（未实现/部分实现/已实现）和验证状态（未执行/通过/失败/受环境限制），附命令、执行日期、源码 revision 或 dirty 状态/内容 fingerprint、平台与工具版本、脱敏结果及 artifact 路径。统计须给出适用总数、执行/通过/失败/跳过数量，不能用少量通过用例替代完整矩阵；代码或部署配置变化后标记受影响证据待复验。

开发工程可运行、功能矩阵完成、生产部署验证是不同里程碑。平台或凭据不足时记录缺少的前提，不得把静态配置验证写成真实部署通过；首次交付执行一次归档恢复演练，后续季度演练记录到期计划与实际结果，不要求等待一个季度，也不能声称未来演练已通过。提示词版本与实现版本独立，文档升级不会使现有实现自动符合新契约。

只有同时满足以下条件才算 Phase 1 完成；分阶段报告不豁免任何适用条件：

- 本次 `PROJECT_DISPLAY_NAME/PROJECT_SLUG/PROJECT_DB_PREFIX`、资源派生值和九个宿主机端口均来自调用者输入并通过格式/冲突校验；`docs/project-identity.md`、`docs/ports.md`、`.env.example` 与 Compose 最终插值一致。
- `.gitignore`、各 build context 的 `.containerignore`、secret scanning、ignore fixture 和镜像内容检查全部通过；`.env`、私钥、证书生成物、诊断包、备份、日志、宿主机依赖和测试报告均未进入 Git、build context 或镜像层，`.env.example`、migration 与 lockfile 未被误忽略。
- 除通用模板源文件 `docs/prompts/rebuild-rbac-system-v1.md` 外，生成物不存在未解析模板参数、错误模板示例工程名、项目身份/hostname/origin/宿主机端口 magic literal 或跨工程 namespace；两套不同输入的 `CFG-*` 隔离测试通过。
- 空数据库可用 Alembic 构建，seed 可重复执行且没有默认公开密码。
- 表、约束、索引与第 5 节一致。
- 注册→邮件验证→管理员审批/拒绝流程完整，邮件 token 不以明文落库或进入日志。
- real/decoy registration status token 行为不可枚举，来源、DTO、header、有效期、清理策略和测试完整。
- 登录后改密、忘记密码重置、管理员重置、首次登录强制改密和最近密码防复用正确。
- 登录、rotation、重放检测、退出、密码修改和会话撤销正确。
- 用户角色授权、角色权限授权、多角色权限并集、权限即时失效与审计全部正确。
- `super_admin` 始终启用且权限集合严格等于完整 permission catalog；任何 API 都不能破坏该不变量。
- 软删除释放原 username/email 且不可恢复 deleted 身份；`users.activate` 与资料编辑权限分离；登录限流和临时锁定的顺序、阈值、故障策略均通过测试。
- `users`、`user_profiles`、`user_preferences` 边界清楚且每个用户关联完整；本人 Profile 修改、username 重新认证变更、email 二次确认、并发唯一性、通知、会话失效和脱敏审计全部通过。
- Preferences 是服务端持久化且按用户隔离的真实功能；亮度模式、Default/Eye Care/Sepia/Forest palette、对比度、密度、动态效果、时区、分页大小均有实际消费者，管理员不能静默修改个人偏好，强制安全通知不可关闭。
- 所有管理 API 后端权限校验和本人数据范围测试通过。
- 并发 refresh、并发唯一创建、最后 super-admin 和幂等写测试通过。
- login history 与 action history 分工清楚、可筛选、不可普通修改且已脱敏。
- 后端/Nginx JSON 日志和前端错误遥测字段受控、可用 request/trace id 关联且通过 canary secret 泄漏测试；日志采集失败不会阻塞业务或撑爆磁盘。
- development/test/production 日志 profile、依赖耗时、异常 fingerprint/stack、前端安全 breadcrumb/Support ID、按 request/trace 检索及脱敏 diagnostics 在 Windows/Linux 均真实可用；可从注入故障的 Support ID 定位到具体服务、operation、版本和 source frame。
- 生产日志按 UTC 日次幂等归档到独立加密存储，热/冷/审计保留期、26 小时告警、生命周期删除和首次归档恢复演练实际通过，季度演练计划已配置且交付时已到期的演练有通过证据；运行日志不混入 `${BACKUP_EXTENSION}` bundle。
- 无需表/schema 清单即可把包含任意数量数据库对象的 `${BACKUP_EXTENSION}` bundle 恢复到空 PostgreSQL；checksum/Ed25519、safety backup、隔离恢复、验证和回滚流程通过。
- 管理员能按权限创建/下载/导入/校验备份；只有最近重新认证的 super-admin 能启动 restore，API 账号本身没有 CREATEDB/superuser。
- 普通账户区和管理控制台完全分离，普通用户看不到管理 UI；特权账户保护、角色授予子集与并发越权测试通过，改密全部退出、family 即时撤销及双标签页协调通过。
- `system/light/dark × default/eye_care/sepia/forest` 主题组合在 Public/Account/Admin 全布局无首屏闪烁、可跨刷新/设备同步且共享浏览器不串号；全部 palette 的 light/dark/high contrast/forced-colors/reduced-motion 和管理员视觉身份通过自动化 token、可访问性与视觉回归测试。
- Nginx/容器配置可运行，并提供单机与云部署差异说明；生产入口、跨信任边界 upstream、PostgreSQL、Redis、对象存储和 SMTP 的 TLS/证书验证满足第 14 节且不能静默降级。
- 本地完整栈只通过 `DEV_PUBLIC_ORIGIN` 访问，开发 CA、Nginx TLS、WSS HMR、Secure Cookie、Origin、Playwright 和 smoke 已真实测通；Vite/API 没有浏览器可绕过的宿主机 HTTP 入口。
- development profile 的 RedisInsight 使用锁定 digest、独立命名 volume 和 `/api/health/`，仅绑定 `${DEV_BIND_ADDRESS}:35540` 在显式启用后能通过 `redis:6379` 连接本项目 Redis；staging/production 配置、镜像清单和 volume 中不存在 RedisInsight。
- Playwright npm package、E2E 镜像与浏览器 executable 版本严格一致；专用容器中的 Chromium 和 Firefox 均实际执行通过，测试不会因应用容器缺少浏览器或运行时下载而产生假通过。
- README 的 Windows/Linux 冷启动、数据库/Redis/RedisInsight/Mailpit 连接表和 bootstrap 凭据来源完整，未包含任何实际秘密；development/test 使用 uv/npm 与 Podman 的职责、production 只运行不可变镜像的边界清楚。
- Linux 单机 production Quadlet units 已通过与 `compose.prod.yml` 的 drift test、开机启动、失败重启、受控 migration、升级/回滚、证书轮换和主机重启 smoke；Windows 开发不依赖 systemd，云部署差异有明确 runbook。
- 所有编号测试有真实代码且实际执行通过；报告实际结果和基础负载指标。
- OpenAPI 中每个 endpoint 都被 endpoint matrix 和自动化测试覆盖，完整 Podman 栈的黑盒 smoke 通过。
- `scripts/check_ports.py` 在 CI 中通过；合并后的 Compose 配置及所有开发/测试服务不存在 `30000–39999` 之外或未登记的宿主机监听端口，启动前端口占用检查有自动化测试。
- 没有实现任何学习、LLM、Vocab 或其他业务功能。

最终回复必须列出关键文件、migration revision、seed 命令、启动命令、测试命令与实际结果、架构决策、已知限制和需要轮换的凭据。不得用“理论上可运行”代替验证。

## 18. 本次文档修订的技术依据

2026-09-05 通过 Context7 核对以下官方资料；实现时仍须按锁定版本复核。授权边界、改密全部退出和 E2E 网络拓扑是本项目设计决策，不是框架默认行为。

- [Podman Quadlet](https://docs.podman.io/en/latest/markdown/podman-systemd.unit.5.html)：生成的 service 不能直接 enable，开机启动由 Quadlet `[Install]` 声明；reload 后 start。
- [Playwright Docker](https://github.com/microsoft/playwright/blob/main/docs/src/docker.md)：容器访问本地服务需要显式网络配置。本文选择共享 web-test 网络命名空间，实际 Podman provider 兼容性由 DEP-012 验证。
- [Playwright 浏览器安装](https://github.com/microsoft/playwright/blob/main/docs/src/browsers.md)：`NODE_EXTRA_CA_CERTS` 用于 Node 侧自定义 CA；该说明不能替代 Chromium/Firefox 页面访问的证书信任测试。


2026-09-06（v1.14）再次使用 Context7 核对：

- [PostgreSQL 16 passfile](https://www.postgresql.org/docs/16/libpq-pgpass.html) 与 [libpq 环境变量](https://www.postgresql.org/docs/16/libpq-envars.html)：passfile 文件权限和 `PGPASSFILE`；`PGPASSWORD` 不是默认安全替代。目录 0700 与秘密文件 0600 分别处理。
- [Uvicorn proxy headers 实现](https://github.com/kludex/uvicorn/blob/main/middleware/proxy_headers.py)：可信 hostname 不自动解析为 IP，代理允许列表必须按真实 peer 验证。
- [Nginx upstream](https://nginx.org/en/docs/http/ngx_http_upstream_module.html)：DNS 地址更新依赖适当 resolver/upstream 配置和版本能力；本文允许动态解析或受控网关重载两种经实测的实现。
- 历史参考实例在 Podman 5.8.1 / Compose provider 5.1.1 下遇到过探针参数、上游重建后的 DNS 缓存及证书库重复初始化问题；这些仅是需复验的案例，不是所有平台的框架缺陷或本模板的已通过证据。新的生成工程须自行验证，并生成自己的 `docs/toolchain.md`；使用本模板不依赖该历史实例的文件。

2026-09-06（v1.15）通过 Context7 核对 [Compose profiles](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/profiles.md) 与 [profile 依赖约束](https://github.com/docker/docs/blob/main/content/reference/compose-file/profiles.md)：显式指定服务只拉起该服务及其依赖，同 profile 的其他服务不会因此全部启动。上述服务白名单与数量是本项目设计契约，必须用实际 Podman Compose provider 验证，不是工具默认保证。

2026-09-06（v1.16）通过 Context7 核对 [mkcert 官方说明](https://github.com/FiloSottile/mkcert/blob/master/README.md)：`-install` 安装本机 CA 信任，`TRUST_STORES` 选择目标信任库，`-uninstall` 撤销对应信任；Firefox 安装后需要重启。第 14 节的分阶段验证和失败门禁是本项目验收要求，不从证书生成或容器测试结果推断宿主机已受信。

2026-09-06（v1.17）通过 Context7 核对 [Compose 多文件合并](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/multiple-compose-files/merge.md) 与 [profiles](https://github.com/docker/docs/blob/main/content/manuals/compose/how-tos/profiles.md)：按文件顺序合并服务定义，profile 控制启动选择；本模板通过测试定义只存在于测试文件来保证生产配置不包含测试服务。
