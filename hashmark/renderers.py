"""Human-readable deterministic Markdown and offline HTML renderers."""

from __future__ import annotations

import html
from collections import defaultdict
from collections.abc import Iterable, Mapping
from typing import Any


def _failure_first(results: Iterable[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    order = {"FAIL": 0, "SKIPPED": 1, "PASS": 2}
    return sorted(results, key=lambda item: (order[item["status"]], item["algorithm"], item["vector_id"], item["backend"]))


def _digest(value: str | None) -> str:
    return value if value is not None else "not exposed by EVM runner"


def render_markdown(report: Mapping[str, Any]) -> str:
    """Render one deterministic, failure-first Markdown report."""

    summary = report["summary"]
    lines = [
        f"# Hashmark evidence report — {summary['status']}",
        "",
        "> Informal conformance evidence only; not formal certification or a security audit.",
        "",
        "## Summary",
        "",
        "| Total | Passed | Failed | Skipped | Target suites | Differential comparisons |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {summary['total']} | {summary['passed']} | {summary['failed']} | {summary['skipped']} "
            f"| {summary['target_suites']['passed']}/{summary['target_suites']['total']} "
            f"| {summary['differential_comparisons']['passed']}/{summary['differential_comparisons']['total']} |"
        ),
        "",
        "## Target matrix",
        "",
        "| Backend | Status | Test identifiers | Diagnostic |",
        "| --- | --- | --- | --- |",
    ]
    for target in report["target_runs"]:
        identifiers = ", ".join(f"`{item}`" for item in target["test_identifiers"]) or "—"
        diagnostic = target["diagnostic"] or "—"
        lines.append(f"| {target['backend']} | **{target['status']}** | {identifiers} | {diagnostic} |")

    failures = [item for item in report["results"] if item["status"] != "PASS"]
    if failures:
        lines.extend(["", "## Failures and skipped evidence", ""])
        for item in _failure_first(failures):
            lines.extend(
                [
                    f"### {item['status']}: `{item['vector_id']}` on {item['backend']}",
                    "",
                    f"- Expected: `{item['expected_digest']}`",
                    f"- Fe: `{_digest(item['fe_digest'])}`",
                    f"- Oracle: `{item['oracle_digest']}`",
                    f"- Diagnostic: {item['diagnostic'] or 'none'}",
                    "",
                ],
            )

    grouped: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for item in _failure_first(report["results"]):
        grouped[item["algorithm"]].append(item)
    for algorithm in ("sha256", "keccak256"):
        if algorithm not in grouped:
            continue
        title = "SHA-256" if algorithm == "sha256" else "Ethereum Keccak-256"
        lines.extend([f"## {title} results", ""])
        for item in grouped[algorithm]:
            lines.extend(
                [
                    f"### {item['status']}: `{item['vector_id']}` / {item['backend']}",
                    "",
                    f"- Category: `{item['category']}`",
                    f"- Input length: {item['input_length_bytes']} bytes",
                    f"- Input SHA-256: `{item['input_sha256']}`",
                    f"- Expected: `{item['expected_digest']}`",
                    f"- Fe: `{_digest(item['fe_digest'])}`",
                    f"- Oracle: `{item['oracle_digest']}`",
                    f"- Evidence basis: `{item['evidence_basis']}`",
                    f"- Source: [{item['source_name']}]({item['source_url']}) — {item['source_case_id']}",
                    f"- Notes: {item['notes'] or '—'}",
                    "",
                ],
            )

    lines.extend(
        [
            "## Provenance",
            "",
            f"- Source revision: `{report['source_revision']}`",
            f"- Source tree SHA-256: `{report['source_tree_sha256']}`",
            f"- Fixture manifest SHA-256: `{report['fixture_manifest_sha256']}`",
            f"- Fe: `{report['toolchain']['fe']}`",
            f"- Python: `{report['toolchain']['python']}`",
            f"- PyCryptodome: `{report['toolchain']['pycryptodome']}`",
            f"- Report schema: `{report['schema_version']}`",
            "",
            "## Limitations",
            "",
        ],
    )
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(["", "## Reproduce", "", "```console", "python -m hashmark run --all --backend all --format all --output-dir reports/local", "```", ""])
    return "\n".join(lines)


CSS = """
:root{color-scheme:dark;--hm-bg:#101312;--hm-surface:#171d1a;--hm-raised:#202824;--hm-border:#596d60;--hm-border-strong:#6d8275;--hm-text:#edf2ed;--hm-secondary:#bac6bd;--hm-muted:#89988e;--hm-accent:#c7f36b;--hm-pass:#a8e6a1;--hm-fail:#ff8d83;--hm-warn:#f1c879;--hm-info:#9bc8e8;--hm-focus:#d7ff8a;--hm-mono:ui-monospace,SFMono-Regular,Consolas,"Liberation Mono",monospace;--hm-sans:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
*{box-sizing:border-box}html{background:var(--hm-bg);color:var(--hm-text);font-family:var(--hm-sans);font-size:14px;line-height:1.5}body{margin:0}.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}.summary-visible{display:contents}.skip{position:absolute;left:12px;top:-60px;background:var(--hm-accent);color:#17200e;padding:10px 14px;z-index:2}.skip:focus{top:12px}a{color:var(--hm-info);text-underline-offset:3px}a:focus-visible,summary:focus-visible{outline:2px solid var(--hm-focus);outline-offset:3px}.shell{max-width:1200px;margin:0 auto;padding:32px 24px 48px}.shell,main,main>section,.panel,.results,.result{min-width:0}.report-header{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:start;border:1px solid var(--hm-border);border-bottom-color:var(--hm-border-strong);padding:24px;background:var(--hm-surface)}.wordmark{font:700 18px/1 var(--hm-mono);letter-spacing:-.04em}.mark{color:var(--hm-accent);margin-right:8px}.eyebrow{font:500 12px/18px var(--hm-mono);color:var(--hm-muted);text-transform:uppercase;letter-spacing:.08em;margin:0 0 8px}.report-header h1{font-size:28px;line-height:34px;margin:0}.meta{text-align:right;color:var(--hm-secondary);font:12px/18px var(--hm-mono)}.status{display:inline-block;border:1px solid currentColor;border-radius:4px;padding:3px 8px;font:700 12px/18px var(--hm-mono);letter-spacing:.06em}.PASS{color:var(--hm-pass)}.FAIL{color:var(--hm-fail)}.SKIPPED,.UNAVAILABLE,.NOT_RUN{color:var(--hm-warn)}.summary-strip{display:grid;grid-template-columns:repeat(6,1fr);border:1px solid var(--hm-border);border-top:0;background:var(--hm-surface)}.metric{padding:16px;border-right:1px solid var(--hm-border)}.metric:last-child{border-right:0}.metric dt{color:var(--hm-muted);font:500 12px/18px var(--hm-mono)}.metric dd{font:700 20px/26px var(--hm-mono);margin:2px 0 0}main{display:grid;gap:48px;margin-top:48px}.section-head{display:flex;justify-content:space-between;gap:16px;align-items:baseline;margin-bottom:16px}.section-head h2{font-size:18px;line-height:24px;margin:0}.section-head p{color:var(--hm-muted);margin:0}.panel{border:1px solid var(--hm-border);background:var(--hm-surface)}.table-wrap{width:100%;overflow-x:auto}table{width:100%;border-collapse:collapse;min-width:760px}caption{text-align:left;padding:16px;font-weight:650;border-bottom:1px solid var(--hm-border)}th,td{padding:12px 14px;border-bottom:1px solid var(--hm-border);text-align:left;vertical-align:top}th{color:var(--hm-secondary);font-size:12px}tbody tr:last-child td{border-bottom:0}.mono,code{font-family:var(--hm-mono);overflow-wrap:anywhere}.diagnostic{max-width:44ch;color:var(--hm-secondary)}.alert{border:1px solid var(--hm-fail);background:var(--hm-surface);padding:16px}.alert h3{margin:0 0 8px;color:var(--hm-fail)}.alert p{margin:6px 0}.results{display:grid;gap:8px}.result{border:1px solid var(--hm-border);border-radius:4px;background:var(--hm-surface)}.result[open]{border-color:var(--hm-border-strong);background:var(--hm-raised)}summary{cursor:pointer;display:grid;grid-template-columns:90px minmax(170px,1fr) 120px 90px 90px;gap:12px;align-items:center;min-height:48px;padding:10px 14px}summary::marker{color:var(--hm-accent)}.result-body{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;border-top:1px solid var(--hm-border);padding:16px}.evidence{margin:0}.evidence>div{display:grid;grid-template-columns:145px 1fr;gap:12px;padding:7px 0;border-bottom:1px solid var(--hm-border)}.evidence>div:last-child{border:0}.evidence dt{color:var(--hm-muted)}.evidence dd{margin:0}.provenance{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px 24px;margin:0;padding:18px}.provenance div{min-width:0}.provenance dt{color:var(--hm-muted);font-size:12px}.provenance dd{margin:4px 0 0}.limitations{margin:0;padding:18px 18px 18px 36px}.limitations li+li{margin-top:8px}.report-footer{margin-top:48px;padding-top:24px;border-top:1px solid var(--hm-border);color:var(--hm-muted)}
@media(max-width:900px){.summary-strip{grid-template-columns:repeat(3,1fr)}.metric:nth-child(3){border-right:0}.metric:nth-child(-n+3){border-bottom:1px solid var(--hm-border)}summary{grid-template-columns:82px minmax(150px,1fr) 100px 76px}.summary-backend{display:none}}
@media(max-width:640px){.shell{padding:12px}.report-header{grid-template-columns:1fr;padding:18px}.meta{text-align:left}.summary-strip{grid-template-columns:repeat(2,1fr)}.metric:nth-child(2n){border-right:0}.metric:nth-child(-n+4){border-bottom:1px solid var(--hm-border)}main{gap:32px;margin-top:32px}.section-head{display:block}.section-head p{margin-top:4px}summary{grid-template-columns:74px 1fr 70px}.summary-category,.summary-length{display:none}.result-body,.provenance{grid-template-columns:1fr}.evidence>div{grid-template-columns:1fr;gap:2px}.report-header h1{font-size:24px;line-height:30px}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
@media print{html{background:#fff;color:#111}.shell{max-width:none;padding:0}.report-header,.summary-strip,.panel,.result,.result[open],.alert{background:#fff;color:#111;border-color:#777}a{color:#111}.provenance a[href]::after{content:" (" attr(href) ")"}.status{color:#111}.result:not([open]) .result-body{display:grid}details{break-inside:avoid}.table-wrap{overflow:visible}table{min-width:0;font-size:10px}.report-footer{color:#333}}
"""


def _esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def _status(value: str) -> str:
    escaped = _esc(value)
    return f'<span class="status {escaped}">{escaped}</span>'


def _result_detail(item: Mapping[str, Any]) -> str:
    source = f'<a href="{_esc(item["source_url"])}">{_esc(item["source_name"])}</a>'
    fields = [
        ("Input SHA-256", item["input_sha256"], True),
        ("Expected digest", item["expected_digest"], True),
        ("Fe digest", _digest(item["fe_digest"]), True),
        ("Oracle digest", item["oracle_digest"], True),
        ("Evidence basis", item["evidence_basis"], True),
        ("Source", source, False),
        ("Source case", item["source_case_id"], False),
        ("Notes", item["notes"] or "—", False),
        ("Diagnostic", item["diagnostic"] or "—", False),
    ]
    rows = "".join(
        f'<div><dt>{_esc(label)}</dt><dd class="{"mono" if mono else ""}">{value if not mono and label == "Source" else _esc(value)}</dd></div>'
        for label, value, mono in fields
    )
    accessible_name = (
        f'{item["status"]} {item["vector_id"]}; {item["algorithm"]}; {item["category"]}; '
        f'{item["input_length_bytes"]} bytes; {item["backend"]} backend'
    )
    return (
        f'<details class="result" data-status="{_esc(item["status"])}">'
        f'<summary><span class="sr-only">{_esc(accessible_name)}</span><span class="summary-visible" aria-hidden="true">'
        f'{_status(item["status"])}<span class="mono">{_esc(item["vector_id"])}</span>'
        f'<span class="summary-category">{_esc(item["category"])}</span>'
        f'<span class="summary-length">{item["input_length_bytes"]} B</span>'
        f'<span class="summary-backend mono">{_esc(item["backend"])}</span></span></summary>'
        f'<div class="result-body"><dl class="evidence">{rows}</dl></div></details>'
    )


def render_html(report: Mapping[str, Any]) -> str:
    """Render a semantic, responsive, self-contained offline report."""

    summary = report["summary"]
    metrics = [
        ("Executed", summary["total"]), ("Passed", summary["passed"]),
        ("Failed", summary["failed"]), ("Skipped", summary["skipped"]),
        ("Target suites", f"{summary['target_suites']['passed']}/{summary['target_suites']['total']}"),
        ("Differential", f"{summary['differential_comparisons']['passed']}/{summary['differential_comparisons']['total']}"),
    ]
    metric_html = "".join(f'<dl class="metric"><dt>{_esc(label)}</dt><dd>{_esc(value)}</dd></dl>' for label, value in metrics)
    target_rows = "".join(
        f'<tr><td class="mono">{_esc(item["backend"])}</td><td>{_status(item["status"])}</td>'
        f'<td>{_esc(", ".join(item["test_identifiers"]) or "—")}</td>'
        f'<td class="diagnostic">{_esc(item["diagnostic"] or "—")}</td></tr>'
        for item in report["target_runs"]
    )
    failures = [item for item in _failure_first(report["results"]) if item["status"] != "PASS"]
    failure_html = ""
    if failures:
        failure_items = "".join(
            f'<div class="alert"><h3>{_esc(item["status"])} — <span class="mono">{_esc(item["vector_id"])}</span></h3>'
            f'<p>Backend: <span class="mono">{_esc(item["backend"])}</span></p>'
            f'<p class="mono">Expected: {_esc(item["expected_digest"])}</p>'
            f'<p class="mono">Actual: {_esc(_digest(item["fe_digest"]))}</p>'
            '<p>Verify the source vector and independent oracle before changing expected values.</p></div>'
            for item in failures
        )
        failure_html = f'<section aria-labelledby="failures"><div class="section-head"><h2 id="failures">Failures and skipped evidence</h2></div><div class="results">{failure_items}</div></section>'
    algorithm_sections = []
    for algorithm, title in (("sha256", "SHA-256"), ("keccak256", "Ethereum Keccak-256")):
        items = [item for item in _failure_first(report["results"]) if item["algorithm"] == algorithm]
        if not items:
            continue
        algorithm_sections.append(
            f'<section aria-labelledby="{algorithm}"><div class="section-head"><h2 id="{algorithm}">{title}</h2>'
            f'<p>{len(items)} backend/vector records</p></div><div class="results">'
            + "".join(_result_detail(item) for item in items) + "</div></section>"
        )
    provenance = [
        ("Source revision", report["source_revision"]), ("Source tree SHA-256", report["source_tree_sha256"]),
        ("Fixture manifest SHA-256", report["fixture_manifest_sha256"]), ("Fe", report["toolchain"]["fe"]),
        ("Python", report["toolchain"]["python"]), ("PyCryptodome", report["toolchain"]["pycryptodome"]),
        ("Report schema", report["schema_version"]),
    ]
    provenance_html = "".join(f'<div><dt>{_esc(label)}</dt><dd class="mono">{_esc(value)}</dd></div>' for label, value in provenance)
    limitations = "".join(f"<li>{_esc(item)}</li>" for item in report["limitations"])
    return f'''<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='4' fill='%23171d1a'/%3E%3Cpath d='M10 6 8 26M21 6l-2 20M5 12h22M4 20h18l5-5' fill='none' stroke='%23c7f36b' stroke-width='3' stroke-linecap='square'/%3E%3C/svg%3E">
<meta name="color-scheme" content="dark"><title>Hashmark evidence report — {_esc(summary['status'])}</title><style>{CSS}</style></head>
<body><a class="skip" href="#report-main">Skip to evidence</a><div class="shell">
<header class="report-header"><div><p class="eyebrow"><span class="mark">##✓</span>hashmark / evidence report</p><h1>Cryptographic conformance evidence</h1></div>
<div class="meta">{_status(summary['status'])}<br>project {_esc(report['project']['version'])}<br>schema {_esc(report['schema_version'])}</div></header>
<section class="summary-strip" aria-labelledby="summary-heading"><h2 class="sr-only" id="summary-heading">Report summary</h2>{metric_html}</section><main id="report-main">
<section aria-labelledby="targets"><div class="section-head"><h2 id="targets">Target matrix</h2><p>Skipped is never passing.</p></div>
<div class="panel table-wrap"><table><caption>Fe target execution</caption><thead><tr><th scope="col">Backend</th><th scope="col">Status</th><th scope="col">Test identifiers</th><th scope="col">Diagnostic</th></tr></thead><tbody>{target_rows}</tbody></table></div></section>
{failure_html}{''.join(algorithm_sections)}
<section aria-labelledby="provenance"><div class="section-head"><h2 id="provenance">Provenance and toolchain</h2></div><dl class="panel provenance">{provenance_html}</dl></section>
<section aria-labelledby="limitations"><div class="section-head"><h2 id="limitations">Limitations</h2></div><div class="panel"><ul class="limitations">{limitations}</ul></div></section>
</main><footer class="report-footer"><p>All executed checks passed only when every requested target and vector completed. This report is self-contained and makes no network requests.</p>
<p class="mono">Reproduce: python -m hashmark run --all --backend all --format all --output-dir reports/local</p></footer></div></body></html>'''
