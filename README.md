# Кроссплатформенные эксперименты ai-stp

Раннер поддерживает профили `antigravity`, `codex`, `claude-code`, `pi`,
`pi-omp`, `opencode` и `grok-build` на Windows, macOS и Linux. Общий
`harnesses.yaml` не содержит путей конкретного пользователя. Локальные пути и
модель задаются в игнорируемом `harnesses.local.yaml` по образцу
`harnesses.local.example.yaml`.

Требования: Python 3.11+, PyYAML, `ai-stp`, setup-provider нужного харнесса и
соответствующий delegate-скилл. Корень скиллов по умолчанию — соседний
`../my_skills`; другое расположение задаётся `AI_STP_SKILLS_ROOT`, бинарник CLI
— `AI_STP_BIN`.

```bash
python doctor.py --profile codex
python run_all.py --harness-profile codex --ids E00 E01
```

Для матрицы коллега запускает вторую команду для каждого доступного профиля на
Windows, macOS и Linux. `run_all.py` сам вызывает readiness-check и не начинает
изменяющие target опыты, пока CLI, delegate и provider не найдены. В CI задайте
`AI_STP_BIN`, `AI_STP_SKILLS_ROOT`, скопируйте локальные overrides и сохраняйте
`runs/` как artifact.

Каждый запуск пишет отдельный каталог в `runs/<UTC stamp>/` и `summary.yaml`.
Неготовый delegate/provider виден заранее в `doctor.py`; раннер не устанавливает
CLI, не выполняет вход и не читает секреты. Проверка каждой ОС выполняется на
самой ОС — эмуляция названием платформы не считается доказательством.

## Исторический корпус Antigravity

Один документ. На каждый опыт — подпапка `{timestamp}_{harness}_{id}`.
Внутри: `task.yaml` (задача, команды, **промпт**) и `results.yaml` (факт).

Создано: `20260825T160000`. Харнесс первого прогона: `antigravity`. Опытов: **57**.

Снимок живого дома (не трогать): `C:\Users\User\a_projects\agy-live-baseline-20260825-145349`.

## Зачем

Проверяем **сам ai-stp на Windows** в связке с харнессом, по каждому виду компонента.
Ставит и снимает только CLI. Датчик «воспользовался ли харнесс» — headless `agy` с промптом из `task.yaml`.

Дальше те же папки и тот же документ для `claude-code`, `codex`, `grok-build` — меняется поле `harness` и префикс папки.

## Правила круга

1. Сложить текущий ящик в бэкап (`backup.live_snapshot` уже есть; при прогоне ещё `./pre-state` в папке опыта).
2. Сделать харнесс **голым** (пустой сетап через ai-stp; если CLI не умеет — `results.bare_method: blocked` и на этом опыт кончается, не npx).
3. Накатить **только payload** опыта командами из `task.yaml` → `ai_stp`.
4. Передать **ровно** поле `prompt` в делегат: `--task`.
5. Записать ответ Agy и лог CLI в `results.yaml`.
6. Вердикт: `pass` / `fail` / `blocked`.
7. Следующий опыт снова с голого. Полный дом возвращать только опытом E62.

Запрещено: `npx skills`, ручное копирование скиллов в `~/.gemini`, любой установщик кроме `ai-stp`.

## Команды, которыми вообще умеет CLI

Наблюдение: `doctor`, `toolchain harnesses`, `component discover`, `target status`, `setup import inspect`.
Реестр: `component adopt`, `select propose/confirm`.
Постановка в харнесс: `install plan` / `apply` (пишет **провайдер**, не CLI).
Свой скилл управления: `skill install` / `remove` — **только** канон `ai-stp`.
Откат: `install plan --action rollback`.

Нет команды «поставь ponytail в Agy минуя сетап». Нет npx. Нет провайдера на этой машине на старте — часть опытов обязана получить `blocked`. Это и есть результат.

## Перечень

