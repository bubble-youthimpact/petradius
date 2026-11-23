"""PetRadius interactive guides.

Content comes from the PetRadius guide PDFs in assets/docs/. Each guide gets its own page at
/guides/<slug>/ (built by build.py), with interactive parts handled by assets/js/guides.js.

To add a guide: add an entry to GUIDES and a matching function in BODIES that returns its HTML.
"""

STAGES = [("before", "Before you adopt"), ("home", "Bringing your pet home"), ("care", "Everyday care")]

GUIDES = [
    # In reading order: before you adopt -> bringing your pet home -> everyday care.
    # stage: before | home | care.  species: "dog", "cat" or "dog cat".
    {"slug": "dog-readiness-checklist", "title": "Is a Dog Right for You?",
     "short": "A 12-point self-assessment of your time, budget, home and long-term plans. Get your result instantly.",
     "tag": "Self-assessment", "stage": "before", "species": "dog", "minutes": 4, "icon": "clipboard", "pages": 2,
     "intro": "Bringing a dog into your life is a rewarding 10-to-15-year commitment. Tick each statement that honestly describes you and see your readiness score."},
    {"slug": "dog-adoption-budget-breakdown", "title": "Dog Adoption Budget Breakdown",
     "short": "Plan adoption fees, startup supplies and monthly care with a budget calculator that adds it up for you.",
     "tag": "Calculator", "stage": "before", "species": "dog", "minutes": 5, "icon": "book", "pages": 1,
     "intro": "Welcoming a rescue dog is incredibly rewarding, and it comes with real costs. Enter your own estimates to plan your first year."},
    {"slug": "first-week-checklist", "title": "First Week Checklist",
     "short": "A day-by-day checklist for a safe, calm and structured first week with your new pet.",
     "tag": "Checklist", "stage": "home", "species": "dog cat", "minutes": 3, "icon": "calendar", "pages": 1,
     "intro": "Bringing a new pet home is a major transition. Work through this checklist during your pet’s critical first week — your progress is saved on this device."},
    {"slug": "pet-owners-essential-guide", "title": "The New Pet Owner’s Essential Blueprint",
     "short": "Settling-in rules, critical dos and don’ts, and smart hacks for new dog and cat owners.",
     "tag": "Tips & rules", "stage": "home", "species": "dog cat", "minutes": 6, "icon": "paw", "pages": 4,
     "intro": "A practical guide to welcoming your new companion home. Switch between dogs and cats to see what matters most in the first weeks."},
    {"slug": "pet-nutrition-feeding-guide", "title": "Pet Nutrition & Feeding Guide",
     "short": "Feeding schedules by life stage, a food-switch planner and the foods your pet must never eat.",
     "tag": "Planner & reference", "stage": "care", "species": "dog cat", "minutes": 4, "icon": "leaf", "pages": 1,
     "intro": "Proper diet and feeding habits lay the foundation for your pet’s lifelong health and energy."},
    {"slug": "pet-health-guide", "title": "Pet Health & Veterinary Guide",
     "short": "Core vaccines, year-round preventive care and the warning signs that need a vet right away.",
     "tag": "Reference", "stage": "care", "species": "dog cat", "minutes": 3, "icon": "shield", "pages": 1,
     "intro": "Proactive medical care protects your pet against preventable diseases and helps catch health concerns early."},
    {"slug": "pet-behavior-guide", "title": "Pet Behavior & Communication Guide",
     "short": "Read dog and cat body language, handle common challenges and train with positive reinforcement.",
     "tag": "Reference", "stage": "care", "species": "dog cat", "minutes": 5, "icon": "eye", "pages": 2,
     "intro": "Understanding your pet’s body language is essential for building trust, preventing anxiety and handling common challenges."},
]


def _check_items(e, key, items, start=0):
    out = []
    for i, (title, desc) in enumerate(items, start):
        out.append(f"""            <label class="g-check-item">
              <input type="checkbox" data-id="{key}-{i}">
              <span class="g-box" aria-hidden="true"></span>
              <span class="g-check-text"><strong>{e(title)}</strong><small>{e(desc)}</small></span>
            </label>""")
    return "\n".join(out)


