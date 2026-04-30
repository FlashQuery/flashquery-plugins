# LLM Usage Reporting Workflow

Use this workflow when the user asks about AI costs, token usage, model activity, or wants to audit LLM calls made by FlashQuery.

Requires Supabase to be configured. If `get_llm_usage` returns `isError: true`, tell the user that LLM usage reporting requires a Supabase connection.

## Routing by intent

| User intent | Mode | Key params |
|-------------|------|------------|
| "How much have we spent this week?" | `summary` | `period: "7d"` |
| "What's our total all-time AI spend?" | `summary` | `period: "all"` |
| "Which purposes are using the most tokens?" | `by_purpose` | `period: "30d"` |
| "Which model is called most often?" | `by_model` | — |
| "Show me the last 20 AI calls" | `recent` | `limit: 20` |
| "What did that last skill run cost?" | `recent` | `trace_id: "<id>"` |
| "Show me all calls for summarization" | `recent` | `purpose_name: "summarization"` |

---

## Mode: summary

Returns aggregate totals for the selected time window plus an optional comparison to the prior period.

```
get_llm_usage(
  mode: "summary",
  period: "7d"   // or "24h", "30d", "all"
)
```

**Key fields to surface:**
- `total_spend_usd` — total spend for the period
- `total_calls` — number of LLM calls
- `avg_cost_per_call_usd`, `avg_latency_ms`
- `top_purpose`, `top_model_name`
- `vs_prior_period.spend_delta_pct` / `calls_delta_pct` — % changes vs. prior equivalent window (absent when `period: "all"`)

**Date range override:** pass `from_date` and `to_date` (ISO 8601) instead of `period` for a custom window. `to_date` without `from_date` is not allowed.

---

## Mode: by_purpose

Breaks down usage per named purpose (as configured in `flashquery.yml`), sorted by call count descending. Useful for understanding which workflows drive the most spend.

```
get_llm_usage(
  mode: "by_purpose",
  period: "30d"
)
```

**Key fields per row:**
- `purpose_name` — the purpose alias (or `"_direct"` for `resolver: "model"` calls)
- `calls` — number of calls for this purpose
- `pct_of_total_calls` — fraction of total calls [0, 1]; multiply by 100 to display as a percentage
- `spend_usd`, `avg_cost_per_call_usd`, `avg_latency_ms`
- `primary_model_hit_rate` — fraction of calls that used the first model in the purpose's chain (i.e., no fallback needed); multiply by 100 for percentage

**Note:** `_direct` represents calls made with `resolver: "model"` rather than through a named purpose.

---

## Mode: by_model

Breaks down usage per model alias, sorted by call count descending. Useful for understanding which models are actually being used.

```
get_llm_usage(
  mode: "by_model",
  period: "7d"
)
```

**Key fields per row:**
- `model_name` — the model alias (e.g. `"fast"`), not the underlying API model string
- `provider_name` — which provider served the calls
- `calls`, `spend_usd`, `avg_cost_per_call_usd`, `avg_latency_ms`
- `pct_of_total_calls` — fraction [0, 1]
- `avg_fallback_position` — average position in the fallback chain used; null when all calls were direct (resolver=model)

---

## Mode: recent

Returns a log of recent individual LLM calls, newest first. Useful for auditing a specific run or seeing what just happened.

```
get_llm_usage(
  mode: "recent",
  limit: 20         // default 20, max 1000
)
```

**Filter by trace:** to see all calls from a single skill run, pass the `trace_id` that was set on `call_model`:
```
get_llm_usage(
  mode: "recent",
  trace_id: "report-draft-001"
)
```

**Filter by purpose:**
```
get_llm_usage(
  mode: "recent",
  purpose_name: "summarization"
)
```

**Key fields per row:**
- `timestamp` — when the call was made
- `purpose_name` — purpose alias or `"_direct"`
- `model_name` — model alias used
- `tokens.input`, `tokens.output`, `cost_usd`
- `latency_ms`
- `trace_id` — correlation ID if one was set

---

## Interpreting and presenting results

- **`pct_of_total_calls`** is a fraction, not a percentage. Always multiply by 100 when presenting to the user (e.g., `0.34 → 34%`).
- **`primary_model_hit_rate`** is likewise a fraction.
- **`vs_prior_period`** fields are absent (not null) when `period: "all"` — do not try to reference them in that case.
- **Delta fields** (`spend_delta_pct`, `calls_delta_pct`) are null when the prior period had zero calls — report "no prior data" in that case.
- **`avg_fallback_position`** is null when all calls in the group have no fallback position (e.g., all were direct model calls). This is normal; it means no fallback chain was used.

---

## Example patterns

**"How much have we spent on AI this week?"**
→ `get_llm_usage(mode: "summary", period: "7d")` → report `total_spend_usd` and compare to `vs_prior_period.spend_delta_pct`

**"Which purpose costs the most?"**
→ `get_llm_usage(mode: "by_purpose", period: "30d")` → sort by `spend_usd`, report top 3

**"What did the last report generation run cost?"**
→ `get_llm_usage(mode: "recent", trace_id: "<id from that run>")` → sum `cost_usd` across the returned rows

**"Show me all AI calls from today"**
→ `get_llm_usage(mode: "recent", from_date: "<today>", to_date: "<today>", limit: 100)`

**"Are we hitting fallbacks a lot for summarization?"**
→ `get_llm_usage(mode: "by_purpose", period: "30d")` → find the `summarization` row → report `primary_model_hit_rate` (as %)
