# Skill versions changelog

Immutable snapshots. Rollback forks forward (does not rewrite history).

- `v0001_20261001-234339_1-1-1` · snapshot · score=n/a (v1.1 pre-Phase1 baseline) · source=seed · parent=- · initial seed
- `v0002_20261001-234605_4-4-6-6` · snapshot · score=evals 4/4, body 6/6 · source=manual · parent=v0001_20261001-234339_1-1-1 · S3: Freedom + Harness attach + evals scaffold
- `v0003_20261001-234811_6-6-8-8` · snapshot · score=evals 6/6, body 8/8 · source=manual · parent=v0002_20261001-234605_4-4-6-6 · S5: brainstorm mode (second-ring <=2, checkpoint-write deferred)
- `v0004_20261002-000815_8-8-8-8` · snapshot · score=evals 8/8, body 8/8 · source=manual · parent=v0003_20261001-234811_6-6-8-8 · S5 fix: v1.2 header (was left uncommitted at f836d08) + cap(<=5) violation eval
