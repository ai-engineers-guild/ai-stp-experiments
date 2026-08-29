# Быстрый старт

## Назначение

`ai-stp-experiments` — декларативный corpus из 81 фикстуры. Он проверяет
`ai-stp` через внешние setup-system и headless observer-delegate. Этот репозиторий
не содержит controller, runner, credentials или target state.

## Подготовка

Нужны Python 3.11+, Git и локальные checkout setup-system:

- [`ai-stp`](https://github.com/ai-engineers-guild/ai-stp);
- [`antigravity-setup-system`](https://github.com/NDDev-OpenNetwork/antigravity-setup-system);
- [`pi-setup-system`](https://github.com/NDDev-OpenNetwork/pi-setup-system);
- [`grok-setup-system`](https://github.com/NDDev-OpenNetwork/grok-setup-system);
- [`codex-setup-system`](https://github.com/NDDev-OpenNetwork/codex-setup-system).

```bash
git clone https://github.com/ai-engineers-guild/ai-stp-experiments.git
cd ai-stp-experiments
python -m venv .venv
python -m pip install -e .
```

## Проверка фикстур

```bash
python matrix.py validate
python -m unittest
python generate_index.py
```

Для просмотра одного варианта:

```bash
python matrix.py generate --category hooks --id H01 --harness antigravity --os windows
python materialize.py experiments/hooks/H01/fixtures/main --harness antigravity --output _generated/H01
```

`payload/common` — общий исходник. `payload/harnesses/<profile>` — только
настоящая native-проекция конкретного harness. Materialized output во
временной зоне не является готовым target-tree.

## Полный lifecycle

Внешний controller выбирает строку матрицы и через установленный skill вызывает
`ai-stp` для plan, backup, install и rollback. `ai-stp` вызывает setup-system,
который пишет disposable target. Между install и rollback ровно один раз
запускается read-only observer в headless harness. Evidence сохраняется в
локальном ignored `runs/`.

`runs/`, `results/`, `_generated/` и `dist/` не коммитятся. После нового запуска
обновите локальный каталог:

```bash
python generate_index.py
```

`index.md` — только список локальных запусков, а не копия evidence.

## Веточная модель

- `dev` — default branch и интеграционная ветка;
- `feature/<name>` создаётся от `dev` и вливается обратно в `dev` через PR;
- `main` — protected release branch;
- в `main` допускается только PR из `dev`.

Не добавляйте в corpus controller, `run.py`, provider wrapper, логи, ключи или
абсолютные пути машины.
