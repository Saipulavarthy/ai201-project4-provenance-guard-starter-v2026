# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

A submission arrives at POST /submit as JSON with text and creator_id. The route first checks that both are present, that the text is not empty, and that it is not enormous. It then runs signal one, detector.model_signal, which scores how predictable the text is to a local gpt2 model and returns a model_score between 0 and 1, where higher means more likely AI. Next it runs signal two, stylometry.style_signal, which measures sentence length spread, vocabulary variety and punctuation density and returns a style_score on the same scale. scoring.combine_signals merges the two into one combined score. scoring.score_to_label turns that score into one of three labels: high-confidence AI, high-confidence human, or unsure, each with a plain-English sentence for the reader. audit.log_decision then writes the content_id, creator_id, guess, both signal scores, the combined score, the label and a status to logs/audit.jsonl. Finally the route returns the content_id, guess, confidence and label text as JSON. If the writer disagrees, they send the content_id and their reasoning to POST /appeal, which records the appeal next to the original decision and moves the item to under_review.

Signal one measures perplexity: how surprised gpt2 is by each next word. Machine-written text tends to be more predictable, so low perplexity pushes the score toward AI. It cannot see meaning or intent, and it misreads plain writing. Simple, common-word prose, such as writing by second-language writers or younger writers, scores as machine-like, while dense, ornate prose tends to score as human. It reads only the first 400 tokens, so anything after that is invisible to it.

Signal two measures the text as text. Low variation in sentence length, a narrow vocabulary and flat punctuation all suggest AI. It cannot see what the text says, so typos, splitting or joining sentences, or pasting in a quotation can move the score without changing who wrote it. Vocabulary variety also falls naturally as text gets longer, so length alone shifts it.

The false positive: a real writer submits their own plain, simple essay. Signal one finds it predictable and scores it high, signal two sees even sentence lengths and scores it high too, and the combined score lands above the AI threshold. They see a label saying the text was probably written by AI, which is a false accusation. Their only recourse is POST /appeal with their reasoning. The system records it, sets the status to under_review and confirms, but does not re-check automatically, so a human has to review it. This case is why the unsure band has to be wide and why the AI label should be hard to reach.

POST /submit takes JSON {"text": string, "creator_id": string} and returns {"content_id": string, "guess": "ai" | "human" | "unsure", "confidence": number between 0 and 1, "label": string, "model_score": number, "style_score": number}. Missing, empty or oversized text returns a 400 with an error message, and an unavailable detector model returns a 503. POST /appeal takes JSON {"content_id": string, "reasoning": string} and returns {"content_id": string, "status": "under_review", "message": string}. An unknown content_id returns a 404 and an empty reasoning returns a 400.

---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:**

**Why that might differ between human and AI writing:**

**What it can't see:**

### Signal two — the style signal

**What it measures:**

**Why that might differ between human and AI writing:**

**What it can't see:**

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

The combining rule is scoring.py::combine_signals. It is a weighted average of the two signals, 0.6 for the model signal (detector.model_signal) and 0.4 for the style signal (stylometry.style_signal), with the weights set in config.py. I weighted the model signal higher because it separated my casual and AI test texts more widely, from three samples, so the weights are a starting guess. The AI threshold is deliberately hard to reach because on a writing site a wrong accusation costs more than a missed detection. I set HUMAN_THRESHOLD to 0.35 and AI_THRESHOLD to 0.75 in config.py. In my four-input test, clearly AI text scored 0.715, lightly edited AI 0.679, formal human-style text 0.724 and casual human-style text 0.283. No threshold separates the AI text from the formal text, so I raised the AI threshold to protect writers, at the cost that typical AI text now lands in unsure. All four test texts were written by me or generated by me, so the threshold is a guess and not a measurement.

Findings from the second signal: sentence_length_spread reached its maximum on both the AI and the formal text, so it could not tell them apart. punctuation_density scored the formal text higher than the AI text because formal prose has fewer commas and dashes per word. type_token_ratio contributed about 0 on every test text, because texts under 100 words have a ratio of 0.8 to 0.9, above its human anchor. Both signals mostly separated casual writing from plain or formal writing, not human from AI.

