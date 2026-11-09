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

Moment 1: acceptance criteria. I asked an AI chat assistant to draft my five acceptance criteria, and I told it to write them. It came back with five criteria with numbers and reasons: at most 1 of 10 of my own pieces labeled high-confidence AI, an average score gap of at least 0.30 between clearly AI and clearly human pairs, all three labels reachable, appeals recorded in 10 of 10 tests, and five kinds of bad input rejected cleanly. I read them and committed them as drafted, without changing any number. That means I did not write the criteria myself, and the course notes that a criterion you did not write is harder to defend, so I am saying so here. Parts of what the draft assumed turned out to be wrong in my own tests, for example that the AI text would always score above the human text, and I will diagnose those in the next unit.

Moment 2: the combining rule and the AI threshold. After running both signals on four test texts, I asked the same assistant for options for combining them. It gave me three: a plain average, a weighted average with the AI threshold raised, and a disagreement shrink. I chose the weighted average and did not use the shrink. I then raised the AI threshold from 0.65 to 0.75, because a plain, formal paragraph that I wrote scored 0.72 and a generic AI paragraph scored 0.72 too, so the formal text would have been labeled high-confidence AI at 0.65. The assistant's suggestion was a starting point. The test texts, including the human ones, were written or generated by me, so the threshold is a guess from four samples and not a measurement.

How the code was written: the code in app.py, stylometry.py and scoring.py was written by a VS Code AI coding assistant from prompts I pasted in, one step at a time. After each step I ran the service and checked the responses with curl before moving on. The audit log in logs/audit.jsonl contains my real test submissions, including a few early ones where the test text was an unfilled placeholder phrase.

Unit 8: I used the same AI chat assistant and a VS Code coding assistant, one step at a time, and checked every result with curl or the eval runner before moving on. The ten pieces of writing in scenarios.py under "my own writing" and the other test texts were written by the chat assistant, not by me, so criterion 1 does not test my own writing, and the README says so wherever it reports that result. The chat assistant also suggested the length check as my one improvement, because my own bad-input run showed the route accepted a 100,000-character text, and I accepted it. The coding assistant wrote the rate-limiting changes, the refusal logging, the length check and the temporary script that checked appeals, from prompts I pasted in. I did not write the attack set, and I never received it, so nothing in this unit was tested against it.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

Limits: 5 requests per minute and 50 per day on POST /submit, set in config.py as RATE_LIMIT_PER_MINUTE and RATE_LIMIT_PER_DAY, with RATE_LIMITING_ENABLED = True.

<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

Why these numbers: a real writer submits a few pieces of work an hour, so 5 a minute is above anything a person pastes by hand, and a person who hits it only has to wait a minute. A script mapping my thresholds would send many variations in quick succession. The per-minute limit slows that to 5 probes a minute, and the per-day limit caps it at 50 a day. I did not choose a stricter limit because a wrongly blocked writer cannot submit their own work at all, and I did not choose a looser one because the cost of each submission is a local model run.

<!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

What the limit keys on: rate_limit_key in app.py counts requests per creator_id when the request body has a non-blank string creator_id, and per IP address otherwise (invalid JSON, a missing or blank creator_id). The limiter runs before my validation, so a malformed request still uses up one of the 5 and the request that goes over gets a 429 instead of a 400.

The weakness: the creator_id is chosen by the caller. A script that sends a new creator_id with each request gets a fresh allowance every time, so it is never limited at any speed. My flood test only produced 429s because --flood reuses one creator_id. Keying on the IP address instead would stop that, at the cost that everyone behind the same connection would share one limit. I kept the starter's per-creator key for this unit and note the weakness here instead of fixing it, because the rate limiter and the log are the only changes this unit allows apart from my one improvement.

<!-- python run_attacks.py --flood 15 -->

Flood test (python run_attacks.py --flood 15, 15 submissions from one creator_id):
```
15 submissions as 'flood_tester' against http://127.0.0.1:5001

  [ 1/15] 200
  [ 2/15] 200
  [ 3/15] 200
  [ 4/15] 200
  [ 5/15] 200
  [ 6/15] 429
  [ 7/15] 429
  [ 8/15] 429
  [ 9/15] 429
  [10/15] 429
  [11/15] 429
  [12/15] 429
  [13/15] 429
  [14/15] 429
  [15/15] 429

200 200 200 200 200 429 429 429 429 429 429 429 429 429 429

10 of 15 were rate limited.
```