| ID | Папка | Вид | Payload | Заголовок | Статус |
|---|---|---|---|---|---|
| E00 | `20260825T160000_antigravity_E00` | baseline | current-home | Живой discover до очистки | pass |
| E01 | `20260825T160000_antigravity_E01` | bare | empty-setup | Голый харнесс через ai-stp | pass |
| E02 | `20260825T160000_antigravity_E02` | skill | ai-stp | Поставить канонический скилл ai-stp | blocked |
| E03 | `20260825T160000_antigravity_E03` | skill | ai-stp | Снять канонический скилл ai-stp | pass |
| E10 | `20260825T160000_antigravity_E10` | skill | ai-repo-safety | Голый + один скилл ai-repo-safety | blocked |
| E11 | `20260825T160000_antigravity_E11` | skill | audit-bt-tz-realization | Голый + один скилл audit-bt-tz-realization | blocked |
| E12 | `20260825T160000_antigravity_E12` | skill | confluence-gitlab-sync | Голый + один скилл confluence-gitlab-sync | blocked |
| E13 | `20260825T160000_antigravity_E13` | skill | dlt-skill | Голый + один скилл dlt-skill | blocked |
| E14 | `20260825T160000_antigravity_E14` | skill | find-skills | Голый + один скилл find-skills | blocked |
| E15 | `20260825T160000_antigravity_E15` | skill | grill-my-resume-as-manager | Голый + один скилл grill-my-resume-as-manager | blocked |
| E16 | `20260825T160000_antigravity_E16` | skill | grilling | Голый + один скилл grilling | blocked |
| E17 | `20260825T160000_antigravity_E17` | skill | herdr | Голый + один скилл herdr | blocked |
| E18 | `20260825T160000_antigravity_E18` | skill | impeccable | Голый + один скилл impeccable | blocked |
| E19 | `20260825T160000_antigravity_E19` | skill | ponytail | Голый + один скилл ponytail | blocked |
| E20 | `20260825T160000_antigravity_E20` | skill | ponytail-audit | Голый + один скилл ponytail-audit | blocked |
| E21 | `20260825T160000_antigravity_E21` | skill | ponytail-debt | Голый + один скилл ponytail-debt | blocked |
| E22 | `20260825T160000_antigravity_E22` | skill | ponytail-gain | Голый + один скилл ponytail-gain | blocked |
| E23 | `20260825T160000_antigravity_E23` | skill | ponytail-help | Голый + один скилл ponytail-help | blocked |
| E24 | `20260825T160000_antigravity_E24` | skill | ponytail-review | Голый + один скилл ponytail-review | blocked |
| E25 | `20260825T160000_antigravity_E25` | skill | skill-conductor | Голый + один скилл skill-conductor | blocked |
| E26 | `20260825T160000_antigravity_E26` | skill | spec-review | Голый + один скилл spec-review | blocked |
| E27 | `20260825T160000_antigravity_E27` | skill | spec-write | Голый + один скилл spec-write | blocked |
| E28 | `20260825T160000_antigravity_E28` | skill | twinby-context | Голый + один скилл twinby-context | blocked |
| E29 | `20260825T160000_antigravity_E29` | skill | workflow-herdr | Голый + один скилл workflow-herdr | blocked |
| E30 | `20260825T160000_antigravity_E30` | skill | jira-daily-pm-radar | Голый + скилл jira-daily-pm-radar из ~/.gemini/skills | blocked |
| E31 | `20260825T160000_antigravity_E31` | skill | langfuse | Голый + скилл langfuse | blocked |
| E32 | `20260825T160000_antigravity_E32` | mcp | playwright | Голый + один MCP playwright | blocked |
| E33 | `20260825T160000_antigravity_E33` | mcp | context7 | Голый + один MCP context7 | blocked |
| E34 | `20260825T160000_antigravity_E34` | mcp | deepwiki | Голый + один MCP deepwiki | blocked |
| E35 | `20260825T160000_antigravity_E35` | mcp | eslint | Голый + один MCP eslint | blocked |
| E36 | `20260825T160000_antigravity_E36` | mcp | shadcn | Голый + один MCP shadcn | blocked |
| E37 | `20260825T160000_antigravity_E37` | mcp | figma | Голый + один MCP figma | blocked |
| E38 | `20260825T160000_antigravity_E38` | mcp | chrome-devtools | Голый + один MCP chrome-devtools | blocked |
| E39 | `20260825T160000_antigravity_E39` | mcp | ast-grep | Голый + один MCP ast-grep | blocked |
| E40 | `20260825T160000_antigravity_E40` | mcp | ripgrep | Голый + один MCP ripgrep | blocked |
| E41 | `20260825T160000_antigravity_E41` | mcp | semble | Голый + один MCP semble | blocked |
| E42 | `20260825T160000_antigravity_E42` | mcp | serena | Голый + один MCP serena | blocked |
| E43 | `20260825T160000_antigravity_E43` | mcp | github | Голый + один MCP github | blocked |
| E44 | `20260825T160000_antigravity_E44` | mcp | gitlab | Голый + один MCP gitlab | blocked |
| E45 | `20260825T160000_antigravity_E45` | mcp | atlassian | Голый + один MCP atlassian | blocked |
| E46 | `20260825T160000_antigravity_E46` | hook | herdr | Голый + только хук herdr | blocked |
| E47 | `20260825T160000_antigravity_E47` | setting | antigravity-cli/settings.json | Голый + только setting | blocked |
| E48 | `20260825T160000_antigravity_E48` | plugin | antigravity-cli/plugins | Голый + только plugin | blocked |
| E49 | `20260825T160000_antigravity_E49` | agent | config/agents | Голый + только agent | blocked |
| E50 | `20260825T160000_antigravity_E50` | command | .agents/commands | Голый + command в проекте (глобальных нет) | blocked |
| E51 | `20260825T160000_antigravity_E51` | instruction | .agents / AGENTS.md | Голый + instruction в проекте | blocked |
| E52 | `20260825T160000_antigravity_E52` | setup | ponytail+spec-write | Два скилла в одном сетапе: ponytail + spec-write | blocked |
| E53 | `20260825T160000_antigravity_E53` | setup | all-config-skills | Сетап из 20 скиллов | blocked |
| E54 | `20260825T160000_antigravity_E54` | setup | all-mcp | Сетап только MCP (все 14) | blocked |
| E55 | `20260825T160000_antigravity_E55` | setup | hooks-only | Сетап только хуки | blocked |
| E56 | `20260825T160000_antigravity_E56` | setup | empty | Пустой сетап (явная пустота) | pass |
| E57 | `20260825T160000_antigravity_E57` | import | C:\Users\User\a_projects\agy-live-baseline-20260825-145349 | import inspect снимка | pass |
| E58 | `20260825T160000_antigravity_E58` | provider | none | install apply без провайдера — ожидаемый отказ | pass |
| E59 | `20260825T160000_antigravity_E59` | target | status | target status после попытки установки | blocked |
| E60 | `20260825T160000_antigravity_E60` | target | rollback | rollback через ai-stp | blocked |
| E61 | `20260825T160000_antigravity_E61` | source | anthropics/skills frontend-design | component source parse внешнего скилла (не npx) | pass |
| E62 | `20260825T160000_antigravity_E62` | restore | live-full | Восстановить полный дом бэкапом ai-stp | blocked |

## Порядок

E00 (не чистить) → E01 голый → E02–E03 канон ai-stp → E10–E29 по одному скиллу → E30–E31 gemini/skills → E32–E45 по одному MCP → E46–E51 виды компонента → E52–E56 сетапы → E57–E62 контур CLI (import, provider, status, rollback, restore).

Стоп, если E01 не смог сделать голый ящик через ai-stp: дальше все «накаты» бессмысленны, пока нет apply/провайдера. Тогда чиним CLI/провайдер, не обходим файлами.