def _tabs(e, name, panels, cls=""):
    """panels: [(label, html)]"""
    btns, bodies = [], []
    for i, (label, html) in enumerate(panels):
        sel = "true" if i == 0 else "false"
        tabidx = "" if i == 0 else ' tabindex="-1"'
        hid = "" if i == 0 else " hidden"
        btns.append(f'<button type="button" role="tab" id="t-{name}-{i}" aria-controls="p-{name}-{i}" aria-selected="{sel}"{tabidx}>{e(label)}</button>')
        bodies.append(f'<div class="g-panel" role="tabpanel" id="p-{name}-{i}" aria-labelledby="t-{name}-{i}"{hid}>{html}</div>')
    return (f'<div class="g-tabs {cls}" data-tabs><div class="g-tablist" role="tablist">{"".join(btns)}</div>'
            f'{"".join(bodies)}</div>')


def _section(num, title, inner, lead=""):
    lead_html = f'<p class="g-lead">{lead}</p>' if lead else ""
    return f"""        <section class="g-section">
          <h2><span class="g-num">{num}</span>{title}</h2>
          {lead_html}
          {inner}
        </section>"""


def _dos_donts(e, icon, dos, donts):
    li = lambda items, cls: "".join(f'<li><strong>{e(t)}</strong> {e(d)}</li>' for t, d in items)
    return f"""<div class="g-dd">
            <div class="g-dd-col do"><h3>{icon('heart')}What to do</h3><ul>{li(dos, 'do')}</ul></div>
            <div class="g-dd-col dont"><h3>{icon('x')}What not to do</h3><ul>{li(donts, 'dont')}</ul></div>
          </div>"""


def _tips(e, tips):
    return '<div class="g-tips">' + "".join(
        f'<div class="g-tip"><span class="g-tip-n">{i}</span><h3>{e(t)}</h3><p>{e(d)}</p></div>'
        for i, (t, d) in enumerate(tips, 1)) + "</div>"


