# Corrections log — Professor Davis Coakley Award 2026

This log records every change made to artists' source text while extracting
`source/entries.docx` into `content/pieces.yaml`. Nothing beyond what is
listed here was altered — wording, tone and each artist's own capitalisation
of their title are preserved exactly as submitted.

## Corrections applied (as instructed)

| Piece | Before | After | Reason |
|---|---|---|---|
| 01 — Artificial Creativity | "artificial creativity.One in English" (split across a stray paragraph break) | "artificial creativity. One in English" | Listed correction; the paragraph break between "creativity." and "One" was a copy‑paste artifact, so the three fragments (P6–P8 of the source) were rejoined into one continuous description paragraph. |
| 01 — Artificial Creativity | "Persian poet Saadi Shiazi's epic" | "Persian poet Saadi Shirazi's epic" | Listed correction (misspelled name). |
| 01 — Artificial Creativity | "even of AI may treat us as Körper" | "even if AI may treat us as Körper" | Listed correction (typo: of → if). |
| 01 — Artificial Creativity | "100000rial note" | "100,000-rial note" | Listed correction (formatting). |
| 11 — The Voice Within | "Speech &amp; Language Therapist" | "Speech & Language Therapist" | Listed correction (unescaped HTML entity left in source). |

## Requires approval

| Piece | Before | After | Reason |
|---|---|---|---|
| 11 — The Voice Within | "...The collection was co‑curated by Marina Cassidy (Music Therapist) and Deirdre Leavy (Speech & Language Therapist). Marina Cassidy, Music Therapist, SJH." | "...The collection was co‑curated by Marina Cassidy (Music Therapist) and Deirdre Leavy (Speech & Language Therapist)." | Marina Cassidy is already credited by name and role in the immediately preceding sentence; the trailing "Marina Cassidy, Music Therapist, SJH." repeats it. **This removal has been applied in `pieces.yaml` pending your explicit sign‑off** — say the word and I'll restore it if you'd rather keep the repeated credit line. |

## Typography normalisation (mechanical, not wording changes)

Applied uniformly and not itemised further: non‑breaking spaces (`\xa0`)
converted to ordinary spaces; runs of multiple spaces collapsed to one;
leading/trailing whitespace stripped from every paragraph; straight quote
marks converted to typographic marks (`'`→`’`, `"…"`→`“…”`). This affected:
"Siobhán O'Reilly" → "Siobhán O'Reilly", "Éilis O'Neill" → "Éilis O'Neill",
"sheep's wool" → "sheep's wool", "women's experiences"/"women's voices" →
"women's experiences"/"women's voices", and the three quoted "body" phrases
in piece 01's Leib/Körper paragraph.

Per the brief, *Leib* and *Körper* were italicised (markdown `*asterisks*`)
everywhere they appear in piece 01.

## Fields inferred, not present verbatim in source

The brief's schema requires a short `form` label for the card even where
the source document didn't give one as a discrete field. These two are
inferred from the medium/description rather than quoted from the artist —
flagging for your review:

- **04 — Da**: source gives only "Medium: Oil on canvas with encaustic
  medium", no separate form line. Set `form: "Painting"`.
- **08 — The Breast Series**: source gives "Original artwork: ink on paper.
  Exhibited work: ink drawing, digitally reproduced as an archival canvas
  print", no separate form line. Set `form: "Ink drawing"`.

## Flagged, not changed

- **01 — Artificial Creativity, both table cells**: the two poem
  descriptions begin "1. The first, ..." and "2. This second in the
  diptych is ...". This manual numbering is redundant with the section
  headings ("Fear Lasta lampAI" / "AI I AM: Bani Adam for the New Age")
  once rendered on the piece page, but it's the artist's own text
  structure, not a typo — left verbatim.
- **06 — Approaches**: medium reads "Hands-Plaster" with no space
  (source runs: "...Hands-" + "Plaster "). Could be a missing space/colon
  ("Hands: Plaster" or "Hands – Plaster") lost in a bold/italic run break,
  similar to the "Dr.** Ciarán **Trolan" artifact elsewhere in the doc —
  but since it's ambiguous which the artist intended, it was left exactly
  as extracted rather than guessed at. Please confirm the intended text.
- **13 — Growing into Ourselves: The Human Journey Across Generations**
  (Liz Nolan): role, form, medium and description are all absent from the
  source document — this is the one entry that needs new material from
  the artist before it can go to print, not just a text fix.

## Fields verified empty (not omissions)

- **02 — You Are Heard** (Lanyi Yan), **04 — Da** (Aran Young),
  **12 — Balancing space between still time** (Dr Karie Dennehy): no
  description text anywhere in the source document. `status:
  missing_description`; their piece pages will show only the header and
  metadata until a description is added.
- **07 — Lipstick** and **02 — You Are Heard**: source has no video or
  audio link for either piece; `video_url` / `audio_url` left empty.
