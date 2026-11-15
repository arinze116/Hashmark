# Hashmark design system

## Product and rationale

Hashmark is a local Fe cryptographic conformance tool. Its single visual surface is an offline evidence report consumed by developers, reviewers, maintainers, and hackathon judges. The interface must feel precise, inspectable, restrained, and honest about limitations.

The direction is **cryptographic lab notebook**: editorial section rhythm from [Sift](https://sift-ds.framer.ai/), bounded layout discipline from [Saasbright](https://forgiving-needs-325167.framer.app/), and measured grid semantics from [Cursor](https://cursorswarm.framer.website/). Detailed research lives in `docs/design-references/reference-notes.md`.

## Principles

1. Evidence before decoration: exact values, provenance, and failure recovery are the visual priority.
2. Status is explicit: PASS, FAIL, NOT RUN, UNAVAILABLE, and SKIPPED always appear as text.
3. Density is controlled: compact tables, roomy section boundaries, and no dashboard-card repetition.
4. Limitations stay visible: informal verification and compiler-maturity caveats are never buried.
5. Offline means complete: no scripts, remote fonts, images, stylesheets, or network requests.

## Tokens

```css
:root {
  color-scheme: dark;
  --hm-bg: #101312;
  --hm-surface: #171d1a;
  --hm-surface-raised: #202824;
  --hm-border: #596d60;
  --hm-border-strong: #6d8275;
  --hm-text: #edf2ed;
  --hm-text-secondary: #bac6bd;
  --hm-text-muted: #89988e;
  --hm-accent: #c7f36b;
  --hm-accent-foreground: #17200e;
  --hm-pass: #a8e6a1;
  --hm-fail: #ff8d83;
  --hm-warn: #f1c879;
  --hm-info: #9bc8e8;
  --hm-focus: #d7ff8a;
  --hm-radius-sm: 4px;
  --hm-radius-md: 8px;
  --hm-radius-lg: 12px;
  --hm-space-1: 4px;
  --hm-space-2: 8px;
  --hm-space-3: 12px;
  --hm-space-4: 16px;
  --hm-space-6: 24px;
  --hm-space-8: 32px;
  --hm-space-12: 48px;
  --hm-mono: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace;
  --hm-sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
```

Use only the named palette. Raised surfaces use colour plus a 1 px border, never a large shadow. Borders communicate structure; radius softens edges without producing floating pills.

## Typography

- Report title: 28/34, 700, sans.
- Section title: 18/24, 650, sans.
- Body: 14/21, 400, sans; maximum prose measure 72 characters.
- Metadata: 12/18, 500, sans.
- Digests, IDs, versions, paths, and counts: 12/18, 400, monospace.
- Terminal captures: 13/20 monospace.
- Headings use sentence case. Labels use concise uppercase only where it improves scanning.

## Layout and breakpoints

- Maximum report width: 1200 px.
- Desktop: 12-column grid, 24 px gutters, 32 px page inset.
- Tablet: 8-column grid, 20 px gutters, 24 px inset.
- Mobile: one flow column, 12–16 px inset.
- Breakpoints: 640, 768, 1024, and 1280 px.
- Main section spacing: 48 px desktop, 32 px mobile.
- Wide evidence tables live in labelled overflow containers. The page itself must not scroll horizontally.

At desktop, metadata may use side-by-side definition lists. Below 768 px, summary groups wrap and metadata stacks. Below 480 px, result details use definition lists rather than squeezed multi-column rows.

## Information hierarchy

1. Skip link.
2. Header: wordmark, schema/project versions, overall status.
3. Summary strip: executed, passed, failed, skipped, algorithm coverage.
4. Target matrix: native and EVM with explicit status and diagnostic.
5. Failure section, when present.
6. Algorithm result sections.
7. Provenance and toolchain metadata.
8. Limitations and reproduction commands.

Failures always precede passes. An empty result set is an error state and must never resemble PASS.

## Components and states

### Wordmark

Lowercase monospace `hashmark` plus a two-line hash/check motif. It must read as developer tooling, not a token or chain logo.

### Status label

Text-first component with a bordered rectangular shape. Variants: PASS, FAIL, SKIPPED, NOT RUN, UNAVAILABLE. Colour reinforces the word but never replaces it. Avoid rounded pills.

### Summary strip

A single bordered region divided by rules. It wraps into two columns and then one column rather than becoming repeated cards.

### Target matrix

Semantic table with a caption and scope-aware column headers. Diagnostics wrap under the relevant target. UNAVAILABLE explains the platform limitation.

### Result table

Default columns: status, vector, category, length, expected, Fe, oracle, source. Digest values use monospace and `overflow-wrap: anywhere`. On small screens, place each record in semantic `details` with a definition list if the table becomes unreadable.

### Evidence detail

Use native `details`/`summary`, visible focus styles, and no script. The summary names the vector, algorithm, length, backend, and status. Expanded content exposes input fingerprint, all digest values, source case, notes, and recovery guidance.

### Failure callout

Border-left or top rule in `--hm-fail`, explicit `Conformance failure detected`, expected/actual values, and the instruction to verify source and oracle before changing fixtures.

### Empty, partial, and error states

- Empty: `No results were produced. Check the command, fixture selection and runner output.`
- Partial: `Some targets were not executed. A skipped target is not a passing target.`
- Invalid fixture and missing toolchain are CLI states; a generated report must not claim success.
- Report write failure is terminal-only because no trusted report exists.

## Interaction and motion

- No JavaScript.
- Native `details` interactions only.
- Optional 120 ms opacity/height transitions are allowed only if implementable without script; omit them if they add complexity.
- `prefers-reduced-motion: reduce` disables all transitions and smooth scrolling.
- Hover never reveals unique information.
- Focus ring: 2 px `--hm-focus` with at least 2 px offset; never clipped.

## Accessibility

- WCAG 2.2 AA target; minimum 4.5:1 body contrast and 3:1 large text/boundaries.
- `lang="en"`, one `h1`, ordered headings, `header`, `main`, `section`, and `footer` landmarks.
- Include a skip link and semantic table captions/headers.
- Links are underlined or otherwise identifiable without colour.
- Digest text is selectable and wraps or scrolls without clipping.
- Touch targets are at least 44 px where an interactive control exists.
- The report remains usable at 200% zoom and 320 px viewport width.
- Print styles use white background, dark text, visible URLs, and no clipped tables.

## Data and imagery

There are no charts, decorative illustrations, remote images, or live metrics. Counts are factual labels. Real terminal/report screenshots belong in README documentation, not inside generated evidence reports.

## Performance and safety

- One self-contained HTML file with inline CSS and no executable script.
- Escape every fixture-derived string and permit clickable source links only for validated HTTPS URLs.
- Target under 250 KiB plus evidence text for the standard corpus.
- Render 1,000 rows without layout thrashing; prefer static HTML and CSS.

## Anti-patterns

- Crypto coins, chains, circuit motifs, world maps, radial risk scores, and certification seals.
- Purple/blue glow, gradients, glassmorphism, particle fields, or animated hashes.
- Generic sidebar dashboard shells and repeated metric cards.
- Giant marketing headlines, fake telemetry, benchmark theatre, or implied security certification.
- Colour-only state, hidden provenance, truncated digests, or success treatment for skipped/empty runs.
