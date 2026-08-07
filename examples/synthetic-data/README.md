# Synthetic data examples

This directory contains a deterministic, entirely synthetic Jira-like delivery dataset. It represents a small fictional delivery environment with initiatives, epics, stories, bugs, multiple teams, sprint assignments, capacity, status history, and explicit dependencies.

The records deliberately represent both healthy and problematic delivery conditions:

- valid parent-child hierarchy and multiple issue types;
- missing parents, estimates, and team ownership;
- completed work, work in progress, blocked work, and long-running work;
- sprint-assigned work, work outside a sprint, and spillover from an earlier sprint;
- explicit blocking and dependency relationships; and
- cancelled work that is excluded from forecast-ready totals.

Problematic records exist so the evidence-quality analysis has meaningful cases to detect. They remain visible in the output with issue keys, problem types, and human-readable reasons; they are not silently dropped or allowed to contaminate forecast-ready totals.

The files are public documentation, regression evidence, and demonstration data. They contain no production export, real Jira key, real person, customer, company, or private system information. Keep future examples fabricated rather than anonymising operational data.
