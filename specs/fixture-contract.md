# Контракт экспериментальных фикстур

## Цель

Репозиторий проверяет связку `ai-stp CLI × provider × OS × harness × component`
одинаковым способом для восьми видов компонентов и полного сетапа.

## Структура

```text
experiments/<category>/<experiment-id>/
├── experiment.yaml
└── fixtures/<fixture-id>/
    ├── fixture.yaml
    ├── passport-patch.json
    └── payload/
        ├── common/                 # необязательная общая часть payload
        └── harnesses/<profile>/    # байты компонента для этого варианта
    └── passport-overrides/<profile>.json # необязательный merge override
```

Категории фиксированы: `instructions`, `skills`, `mcps`, `hooks`, `commands`,
`agents`, `plugins`, `settings`, `setups`. Категория `agents` соответствует
каноническому component type `agent`; роль такого компонента может быть
`subagent`.

`experiment.yaml` владеет гипотезой, доступными provider-вариантами, порядком
фикстур и ожидаемым наблюдением. `fixture.yaml` владеет одним физическим компонентом,
логическими объектами внутри него и тремя механически проверяемыми состояниями:

- `baseline` — состояние до операции;
- `installed` — состояние после установки и наблюдения;
- `restored` — состояние после rollback; обязано совпадать с `baseline`.

Если нативный способ вызова различается, `observe.<harness>_probe.probe`
переопределяет только read-only probe данного харнесса. Например, один provider
может проецировать plugin как tool, а другой — как skill внутри plugin. Observer
проверяет фактическую нативную поверхность и не требует несуществующий вид вызова.

Payload является исходным компонентом, а не готовым target-tree. Если сохранённая
фикстура повторяет нативную раскладку для удобства чтения, variant объявляет
`source_subpath` и `authoring_path`: materializer переносит только исходный
компонент в discoverable authoring layout. Нативную проекцию всегда строит
`ai-stp`, а записывает setup-system.

Один агрегирующий нативный файл может представлять несколько логических
объектов (например, два MCP server или два hook handler). Это отражается в
`objects`, но остаётся одной fixture и одним паспортом.

## Наблюдение

```text
любой controller harness + skill ai-stp
→ backup через ai-stp и setup-system
→ install через ai-stp и setup-system
→ observer prompt: installed
→ rollback через ai-stp и setup-system
→ механическое сравнение managed state с backup
```

Репозиторий не вызывает CLI, provider или harness. Любой controller harness
следует установленному skill `ai-stp`; target harness выбирается независимо и
может совпадать с controller harness. Ограничения конкретной операции определяет
skill, а не корпус экспериментов. Только provider, вызванный через `ai-stp`, пишет
target, создаёт backup и выполняет rollback по точному `backup_ref`.

Observer вызывается ровно один раз между install и rollback. Он ничего не
устанавливает, не удаляет, не включает и не выключает. Он перечисляет по именам видимые `instruction`, `skill`, `mcp`,
`hook`, `command`, `agent`, `plugin` и `setting`, после чего пишет отдельный
`state/<experiment>-<harness>-installed.yaml`. Пустая категория записывается как
пустой список, ненаблюдаемая — как пустой список с пояснением в `notes`.

Observer YAML является наблюдением харнесса, а не доказательством provider
операций. Plan digest, operation, backup, managed state и rollback evidence
сохраняет controller harness из машинных ответов `ai-stp`.

Результаты, логи, snapshots и сгенерированная матрица являются локальными
артефактами и не коммитятся.

## Критерии приёмки

- валидатор находит ровно девять категорий и хотя бы один experiment в каждой;
- валидатор требует ровно 25 skill, 16 mcp, 10 hook, по 5 остальных компонентов
  и 5 setup — всего 81 логический experiment;
- каждый experiment и fixture имеют manifest;
- пути и команды не содержат machine-specific абсолютных путей;
- harness overlay не заменяет общий manifest или паспорт;
- setup содержит минимум по два skill, hook, mcp, setting и agent;
- для каждой строки матрицы генерируется ровно один installed observer prompt;
- observer возвращает строгий YAML в финальном ответе, а state-файл сохраняет
  controller; observer не пишет evidence сам;
- observer только инвентаризирует видимые объекты и не выполняет sample task;
- lifecycle не кодируется списком команд в этом репозитории;
- одна команда строит матрицу по OS, harness, category, experiment и fixture.
- матрица не удаляет отсутствующий provider-вариант, а помечает его
  `expected: unsupported`.
