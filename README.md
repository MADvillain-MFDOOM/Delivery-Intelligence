# Delivery Intelligence

Jira-based delivery intelligence for evidence-driven planning, flow analysis, forecasting, and delivery governance.

This repository is a public reference implementation shell. It is intentionally generic and uses synthetic examples only; it is not a copy of any organisation's internal delivery system.

## Purpose

Delivery Intelligence is intended to help teams turn governed Jira data into transparent delivery signals and decision-ready reporting. The initial release establishes the public conceptual model, documentation, configuration boundary, and package layout before reusable implementation is introduced.

The conceptual flow is:

```text
Jira
  → governed extraction
  → evidence-quality validation
  → delivery analysis
  → forecasting and diagnostics
  → decision-ready reporting
```

## Core principles

- Evidence before opinion.
- Metrics support decisions, not vanity reporting.
- Invalid data remains visible but should not contaminate forecasting.
- Delivery governance should be encoded where practical.
- Configuration should remain separate from analysis logic.
- Traceability and auditability matter.
- Synthetic data should be sufficient to demonstrate public examples.

## High-level architecture

The planned system is modular: acquisition obtains Jira records, normalisation maps them to a public conceptual model, validation assesses evidence quality, analysis derives flow measures, forecasting and diagnostics assess future delivery, and reporting presents conclusions with traceable caveats. See [docs/architecture.md](docs/architecture.md).

## Repository structure

- `docs/` — public architecture, model, and metric definitions.
- `src/` — package boundaries for future reusable implementation.
- `config/` — generic, environment-driven example configuration.
- `examples/synthetic-data/` — guidance for safe public examples.
- `tests/` — future automated checks.

## Current maturity/status

Synthetic Jira data can be loaded and normalised, evidence quality can be validated, and delivery items can be classified for forecast readiness. The first forecasting algorithm is also available: it generates evidence-gated delivery scenarios from historical completed points. Dashboards and live Jira acquisition are not implemented yet.

### Evidence Quality / Forecast Readiness

The public example follows this flow:

```text
Synthetic Jira data
  → load and normalise
  → validate evidence quality
  → classify forecast readiness
  → expose invalid scope
  → generate decision-ready output
```

Run the console example from the repository root with:

```bash
python3 -m src.reporting.console
```

The result is also captured as a behavioural contract in `examples/expected-output/evidence-quality.json`.

### Delivery Forecasting

Generate a concise scenario report with:

```bash
python3 -m src.reporting.forecast_console
```

Emit the complete `DeliveryForecast.v1` JSON contract with:

```bash
python3 -m src.reporting.forecast_console --json
```

The forecast uses configured historical throughput percentiles. It assigns completed work to the sprint window containing its resolution date, forecasts only evidence-ready estimated item types, exposes invalid scope, and reports insufficient history rather than overstating confidence.

## Safety and data handling

Never commit credentials, tokens, private URLs, production exports, or identifiable company, customer, or employee information. Use synthetic or fully anonymised data in examples and issues. Review [SECURITY.md](SECURITY.md) before contributing.

## Getting started

Setup and runnable examples will be documented when the first reusable implementation lands. For now, start with the conceptual model, metrics catalogue, and `config/example.yaml`.

## Planned capabilities

- Governed Jira extraction with explicit scope and provenance.
- Normalised delivery-item and hierarchy representations.
- Evidence-quality checks and visible exclusion reasons.
- Flow, aging, WIP, capacity, spillover, and dependency analysis.
- Additional forecasting methods, calibration, and diagnostics.
- Decision-ready reports with traceable inputs and caveats.
- Tests and synthetic fixtures that can run without private systems.
