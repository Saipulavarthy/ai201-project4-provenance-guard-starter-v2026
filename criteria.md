# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1.

<!-- Your criterion. It must name a number. -->

Of 10 pieces I wrote myself (a mix of casual, plain and formal), at most 1 is labeled high-confidence AI, on each of three trials.

**Why this target:**
A wrong accusation costs a writer more than a missed detection costs the site, and 1 in 10 is the smallest rate I can measure with 10 pieces. I am not asking for zero because signal one scores plain writing as machine-like, but more than 1 would mean the AI label is being handed out too easily.

---

## 2.

<!-- Your criterion. -->

On 5 pairs of clearly-AI and clearly-human text, the AI text scores higher than its human partner in all 5 pairs, and the average gap in combined score is at least 0.30.

**Why this target:**
The unsure band runs from 0.35 to 0.65, which is 0.30 wide. A gap smaller than that means a typical clear pair never lands on opposite sides, and the labels would mostly be "unsure".

---

## 3.

<!-- Your criterion. -->

I can produce each of the three labels (high-confidence AI, high-confidence human, unsure) with a real submission on each of three trials, and scoring.label_ranges() shows no gap.

**Why this target:**
While style_signal returns a constant, the combined score can only reach 0.25 to 0.75, so "human" is nearly unreachable. A label no input can produce means the system is broken.

---

## 4.

<!-- Your criterion. -->

In 10 of 10 test appeals with a valid content_id, the status becomes under_review, and the appeal appears in GET /log with the original decision still there. An unknown content_id returns a 404 and writes nothing.

**Why this target:**
The appeal is the only recourse a falsely accused writer has, and it involves no model, so it is deterministic and I allow no misses.

---

## 5.

<!-- Your criterion. -->

Five bad inputs (missing text, empty string, whitespace only, 100,000 characters, and text under 3 tokens) each return a JSON error, 400 or 503 if the model is unavailable. All 5 do so without crashing or writing a decision entry.

**Why this target:**
model_signal raises an error on under 3 tokens and reads only 400 tokens, so a huge or empty input must be rejected cleanly instead of reaching the model.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
