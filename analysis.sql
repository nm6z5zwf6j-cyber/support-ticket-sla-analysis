WITH observed AS (
  SELECT *, datetime(created, '+' || target_minutes || ' minutes') AS deadline
  FROM tickets
  WHERE created <= datetime(:cutoff)
), classified AS (
  SELECT *, CASE
    WHEN responded IS NOT NULL AND datetime(responded) <= datetime(:cutoff)
      THEN CASE WHEN datetime(responded) <= deadline THEN 'met' ELSE 'breached' END
    WHEN deadline <= datetime(:cutoff) THEN 'breached'
    ELSE 'pending'
  END AS sla_status
  FROM observed
)
SELECT priority, COUNT(*) AS tickets,
       SUM(sla_status = 'met') AS met,
       SUM(sla_status = 'breached') AS breached,
       SUM(sla_status = 'pending') AS pending,
       ROUND(100.0 * SUM(sla_status = 'met') / NULLIF(SUM(sla_status != 'pending'), 0), 2) AS sla_met_pct_decided
FROM classified GROUP BY priority ORDER BY priority;
