# Corrections log — Professor Davis Coakley Award 2026

This log records every change made to artists' source text while extracting
`source/entries.docx` into `content/pieces.yaml`. Nothing beyond what is
listed here was altered — wording, tone and each artist's own capitalisation
of their title are preserved exactly as submitted.

## Update — `source/entries_v2.docx` (2026-09-29)

A revised source document was supplied. It filled in the two previously
missing descriptions (pieces 02 and 13) but did **not** address any of the
wording queries raised above (Voice Within duplicate credit, Approaches
"Hands-Plaster") — those are all still open, unchanged, in the new file too.

**Two pieces were missing from this revised document — confirmed as an
intentional withdrawal, not accidental loss:** No. 04 "Da" (Aran Young) and
No. 08 "The Breast Series" (Fiona Connaughtan). Per instruction, both were
removed entirely from `pieces.yaml`, and the remaining 11 pieces were
**renumbered 01-11** (in their original relative order) so the gap doesn't
show. This deliberately overrides the brief's own "never renumber, ids are
permanent" rule — a one-time exception, done before anything went to an
actual printer. Old → new id mapping, for anyone cross-referencing the
original entry numbers or an earlier draft of the cards/site:

| Old id | New id | Title |
|---|---|---|
| 01 | 01 | Artificial Creativity: Standing On The Shoulders Of Algorithms |
| 02 | 02 | You Are Heard |
| 03 | 03 | Bealtaine |
| 04 | — | **Da — withdrawn** |
| 05 | 04 | The Craft of Care |
| 06 | 05 | Approaches |
| 07 | 06 | Lipstick |
| 08 | — | **The Breast Series — withdrawn** |
| 09 | 07 | Step by Step |
| 10 | 08 | The Hands That Carry Tomorrow |
| 11 | 09 | The Voice Within |
| 12 | 10 | Balancing space between still time |
| 13 | 11 | Growing into Ourselves: The Human Journey Across Generations |

Every URL, QR code and printed card for ids 04-11 changed as a result (only
01-03 kept their original number). Any previously-sent card PDF or shared
link for pieces 05 and up from before 2026-09-29 is now out of date.

### 02 — You Are Heard: now complete, but the credit line is ambiguous

Source text (verbatim): "Lanyi Yan, Lanyi Yan (composer and singer), Grace
Park (pianist, St James's Hospital" — the name "Lanyi Yan" appears twice in
a row, and the parenthesis after "pianist" is never closed. Reconstructed
as:
- `artist`: "Lanyi Yan"
- `role`: "Composer and singer"
- `affiliation`: "with Grace Park, pianist, St James's Hospital"

**This is a reconstruction, not a transcription — please confirm it's
correct**, particularly whether "St James's Hospital" belongs to Grace
Park's credit or is a separate affiliation line for the whole piece.

Description added verbatim (typographic quotes/apostrophes normalised,
non-breaking spaces converted to regular spaces, per the standing policy
below). Missing a final full stop in the source — left as is; see "Flagged,
not changed."

### 13 — Growing into Ourselves: credited artist changed entirely

The source now credits five people, not "Liz Nolan" as before: Keyleigh
Murphy (Transition Year Art student), Claire Doyle (Art teacher) of
Presentation Secondary School Kilkenny, and Kathleen Kenny, Margaret
Farrell, Teresa Nolan of Carlow Kilkenny ICPOP. Liz Nolan is now named
*inside* the description as the project's facilitator, not as the artist.
This reads as a genuine correction (the original document apparently had a
placeholder or wrong name), not an error introduced this round — but
flagging clearly since it changes who's credited.

Source text (verbatim) for the credit line: "Keyleigh Murphy, (Transition
Year Art student, Claire Doyle Art teacher, Presentation Secondary School
Kilkenny); Kathleen Kenny, Margaret Farrell, Teresa Nolan (Carlow Kilkenny
ICPOP – Integrated Care Programme for Older Persons)." Reconstructed into
`role` (see `pieces.yaml`) by moving a stray comma and adding one missing
comma ("Claire Doyle Art teacher" → "Claire Doyle (Art teacher)") so it
reads as intended — **please confirm this reconstruction**. `artist` is
left blank and the full credit put in `role`, matching how piece 11 (The
Voice Within) handles a group/multi-person credit.