The five requests inside the limit were accepted and the ten after were rejected. The service records each rejection in logs/audit.jsonl, with no content_id, for example:
```
{
  "creator_id": "flood_tester",
  "event": "rejected",
  "limit": "5 per 1 minute",
  "reason": "rate_limited",
  "status": "rejected",
  "timestamp": "2026-11-08T19:22:05+00:00"
}
```

Refusals from my own route are logged too, with audit.log_rejection. An empty text, a missing text field and a text under 3 tokens each leave a rejected entry with the reason and the text length, and never the text itself:
```
{
  "creator_id": "log_check",
  "event": "rejected",
  "reason": "empty_text",
  "status": "rejected",
  "text_length": 0,
  "timestamp": "2026-11-08T19:24:53+00:00"
}
```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

I did not run the staff attack set. My TF did not send attack_set.zip, I asked for it and received no reply, and the unit says not to go looking for it early, so python run_attacks.py --set was never run. There are therefore no held-or-broke marks for the staff attacks, and I have not written a substitute set to stand in for it. What I have instead is the flood test in the Rate Limiting section, the five-criteria runs in Run Log and Verdicts, and my audit log. The ten entries below come from those runs, not from an attack run: the flood test, the bad-input scenarios, and the five-criteria scenarios.

The worst outcome I found is entry 5: a text made of the word "word" repeated 20,000 times was labeled ai at a combined score of 0.999 and returned a 200, because the route has no length or sanity check. A real writer is not harmed by this input, but anyone can use repetition to force an AI label on a submission.

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

The score of each entry is in the JSON. The ten entries:

1. Flood test: a request past the 5-per-minute limit, rejected and logged.
```json
{
  "timestamp": "2026-11-08T19:22:05+00:00",
  "creator_id": "flood_tester",
  "event": "rejected",
  "status": "rejected",
  "reason": "rate_limited",
  "limit": "5 per 1 minute"
}
```

2. Bad-input scenario: empty text, refused by the route.
```json
{
  "timestamp": "2026-11-08T19:53:55+00:00",
  "creator_id": "eval_bad_empty",
  "event": "rejected",
  "status": "rejected",
  "reason": "empty_text",
  "text_length": 0
}
```

3. Bad-input scenario: no text field at all, refused by the route.
```json
{
  "timestamp": "2026-11-08T19:53:55+00:00",
  "creator_id": "eval_bad_missing",
  "event": "rejected",
  "status": "rejected",
  "reason": "bad_request"
}
```

4. Bad-input scenario: "hi", too short for the model, refused by the route.
```json
{
  "timestamp": "2026-11-08T19:53:55+00:00",
  "creator_id": "eval_bad_short",
  "event": "rejected",
  "status": "rejected",
  "reason": "text_too_short",
  "text_length": 2
}
```

5. Bad-input scenario: "word" repeated 20,000 times, accepted and labeled ai at 0.9985.
```json
{
  "timestamp": "2026-11-08T19:53:55+00:00",
  "content_id": "6692e9dc-8315-4ff1-a920-6395ecab9220",
  "creator_id": "eval_bad_huge",
  "guess": "ai",
  "model_score": 0.9975,
  "style_score": 1.0,
  "combined_score": 0.9985,
  "label": "Our checks suggest this may have been written with an AI tool. We can be wrong, especially with short or plain writing. If you wrote it yourself, you can appeal, and your appeal will be recorded and the item marked as under review.",
  "status": "decided"
}
```

6. Label coverage: the plain committee paragraph, written as a stand-in for human text, labeled ai.
```json
{
  "timestamp": "2026-11-08T19:53:54+00:00",
  "content_id": "baf8861f-108e-4419-9f67-ab2f2a278e6d",
  "creator_id": "eval_label covera_3",
  "guess": "ai",
  "model_score": 0.8352,
  "style_score": 0.6667,
  "combined_score": 0.7678,
  "label": "Our checks suggest this may have been written with an AI tool. We can be wrong, especially with short or plain writing. If you wrote it yourself, you can appeal, and your appeal will be recorded and the item marked as under review.",
  "status": "decided"
}
```

7. My own writing: the highest-scoring piece, the formal study-limitations paragraph, 0.045 under the AI line.
```json
{
  "timestamp": "2026-11-08T19:53:50+00:00",
  "content_id": "ecb164b4-1bc8-4982-8c75-503d7f55febb",
  "creator_id": "eval_my own writi_10",
  "guess": "unsure",
  "model_score": 0.7565,
  "style_score": 0.6272,
  "combined_score": 0.7048,
  "label": "We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything.",
  "status": "decided"
}
```

