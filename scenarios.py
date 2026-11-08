"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        "texts": [
            "spent most of sunday trying to fix my bike chain and ended up with grease on literally everything, including the cat somehow. watched three tutorials, none of which matched the bike i actually own. in the end my neighbour wandered over, looked at it for about four seconds and said the derailleur was bent. he fixed it with a screwdriver and a bit of force. i felt both grateful and mildly stupid. rode to the shop afterwards just to make sure it worked and bought a tin of biscuits as a thank you.",
            "we finally booked the trip after two months of everyone saying they were free and then suddenly not being free. it's going to be a cheap hostel near the coast, four of us, one bathroom, which is going to be an adventure. dev wants to hike every day and i want to sit near water with a book, so we've agreed to alternate. my plan is to pack light and then immediately regret it. honestly just excited to be somewhere that isn't my desk for a few days, even if it rains the whole time.",
            "the library was packed today so i ended up working in the corner of a cafe that plays the same playlist on a loop. by the third hour i could have sung along to every song. got through most of the problem set though, apart from the last question which i stared at until it stopped making sense. the barista gave me a free refill when she noticed how long i'd been there, which was kind. i'm going to try office hours tomorrow and see if anyone else got stuck on number six.",
            "This semester I built a small weather dashboard for my web development course. It pulls forecast data from a public API and shows the next five days as cards, with a simple chart for temperature. Most of the work went into handling errors, like when the API is slow or a city name is spelled wrong. I used plain JavaScript instead of a framework so I could understand how the pieces fit together. If I did it again I would add caching so the page loads faster and doesn't call the service every time someone refreshes.",
            "In the lab we measured how the period of a pendulum changes with its length. We timed twenty swings for each of six lengths and divided by twenty to reduce the timing error. The results followed the expected square root relationship fairly well, though the longest length was a little off, probably because the string stretched slightly. Our estimate of gravitational acceleration came out at 9.6 metres per second squared, about two percent below the accepted value. Next time we would use a photogate instead of a stopwatch, since our reaction time was the biggest source of error.",
            "To set up the project, first clone the repository and create a virtual environment inside the folder. Install the dependencies from the requirements file, then run the check script to make sure everything works. If the check fails on memory, close other programs and try again. The model downloads the first time you run the detector, so do that before class. I keep two terminals open, one for the server and one for testing with curl, and I label them so I don't type commands into the wrong one.",
            "I think the networking course is harder than it looks at first, mostly because the ideas build on each other. You can follow each lecture and still get lost on the homework if you skipped the previous week. What helped me was drawing the packet path on paper for every example, from the application down to the wire and back up. It's slow, but after a few of them the layers stopped feeling like a list to memorise. I still mix up some of the timers, so I'm making a small table to check before the exam.",
            "The adoption of renewable energy in the region has accelerated over the past decade, driven by falling costs and supportive policy. However, the transition has not been uniform. Rural areas with abundant wind resources have benefited from new investment, while urban centres continue to depend on older infrastructure. This disparity suggests that policy alone is insufficient and that grid upgrades are equally necessary. Consequently, any assessment of progress should consider both generation capacity and the capacity of the network to distribute that energy reliably to consumers.",
            "I am writing to apply for the software engineering internship advertised on your careers page. I am a third year Computer Engineering student with a business minor, and I have built several projects in Python, JavaScript and Swift, including a classifier for online discussion posts and a web service that scores text for likely machine generation. I am particularly interested in the opportunity to work on production systems and to learn from experienced engineers. I would welcome the chance to discuss how my skills could contribute to your team, and I am available for an interview at your convenience.",
            "The results indicate that structured feedback during the first weeks of a course improves later performance. Students who received written comments each week scored higher on the final assessment than those who received only grades. Nevertheless, the study has important limitations. The sample was small and drawn from a single course, and students were not randomly assigned to groups. These factors limit the extent to which the findings can be generalised. Further work with a larger and more varied sample would be needed before firm conclusions can be drawn.",
        ],
    },
    {
        "name": "spread ai",
        "criterion": 2,
        "texts": [
            "Effective time management is a crucial skill in both personal and professional settings. By prioritizing tasks, setting clear goals, and minimizing distractions, individuals can significantly improve their productivity. Furthermore, regular reflection helps ensure continued progress and long-term success.",
            "Climate change represents one of the most pressing challenges of our time. It affects ecosystems, economies, and communities around the world. Addressing it requires coordinated action, innovative technologies, and a sustained commitment from governments, businesses, and individuals alike.",
            "Healthy eating plays an essential role in maintaining overall well-being. A balanced diet that includes fruits, vegetables, whole grains, and lean proteins can reduce the risk of chronic disease. Moreover, mindful eating habits contribute to better energy levels and mental clarity.",
            "Artificial intelligence is transforming the way organizations operate across a wide range of industries. It enables faster decision-making, greater efficiency, and new opportunities for innovation. However, it is important to address concerns related to privacy, fairness, and accountability.",
            "Travelling to new places offers countless opportunities for personal growth and cultural understanding. It allows individuals to step outside their comfort zones, engage with diverse perspectives, and create lasting memories. Ultimately, travel enriches both the mind and the spirit.",
        ],
    },
    {
        "name": "spread human",
        "criterion": 2,
        "texts": [
            "honestly i have no idea why my sourdough keeps coming out flat. followed the recipe twice, even bought a thermometer, and it still looks like a frisbee. my flatmate says the starter is dead but it bubbles every morning so who knows. trying again saturday.",
            "went to my cousins wedding and the dj played the same three songs for like two hours. the cake was good though, lemon with some kind of cream. got home at one and my feet are still angry at me.",
            "so the landlord finally fixed the heating but now it only works if you whack the pipe under the sink. nobody told me that. found out because my neighbour heard banging and came to check if i was ok.",
            "tried to learn guitar from youtube for a month. can play two chords badly and one song if you squint. my fingers hurt, the dog leaves the room whenever i start, and yet i keep going. weird.",
            "forgot my umbrella again so naturally it poured the whole walk home. dripped through the hallway, stepped on the cat, apologised to the cat. made toast and ate it standing up. fine. fine day overall.",
        ],
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "texts": [
            "ok so my bus was late again and i swear the driver just stopped for a coffee, i am not even joking, we sat outside a bakery for like ten minutes. got to work wet and annoyed. my manager said nothing which was worse. then the printer jammed, obviously. lunch was a sad sandwich at my desk while i pretended to read emails. anyway the day got better around four when someone brought in leftover cake from a birthday i did not know about, so i ate two slices and left early feeling weirdly fine about everything.",
            "Remote work has become an increasingly important topic in modern organizations. It offers numerous benefits, including improved flexibility, reduced commuting time, and access to a broader talent pool. However, it also presents challenges such as maintaining team cohesion and ensuring effective communication. Furthermore, organizations must carefully consider how to balance productivity with employee well-being. Ultimately, a thoughtful and adaptive approach is essential for success in this evolving landscape.",
            "The committee met on Tuesday to review the proposed changes to the budget. After some discussion, members agreed that the plan needed more detail before a vote could take place.",
        ],
    },
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"creator_id": "eval_bad_missing"},
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": "   \n   ", "creator_id": "eval_bad_blank"},
            {"text": "word " * 20000, "creator_id": "eval_bad_huge"},
            {"text": "hi", "creator_id": "eval_bad_short"},
        ],
    },
    # Criterion 4 (appeal path) is tested by hand, not by this file.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
