---
status: draft — week 1
started: 2026-09-07
source: adapted from Dana Zellers' "The Brief and the Sweep" (Sept 2026)
---

# Daily Brief and Sweep — Dawn's build

Two systems, adapted from a colleague's notes but built around Dawn's own inbox
taxonomy, business mix, and boundaries — not copied wholesale.

## System 1 — Morning Brief

**Autonomy level (Dawn's explicit call, not Dana's default):**
Read and flag only. May **draft** email replies as text for Dawn's review inside
the handoff file. Never sends, archives, edits, or deletes anything without an
explicit discussion with Dawn first.

**Runs in its own conversation, read-only against everything except:**
- `handoff.md` in this folder — action items and drafted replies get appended here
- `../../03 OUTPUT/Story Bank/story-bank.md` — content-worthy material gets
  appended here. Lives in 03 OUTPUT, not this system folder, because it's a
  golden-nugget file meant to feed wiki updates, not operational routing
  state like `handoff.md` (which gets cleared once Dawn routes it)

It never touches a week card, task list, CRM, or completions log directly. Dawn's
own working session reads `handoff.md`, routes each item to its real home, and
clears it.

**Archive-and-reset (Dawn's call, 2026-09-08 — revisit if it stops fitting):**
`handoff.md` is always meant to reflect only the current, unrouted queue — not
grow forever, and not silently overwrite unrouted work either. So at the start
of every brief run:
1. If `handoff.md` already exists and has content in it, move that content
   as-is to `handoff-archive/[date from its own header].md` (the date already
   in the file's `# Handoff — [date]` line, not necessarily today — it may be
   a day or more old if it never got routed).
2. Create a fresh `handoff.md` for today, per `handoff-template.md`.

This means nothing routed late is ever silently lost — it's archived, not
deleted — but the working file itself always starts each day clean. If a
prior day's content shows up in the archive, that's itself worth mentioning
in the new brief (e.g. "yesterday's handoff never got routed — archived,
here's what was in it") since an accumulating backlog is a signal something's
not being kept up with.

**Sources:**
- Outlook calendar (real events only — never Dawn's own timeblocks). Found by
  testing, not by trusting Outlook's `isMeeting` flag (confirmed unreliable —
  a genuine external meeting with a video link and outside organizer read
  `isMeeting: false`, identical to a personal timeblock). **A calendar entry
  counts as a real event if any of the following are true:**
  - The organizer is someone other than Dawn (not `dm.garibaldi@outlook.com`,
    "Dawn Garibaldi," "Garibaldi, Dawn," or her ASG addresses)
  - It has a location, or a video link (Zoom/Meet/Teams) or dial-in info in
    the body
  - The attendees list includes someone other than Dawn

  **Otherwise it's a personal placeholder/timeblock** — organized by Dawn,
  no location or link, no other attendees (e.g. "DRIVE," "Repatha!!!," or a
  named hold like "Bryan Fillmore from IBC??" used to block a Calendly slot
  before the real invite lands) — and gets excluded from the brief.

  **When a placeholder and a real event land in the same time slot** (the
  placeholder having done its job of holding the slot until the real invite
  arrived), show only the real event — the placeholder doesn't need separate
  mention once it's served its purpose.
- Email, filtered through the existing taxonomy at
  `../../Multiple Email Accounts/Email/email-taxonomy.md` (this is the older,
  scaffolded taxonomy doc — the live one `email-triage` actually reads is
  `../Email_Triage/Email/email-taxonomy.md`, see below) — categories 2
  (1099 partner) and 3 (direct client) surface individually and first;
  category 1 (solicitations) stays corralled per that taxonomy's existing rule
  and is never individually surfaced

**Multi-address routing — already built, not re-invented here.** Dawn's
mailbox (d.garibaldi@amplifystrategy.com) runs on privateemail.com over plain
IMAP/SMTP, accessed through the existing `email-triage` skill at
`../Email_Triage/` (a sibling project folder). That skill already receives forwarded
mail from Dawn's other business addresses (Talent Growth Partners, Positive
Intelligence, Zenata, others) and, as of this build, determines the original
recipient address per message (from the `To:` header, falling back to
`Delivered-To`/`X-Original-To`) and tags any drafted reply with
`[SEND FROM <original address>]` plus an in-body reminder — see
"Determining the Original Recipient Address" in that skill's `SKILL.md`.

The brief should call `email-triage`'s scripts directly (or run the skill
itself) rather than re-implement email access — this is the "check for
existing skills first" principle. The brief's own job on top of that is
narrower: apply Dana's urgency bar and calibration rules to decide what
surfaces in `handoff.md`, using `email-triage`'s classification and drafts as
input rather than re-classifying from scratch.

Needs verification: confirm on one real message from each forwarded address
(TGP, PI, Zenata) that the original recipient actually survives forwarding
intact — some forwarding setups rewrite `To:` and don't set the fallback
headers either, in which case that message just won't get a
`[SEND FROM ...]` tag and should be treated as ASG-native by default rather
than guessed at.