# ----------------------------------------------------------------------
def essential(e, icon):
    dog_dos = [
        ("Establish a routine:", "Feed, walk and crate your dog at the exact same times every day to minimize transition anxiety."),
        ("Crate training:", "Use the crate as a positive sanctuary, never as a punishment. Feed meals inside it to build positive associations."),
        ("Socialize mindfully:", "Introduce new environments, sounds and people gradually, always pairing the experience with high-value treats."),
        ("Provide mental enrichment:", "Use puzzle feeders, frozen KONGs and sniff walks. 15 minutes of sniffing equals roughly 1 hour of physical running."),
    ]
    dog_donts = [
        ("Don’t punish after the fact:", "Dogs can’t connect a punishment with a past action. Punishing a chewed shoe from an hour ago only teaches them to fear you."),
        ("Avoid dangerous foods:", "Never feed chocolate, grapes, raisins, onions, garlic, macadamia nuts, or anything containing xylitol."),
        ("Don’t skimp on leash safety:", "Avoid retractable leashes — they offer minimal control and can cause friction burns or snap unexpectedly."),
        ("Don’t rush the dog park:", "Wait until your dog completely trusts you and responds reliably to a recall before entering off-leash areas."),
    ]
    dog_tips = [
        ("The toy rotation hack", "Keep only 3–4 toys out and hide the rest. Swap them weekly to keep things exciting without buying new toys."),
        ("Perfecting the recall", "Never call your dog for something they dislike (baths, leaving the park, nail trims). Walk to them instead, so their name always means good things."),
        ("Decompression walks", "Use a 10–15 ft long line in an open field so your dog can explore and sniff at their own pace. It rapidly lowers stress levels."),
    ]
    rule = """<ol class="g-timeline">
              <li><span class="g-tl-badge">3 days</span><h3>Overwhelmed</h3><p>They feel anxious and unsure. Keep things quiet and predictable.</p></li>
              <li><span class="g-tl-badge">3 weeks</span><h3>Settling in</h3><p>They start to relax and show their true personality.</p></li>
              <li><span class="g-tl-badge">3 months</span><h3>At home</h3><p>They’ve built complete trust and understand their routine.</p></li>
            </ol>"""
    dog = (f'<div class="g-callout"><h3>The 3-3-3 rule for rescue dogs</h3>{rule}</div>'
           f'<h3 class="g-h3">Critical dos & don’ts</h3>{_dos_donts(e, icon, dog_dos, dog_donts)}'
           f'<h3 class="g-h3">Pro tips & smart hacks</h3>{_tips(e, dog_tips)}')

    cat_dos = [
        ("Follow the litter box rule:", "Always provide N + 1 litter boxes, where N is the number of cats. Place them in quiet, low-traffic areas."),
        ("Provide vertical space:", "Cats feel secure up high. Cat trees, window perches and wall shelves increase their livable territory."),
        ("Invest in scratching posts:", "Provide vertical and horizontal scratchers near sleeping areas — cats scratch to stretch and mark territory."),
        ("Keep water separate:", "Place water bowls a few feet away from food. In nature, cats avoid water near their prey."),
    ]
    cat_donts = [
        ("Never declaw your cat:", "Declawing amputates the last bone of each toe, causing chronic pain, aggression and litter box avoidance. Use scratching posts and nail caps instead."),
        ("Avoid poisonous plants:", "Lilies are highly toxic — even a little pollen can cause fatal kidney failure. Check houseplants like pothos and monsteras too."),
        ("Don’t play with bare hands:", "Using fingers as toys teaches your cat that skin is a target. Use wand toys instead."),
        ("Don’t force socialization:", "Let your cat initiate contact. Pulling a hiding cat out from under the bed creates anxiety and distrust."),
    ]
    cat_tips = [
        ("The slow blink", "Make eye contact, slowly close and open your eyes, then look away. It’s the ultimate feline sign of trust."),
        ("Encourage hydration", "Cats have a low thirst drive and prefer moving water. A circulating fountain helps reduce urinary and kidney issues."),
        ("Scent swapping", "Rub a clean sock along your cat’s cheeks and place it in common rooms, so the house already smells familiar."),
    ]
    cat = ('<div class="g-callout"><h3>The basecamp method</h3><p>Cats are intensely territorial. Start a new cat in a single room — their “basecamp” — with food, water, a litter box and a scratching post for the first 5–7 days before expanding access.</p></div>'
           f'<h3 class="g-h3">Critical dos & don’ts</h3>{_dos_donts(e, icon, cat_dos, cat_donts)}'
           f'<h3 class="g-h3">Pro tips & smart hacks</h3>{_tips(e, cat_tips)}')
    return _tabs(e, "species", [("\U0001F436 New dog owners", dog), ("\U0001F431 New cat owners", cat)], "g-tabs-big")


