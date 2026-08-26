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
        └── harnesses/<profile>/    # нативная проекция setup-system
    └── passport-overrides/<profile>.json # необязательный merge override
```

Категории фиксированы: `instructions`, `skills`, `mcps`, `hooks`, `commands`,
`agents`, `plugins`, `settings`, `setups`. Категория `agents` соответствует
каноническому component type `agent`; роль такого компонента может быть
`subagent`.

`experiment.yaml` владеет целью, доступными provider-вариантами, порядком фикстур и
проверкой observer. `fixture.yaml` владеет одним физическим компонентом,
логическими объектами внутри него и тремя ожидаемыми состояниями:

- `baseline` — состояние до операции;
- `installed` — состояние после установки и наблюдения;
- `restored` — состояние после rollback; обязано совпадать с `baseline`.

Один агрегирующий нативный файл может представлять несколько логических
объектов (например, два MCP server или два hook handler). Это отражается в
`objects`, но остаётся одной fixture и одним паспортом.

## Жизненный цикл

```text
doctor → baseline snapshot → ai-stp plan/approve/apply → filesystem assertions
→ target-harness observer → ai-stp rollback → restored snapshot comparison
```

Только provider, вызванный через ai-stp, пишет target. Backup создаёт provider,
а rollback использует точный `backup_ref`. Раннер не удаляет live-файлы вручную.
По умолчанию используется изолированный HOME. Live target разрешается только
явным флагом и после успешного doctor.

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
- observer запускается только после успешной установки;
- rollback запускается в `finally`, а restored snapshot сравнивается с baseline;
- одна команда строит матрицу по OS, harness, category, experiment и fixture.
- матрица не удаляет отсутствующий provider-вариант, а помечает его
  `expected: unsupported`.
