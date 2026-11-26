# دليل تشغيل وعرض المشروع للمبتدئ

هذا الدليل مكتوب لشخص لا يعرف Docker أو قواعد البيانات أو Kestra. امشِ بالترتيب، ولا
تنتقل إلى خطوة إلا بعد أن ترى النتيجة المتوقعة تحتها.

## 1. المشروع بيعمل إيه؟

المشروع يأخذ بيانات متجر إلكتروني حقيقية من Olist ويحوّلها إلى معلومات تصلح للتحليل:

```text
9 CSV files
    ↓
Raw ingestion (حفظ البيانات الأصلية بدون تغيير)
    ↓
Clean layer (تحويل الأنواع وتنظيف البيانات)
    ↓
Data warehouse (جداول منظمة للتحليل)
    ↓
Quality gate (12 اختبار جودة)
    ↓
Kestra (تشغيل ومتابعة كل المراحل)
    ↓
Power BI views (بيانات جاهزة للداشبورد)
```

الأسئلة التي يجاوب عنها المشروع:

1. ما أكثر فئات المنتجات تحقيقًا للمبيعات؟
2. كيف تتغير المبيعات وعدد الطلبات كل شهر؟
3. ما أكثر الولايات البرازيلية مساهمة في المبيعات؟

## 2. الأدوات باختصار

| الأداة | معناها البسيط |
|---|---|
| GitHub | مكان حفظ ومشاركة ملفات المشروع |
| Docker Desktop | يشغّل كل أجزاء المشروع بدون تثبيت كل أداة وحدها |
| PostgreSQL | قاعدة البيانات التي تحفظ البيانات الخام والمنظفة |
| pgAdmin | شاشة رسومية نفتح منها PostgreSQL وننفذ SQL |
| Python | ينفذ ingestion وtransformation واختبارات الجودة |
| Kestra | ينظم مراحل الـpipeline ويعرض نجاح أو فشل كل مرحلة |
| Power BI | يحول النتائج إلى charts وdashboard |

## 3. قبل أول تشغيل

ثبّت:

- Git: <https://git-scm.com/downloads>
- Docker Desktop: <https://www.docker.com/products/docker-desktop/>
- متصفح مثل Chrome
- Power BI Desktop فقط لو ستبني ملف `.pbix`

افتح Docker Desktop وانتظر حتى تظهر **Engine running**. افتح PowerShell ثم تأكد:

```powershell
git --version
docker --version
docker compose version
docker info
```

لو `docker info` أعطى error، لا تكمل؛ افتح Docker Desktop وانتظر ثم جرّب مرة ثانية.

## 4. تنزيل المشروع من GitHub

نفّذ في PowerShell:

```powershell
New-Item -ItemType Directory -Path C:\Projects -Force
Set-Location C:\Projects
git clone https://github.com/AhmedHossamm2003/Ecommerceproject.git
Set-Location Ecommerceproject
```

## 5. تجهيز ملف الإعدادات

المشروع لا يرفع كلمات السر على GitHub. أنشئ نسخة محلية من ملف المثال:

```powershell
Copy-Item .env.example .env
notepad .env
```

غيّر كل قيمة مكتوب فيها `replace_with_a_strong_local_password`. احتفظ بكلمات السر عندك ولا
ترفع `.env` إلى GitHub.

لو المشروع موجود في `C:\Projects\Ecommerceproject`، اجعل مسار البيانات داخل `.env`:

```dotenv
PIPELINE_RAW_DATA_HOST_PATH=/run/desktop/mnt/host/c/Projects/Ecommerceproject/data/raw
```

بيانات الدخول تأتي من نفس `.env`:

- pgAdmin: `PGADMIN_DEFAULT_EMAIL` و`PGADMIN_DEFAULT_PASSWORD`
- Kestra: `KESTRA_ADMIN_USERNAME` و`KESTRA_ADMIN_PASSWORD`
- PostgreSQL: `POSTGRES_USER` و`POSTGRES_PASSWORD`

## 6. تنزيل بيانات Olist

