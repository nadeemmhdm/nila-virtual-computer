# Resource Usage Strategy

This project targets a complete host with only 4 GB RAM. Resource usage therefore affects correctness, not only performance.

## Design budget

The foundation aims to keep always-on services limited to the FastAPI backend, static frontend serving, SQLite and lightweight monitoring. Heavy components should be started on demand.

Indicative future operating policy:

| Component | Policy |
|---|---|
| FastAPI + SQLite | resident |
| Static web desktop | served as files |
| llama.cpp runtime | one controlled instance; unload when configured |
| Small Q4 GGUF | selected only if estimated RAM fits budget |
| Chromium/Playwright | on demand; idle timeout |
| Heavy task | one at a time by default |
| Project dev server | tied to owning task |

## Pressure thresholds

Default policy direction:

- below 75% RAM: NORMAL
- 75–84%: PRESSURE — avoid new unnecessary workers
- 85–91%: HIGH — stop idle workers and queue heavy work
- 92%+: CRITICAL — pause eligible AI/background work and preserve core UI/service availability

The backend exposes this classification from `/api/resources`.

## Swap

Swap can reduce the chance of an out-of-memory termination during short spikes, but swapping model/browser pages heavily can make the machine unusable. The platform must not size workloads as though swap were normal RAM.

## AI context

Never continuously feed the local model full terminal history, complete webpages, entire project trees or all prior task logs. Store large observations externally and retrieve compact relevant slices. Summarize old task events.

## Browser lifecycle

AI-controlled Chromium is expected to be the most significant transient process besides the model. It must start only when a task requires it and terminate after a configurable idle timeout. Multiple automation browser instances should be rejected under memory pressure.

## Measurements required before final release

The final resource report must contain measurements on a real or constrained 4 GB Debian target for:

1. idle OS + Nila services;
2. frontend connected;
3. AI model loaded but idle;
4. AI inference;
5. terminal/file task execution;
6. Chromium active;
7. AI + Chromium simultaneously;
8. task completion cleanup;
9. recovery after pressure/high-pressure states.

The current foundation document intentionally does not invent RAM numbers that have not yet been measured on the target host.
