# Правила для ai-stp-experiments

## Назначение

Это декларативный corpus из 81 эксперимента для проверки `ai-stp` через
делегирование headless observer в реальные target harnesses. Репозиторий
содержит только manifest, fixture payload, passport patch и observer prompt.

Не добавлять сюда controller, runner, `run.py`, provider wrapper, lifecycle
скрипты, credentials, логи или target state. Lifecycle выполняется внешним
controller; evidence сохраняется в ignored `runs/`.

## Fixture contract

- Использовать `payload/common` по умолчанию: одна общая фикстура должна работать
  для всех совместимых харнессов.
- Использовать `payload/harnesses/<profile>` только для настоящего native
  различия формата, пути, entry point или runtime API.
- Если common и native payload нельзя оставлять вместе, явно указывать `exclude`
  в соответствующей variant.
- `passport-overrides/<profile>.json` должен содержать только различия паспорта.
- `fixture.yaml` описывает logical objects, states, variants и managed paths;
  `experiment.yaml` описывает гипотезу, состав и expected observation.
- Абсолютные пути машины запрещены. Секреты, ключи, токены, auth-файлы и
  содержимое `.env` запрещены.

`setup` — категория композиции. Component types только такие: `instruction`,
`skill`, `mcp`, `hook`, `command`, `agent`, `plugin`, `setting`.

## Харнессы и unsupported

Матрица строится по осям OS × harness × category × experiment × fixture.
Отсутствующий native variant остаётся строкой с `expected: unsupported` и
машинной причиной. Не объявлять fixture runnable только ради красивой
статистики.

Общие setup-system:

- [`ai-stp`](https://github.com/ai-engineers-guild/ai-stp);
- [`antigravity-setup-system`](https://github.com/NDDev-OpenNetwork/antigravity-setup-system);
- [`pi-setup-system`](https://github.com/NDDev-OpenNetwork/pi-setup-system);
- [`grok-setup-system`](https://github.com/NDDev-OpenNetwork/grok-setup-system);
- [`codex-setup-system`](https://github.com/NDDev-OpenNetwork/codex-setup-system).

## Lifecycle boundary

Внешний controller обязан:

1. создать отдельный disposable target;
2. использовать установленный skill и CLI `ai-stp` для plan, backup, install и
   rollback;
3. сохранить exact plan digest, operation IDs, provider state и `backup_ref`;
4. вызвать target harness delegate в headless-режиме ровно один раз между
   install и rollback;
5. выполнить rollback в `finally`, включая timeout/crash observer;
6. сравнить restored managed state с baseline механически.

Observer read-only: он не устанавливает, не удаляет, не включает и не выключает
компоненты. Нельзя считать file existence доказательством runtime behaviour.
Provider не вызывается напрямую: итоговое состояние пишет только setup-system,
вызванный через `ai-stp`.

## Команды

```bash
python matrix.py validate
python -m unittest test_matrix.py
python generate_index.py
```

Перед commit проверить diff, не добавлять ignored evidence и убедиться, что
изменения ограничены corpus/documentation.