الـCSV الأصلية ليست على GitHub لأنها كبيرة وتأتي من Kaggle.

1. افتح <https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce>.
2. سجل الدخول وحمّل الملف.
3. فك الضغط داخل `Ecommerceproject\data\raw` مباشرة.
4. تأكد أن داخل `data\raw` توجد 9 ملفات CSV، وليس مجلدًا آخر يحتويها.

الأسماء المطلوبة موجودة بالتفصيل في [`data/README.md`](../data/README.md).

## 7. أسرع طريقة لتشغيل المشروع كله

### الاختيار الأسهل: أمر واحد

من داخل مجلد المشروع شغل:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 start
```

السكربت يتأكد أن Docker يعمل، وأن `.env` والملفات التسعة موجودة، ثم يشغل المراحل كلها
بالترتيب. لمعرفة حالة الخدمات أو تشغيل الاختبارات أو الإيقاف الآمن:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 status
powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 test
powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 stop
```

### الاختيار التعليمي: الأوامر مرحلة بمرحلة

نفّذ الأوامر التالية من داخل مجلد `Ecommerceproject`:

```powershell
docker compose up -d postgres pgadmin
docker compose --profile ingestion build ingestion
docker compose --profile ingestion run --rm ingestion --strict-files
docker compose --profile transformation build transformation
docker compose --profile transformation run --rm transformation
docker compose --profile quality build quality
docker compose --profile quality run --rm quality
docker compose --profile bi build bi-prepare
docker compose --profile bi run --rm bi-prepare
docker compose --profile orchestration up -d kestra-postgres kestra
docker compose --profile orchestration ps
```

الأوامر التي تحتوي `build` قد تأخذ وقتًا أول مرة لأنها تبني صور Docker. نجاح الأمر يعني أنه
انتهى بـexit code `0` ولم تظهر رسالة `failed`.

## 8. كل مرحلة بتعمل إيه؟

### المرحلة 1: تشغيل قاعدة البيانات وpgAdmin

```powershell
docker compose up -d postgres pgadmin
docker compose ps
```

المفروض `postgres` و`pgadmin` يظهر أمامهما `healthy`.

### المرحلة 2: Raw ingestion

```powershell
docker compose --profile ingestion run --rm ingestion --strict-files
```

تقرأ ملفات CSV وتحفظ القيم الأصلية في `raw_data` مع اسم الملف، رقم السطر، hash، ووقت
التشغيل. إعادة نفس الملف لا تضاعف البيانات.

النتيجة المعروفة للبيانات الرسمية: **1,550,922 raw rows**.

### المرحلة 3: Cleaning وdata warehouse

```powershell
docker compose --profile transformation run --rm transformation
```

تحول النصوص إلى تواريخ وأرقام صحيحة، تسجل السطور المرفوضة، ثم تبني dimensions وfact table
وanalytical views.

النتيجة المعروفة:

- **1,289,091 clean rows**
- **112,650 fact rows**
- **0 rejected rows**
- إجمالي item revenue = **13,591,643.70**

### المرحلة 4: Quality gate

```powershell
docker compose --profile quality run --rm quality
```

تشغل 12 قاعدة جودة. إذا فشل اختبار blocking، يتوقف الأمر بكود خطأ حتى لا تصل بيانات غير
موثوقة إلى التقرير. النتيجة المتوقعة: **12/12 passed**.

### المرحلة 5: تجهيز Power BI

```powershell
docker compose --profile bi run --rm bi-prepare
```

ينشئ views جاهزة للتقرير. ملفات Power Query وDAX والـtheme موجودة في `powerbi/`.

### المرحلة 6: Kestra

```powershell
docker compose --profile orchestration up -d kestra-postgres kestra
```

افتح <http://localhost:8080> وسجل الدخول بقيم Kestra من `.env`. افتح flow:

```text
university.ecommerce / olist_ecommerce_pipeline
```

الـflow يشغل بالترتيب:

1. `ingest_raw_files`
2. `build_clean_warehouse`
3. `enforce_quality_gate`
4. `prepare_bi_views`

