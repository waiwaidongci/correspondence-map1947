# 禾陌 · 展陈偏好对应图

从匿名参观类别×导览方式计数中读出轮廓结构，同时保留二维图的信息边界。

禾陌公共展陈研究组有18位研究员。现有工作流手工比较导览百分比、把低计数格当强偏好、把二维点图当全部信息；痛点是类别基率被忽略、稀少单元格过度解释、投影质量未进入结论。这里承接“机构级汇总列联表→CA与独立性诊断→人工结构解释→负责人审阅→CSV”，后续导览小样试验独立开展，结构关联不等于因果偏好。

## 快速启动

```sh
cp .env.example .env
docker compose config --quiet
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

访问 [研究折页](http://localhost:18222)，[后端文档](http://localhost:19222/docs)，PG映射17722。首次API启动自动seed，失败只记日志不阻塞API；脚本可独立重复。初始3张4×5或5×4列联表、27个行列类别、60个计数格，总计数1806，含近独立对照和零行/零列稀疏表；基准运行由Python真实计算。

| 账号 | 密码 | 权限 |
|---|---|---|
| admin@hemo.demo | Hemo2026! | admin展陈研究负责人：读、导入/校订、分析、写解释、审阅；仅获批解释可导出 |
| analyst@hemo.demo | Hemo2026! | analyst偏好结构研究员：读、导入/校订、分析、写解释；审阅403；仅获批可导出 |
| viewer@hemo.demo | Hemo2026! | viewer导览观察员：只读与获批CSV；写入403 |

## 一天的研究剧本

1. 09:00 陈陌以analyst登录，核对 `hm-guide-contingency-1.csv` 的4×5计数，N900。
2. 阅读家庭同行、学习小组、独立参访、策展同业四行与五种导览列；可校订某格计数或类别名称，审计保留，历史运行不改。
3. 选择“秋季导览类别研究”、显示前2轴，提交真实Celery队列。
4. worker计算标准化残差SVD，得到总惯量.408904、χ²368.014，图保留82.62%。
5. 读取轴1/轴2贡献和cos²；策展同业显示质量约.127、地图路径约.068，不能只凭二维位置作解释。
6. 核对期望最小24.75、df12及渐近p；再运行稀疏试采，看到零边际剔除和“不可靠”警示。
7. 从有效行/列类别建立解释，写明同行/同列轮廓与跨集距离边界，安排独立导览小样验证。
8. 许禾以admin审阅解释；林叙以viewer下载获批CSV，带上点集、主坐标、显示质量、惯量保留与诊断边界。

## 实体、输入与页面

五个核心实体ContingencyStudy、Category、CellCount、CorrespondenceRun、InterpretationNote贯穿表/model/schema/service/route/API/store/UI。六页为研究折页、列联计数、分析配置、坐标与诊断、解释审阅、研究留痕。CorrespondenceMap、InertiaSummary、RunTable跨页复用，另有Diagnostics及共享Table/Badge/Notice/Empty。

导入2–12行×2–12列非负整数矩阵，每格≤1000000；行与列分别按code唯一，数据库cell(row_id,column_id)唯一且count≥0。未知维度、重复类别、负数、非整数、非有限、总量为零拒绝；最大总N144000000。每格校订是替换并审计，不把重复提交当追加。缺失格在内部表构造时规范为0，导入矩阵必须完整。分类标签是合成机构级汇总，不含个人身份数据。UI接受矩阵JSON与类别标签，不直接解析CSV。

## 对应分析与诊断口径

`services/ca.py`：先剔除总数为0的行/列，结果明确记录被剔除类别；有效行与列各至少2，总N须正。P=X/N，r=P·1，c=Pᵀ·1，S=D_r⁻¹ᐟ²(P−rcᵀ)D_c⁻¹ᐟ²。对S做完整SVD UΣVᵀ；λ_k=σ_k²，总惯量=ΣS_ij²=χ²/N。

行主坐标F=D_r⁻¹ᐟ²UΣ，列主坐标G=D_c⁻¹ᐟ²VΣ。非零轴最大min(R−1,C−1)，奇异值数值容差1e-12；总惯量≤1e-24时判数值零，不给方向、坐标为空、保留比例为null，UI不画伪造轴。每轴按U最大绝对载荷行的符号统一U/V；重复奇异值（相对1e-8内）会标记简并轴，符号固定仍不能消除非唯一旋转。

行点轴贡献r_i F_ik²/λ_k，列点同理，每轴分别合计1；点cos²为该轴坐标平方/完整主坐标距离平方。质心点距离在数值零范围时cos²无定义，报告null而不是100%。显示质量为所选前1/2轴cos²之和；低于.5仅做表示较差的视觉提示，不是显著性检验。图中低质量点淡化并用类别code标注，悬停和完整表保留点名，减少质心附近标签重叠。保留惯量是显示λ之和/总惯量，完整非零轴仍随结果保存。

同行与同列分别具有完整χ²轮廓几何；截断图仅保留相应惯量。这里两集都使用主坐标，**行列两点之间的欧氏近距离不可直接作为可比较的偏好距离**。图不用于行列跨集距离推断；1轴配置时所有点只沿第一轴显示，纵向不放第二轴信息。低cos²点应回到完整坐标/计数阅读。

`services/diagnostics.py`：E_ij=N r_i c_j，Pearson χ²=Σ(X−E)²/E，df=(R−1)(C−1)，渐近p由chi²生存函数。标准残差=(X−E)/√E；校正标准残差=(X−E)/√[E(1−r_i)(1−c_j)]。任一期望<1或超过20%期望<5时标渐近p不可靠，不作强显著结论；即使规则未触发，也依赖独立观察计数与适当抽样。逐格残差未作多重检验校正，只用作描述诊断；不自动解释为逐格显著。

输入指纹覆盖研究id/name/filename/description、全部行列类别元数据、全部单元格的row/column/count、显示轴数、算法版本与容差，稳定排序；行序改变不改指纹，计数/标签/说明/显示轴改变会改。worker把完整SVD、惯量、主坐标、贡献、cos²、期望/残差、零边际与诊断存JSON和PG。有效行列不足、坏矩阵等记录failed，不伪造成功结果。

## 工程与开发

| 层 | 技术 |
|---|---|
| 前端 | React18.3 / TypeScript5.7 / Vite6.4.6 / Nginx1.27 |
| API | Python3.11 / FastAPI / SQLAlchemy2 / Pydantic |
| 计算 | NumPy2.2.1 / SciPy1.15 |
| 数据/队列 | PostgreSQL16 / Redis7 / Celery5.4 + Kombu5.4.2 |
| 认证 | PBKDF2-SHA256 210000轮、JWT HS256 8小时、后端三角色校验 |

Compose恰五服务frontend/backend/worker/db/redis，全健康依赖/探针；Nginx健康检查127.0.0.1，worker定向Celery ping。db-data/redis-data/artifacts命名卷分别保存库、队列和共享计算JSON。Nginx剥离/api/前缀，后端不重复前缀。Kombu固定5.4.2兼容Celery5.4 Redis依赖。

.env.example说明COMPOSE_PROJECT_NAME、FRONTEND_PORT/BACKEND_PORT/DB_PORT、POSTGRES_DB/USER/PASSWORD、JWT_SECRET、SEED_DEMO。演示值用于本机，部署通过环境变量替换。默认自动seed；按研究名/类别自然键插入，不覆盖已有计数或标签修改，基准运行仅缺失时计算。

```sh
# 设置本机可达DATABASE_URL / REDIS_URL / JWT_SECRET
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 19222
# 另一个终端，同环境变量
celery -A src.worker.app worker --concurrency=1
# 前端Vite已代理127.0.0.1:19222
cd frontend
npm ci
npm run dev
```

结构为backend/src/{routes,controllers,services,models,schemas,middlewares,utils,constants,config}、backend/scripts/seed_demo.py、backend/migrations/和frontend/src/{api,stores,types,components/common,hooks,pages,router,utils,constants}。metadata首次建表，migrations记录结构，生产增量迁移需另行规划。请求ID和全局错误两个中间件；审计登录/导入/校订/运行/审阅；CSV公式前缀转义。

共享枚举：backend/src/constants/enums.py中的Role/RunStatus/NoteStatus/Axis，frontend/src/constants/enums.ts对应角色/运行/解释/点集标签；用于鉴权、服务/schema、Badge/Layout/各页面。70个职责源文件，不计__init__及配置。源码不放截图、日志和测试报告；独立测试与真实截图在批次根test-artifacts/gb-0018，TESTING.md列实测与已知差异。

## 范围与License

数据是合成汇总，不证明真实访客偏好或因果效果。稀疏渐近p不可靠，未提供精确检验/Monte Carlo替代；残差未作多格显著性控制。未做生产压测或外部导览验证。Google字体需联网，离线浏览器回退。收尾docker compose down -v --remove-orphans清理本栈演示卷。

MIT，见LICENSE。