8. Score spread: a clearly-AI paragraph that only reached unsure.
```json
{
  "timestamp": "2026-11-08T19:53:52+00:00",
  "content_id": "24c66094-9cae-4ab9-a1c6-88f59ae89291",
  "creator_id": "eval_spread ai_1",
  "guess": "unsure",
  "model_score": 0.7445,
  "style_score": 0.5363,
  "combined_score": 0.6612,
  "label": "We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything.",
  "status": "decided"
}
```

9. Appeal check: an appeal, recorded with status under_review.
```json
{
  "timestamp": "2026-11-09T02:10:56+00:00",
  "content_id": "61c22426-9d24-492a-b92c-b0060e39ad0e",
  "creator_id": "appeal_check_1",
  "event": "appeal",
  "status": "under_review",
  "reasoning": "I wrote this myself."
}
```

10. Appeal check: the original decision for the same content_id, still in the log with status decided.
```json
{
  "timestamp": "2026-11-09T02:10:55+00:00",
  "content_id": "61c22426-9d24-492a-b92c-b0060e39ad0e",
  "creator_id": "appeal_check_1",
  "guess": "unsure",
  "model_score": 0.3869,
  "style_score": 0.5675,
  "combined_score": 0.4591,
  "label": "We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything.",
  "status": "decided"
}
```

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

Scenarios are in scenarios.py and were run with python run_eval.py --label before, three trials each, changing nothing between trials. All three trials came out identical for every scenario, which is expected because neither signal is random. Results are in results/run_2026-11-08_1453_before.md.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | at most 1 of 10 | 0/10 | 0/10 | 0/10 | MET (with caveat) |
| 2. Score spread, AI above human in 5 of 5 pairs, average gap at least 0.30 | 5 of 5, gap at least 0.30 | 5/5, gap 0.400 | 5/5, gap 0.400 | 5/5, gap 0.400 | MET |
| 3. All three labels reachable | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 4. Appeals recorded | 10 of 10 | 10/10 | not repeated | not repeated | MET |
| 5. Bad input rejected cleanly | 5 of 5 | 4/5 | 4/5 | 4/5 | MISSED |

Criterion 4 was tested by hand with a temporary script, once, not three times. It submitted 10 texts under 10 creator_ids (all guessed unsure), appealed each, and checked the log: 10 of 10 appeals returned 200 with status under_review, 10 of 10 original decisions were still in the log, and 10 of 10 appeal entries were recorded. An appeal for the content_id "not-a-real-id" returned 404 unknown_content_id and wrote nothing to the log.

Output for each criterion, from run 1 (produced by app.py::submit, scoring.py::score_to_label and app.py::appeal):

Criterion 1, first "my own writing" text:
```json
{
  "status": 200,
  "guess": "unsure",
  "confidence": 0.4861,
  "model_score": 0.4197,
  "style_score": 0.5858,
  "label": "We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything.",
  "sent": "spent most of sunday trying to fix my bike chain and ended up with gre"
}
```

Criterion 2, first "spread ai" text and first "spread human" text:
```json
[
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.6612,
    "model_score": 0.7445,
    "style_score": 0.5363,
    "label": "We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything.",
    "sent": "Effective time management is a crucial skill in both personal and prof"
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.376,
    "model_score": 0.3238,
    "style_score": 0.4543,
    "label": "We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything.",
    "sent": "honestly i have no idea why my sourdough keeps coming out flat. follow"
  }
]
```

Criterion 3, the three "label coverage" texts:
```json
[
  {
    "status": 200,
    "guess": "human",
    "confidence": 0.2825,
    "model_score": 0.2339,
    "style_score": 0.3553,
    "label": "We think this was probably written by a person. No tool can be certain, so this is our best guess and not a verdict.",
    "sent": "ok so my bus was late again and i swear the driver just stopped for a "
  },
  {
    "status": 200,
    "guess": "unsure",
    "confidence": 0.7153,
    "model_score": 0.8049,
    "style_score": 0.5809,
    "label": "We can't tell whether this was written by a person or with an AI tool. Plain or formal writing can look machine-made to our checks, so this is not a judgment about you or your work. If you wrote it yourself, you don't need to do anything.",
    "sent": "Remote work has become an increasingly important topic in modern organ"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7678,
    "model_score": 0.8352,
    "style_score": 0.6667,
    "label": "Our checks suggest this may have been written with an AI tool. We can be wrong, especially with short or plain writing. If you wrote it yourself, you can appeal, and your appeal will be recorded and the item marked as under review.",
    "sent": "The committee met on Tuesday to review the proposed changes to the bud"
  }
]
```