كل task له logs ومدة تشغيل وحالة. يوجد schedule كل يوم اثنين الساعة 03:00 بتوقيت القاهرة.

## 9. إزاي أفتح قاعدة البيانات وأعرض النتائج؟

افتح <http://localhost:5050> وسجل الدخول بقيم pgAdmin من `.env`.

افتح السيرفر **E-commerce PostgreSQL (Docker)**. لو طلب database password، استخدم
`POSTGRES_PASSWORD` من `.env`. إعداد الاتصال داخل Docker:

| الحقل | القيمة |
|---|---|
| Host | `postgres` |
| Port | `5432` |
| Database | `ecommerce_db` |
| Username | `ecommerce_user` |

من **Query Tool** شغل هذه الاستعلامات واحدًا واحدًا:

```sql
SELECT source_file, COUNT(*)
FROM raw_data.records
GROUP BY source_file
ORDER BY source_file;
```

```sql
SELECT * FROM analytics.vw_executive_kpis;
```

```sql
SELECT * FROM analytics.vw_category_sales LIMIT 10;
```

```sql
SELECT * FROM analytics.vw_monthly_sales ORDER BY sales_month;
```

```sql
SELECT * FROM analytics.vw_state_sales LIMIT 10;
```

لعرض آخر اختبارات الجودة:

```sql
WITH latest AS (
    SELECT gate_run_id
    FROM quality.gate_runs
    ORDER BY started_at DESC
    LIMIT 1
)
SELECT rules.rule_key, results.severity, results.passed,
       results.observed_value, results.expected_value
FROM quality.gate_results AS results
JOIN quality.gate_rules AS rules USING (rule_id)
WHERE results.gate_run_id = (SELECT gate_run_id FROM latest)
ORDER BY rules.sort_order;
```

## 10. إزاي أشغّل الـtests وأعرضها؟

