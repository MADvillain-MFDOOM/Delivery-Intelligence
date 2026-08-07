# Architecture

Delivery Intelligence is designed as a set of separable stages. Each stage should have explicit inputs, outputs, validation rules, and provenance so that an analysis can be reviewed without relying on hidden organisational context.

## Intended modules

### Jira acquisition

Connect to Jira through environment-driven credentials and a configured base URL. Acquisition should limit scope deliberately, record extraction timestamps and query parameters, and avoid embedding organisation-specific project keys or URLs in source code.

### Normalisation

Convert source records into the public conceptual model: delivery items, hierarchy links, ownership labels, status transitions, estimates, dates, dependencies, and source references. Normalisation should preserve raw evidence identifiers without requiring a particular Jira schema.

### Evidence-quality validation

Assess completeness, consistency, timeliness, and suitability for each intended metric. Invalid or ambiguous records remain visible with a reason and quality flag, but are excluded from calculations that require stronger evidence.

### Delivery analysis

Calculate flow and governance measures such as throughput, cycle time, WIP, aging, spillover, capacity, and dependency signals. Analysis logic should consume the normalised model rather than Jira-specific fields wherever practical.

### Forecasting

Use only work that passes explicit forecast-readiness checks. Forecasting should expose assumptions, uncertainty, excluded work, and sensitivity to historical evidence rather than presenting a single unsupported date.

### Reporting

Present decision-oriented findings, metric definitions, evidence-quality summaries, exclusions, and caveats. Reports should make it possible to trace a conclusion back to its inputs and configuration.

### Configuration/governance layer

Keep source settings, hierarchy mappings, status categories, inclusion rules, and governance thresholds in configuration. Secrets belong in the runtime environment, never in tracked files. Configuration should be versioned only when it is generic and safe to publish.

## Boundary rule

The public repository defines interfaces and concepts first. It does not encode any company-specific Jira schema, workflow, policy, customer data, capacity figures, or production integration details.
