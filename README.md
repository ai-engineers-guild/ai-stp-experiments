# ai-stp-experiments

Декларативный corpus для проверки `ai-stp`: эксперименты, фикстуры,
паспорта и read-only observer prompts. Это не runtime-проект и не реализация
`ai-stp`.

Быстрый старт: [QUICKSTART.md](QUICKSTART.md). Лицензия: [LICENSE](LICENSE).

## Граница проекта

В репозитории ровно 81 логический experiment в девяти категориях:

- восемь component types: `instruction`, `skill`, `mcp`, `hook`, `command`,
  `agent`, `plugin`, `setting`;
- категория `setup` — композиция нескольких компонентов, а не девятый
  component type.

Здесь хранятся только `experiment.yaml`, `fixture.yaml`, passport patches,
payload и observer prompts. Здесь не должно быть controller, runner, provider
wrapper, runtime-кода, credentials или live target state.

## Общие фикстуры и projections

Одна fixture описывает один логический компонент. Сначала используется общий
payload:

```text
fixtures/<fixture-id>/
├── fixture.yaml
├── passport-patch.json
├── passport-overrides/<harness>.json
└── payload/
    ├── common/                    # общий исходник по умолчанию
    └── harnesses/<profile>/       # только native-различие харнесса
```

Большинство фикстур общие для всех харнессов. Native projection добавляется,
только когда конкретный харнесс требует другой формат, путь или entry point.
`exclude` убирает из materialized source чужой общий payload, если одновременно
нельзя оставлять portable и native представления. `passport-overrides` меняет
только поля паспорта, отличающиеся у харнесса.

Materializer создаёт временный source tree. Итоговую native-конфигурацию target
строит setup-system через `ai-stp`; payload не является готовым target-tree.
Отсутствующий вариант не маскируется: matrix сохраняет строку с
`expected: unsupported`.

## Как это проверяется

Основной объект проверки — связка:

```text
ai-stp CLI → setup-system → disposable target harness
```

Внешний controller выбирает строку matrix, устанавливает skill `ai-stp`, через
него выполняет plan, backup, install и rollback, а между install и rollback
один раз делегирует read-only observer в headless-режиме. Observer только
инвентаризирует фактические logical objects, managed paths и безопасный probe;
он не меняет конфигурацию. Plan digests, operation IDs, backup refs, provider
responses и observer state сохраняются только во внешнем ignored evidence.

Проект проверяется с такими setup-system:

- [`ai-stp`](https://github.com/ai-engineers-guild/ai-stp) — CLI и сборка setup;
- [`antigravity-setup-system`](https://github.com/NDDev-OpenNetwork/antigravity-setup-system);
- [`pi-setup-system`](https://github.com/NDDev-OpenNetwork/pi-setup-system);
- [`grok-setup-system`](https://github.com/NDDev-OpenNetwork/grok-setup-system);
- [`codex-setup-system`](https://github.com/NDDev-OpenNetwork/codex-setup-system).

Локальные checkout этих setup-system находятся рядом с проектом в
`C:\Users\User\a_projects`. Их код не копируется сюда и не становится
зависимостью fixture corpus.

## Проверка corpus

```bash
python matrix.py validate
python -m unittest test_matrix.py
python matrix.py generate --category hooks --id H01 --harness antigravity --os windows
python materialize.py experiments/hooks/H01/fixtures/main --harness antigravity --output _generated/H01
```

`matrix.py validate` проверяет количество категорий, manifest, payload,
projection mappings и отсутствие machine-specific absolute paths.

## Evidence

`runs/` — только локальный ignored каталог результатов. В нём могут быть
исторические JSON/log/state/report с прежними путями; их не переписывают, потому
что это историческое evidence. Новый controller-код создаётся вне этого
репозитория. В `runs/` не складываются `run.py`, runner или provider wrapper.

После добавления или перемещения run обновляется tracked индекс:

```bash
python generate_index.py
```

`index.md` генерируется скриптом и показывает дочерние элементы `runs/`, не
становясь копией самих результатов.