هذا هو الأمر الذي تعرضه في PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\demo.ps1 test
```

أو استخدم أمر Docker المباشر:

```powershell
docker compose --profile ingestion run --rm --no-deps --entrypoint python ingestion -m unittest discover -s /app/tests -v
```

المفروض ترى أسماء الاختبارات وبجانب كل واحد `ok`، وفي النهاية:

```text
Ran 24 tests
OK
```

الـtests تثبت أن:

- CSV الصحيح يُقرأ كما هو، والصف التالف يُرفض.
- الملف المفقود يعطي error واضحًا.
- إعادة ingestion لا تكرر البيانات.
- فشل قاعدة البيانات لا يُسجل كنجاح.
- SQL لا يمسح raw data.
- star schema وviews موجودة.
- quality rules قابلة للتعديل ونتائجها محفوظة.
- Kestra يشغل المراحل بالترتيب وبه retries وschedule.
- Power BI لا يقرأ إلا من views المسموح بها.

لتشغيل verification SQL كاملة من PowerShell:

```powershell
Get-Content -Raw sql\verify_phase2.sql | docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db
Get-Content -Raw sql\verify_phase3.sql | docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db
Get-Content -Raw sql\verify_phase4.sql | docker compose exec -T postgres psql -U ecommerce_user -d ecommerce_db
```

## 11. سيناريو عرض جاهز في 7 دقائق

قبل العرض افتح ثلاثة أشياء:

1. GitHub على صفحة المشروع.
2. Kestra على صفحة آخر execution ناجح.
3. pgAdmin وفيه Query Tool.

### الدقيقة 0–1: الفكرة

قل: “المشروع يحول تسعة ملفات تجارة إلكترونية خام إلى data warehouse موثوق وبيانات جاهزة
للـPower BI. كل خطوة قابلة للتكرار ومراقبة.” ثم اعرض رسم `docs/architecture.png`.

### الدقيقة 1–2: ملفات المشروع

اعرض GitHub بسرعة:

- `docker-compose.yml`: الخدمات.
- `scripts/`: كود ingestion وtransformation والجودة.
- `sql/`: schemas وviews والتحقق.
- `flows/`: Kestra flow.
- `powerbi/`: ملفات التقرير.
- `tests/`: الاختبارات.

### الدقيقة 2–3: البيانات الخام

في pgAdmin شغل query عدد السطور لكل source file. وضح أن البيانات الخام immutable وأن كل سطر
له lineage يرجعه للملف ورقم السطر.

### الدقيقة 3–4: التنظيف والwarehouse

اعرض `analytics.vw_executive_kpis` ووضح grain: كل صف في fact table يمثل order item، ولذلك
لا نربط payments مباشرة بالitems حتى لا تتضاعف المبيعات.

### الدقيقة 4–5: الجودة والاختبارات

شغل أمر الـ24 test واعرض `OK`. بعدها اعرض آخر 12 quality rules في pgAdmin. الفرق أن unit tests
تختبر الكود، بينما quality gate تختبر البيانات الفعلية.

### الدقيقة 5–6: Kestra

اعرض الرسم الذي فيه أربع tasks باللون الأخضر، ثم افتح logs لأي task. وضح retries والschedule.

### الدقيقة 6–7: نتائج البزنس

اعرض category/month/state views أو صفحات Power BI، ثم اختم: “المشروع reproducible؛ أي شخص
يمكنه clone، يضع البيانات، وينفذ نفس الأوامر ليصل إلى نفس النتائج.”

## 12. أسئلة متوقعة وإجابات قصيرة

**ليه raw data مش على GitHub؟**  لأنها كبيرة ومن Kaggle، لكن أسماء الملفات وطريقة التنزيل
والـhashes والـprofile موجودة.

**ليه استخدمنا JSONB في raw layer؟**  لحفظ كل قيم المصدر بدون فرض أنواع أو تنظيف مبكر.

**ليه fact table على مستوى order item؟**  لأن تحليل المنتجات والمبيعات يحتاج كل item على حدة.

**إزاي منعنا تكرار المبيعات؟**  لم نربط payments متعددة مباشرة مع order items متعددة؛ استخدمنا
الجداول على grain صحيح واختبارات reconciliation.

**إزاي نعرف إن البيانات صحيحة؟**  lineage، rejects، reconciliation، 12 quality rules، و24 test.

**لو شغلنا المشروع مرتين؟**  ingestion idempotent للملف والـhash نفسه، والطبقات المشتقة يعاد
بناؤها بطريقة آمنة.

## 13. إيقاف وتشغيل المشروع بعد ذلك

إيقاف الخدمات مع الاحتفاظ بالبيانات:

```powershell
docker compose --profile orchestration stop
```

تشغيلها مرة ثانية:

```powershell
docker compose --profile orchestration up -d postgres pgadmin kestra-postgres kestra
```

إزالة الـcontainers مع الاحتفاظ بالـvolumes والبيانات:

```powershell
docker compose --profile orchestration down
```

لا تستخدم الأمر التالي إلا لو تريد مسح قاعدة البيانات نهائيًا:

```text
docker compose down --volumes
```

## 14. أشهر المشاكل

**Docker command لا يعمل:** افتح Docker Desktop وانتظر Engine running.

**Port مستخدم:** غيّر `POSTGRES_PORT` أو `PGADMIN_PORT` أو `KESTRA_PORT` في `.env`.

**CSV files missing:** تأكد أن الملفات التسعة مباشرة داخل `data/raw/` وبالأسماء الصحيحة.

**pgAdmin لا يتصل:** استخدم host اسمه `postgres` داخل pgAdmin، وليس `localhost`.

**كلمة السر لا تعمل بعد تعديل `.env`:** الـvolume القديم يحتفظ بالمستخدم القديم. لا تمسحه أثناء
العرض؛ استخدم كلمة السر التي بدأ بها الـvolume أو اعمل reset فقط بعد حفظ ما تحتاجه.

**Kestra لا يرى CSV:** راجع `PIPELINE_RAW_DATA_HOST_PATH` وتأكد أنه مسار Docker Desktop، وليس
مسار Windows العادي.

للمزيد من التفاصيل والأرقام المؤكدة، استخدم [`PRESENTATION_GUIDE.md`](PRESENTATION_GUIDE.md).
