"""
Prometheus metrics for kiro-gateway (midcityit fork, MCIT-371).

HTTP-level metrics (request count, latency histogram, in-flight) are provided
by prometheus-fastapi-instrumentator in main.py. This module adds the
gateway-specific, MODEL-labelled metrics that the generic instrumentator
cannot derive on its own (it only sees route/method/status, not the Kiro
model selected in the request body).

Exposed on the same app at GET /metrics. No secrets are emitted; labels are
model id, route and outcome only.
"""
from __future__ import annotations

from prometheus_client import Counter, Histogram

# Requests by resolved Kiro model + route + outcome (success|error).
MODEL_REQUESTS = Counter(
    "kiro_gateway_model_requests_total",
    "Chat/messages requests handled, labelled by requested model, route and outcome.",
    ["model", "route", "outcome"],
)

# Upstream (Kiro API) errors by model + status class (4xx/5xx/other).
UPSTREAM_ERRORS = Counter(
    "kiro_gateway_upstream_errors_total",
    "Errors returned from the upstream Kiro API, labelled by model and status class.",
    ["model", "status_class"],
)

# Token counts (prompt/completion) by model, when derivable from the request.
TOKENS = Counter(
    "kiro_gateway_tokens_total",
    "Approximate token counts attributed to the gateway, by model and kind (prompt|completion).",
    ["model", "kind"],
)

# End-to-end handler latency by model + route (seconds). Separate from the
# instrumentator's per-route histogram so it carries the model label.
MODEL_LATENCY = Histogram(
    "kiro_gateway_model_request_duration_seconds",
    "End-to-end request duration by model and route.",
    ["model", "route"],
    buckets=(0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30, 60, 120),
)


def status_class(code: int) -> str:
    try:
        return f"{int(code) // 100}xx"
    except (TypeError, ValueError):
        return "other"
