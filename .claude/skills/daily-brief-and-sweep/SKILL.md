---
name: daily-brief-and-sweep
description: >
  Runs Dawn Garibaldi's daily morning brief and sweep — her own bespoke system
  built around her real Outlook calendar, her real ASG business mailbox
  (d.garibaldi@amplifystrategy.com), and her Granola coaching-session notes,
  NOT a generic HTML-artifact morning-brief skill. Reads today's real calendar
  events (filtering out Dawn's own timeblocks), sweeps her mailbox over local
  IMAP scripts, sweeps today's Granola notes for her own follow-up
  commitments, applies her urgency bar and calibration rules, and writes the
  result to `handoff.md` for her to route herself. Make sure to use this
  skill whenever Dawn says things
  like "run the daily brief and sweep," "run brief and sweep," "brief and
  sweep for today," "run today's brief," or any variant asking for her
  morning brief/sweep — even if she doesn't use these exact words. Do NOT
  substitute a generic morning-brief skill or an HTML dashboard artifact for
  this request; that is a different system and does not have access to Dawn's
  real calendar or mailbox setup.
---

# Daily Brief and Sweep

Dawn's read-and-flag morning system. It never sends, archives, edits, or
deletes anything on its own — the one exception is `handoff.md` itself,
which this skill fully owns (see Step 1). Everything it finds gets written to
`handoff.md` for Dawn to route in her own working session; nothing here acts
on the outside world.

## Before you do anything: how email actually works here

Dawn's ASG mailbox (`d.garibaldi@amplifystrategy.com`) is hosted on
privateemail.com and reached **only** over plain IMAP, via the scripts in
this project's own `execution/` folder. **There is no Gmail-style or
Outlook-style MCP connector for this mailbox, and there never will be one —
do not search for one, suggest connecting one, or treat its absence as a
blocker.** If you find yourself looking for an email MCP tool, stop — you're
about to repeat a mistake that's already been made and fixed once. The
scripts below are the entire email interface:

- `execution/imap_search_recent.py --since-hours N [--folder INBOX]` — messages
  from the last N hours (plus anything unseen/flagged in that window).
- `execution/imap_search_query.py --from-addr X / --to-addr X / --text X [--folder INBOX]` —
  search by sender, recipient, or text, for calibration checks (e.g. "has
  Dawn already replied in this thread?", "check Sent Messages for a reply").
  The sent folder on this mailbox is named **`Sent Messages`**, not `Sent`.
- `execution/imap_fetch_message.py --uid U [--folder INBOX]` — full body of one
  message, needed to actually apply the urgency bar and calibration rules
  below (a snippet alone usually isn't enough to tell a closed loop from an
  open one).

Credentials are read automatically by these scripts from
`C:\Users\dmgar\.secrets\Email_Triage\.env` — you never touch the password.
If a script errors on missing credentials, tell Dawn to check that file;
don't try to work around it.

Calendar events come from the already-connected `mcp__outlook-calendar__list_events`
tool — no script needed there. Granola session notes come from the
already-connected Granola tools (list/get meetings, get transcript) — see
Step 4.

---

## Step 1: Archive yesterday's handoff, start today's fresh

`handoff.md` is always meant to hold only the current, unrouted queue — never
growing forever, never silently overwritten either.

1. Check whether `handoff.md` already exists and has content below its
   header.
2. If it does, read the date out of its own `# Handoff — [date]` line (this
   may not be today — it may be older, if it never got routed) and move the
   file **as-is** to `handoff-archive/[that date].md`. Create the
   `handoff-archive/` folder if it doesn't exist.
3. Start a brand new `handoff.md` from `handoff-template.md`'s structure.
4. If step 2 fired (there was unrouted content), say so plainly in today's
   brief — an accumulating backlog is itself a signal worth Dawn seeing, not
   something to quietly paper over.

## Step 2: Pull today's real calendar

Call `mcp__outlook-calendar__list_events` for today (00:00–24:00, Dawn's
local time zone).

**A calendar entry only counts as a real event if at least one of these is
true:**
- The organizer is someone other than Dawn (not `dm.garibaldi@outlook.com`,
  "Dawn Garibaldi," "Garibaldi, Dawn," or any of her ASG addresses).
- It has a location, or a video link (Zoom/Meet/Teams) or dial-in info in the
  body.
- The attendees list includes someone other than Dawn.

**Otherwise it's a personal placeholder or timeblock** (e.g. "DRIVE,"
"Repatha!!!," or a named hold used to block a slot before a real invite
lands) — exclude it from the brief entirely.

Do **not** trust Outlook's `isMeeting` flag as the test — it's been confirmed
unreliable (a genuine external meeting with a video link and outside
organizer read `isMeeting: false`, indistinguishable from a personal
timeblock on that field alone). Use the three signals above instead.

**When a placeholder and a real event land in the same slot** (the
placeholder having held the slot until the real invite arrived), show only
the real event — the placeholder already did its job.

## Step 3: Sweep the mailbox

Run `execution/imap_search_recent.py --since-hours <hours since the last
run>` (use a sensible default like 18–24 hours if you don't know the last
run time). Also check `Junk` the same way if you want to note anything
Dawn manually blocked since last time — but this skill never moves mail
itself; that's `email-triage`'s job in the sibling project, not this one.

For anything that looks like it might need action, pull the full body with
`imap_fetch_message.py` before deciding — a snippet is rarely enough to
apply the rules below correctly.

Filter through the taxonomy at `../Email_Triage/Email/email-taxonomy.md`
(that's the live taxonomy `email-triage` actually maintains). Category 2
(1099 partner) and category 3 (direct client) senders surface individually
and first. Category 1 (solicitations) stays corralled into the rolled-up
"someone's selling you something" line and is never surfaced individually.

**Multi-address routing:** this mailbox also receives mail forwarded from
Dawn's other business addresses (Talent Growth Partners, Positive
Intelligence, Zenata, others). Classify forwarded mail by the *original
sender* in the `From` header, not by the fact that it arrived via
forwarding.

## Step 4: Sweep today's Granola session notes

Call the Granola tools to list meetings and pull today's notes. Any note
with the **Client Session** template applied (headings like "My
Follow-ups," "Client Action Items," "Possible Testimonials" — see
`granola-templates/client-session.md`) is a real coaching session, whether
or not it showed up on the Outlook calendar in Step 2. When it didn't,
reconcile it into Step 2's real-events list and flag the calendar gap —
that's a signal this brief may be missing sessions booked through a
different channel, worth surfacing every time it happens, not just once.

Pull the **"My Follow-ups"** section into `handoff.md`'s Needs action list
— these are Dawn's own commitments, and a dated one (e.g. "before she
leaves for X") satisfies the urgency bar on its own. Leave **"Client Action
Items"** alone — those belong to the client, not Dawn, and aren't hers to
action.

**Confidentiality:** never copy "Key Quotes," "Possible Testimonials," or
"Personal Notes" into `handoff.md` — those stay in the Granola note itself.
If a testimonial or story-bank-worthy line shows up, mention that it exists
and point back to the note; don't lift the client's words into a file this
skill writes to.

If no session happened today, or nothing was captured with the template,
say so briefly rather than skipping the step silently — an empty sweep is
still a checked box.

## Step 5: The urgency bar

> An item is "needs action" only if a named human is expecting something from
> Dawn, or Dawn made a commitment that carries a date.

A platform's deadline is not urgency. A webinar starting soon, a "last
chance" notice, a renewal reminder — none of those are a person waiting on
Dawn.

**Never urgent, standing rule:**
- Opt-in newsletters, digests, event reminders.
- Cold vendor pitches / acquisition-interest solicitations (route to the
  rolled-up weekly line — never surfaced individually).
- LinkedIn service alerts, as distinct from a message from an actual human.
- Funnel-style podcast invitations.

## Step 6: Calibration — the corrections that keep this accurate

- **A reply is not automatically an action.** Read for an unresolved ask; a
  thank-you or confirmation is a closed loop even sitting at the top of the
  inbox.
- **Check the thread for Dawn's own already-sent reply** before flagging —
  use `imap_search_query.py --to-addr <sender> --folder "Sent Messages"` or
  match on `references`/`in_reply_to` against what you already have.
- **Two exceptions where a reply IS the story:** replies to Dawn's own
  speaking/podcast outreach (a booking to make), and real-person replies to
  her newsletter (a relationship opening).
- **Cross-reference the task list** — something already scheduled for later
  in the week is not an emergency today.
- **No client-facing items surfaced as urgent on weekends** — they wait for
  the next working day. This does **not** extend to business travel or
  extended vacation — Dawn actively uses this brief during those periods, so
  nothing gets suppressed just because she's away.
- **The "urgent" keyword override:** if a message from a known client
  (taxonomy category 2 or 3) has the word "urgent" anywhere in the subject
  line, it surfaces as needs-action immediately — overriding the weekend
  rule and every calibration rule above, including "a reply is not
  automatically an action." **This override never applies to category 1
  (solicitations) or an unfamiliar sender** — cold pitches routinely fake
  urgency in the subject line, and honoring the keyword there would just
  reopen the noise this system exists to filter out.

## Step 7: Draft replies — text only, inside handoff.md

For anything that clearly warrants a reply, draft the reply text and place
it in `handoff.md`'s "Drafted replies" section, per `handoff-template.md`'s
format. **This is plain text for Dawn's review, never a real IMAP draft and
never sent.** Nothing in this skill has send or draft-creation capability by
design — that boundary belongs to `email-triage`, a different project.

## Step 8: Write handoff.md

Follow `handoff-template.md`'s exact section structure and order:
Today's top priority → Hard dates today → Real events today → Needs action
(with drafted replies nested under it) → Notable but not urgent → This
week — someone's selling you something → Flags for Dawn to correct.

Keep every line traceable to something you actually found — a calendar
event, a message, a taxonomy match. Quote a subject/sender rather than
paraphrasing when precision matters.

If nothing actionable came in: say so plainly ("No new actionable emails
since the last run") rather than padding the file with empty sections, and
still surface any hard dates or real events from the calendar.

## Step 9: Report back to Dawn

In the chat, give a short summary: today's top priority, anything in "needs
action," anything archived from a stale `handoff.md`, and a pointer to
`handoff.md` for the full detail. Keep it to a few lines — the file is the
detail, the chat message is the headline.

---

## What this skill does not do (by design)

- Never sends email, creates a real email draft, or takes any mailbox action
  (junking, moving, flagging) — that's `email-triage`'s job, a separate
  project and a separate decision Dawn makes there.
- Never edits the task list, CRM, week card, or completions log directly —
  Dawn's own working session reads `handoff.md` and routes each item herself.
- Never surfaces category 1 (solicitations) individually, regardless of
  urgency-sounding language in the subject.
- Never assumes a Gmail/Outlook MCP mail connector exists. If one shows up in
  the tool list someday, this skill still ignores it — the local IMAP
  scripts are the interface, permanently, not a stand-in until something
  better arrives.

## If something breaks

A script exits with a clear error message (missing credentials, bad UID,
mailbox unreachable) rather than failing silently — read it, fix the
narrow thing it names, and don't retry blindly. If the calendar
classification rules in Step 2 misjudge a real event (this has happened
before with `isMeeting`), flag it in `handoff.md`'s "Flags for Dawn to
correct" section rather than silently guessing — that section is how these
rules actually improve over time.