**The rule:**

**The numbers:**

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**



---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 to 0.35 | We think this was probably written by a person. No tool can be certain, so this is our best guess and not a verdict. |
| unsure | 0.35 to 0.75 | We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything. |
| high-confidence AI | 0.75 to 1.00 | Our checks suggest this may have been written with an AI tool. We can be wrong, especially with short or plain writing. If you wrote it yourself, you can appeal, and your appeal will be recorded and the item marked as under review. |

Scores exactly on 0.35 or 0.75 count as unsure.

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

One submission and one appeal, pasted as text from the running service (port 5001, because port 5000 is taken by macOS AirPlay on my machine).

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

**Submission (POST /submit)**

Request:
```
curl -s -X POST http://127.0.0.1:5001/submit -H "Content-Type: application/json" -d '{"text": "The committee met on Tuesday to review the proposed changes to the budget. After some discussion, members agreed that the plan needed more detail before a vote could take place.", "creator_id": "label_ai"}'
```

Response:
```
{
  "confidence": 0.7678,
  "content_id": "d700f264-751b-462c-9f15-4be140171035",
  "guess": "ai",
  "label": "Our checks suggest this may have been written with an AI tool. We can be wrong, especially with short or plain writing. If you wrote it yourself, you can appeal, and your appeal will be recorded and the item marked as under review.",
  "model_score": 0.8352,
  "style_score": 0.6667
}
```

This paragraph is plain, formal text that I wrote as a stand-in for human writing, and it was labeled high-confidence AI. That is the false positive described in What This Does, and it is a known failure of my system.

**Appeal (POST /appeal)**

Request:
```
curl -i -X POST http://127.0.0.1:5001/appeal -H "Content-Type: application/json" -d '{"content_id": "d700f264-751b-462c-9f15-4be140171035", "reasoning": "I wrote this paragraph myself for a budget meeting. It is short and formal because that is how I write minutes."}'
```

Response:
```
HTTP/1.1 200 OK
Content-Type: application/json

{
  "content_id": "d700f264-751b-462c-9f15-4be140171035",
  "message": "Your appeal has been recorded and this item is marked as under review.",
  "status": "under_review"
}
```

**Log entries (GET /log?limit=2)**
```
{
  "combined_score": 0.7678,
  "content_id": "d700f264-751b-462c-9f15-4be140171035",
  "creator_id": "label_ai",
  "guess": "ai",
  "label": "Our checks suggest this may have been written with an AI tool. We can be wrong, especially with short or plain writing. If you wrote it yourself, you can appeal, and your appeal will be recorded and the item marked as under review.",
  "model_score": 0.8352,
  "status": "decided",
  "style_score": 0.6667,
  "timestamp": "2026-11-01T20:23:03+00:00"
}
{
  "content_id": "d700f264-751b-462c-9f15-4be140171035",
  "creator_id": "label_ai",
  "event": "appeal",
  "reasoning": "I wrote this paragraph myself for a budget meeting. It is short and formal because that is how I write minutes.",
  "status": "under_review",
  "timestamp": "2026-11-01T20:25:08+00:00"
}
```

The log only appends, so the original decision keeps status "decided" and the appeal is a second entry with status "under_review" for the same content_id.

**All three labels reached with real submissions**

| Input | model_score | style_score | combined | guess |
|---|---|---|---|---|
| Casual first-person text about a late bus | 0.2339 | 0.3553 | 0.2825 | human |
| Generic remote-work paragraph | 0.8049 | 0.5809 | 0.7153 | unsure |
| Committee paragraph | 0.8352 | 0.6667 | 0.7678 | ai |

**Error paths**

- POST /submit with empty text returns 400 {"error": "empty_text"}, a missing text field returns 400 {"error": "bad_request"}, and text under 3 tokens returns 400 {"error": "text_too_short"}.
- POST /appeal with an unknown content_id returns 404 {"error": "unknown_content_id"} and a missing reasoning returns 400 {"error": "bad_request"}. Neither writes anything to the log.

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