def readiness(e, icon):
    groups = [
        ("Time & daily commitment", [
            ("Daily exercise & mental stimulation", "I can commit at least 1 to 2 hours daily for walks, play and training, regardless of weather or work schedule."),
            ("Workplace schedule & absence", "I’m not routinely away for more than 8 to 10 hours without a plan for potty breaks (dog walker, midday check-in)."),
            ("Patience for training & potty routines", "I’m prepared to spend time on house training, obedience work and behavior challenges without frustration."),
        ]),
        ("Financial readiness", [
            ("Upfront adoption & setup costs", "I’ve budgeted for adoption fees, spay/neuter, crate, leash, harness, bowls and first vet visits ($500 – $1,500+)."),
            ("Routine monthly maintenance", "My budget covers quality food, flea/tick/heartworm prevention, treats and grooming ($100 – $200+/month)."),
            ("Emergency medical reserve / pet insurance", "I have emergency savings or pet insurance for unexpected accidents or illness ($1,000+ potential expense)."),
        ]),
        ("Living space & environment", [
            ("Pet-friendly housing & rules", "My landlord or HOA permits dogs, and I know any breed, weight or count restrictions."),
            ("Safe home environment", "My home is secure (fenced yard or safe walking route) and free of toxic hazards a curious dog could reach."),
            ("Tolerance for mess & wear", "I’m comfortable with pet hair, occasional mud and minor wear on furniture or floors."),
        ]),
        ("Long-term commitment & household", [
            ("10–15 year horizon", "I’m prepared to care for a dog through moves, job changes, new family members and retirement."),
            ("Household & allergy check", "Everyone at home agrees on getting a dog, and no one has severe unmanageable allergies."),
            ("Travel & boarding contingency", "I have a plan for trusted pet care, sitters or boarding when I travel."),
        ]),
    ]
    sections, n = [], 0
    for gi, (title, items) in enumerate(groups, 1):
        sections.append(f'<fieldset class="g-group"><legend><span class="g-num">{gi}</span>{e(title)}</legend><div class="g-check-list">{_check_items(e, "r", items, n)}</div></fieldset>')
        n += len(items)
    results = [
        ("great", "10–12", "You’re in a great position to welcome a dog!", "Start researching breeds or visiting local shelters.", '<a class="btn btn-primary" href="../../pets/">Meet adoptable pets</a>'),
        ("close", "7–9", "You’re on the right track.", "You might need to adjust your schedule, budget or living arrangement before adopting.", '<a class="btn btn-ghost" href="../dog-adoption-budget-breakdown/">Plan your budget</a>'),
        ("wait", "0–6", "Consider waiting a little longer.", "Explore fostering, dog-sitting or volunteering at a shelter to gain experience first.", '<a class="btn btn-ghost" href="../../contact/">Ask about volunteering</a>'),
    ]
    res_html = "".join(f'<div class="g-result" data-result="{k}" hidden><span class="g-result-range">{r} boxes</span><h3>{e(h)}</h3><p>{e(p)}</p>{cta}</div>' for k, r, h, p, cta in results)
    return f"""<div class="g-score-layout" data-checklist="readiness" data-score>
          <div class="g-score-main">{''.join(sections)}</div>
          <aside class="g-score-card" aria-live="polite">
            <div class="g-ring" style="--p:0"><span><b data-score-n>0</b>/12</span></div>
            <p class="g-score-label">boxes checked</p>
            <p class="g-score-hint" data-score-hint>Tick each statement that describes you.</p>
            {res_html}
            <button type="button" class="g-reset" data-reset>Reset checklist</button>
          </aside>
        </div>"""


def first_week(e, icon):
    days = [
        ("Days 1–2", "Arrival & safe space", [
            ("Establish a quiet zone", "Set up a crate, room or bed in a low-traffic area with fresh water and familiar bedding."),
            ("Home & yard safety sweep", "Secure cleaning supplies, toxic plants, wires and small chewable objects."),
            ("Initial bathroom & potty routine", "Take dogs straight to their potty spot outside before going indoors. Place cats directly in their litter box area."),
        ]),
        ("Days 3–5", "Routine & bonding", [
            ("Keep consistent feeding times", "Feed fixed meals at the same time each day, using the food your rescue recommends to avoid stomach upset."),
            ("Gentle exercise & play", "Short, positive play or short leash walks. Avoid busy dog parks or high-stress public spaces early on."),
        ]),
        ("Days 6–7", "Health & long-term setup", [
            ("Wellness exam & microchip check", "Visit your vet for a baseline checkup and make sure ID tags and microchip info are registered."),
            ("Review house rules", "Everyone at home follows the same rules on furniture, treats and basic training cues."),
        ]),
    ]
    blocks, n = [], 0
    for label, title, items in days:
        blocks.append(f"""<div class="g-day">
            <div class="g-day-head"><span class="g-day-badge">{e(label)}</span><h3>{e(title)}</h3></div>
            <div class="g-check-list">{_check_items(e, "w", items, n)}</div>
          </div>""")
        n += len(items)
    return f"""<div data-checklist="first-week">
          <div class="g-progress"><div class="g-progress-top"><strong><span data-done>0</span> of {n} done</strong><button type="button" class="g-reset" data-reset>Reset</button></div>
            <div class="g-bar"><span data-bar></span></div>
            <p class="g-progress-msg" data-complete hidden>\U0001F389 First week complete — great job settling in your new pet!</p>
          </div>
          <div class="g-days">{''.join(blocks)}</div>
        </div>"""