Criterion 4, one row per appeal (app.py::appeal, checked against GET /log):

| # | content_id | appeal code | appeal status | decision in log | appeal in log |
|---|---|---|---|---|---|
| 1 | 61c22426-9d24-492a-b92c-b0060e39ad0e | 200 | under_review | yes | yes |
| 2 | 18bb8239-220a-4a39-b32b-b0eb3aeca069 | 200 | under_review | yes | yes |
| 3 | 2bb08e82-46cb-4a12-8a49-8d3229535c46 | 200 | under_review | yes | yes |
| 4 | c72dc2d2-da3c-4767-b820-6a3614eefc3a | 200 | under_review | yes | yes |
| 5 | 43d39aae-4b6e-4edc-ade3-90a168774fbb | 200 | under_review | yes | yes |
| 6 | ff0b3a90-bc03-4d1b-8a11-bb0a0439daf2 | 200 | under_review | yes | yes |
| 7 | 3f3afc72-3e36-4d1b-97c6-5068f8baea5f | 200 | under_review | yes | yes |
| 8 | f45b849a-a80d-4c4a-ac15-da4b21875a0b | 200 | under_review | yes | yes |
| 9 | 7b481c97-2e08-425a-aa82-cd9b71fb87f9 | 200 | under_review | yes | yes |
| 10 | 00ad4f01-1b11-4bd3-b0e8-b48c8e3b5cbd | 200 | under_review | yes | yes |

Criterion 5, all five "bad input" bodies:
```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"creator_id\": \"eval_bad_missing\"}"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)"
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "   \n   "
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9985,
    "model_score": 0.9975,
    "style_score": 1.0,
    "label": "Our checks suggest this may have been written with an AI tool. We can be wrong, especially with short or plain writing. If you wrote it yourself, you can appeal, and your appeal will be recorded and the item marked as under review.",
    "sent": "word word word word word word word word word word word word word word "
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "hi"
  }
]
```

Verdicts and diagnoses:

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

Criterion 1 is MET, but the ten pieces were written by an AI assistant as stand-ins, not by me, so this result shows how the detector treats those registers and not how it treats my own writing. It is also met only because of where the AI threshold sits. My ten pieces scored between 0.486 and 0.705 and the five AI texts between 0.661 and 0.735, so the two ranges overlap and no threshold separates them. At the old threshold of 0.65 six of my ten pieces would have been labeled AI. The highest piece, a formal paragraph about study limitations, scored 0.705, only 0.045 under the AI line.

Criterion 2 is MET: the AI text scored higher than its human partner in all 5 pairs, with an average AI score of 0.703 against 0.303 for the human texts, a gap of 0.400. This is a gap between plain prose and casual prose more than between AI and human. None of the five clearly-AI texts reached the AI label (all were unsure), and the human texts included two that were also unsure.

Criterion 3 is MET on all three trials: the casual text scored 0.282 and was labeled human, the remote work text 0.715 and unsure, and the committee paragraph 0.768 and ai. The AI label was reached only by the committee paragraph, which is plain text I wrote as a stand-in for a human, so the label fires on short plain text and misses the AI paragraphs.

Criterion 4 is MET as described above.

Criterion 5 is MISSED. Four of the five bad inputs (missing text, empty text, whitespace only, and "hi") returned a 400 as intended. The fifth, 100,000 characters of the word "word" repeated, returned 200 with the label ai at a combined score of 0.999. The stage is the route and the mechanism is that app.py::submit has no length check or sanity check on the text before the signals run. The repeated text gives signal one a model score of 1.00 because the language model finds it perfectly predictable, and signal two a style score of 1.00 because it has no variation, so both signals read it as machine-written. This also means repeating one word is an easy way to get a decision labeled AI. The contract in "What This Does" says oversized text returns a 400, but the code never enforced that, so the README claim was wrong. The log confirms the four refused inputs left only rejected entries: 12 across the three trials (3 each, with reasons bad_request, empty_text, empty_text and text_too_short) and no decision entries, while eval_bad_huge left one decision entry per trial.

Pattern: the misses and the near-misses share one cause. The system's scores track how plain or repetitive a text is, not whether a person wrote it, so a plain text can look like AI and degenerate text looks like certain AI, while thresholds protect writers only by sending nearly everything to unsure.

---

## The Improvement

What I changed: one change, a length check on POST /submit. config.py now has MAX_TEXT_CHARS = 20000, and app.py::submit rejects longer text before either signal runs, with a 400 {"error": "text_too_long"} and an audit.log_rejection entry (reason "text_too_long", with text_length and never the text). Weights, thresholds, labels and both signals are unchanged.

