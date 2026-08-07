# Metrics Catalogue

Initial generic catalogue. Exact event rules, time windows, units, and quality gates belong in configuration or the analysis specification for each use case.

## Throughput

- **Definition:** Number of delivery items meeting the configured completion rule during a reporting period.
- **Purpose:** Describe completed delivery flow and provide historical input to planning or forecasting.
- **Interpretation:** Higher throughput may indicate more completed work, but is meaningful only with stable scope and item definitions.
- **Known caveats:** Sensitive to item sizing, splitting, reopened work, completion-date quality, and changes in reporting behaviour.

## Cycle Time

- **Definition:** Elapsed time between a configured start event and completion event for a completed delivery item.
- **Purpose:** Understand how long work takes once started and identify flow friction.
- **Interpretation:** Use distributions and segments rather than a single average where possible.
- **Known caveats:** Start/finish definitions, pauses, holidays, reopened items, and missing transitions can materially change results.

## Work Item Age

- **Definition:** Elapsed time from the configured start event to the observation time for an incomplete item.
- **Purpose:** Highlight aging work and possible delivery risk.
- **Interpretation:** Older items deserve investigation, not automatic escalation; context and item type matter.
- **Known caveats:** Inaccurate start dates, intentional long-running work, blocked periods, and stale records can distort age.

## WIP

- **Definition:** Count of items that are in progress under the configured scope at a point in time or during a period.
- **Purpose:** Assess flow load and the relationship between starting and finishing work.
- **Interpretation:** Sustained high WIP can increase delay and reduce focus, but a threshold must be context-specific.
- **Known caveats:** Status mapping, parallel work, paused items, and scope changes affect comparability.

## Spillover

- **Definition:** Work planned for one period that remains incomplete at the period boundary or moves into a later period.
- **Purpose:** Identify planning stability and unfinished commitments.
- **Interpretation:** Repeated spillover is a signal to examine scope, dependencies, capacity, and planning rules.
- **Known caveats:** Requires reliable period assignment and boundary dates; legitimate reprioritisation can look like failure.

## Forecast-ready work

- **Definition:** Work that passes configured evidence and eligibility checks for inclusion in a forecast.
- **Purpose:** Prevent weak or ambiguous records from silently influencing projections.
- **Interpretation:** A smaller high-quality population is preferable to a larger opaque one.
- **Known caveats:** Readiness is a quality judgement, not a guarantee of completion; rules should be visible and reviewable.

## Unestimated work

- **Definition:** In-scope work without a usable estimate under the configured estimation rule.
- **Purpose:** Make estimation gaps visible and assess their effect on planning or capacity comparisons.
- **Interpretation:** Unestimated work may be small, large, or intentionally unestimated; it should not be treated as zero.
- **Known caveats:** Estimate fields and units vary; missing values may reflect workflow timing rather than poor practice.

## Excluded work

- **Definition:** Records excluded from a metric or forecast, with a recorded reason.
- **Purpose:** Preserve transparency about population changes and evidence limitations.
- **Interpretation:** Exclusions are part of the result and may reveal process or data-quality improvements.
- **Known caveats:** Broad exclusion rules can hide risk; exclusions should be counted, categorised, and reviewable.

## Capacity

- **Definition:** Configured delivery ability available to a scope and period, using a stated unit and confidence level.
- **Purpose:** Compare expected demand with available ability and support scenario planning.
- **Interpretation:** Capacity is an assumption or estimate unless backed by an explicit source and method.
- **Known caveats:** Availability, interruptions, skill mix, dependencies, and unit comparability can make capacity uncertain.

## Delivery confidence

- **Definition:** A transparent, evidence-based assessment of the likelihood that a defined delivery outcome will be met within a defined window.
- **Purpose:** Support decisions while showing the evidence and uncertainty behind the assessment.
- **Interpretation:** Confidence should be expressed with drivers, assumptions, and caveats—not as an unexplained score.
- **Known caveats:** It is not a probability unless the method is calibrated; stale evidence and changing scope reduce reliability.