def behavior(e, icon):
    def cards(rows, a_label, b_label):
        return '<div class="g-states">' + "".join(
            f'<div class="g-state g-state-{cls}"><h3>{e(state)}</h3><dl><dt>{e(a_label)}</dt><dd>{e(a)}</dd><dt>{e(b_label)}</dt><dd>{e(b)}</dd></dl></div>'
            for cls, state, a, b in rows) + "</div>"
    dogs = cards([
        ("calm", "Relaxed & happy", "Loose body, soft posture, gently wagging tail at neutral height.", "Soft, relaxed eyes; open mouth with relaxed tongue."),
        ("alert", "Alert & curious", "Weight forward, ears perked up, tail held horizontally or slightly high.", "Direct gaze, closed mouth or slight focus, intent expression."),
        ("stress", "Anxious & stressed", "Tense posture, tail tucked low or wagging stiffly, lip licking, yawning.", "Whites of the eyes showing (“whale eye”), avoiding direct contact."),
        ("fear", "Fearful / defensive", "Crouched low, weight shifted back, tail tightly tucked, raised hackles.", "Ears pinned flat, lip curling, growling."),
    ], "Body posture & tail", "Face & eyes")
    cats = cards([
        ("calm", "Relaxed & content", "Tail held high with a slight curve at the tip; ears in neutral position.", "Stretched out or loosely curled; gentle purring or kneading."),
        ("stress", "Overstimulated / annoyed", "Tail twitching, flicking or thumping; ears turned outward or back.", "Rippling skin on the back, sudden freeze, low growl or vocal protest."),
        ("fear", "Frightened / threatened", "Puffed-out “bottle-brush” tail; ears flattened completely.", "Arched back with fur raised, hissing or spitting."),
    ], "Tail & ears", "Body & voice")
    challenges = [
        ("Excessive barking (dogs)", "Identify the trigger — boredom, alertness or separation anxiety. Increase exercise and mental stimulation (puzzle toys). Reward quiet behavior immediately with high-value treats rather than yelling."),
        ("Destructive scratching (cats)", "Scratching is natural marking and stretching. Provide vertical and horizontal sisal scratchers near favorite resting spots. Synthetic pheromone sprays (e.g. Feliway) can reduce stress-related scratching."),
        ("Resource guarding (food & toys)", "Never forcibly take guarded items away. Practice trade-up games: offer a higher-value treat from a safe distance whenever you approach, to build positive associations."),
    ]
    acc = "".join(f'<details class="faq-item"{" open" if i == 0 else ""}><summary>{e(t)}{icon("chevron-down")}</summary><div class="faq-answer"><p>{e(d)}</p></div></details>' for i, (t, d) in enumerate(challenges))
    principles = [
        ("Reward promptly", "Mark the right behavior within 1–2 seconds with praise or a treat."),
        ("Ignore or redirect", "Avoid physical punishment or harsh reprimands — they increase anxiety and escalation."),
        ("Keep sessions short", "5 to 10 minutes of consistent daily training beats long sessions."),
        ("Ask a professional", "For severe aggression, fear or sudden behavior changes, see a veterinary behaviorist or certified trainer."),
    ]
    return (_section(1, "Body language quick reference", _tabs(e, "body", [("\U0001F436 Dogs", dogs), ("\U0001F431 Cats", cats)]),
                     "Choose a species, then match what you see to how your pet is feeling.")
            + _section(2, "Common behavioral challenges", f'<div class="faq-list g-acc">{acc}</div>')
            + _section(3, "Core principles of positive reinforcement", _tips(e, principles)))


