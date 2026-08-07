# Delivery Intelligence Model

This public model describes the concepts needed for delivery analysis without prescribing a specific Jira schema.

## Core concepts

- **Delivery item** — a unit of work tracked from an agreed start point to a defined completion point.
- **Hierarchy** — relationships between delivery items, such as parent, child, initiative, or linked work. The names and levels are configurable.
- **Ownership** — the accountable team or role associated with an item. Public examples should use synthetic labels.
- **Capacity** — the amount of delivery ability available for a defined period, expressed using an explicitly documented unit and confidence level.
- **Throughput** — the count of delivery items meeting the completion rule during a period.
- **Work in progress (WIP)** — items started but not yet meeting the completion rule at a point in time or across a period.
- **Cycle time** — elapsed time between the configured start and completion events.
- **Aging** — elapsed time for an item that is still in progress, measured from the configured start event.
- **Dependencies** — relationships where one item may constrain the start, progress, or completion of another.
- **Forecast readiness** — an assessment of whether an item and its supporting evidence are suitable for inclusion in a forecast.
- **Evidence quality** — the assessed completeness, consistency, timeliness, and provenance of the data supporting a record or metric.
- **Delivery risk signals** — observable conditions such as aging outliers, blocked dependencies, high WIP, repeated spillover, weak evidence, or capacity mismatch. A signal is not automatically a prediction or a diagnosis.

## Model expectations

Every derived metric should identify its population, time window, event definitions, exclusions, and evidence-quality requirements. Hierarchy and ownership are descriptive dimensions unless a documented analysis rule gives them a specific analytical role. Missing or invalid evidence should be represented explicitly rather than silently converted into a favourable value.