`form: "Painting"` is inferred from the description ("inspired the
painting", "an original artwork") — the source still has no discrete form
field, same situation as pieces 04 and 08 below.

On the printed card, this credit line is long enough to wrap to five lines
under the QR code — it still fits inside the card without overflowing, but
it's visibly denser than every other card. Flagging as a design judgment
call: keep the full credit as-is, or would you prefer something shorter
(e.g. "Keyleigh Murphy, Claire Doyle & the Carlow Kilkenny ICPOP team") on
the card specifically, with the full list staying on the web page?

## Corrections applied (as instructed)

| Piece | Before | After | Reason |
|---|---|---|---|
| 01 — Artificial Creativity | "artificial creativity.One in English" (split across a stray paragraph break) | "artificial creativity. One in English" | Listed correction; the paragraph break between "creativity." and "One" was a copy‑paste artifact, so the three fragments (P6–P8 of the source) were rejoined into one continuous description paragraph. |
| 01 — Artificial Creativity | "Persian poet Saadi Shiazi's epic" | "Persian poet Saadi Shirazi's epic" | Listed correction (misspelled name). |
| 01 — Artificial Creativity | "even of AI may treat us as Körper" | "even if AI may treat us as Körper" | Listed correction (typo: of → if). |
| 01 — Artificial Creativity | "100000rial note" | "100,000-rial note" | Listed correction (formatting). |
| 11 — The Voice Within | "Speech &amp; Language Therapist" | "Speech & Language Therapist" | Listed correction (unescaped HTML entity left in source). |

## Suggested changes — NOT applied (not mine to make)

These are not corrections to the source document; the source document is
not mine to edit. `pieces.yaml` currently carries the text exactly as
submitted for both. Logged here so the suggestion isn't lost — whoever
owns the source material can decide whether to action them.

| Piece | Current text | Suggested change | Reason |
|---|---|---|---|
| 11 — The Voice Within | "...The collection was co‑curated by Marina Cassidy (Music Therapist) and Deirdre Leavy (Speech & Language Therapist). Marina Cassidy, Music Therapist, SJH." | Drop the trailing "Marina Cassidy, Music Therapist, SJH." | Marina Cassidy is already credited by name and role in the immediately preceding sentence; the trailing clause repeats it. |
| 06 — Approaches | "Base: Wooden board, prescription medication leaflets. Hands-Plaster" | Something like "Hands: Plaster" or "Hands – Plaster" | Source runs concatenate to "Hands-Plaster" with no space — likely a missing space or colon lost in a bold/italic run break (same artifact class as "Dr.** Ciarán **Trolan" elsewhere in the doc), but ambiguous which the artist intended, so left verbatim rather than guessed at. |

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
- **11 — The Voice Within** (`pieces.yaml`, `artist` field): left blank.
  The source names a group, not an individual; per instruction, the group
  name went into `role` ("Members of Laryngectomy Outpatients Music
  Therapy Voice Group, St. James's Hospital, Dublin") and the explicit
  "Affiliated Institution:" text went into `affiliation`. That leaves
  `artist` empty, which may render oddly on the card/page (a byline with
  nothing after "by"). **Unresolved — flagging so it isn't forgotten**,
  not deciding it here. Template will need to handle the empty-artist
  case gracefully either way.
- **13 — Growing into Ourselves**: "A series of conversations, workshop
  and quotes from ICPOP referrals inspired the painting" — "workshop"
  reads like it should be plural ("workshops") to agree with
  "conversations... and quotes," but this is a plausible artist typo, not
  a listed correction — left verbatim.
- **02 — You Are Heard** and **13 — Growing into Ourselves**: both new
  descriptions end without a final full stop in the source (e.g.
  "...RDS, Dublin" and "...support positive ageing" both just stop).
  Left as submitted rather than silently adding punctuation.

## Fields verified empty (not omissions)

- **04 — Da** (Aran Young), **12 — Balancing space between still time**
  (Dr Karie Dennehy): no description text anywhere in the source document.
  `status: missing_description`; their piece pages will show only the
  header and metadata until a description is added. (02 and 13 were in
  this category too as of the first pass — both now have descriptions,
  see the v2 update above.)
- **07 — Lipstick** and **02 — You Are Heard**: source has no video or
  audio link for either piece; `video_url` / `audio_url` left empty.