def nutrition(e, icon):
    schedule = """<div class="g-picker" data-feed>
            <div class="g-seg" role="radiogroup" aria-label="Species">
              <button type="button" role="radio" aria-checked="true" data-sp="dog">\U0001F436 Dog</button>
              <button type="button" role="radio" aria-checked="false" data-sp="cat">\U0001F431 Cat</button>
            </div>
            <div class="g-seg" role="radiogroup" aria-label="Life stage">
              <button type="button" role="radio" aria-checked="true" data-st="young">Puppy / kitten<small>2–6 months</small></button>
              <button type="button" role="radio" aria-checked="false" data-st="adult">Adult<small>1–7 years</small></button>
              <button type="button" role="radio" aria-checked="false" data-st="senior">Senior<small>7+ years</small></button>
            </div>
            <div class="g-feed-out" aria-live="polite"><span class="g-feed-big" data-feed-meals>3–4</span><span data-feed-text>meals daily (puppy formula)</span></div>
          </div>"""
    labels = """<div class="g-cards2">
            <div class="g-card"><h3>Understanding food labels</h3><p>Look for real meat (chicken, salmon, beef) as the first ingredient, and make sure the label meets AAFCO nutritional standards for your pet’s life stage.</p></div>
            <div class="g-card"><h3>Switching foods safely</h3><p>Mix the new food into the current diet gradually over about a week to prevent stomach upset. Pick a start date to get your plan:</p>
              <div class="g-plan" data-transition>
                <label class="g-date"><span>Start date</span><input type="date" data-start></label>
                <ol class="g-plan-list" data-plan></ol>
              </div>
            </div>
          </div>"""
    toxic = [
        ("☕", "Chocolate, coffee & caffeine", "Contain theobromine/caffeine; cause vomiting, heart arrhythmia and seizures."),
        ("\U0001F347", "Grapes & raisins", "Highly toxic to dogs; can trigger acute kidney failure."),
        ("\U0001F9C5", "Onions, garlic & chives", "Damage red blood cells, causing anemia in both dogs and cats."),
        ("\U0001F36C", "Xylitol (artificial sweetener)", "Found in some peanut butter and candy; causes a rapid insulin release that can lead to liver failure."),
    ]
    tox = '<div class="g-toxic">' + "".join(
        f'<div class="g-tox"><span class="g-tox-emoji" aria-hidden="true">{em}</span><div><h3>{e(t)}</h3><p>{e(d)}</p></div></div>' for em, t, d in toxic) + "</div>"
    return (_section(1, "Feeding schedule by life stage", schedule, "Pick your pet and their age to see how often to feed.")
            + _section(2, "Choosing high-quality food", labels)
            + _section(3, "Unsafe & toxic foods — do not feed", tox))


def health(e, icon):
    def vac(core, noncore):
        return (f'<div class="g-cards2"><div class="g-card g-card-core"><span class="g-pill">Core — essential</span><p>{e(core)}</p></div>'
                f'<div class="g-card"><span class="g-pill muted">Non-core — lifestyle-based</span><p>{e(noncore)}</p></div></div>')
    vaccines = _tabs(e, "vac", [
        ("\U0001F436 Dogs", vac("Rabies, DHPP (Distemper, Hepatitis, Parvovirus, Parainfluenza)", "Bordetella (kennel cough), Lyme, Leptospirosis")),
        ("\U0001F431 Cats", vac("Rabies, FVRCP (Rhinotracheitis, Calicivirus, Panleukopenia)", "FeLV (Feline Leukemia Virus)")),
    ])
    prevent = """<div class="g-cards2">
            <div class="g-card"><h3>Flea, tick & heartworm prevention</h3><p>Give monthly oral or topical preventatives year-round. Heartworm is spread by mosquitoes and needs lifelong prevention.</p></div>
            <div class="g-card"><h3>Annual wellness exams</h3><p>Yearly vet visits for adult pets (twice a year for seniors 7+) for fecal tests, dental checks and routine bloodwork.</p></div>
          </div>"""
    signs = ["Difficulty breathing", "Collapse", "Inability to urinate (especially male cats)", "Pale gums",
             "Ate something toxic", "Continuous vomiting for over 24 hours"]
    checks = "\n".join(f'<label class="g-sign"><input type="checkbox"><span class="g-box" aria-hidden="true"></span><span>{e(s)}</span></label>' for s in signs)
    emergency = f"""<div class="g-emergency" data-emergency>
            <p class="g-lead">Seek immediate veterinary emergency care if you notice any of these. Tick what you’re seeing:</p>
            <div class="g-signs">{checks}</div>
            <div class="g-alert" data-alert hidden role="alert"><strong>Contact your vet or an emergency animal hospital now.</strong> Don’t wait to see if it passes.</div>
          </div>"""
    return (_section(1, "Essential vaccinations", vaccines)
            + _section(2, "Routine preventive care", prevent)
            + _section(3, "When to contact a vet urgently", emergency))