Which diagnosis pointed at it: criterion 5. The 100,000-character repeated-word text returned 200 and the label ai at 0.9985 in the before run. The stage was the route and the mechanism was that nothing checked the input before the signals ran.

Run Log — After (python run_eval.py --label after, three trials, results/run_2026-11-08_2200_after.md):

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | at most 1 of 10 | 0/10 | 0/10 | 0/10 | MET (with the earlier caveat) |
| 2. Score spread | AI above human in 5 of 5, average gap at least 0.30 | 5/5, gap 0.400 | 5/5, gap 0.400 | 5/5, gap 0.400 | MET |
| 3. All three labels reachable | 3 of 3 | 3/3 | 3/3 | 3/3 | MET |
| 4. Appeals recorded | 10 of 10 | not repeated | not repeated | not repeated | MET in the before run; /appeal was not touched by this change |
| 5. Bad input rejected cleanly | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Before and after:

| Criterion | Before | After |
|---|---|---|
| 1 | 0/10, MET | 0/10, MET |
| 2 | 5/5, gap 0.400, MET | 5/5, gap 0.400, MET |
| 3 | 3/3, MET | 3/3, MET |
| 4 | 10/10, MET | not repeated |
| 5 | 4/5, MISSED | 5/5, MET |

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->

Did it help, and how do I know: yes for criterion 5, and nothing else moved. Every guess and combined score for criteria 1 to 3 was identical between the before and after runs (step 1a), so the change touched only the input check. The fix is narrow. It fixes the contract that oversized text is refused, but not the evasion behind it: in a quick check an 18,000-character repeated paragraph (1cac98b3-e11c-4701-b2c6-a3206e0f4a0b in logs/audit.jsonl) still got a 200 and the label ai at a combined score of 0.9983, because repetition looks perfectly machine-written to both signals. The change also has a cost: a genuine text over 20,000 characters, roughly 3,500 words, is now refused, although the detector only reads its first 400 tokens anyway.

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->

Attack Run — After: not run. I never received attack_set.zip, so there is no attack comparison, and the before and after results above cover my own five criteria only.

---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->

All five of my criteria are MET after the improvement, but several of those passes are weaker than they look, and the attack set was never run, so there are failures I have not seen.

Still getting through:
1. Repeated text still gets labeled AI. An 18,000-character paragraph repeated 250 times was labeled ai at a combined score of 0.9983, because repetition looks perfectly machine-written to both signals. The length check only stops this past 20,000 characters. What I would do: add a repetition check before the signals, for example reject or route to unsure any text whose most common sentence makes up a large share of the text. I stopped because this unit allows one improvement and the length check was the one my diagnosis named.
2. My detector does not separate human writing from AI writing, it separates plain or repetitive text from casual text. My ten stand-in human pieces scored 0.486 to 0.705 and my five AI texts scored 0.661 to 0.735, so the ranges overlap and no threshold separates them. None of the five clearly-AI texts reached the AI label. What I would do: replace or add a signal that does not reward plain prose, and test it on real human writing. I stopped because that is a new signal, not one change.
3. The rate limit is easy to dodge. It counts requests per creator_id, and the caller chooses the creator_id, so a script that sends a new one with every request is never limited. What I would do: key the limit on the IP address as well. I stopped because the rate limiter was a required change in this unit and I recorded this weakness in the Rate Limiting section instead of redesigning it.
4. Unknown failures. I never received attack_set.zip, so I do not know which staff attacks would get through. Evasion by typos, rewording and prompt injection are untested.

Criterion I would tighten: criterion 1. It passed 0 of 10 only because the AI threshold sits at 0.75, the ten pieces were written by an AI assistant and not by me, and the highest scored 0.705. I would run it again on ten pieces I wrote myself and require that none score within 0.05 of the AI line.

The gap between what the system was meant to do and what it does: I meant it to estimate whether a person wrote a text. It estimates how predictable and uniform the text is, so plain, formal and repetitive writing reads as machine-made and everything uncertain is pushed into unsure.

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->

The trade if this ran for real: fewer wrong accusations means more AI text getting through. I would keep the AI label hard to reach, as it is, because a false accusation costs a writer their credibility and their work, while a missed detection costs the site some trust. The people who pay for that choice are the other writers and readers who see AI text labeled unsure, and honest writers still pay when they have to appeal, because an appeal is only recorded and nobody re-checks it automatically.

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