**The urgency bar (starting draft, per Dana, to be corrected against two real
weeks before it's trusted):**

> An item is "needs action" only if a named human is expecting something from
> Dawn, or Dawn made a commitment that carries a date.

Corollary: a platform's deadline is not urgency. A webinar starting soon, a
"last chance" notice, a renewal reminder — none of those are a person waiting
on Dawn.

**Never urgent, standing rule (borrowed from Dana as a starting point — confirm
or correct after two weeks of real flags):**
- Opt-in newsletters, digests, event reminders
- Cold vendor pitches / acquisition-interest solicitations (already routed to
  the taxonomy's holding area — should not reach the brief at all)
- LinkedIn service alerts, as distinct from a message from an actual human
- Funnel-style podcast invitations

**Calibration rules to apply from day one (Dana's hard-won corrections):**
- A reply is not automatically an action — read for an unresolved ask; a
  thank-you or confirmation is a closed loop even sitting at the top of the inbox
- Check the thread for Dawn's own already-sent reply before flagging
- Two exceptions where a reply IS the story: replies to Dawn's own speaking/
  podcast outreach (a booking to make), and real-person replies to her
  newsletter (a relationship opening)
- Cross-reference the task list before bucketing — something already scheduled
  for later in the week is not an emergency today
- No client-facing items surfaced as urgent on weekends — they wait for the
  next working day. **This does NOT extend to business travel or extended
  vacation** — Dawn intends to actively use the brief during those periods,
  so nothing gets suppressed just because she's away.
- **The "urgent" keyword override:** Dawn has told her clients that if a
  request is genuinely time-sensitive during one of her periods of extended
  absence (starting with Sept/Oct 2026 travel), they should put the word
  "urgent" anywhere in the subject line. If a message from a known client
  (taxonomy category 2 or 3 — 1099 partner or direct client) has "urgent" in
  the subject, it surfaces as needs action immediately, overriding the
  weekend rule and every other calibration rule above (including "a reply is
  not automatically an action" — an urgent-tagged reply still surfaces).
  **Guardrail: this override does NOT apply to category 1 (solicitations) or
  any unfamiliar sender** — cold pitches routinely fake urgency in the
  subject line ("URGENT: respond today"), and honoring the keyword there
  would just reopen the exact noise this system exists to filter out.

**Not included in week 1, by Dawn's decision:**
- No habits line — keep the brief work-only

**What the brief writes, format:**
See `handoff-template.md` for the exact section layout of `handoff.md`.

## System 2 — Granola templates + daily sweep

Starting with two templates, not Dana's nine, per her own advice to start small:

1. **Client Session** — coaching sessions (see `granola-templates/client-session.md`)
2. **Discovery Sales** — discovery/sales calls (see `granola-templates/discovery-sales.md`)

Both use `###` markdown headings (not bold — tested by Dana as the biggest
readability fix), split action items into two sections (Dawn's follow-ups /
their follow-ups, never merged), and explicitly permit empty sections
("if nothing shifted, say so") rather than inventing content.

**Granola folders, at this starting stage (2026-09-08 — revisit once volume
makes a flat folder hard to scan):** one flat folder for each of the two
template types — e.g. "Client Sessions" and "Discovery & Sales" — not a
folder per individual client or prospect. Dana's own system used per-client
folders, but that's a second new habit stacked on top of learning the
templates and the sweep itself; each note's title already includes the
client/prospect name, so a flat folder plus title/search covers retrieval
for now. Move to per-client folders later if a flat folder actually becomes
hard to navigate — not before.

**Confidentiality provenance rule (applies to the story bank):** anything
captured toward `story-bank.md` stays theme-level and anonymized by default —
client identity stripped unless Dawn explicitly clears using it, and Dawn's
own material is the only material free of that restriction.

**Testimonials are routed separately, not anonymized.** Both templates'
"Possible Testimonials" section captures a client's exact words about Dawn's
work. Unlike the story bank, this content is *meant* to stay attributed to a
real client — that's the whole point of a testimonial — so it goes to its own
file, `../../03 OUTPUT/Testimonials/testimonials.md`, with permission tracked
per entry rather than identity stripped. Nothing from here gets used publicly
until that permission box is checked.

**Where the live files actually are vs. the templates:**
- `story-bank-template.md` and `testimonials-template.md` in *this* project
  folder are the spec/reference — what shape a new entry takes. They stay
  here as documentation of the system.
- `story-bank.md` and `testimonials.md` themselves — the live, continuously
  appended files — live at `../../03 OUTPUT/Story Bank/story-bank.md` and
  `../../03 OUTPUT/Testimonials/testimonials.md`, so they sit alongside
  Dawn's other finished/golden-nugget deliverables and get picked up by
  vault-wiki-updater runs. `handoff.md` stays in this project folder — it's
  operational routing state, not a golden nugget, and gets cleared once
  routed.

**The sweep is manual, by design, for now:** these are Granola-side templates —
Dawn applies the right one from Granola's enhance menu and files the note into
its folder at the end of each day. No automation exists yet for that step
(Granola's connected tools here are read-only query tools; template creation
and filing happen in the Granola app itself).

## Open items before this goes live

- [ ] Dawn reviews `handoff-template.md`, `testimonials-template.md`,
      `granola-templates/client-session.md`, and
      `granola-templates/discovery-sales.md`
- [ ] Dawn pastes the two templates into Granola's template builder (enhance
      menu → new template) and confirms the section instructions read right
- [ ] Run the brief manually (on request) for a few days before scheduling the
      recurring 8am weekday task — nothing gets scheduled until Dawn says so
- [ ] After ~2 weeks of real flags, revisit the urgency bar and never-urgent
      list above and correct them against what actually got flagged wrong
