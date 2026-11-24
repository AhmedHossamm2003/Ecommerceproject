-- Read-only verification for the latest Phase 4 quality-gate execution.

SELECT gate_run_id, transformation_run_id, status, rules_evaluated,
       blocking_failures, warning_failures, started_at, finished_at, error_message
FROM quality.gate_runs
ORDER BY started_at DESC
LIMIT 5;

WITH latest AS (
    SELECT gate_run_id
    FROM quality.gate_runs
    ORDER BY started_at DESC
    LIMIT 1
)
SELECT rules.rule_key, rules.description, results.severity,
       results.observed_value, results.comparison, results.expected_value,
       results.passed, results.executed_at
FROM quality.gate_results AS results
JOIN quality.gate_rules AS rules USING (rule_id)
WHERE results.gate_run_id = (SELECT gate_run_id FROM latest)
ORDER BY rules.sort_order, rules.rule_id;

SELECT rule_key, severity, enabled, comparison, expected_value, description
FROM quality.gate_rules
ORDER BY sort_order, rule_id;