def budget(e, icon):
    groups = [
        ("once", "Initial adoption & medical fees", "Usually covers initial vet exams, vaccinations, spay/neuter and microchipping.", [
            ("Shelter adoption fee", "Varies by age, breed and organization"),
            ("Initial health check & vaccines", "Follow-up wellness exam and boosters"),
            ("Microchip registration", "Lifetime registry activation"),
        ]),
        ("once", "Essential startup supplies", "Foundational supplies for safety, comfort and training.", [
            ("Collar, leash & ID tags", "Durable nylon or leather, personalized tags"),
            ("Crate & dog bed", "Sized for adult weight"),
            ("Food & water bowls", "Stainless steel or ceramic"),
            ("Initial toys & chews", "Interactive toys, chew deterrents"),
        ]),
        ("month", "Ongoing monthly expenses", "Consistent monthly costs for health, nutrition and wellbeing.", [
            ("Dog food & treats", "Quality kibble or raw diet, plus training treats"),
            ("Flea, tick & heartworm prevention", "Monthly preventative medication"),
            ("Routine vet care (monthly set-aside)", "Annual checkups, grooming and emergency fund"),
        ]),
    ]
    blocks, n = [], 0
    for gi, (kind, title, lead, items) in enumerate(groups, 1):
        rows = []
        for name, note in items:
            rows.append(f"""<label class="g-money-row">
                <span class="g-money-name"><strong>{e(name)}</strong><small>{e(note)}</small></span>
                <span class="g-money-input"><span>$</span><input type="number" inputmode="decimal" min="0" step="1" placeholder="0" data-cost="{kind}" data-id="b-{n}" aria-label="{e(name)} cost"></span>
              </label>""")
            n += 1
        per = " / month" if kind == "month" else ""
        blocks.append(f"""<div class="g-money-group">
              <h3><span class="g-num">{gi}</span>{e(title)}</h3>
              <p class="g-lead">{e(lead)}</p>
              {''.join(rows)}
              <div class="g-subtotal"><span>Subtotal</span><strong data-subtotal="{gi}">$0{per}</strong></div>
            </div>""")
    return f"""<div class="g-budget" data-budget>
          <div class="g-budget-main">{''.join(blocks)}
            <div class="g-callout"><h3>Financial planning tip</h3><p>Set aside an emergency fund or consider pet insurance to help cover unexpected vet procedures or sudden health issues.</p></div>
          </div>
          <aside class="g-budget-sum" aria-live="polite">
            <h3>Your estimate</h3>
            <div class="g-sum-row"><span>One-time costs</span><strong data-total="once">$0</strong></div>
            <div class="g-sum-row"><span>Monthly costs</span><strong data-total="month">$0</strong></div>
            <div class="g-sum-row big"><span>First-year total</span><strong data-total="year">$0</strong></div>
            <p class="g-sum-note">One-time costs + 12 months of monthly costs. Typical ranges: $500–$1,500+ upfront and $100–$200+ a month.</p>
            <button type="button" class="g-reset" data-reset>Clear all</button>
          </aside>
        </div>"""


BODIES = {
    "pet-owners-essential-guide": essential,
    "dog-readiness-checklist": readiness,
    "first-week-checklist": first_week,
    "pet-behavior-guide": behavior,
    "pet-nutrition-feeding-guide": nutrition,
    "pet-health-guide": health,
    "dog-adoption-budget-breakdown": budget,
}
