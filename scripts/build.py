#!/usr/bin/env python3
"""
PetRadius static site builder.

Edit the PETS / RESOURCES data below, then run from the repo root:

    python3 scripts/build.py

Every page is written as  <folder>/index.html  so URLs stay clean
(e.g. /about/ instead of /about.html). All links are relative, so the
site works on a GitHub Pages user site (name.github.io) or a project
site (name.github.io/repo/).
"""
import html
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE_NAME = "PetRadius"
EMAIL = "petradius.official@gmail.com"
INSTAGRAM_HANDLE = "petradiusofficial"
INSTAGRAM_URL = "https://www.instagram.com/petradiusofficial/"
TAGLINE = "Connecting loving families with pets in need of a forever home."

# ----------------------------------------------------------------------
# DATA
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# PETS — loaded from scripts/data/pets.csv (export of the "Pets" sheet)
# Photos: put a square image at assets/img/pets/<slug>.webp (or .jpg/.png)
# and it will be used automatically; otherwise a placeholder is shown.
# ----------------------------------------------------------------------
import csv
import re

PETS_CSV = os.path.join(ROOT, "scripts", "data", "pets.csv")

SHELTERS = {
    "irvine animal care center": {"name": "Irvine Animal Care Center", "location": "Irvine, CA",
                                  "url": "https://cityofirvine.gov/irvine-animal-care-center/adopt-pet"},
    "no stray left behind": {"name": "No Stray Left Behind", "location": "Tustin, CA",
                             "url": "https://www.nostrayleftbehind.com/adopt-a-dog.html"},
    "oc animal care": {"name": "OC Animal Care", "location": "Tustin, CA", "url": "https://www.ocpetinfo.com/adopt"},
    "laguna beach": {"name": "Laguna Beach Animal Shelter", "location": "Laguna Beach, CA",
                     "url": "https://www.petfinder.com/member/us/ca/laguna-beach/laguna-beach-animal-shelter-ca25"},
    "la animal services": {"name": "LA Animal Services", "location": "Los Angeles, CA",
                           "url": "https://www.laanimalservices.com/adopt"},
    "pets in need": {"name": "Pets In Need", "location": "Redwood City, CA", "url": "https://www.petsinneed.org"},
    "pasedena humane": {"name": "Pasadena Humane", "location": "Pasadena, CA", "url": "https://pasadenahumane.org"},
    "pasadena humane": {"name": "Pasadena Humane", "location": "Pasadena, CA", "url": "https://pasadenahumane.org"},
}

# Small clean-ups for typos / missing columns in the sheet
BREED_FIXES = {"Skey Terrier": "Skye Terrier", "German Shephard Mix": "German Shepherd Mix",
               "Staffordshire Bull terrier": "Staffordshire Bull Terrier", "Jack Russell Terrier mix": "Jack Russell Terrier Mix",
               "Poodle mix": "Poodle Mix", "Chihuahua / Mixed Breed (Medium)": "Chihuahua / Mixed Breed"}
NAME_OVERRIDES = {
    # Breed, age and gender come from Mimi's story ("10-year-old Pit Bull mix", "her")
    "Mimi": {"breed": "Pit Bull Mix", "age": "Senior", "gender": "Female"},
    # Bonded pair: Remi is female, Harley is male
    "Harley AND Remi": {"name": "Harley & Remi", "gender": "Male & Female"},
}
FEATURED = ["aj", "rollie-pollie", "lili", "poppy"]
EMPTY_NOTES = ("reference: story", "detailed personality story isn")


def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower().replace("&", "and")).strip("-")


def clean(text):
    return re.sub(r"[ \t]+", " ", (text or "").replace("\r", "")).strip()


def parse_medical(text):
    out = {}
    # Labels need a colon ("Medical:") so words like "medical records" aren't split; "Weight 9 lbs" is allowed
    parts = re.split(r"\b(Medical|Meical|Color)\s*:|\b(?:(Weight)\s*:|(Weight)(?=\s+\d))", text or "", flags=re.I)
    parts = [x for x in parts if x is not None]
    for i in range(1, len(parts) - 1, 2):
        key = parts[i].lower().replace("meical", "medical")
        val = clean(parts[i + 1]).strip(" .")
        if val.startswith("(") and val.endswith(")"):
            val = val[1:-1].strip()
        if not val or val.lower().startswith("not listed"):
            continue
        if key == "weight":
            val = re.sub(r"\s*(lbs?|pounds)\b\.?", " lbs", val, flags=re.I).strip()
            val = re.sub(r"(\d)\s*-\s*(\d)", "\\1\u2013\\2", val)
            if re.fullmatch(r"[\d.]+", val):
                val += " lbs"
        out[key] = val[0].upper() + val[1:]
    return out


def find_photo(slug):
    for ext in ("webp", "jpg", "jpeg", "png"):
        if os.path.exists(os.path.join(ROOT, "assets", "img", "pets", f"{slug}.{ext}")):
            return f"assets/img/pets/{slug}.{ext}"
    return None


def load_pets():
    pets, seen = [], set()
    with open(PETS_CSV, newline="", encoding="utf-8-sig") as fh:
        rows = list(csv.reader(fh))
    for row in rows[1:]:
        row = (row + [""] * 11)[:11]
        name, breed, age, gender, story, _img, medical, traits, shelter, hours, _extra = row
        name = clean(name)
        if not name:
            continue
        ov = NAME_OVERRIDES.get(name, {})
        breed = ov.get("breed") or clean(re.sub(r"\s*\n\s*", " ", breed))
        breed = BREED_FIXES.get(breed, breed)
        age = (ov.get("age") or clean(age)).title()
        gender = (ov.get("gender") or clean(gender)).title().replace("And", "&")
        story = (story or "").replace("\r", "").strip()
        traits = clean(traits)
        if traits.lower().startswith(EMPTY_NOTES):
            traits = ""
        if len(traits) > 140:          # long first-person bios live in the traits column
            story = (story + "\n\n" + traits).strip() if story else traits
            traits = ""
        sh = SHELTERS.get(clean(shelter).lower(), {"name": clean(shelter), "location": "", "url": ""})
        pet_type = "Cat" if "shorthair" in breed.lower() else "Dog"
        slug = slugify(ov.get("name", name))
        if slug in seen:
            slug = f"{slug}-{slugify(sh['name'])}"
        seen.add(slug)
        med = parse_medical(medical)
        pets.append({
            "slug": slug, "name": ov.get("name", name), "type": pet_type, "breed": breed or "Mixed breed",
            "age": age, "sex": gender, "location": sh["location"],
            "medical": med.get("medical", ""), "color": med.get("color", ""), "weight": med.get("weight", ""),
            "characteristics": traits, "story": story,
            "shelter": sh["name"], "shelter_location": sh["location"], "shelter_url": sh["url"],
            "hours": clean(hours),
            "photo": find_photo(slug),
            "featured": slug in FEATURED,
        })
    # Pets with photos first, then the rest in sheet order
    pets.sort(key=lambda x: 0 if x["photo"] else 1)
    return pets


def pet_img(pet):
    return pet["photo"] or f"assets/img/pets/placeholder-{pet['type'].lower()}.webp"


PETS = load_pets()

RESOURCES = [
    # (section, title, description, image, url)
    ("guide", "Pet Owner's Essential Guide", "A practical guide to welcoming your new canine companion home",
     "pet-owners-essential-guide", "https://ab749b1020e6b18e17bd6108ef43b12e.cdn.bubble.io/f1785722489065x939737311521714400/Pet_Owners_Essential_Guide.pdf"),
    ("guide", "Is a Dog Right for You? A Comprehensive Readiness Checklist", "A practical self-assessment & readiness checklist for prospective dog owners",
     "dog-readiness-checklist", "https://ab749b1020e6b18e17bd6108ef43b12e.cdn.bubble.io/f1785722494051x827319255128716500/Is%20a%20Dog%20Right%20for%20You_%20A%20Comprehensive%20Readiness%20Checklist.pdf"),
    ("guide", "Pet Behavior Guide", "Understanding your pet’s body language and behavioral cues is essential for building trust, preventing anxiety, and addressing common challenges effectively.",
     "pet-behavior-guide", "https://ab749b1020e6b18e17bd6108ef43b12e.cdn.bubble.io/f1788950237522x459334904184573600/Pet%20Behavior%20Guide.pdf"),
    ("guide", "First Week Checklist", "Bringing a new pet home is a major transition. Use this step-by-step checklist to ensure a safe, calm, and structured setup during your pet's critical first week.",
     "first-week-checklist", "https://ab749b1020e6b18e17bd6108ef43b12e.cdn.bubble.io/f1788950471049x114177018173015070/First%20Week%20Checklist.pdf"),
    ("guide", "Pet Nutrition & Feeding Guide", "Proper diet and feeding habits lay the foundation for your pet's lifelong health and energy. Use this guide to manage feeding schedules and avoid hazardous foods.",
     "pet-nutrition-feeding-guide", "https://ab749b1020e6b18e17bd6108ef43b12e.cdn.bubble.io/f1788950675084x822288546177472900/Pet%20Nutrition%20%26%20Feeding%20Guide.pdf"),
    ("guide", "Pet Health Guide", "Proactive medical care keeps your pet protected against preventable diseases and helps identify health concerns early before they become critical.",
     "pet-health-guide", "https://ab749b1020e6b18e17bd6108ef43b12e.cdn.bubble.io/f1788950763870x926942003721289900/Pet%20Health%20Guide.pdf"),
    ("website", "AAHA Canine Vaccination Guidelines", "These Guidelines empower veterinarians to make the best possible personalized recommendations for their patients by determining which vaccines are essential for each individual dog.",
     "aaha-vaccination-guidelines", "https://www.aaha.org/resources/2022-aaha-canine-vaccination-guidelines/"),
    ("website", "Dog Leash", "Heavy Duty Nylon Webbing, Padded Handle for Comfort, Visible at Night, for Walking & Training",
     "dog-leash", "https://www.amazon.com/dp/B08574XLL8"),
    ("website", "Dog Food", "Development puppy food with DHA for brain and vision development, calcium to build strong bones and teeth, for large dogs",
     "dog-food", "https://www.amazon.com/dp/B002OY0Q9K"),
    ("website", "Dog Bed", "Soothing Raised Rim, Plush Faux Fur, Keeps Its Shape, Machine Washable, Non-Slip Waterproof Base, Dark Grey, Small",
     "dog-bed", "https://www.amazon.com/dp/B0DVH7XXXN"),
    ("website", "How To Groom Your Dog Like a Pro", "A practical guide for dog owners who want to keep their pup looking and feeling great without the salon appointment.",
     "dog-grooming", "https://www.igroomhub.com.au/blog/how-to-groom-a-dog"),
    ("website", "Pet Age Calculator", "Ever wonder how old your dog is in human years?",
     "pet-age-calculator", "https://www.pedigree.com/age-calculator"),
    ("website", "ASPCA Pet Care", "The ASPCA\u2019s pet care hub, with guides for dogs, cats and horses, poison control advice, pet planning and seasonal safety tips.",
     "aspca-pet-care", "https://www.aspca.org/pet-care"),
    ("website", "Humane World Animal Care Resources", "Expert-curated guides from Humane World for Animals on adoption, health, behavior and living humanely alongside pets and wildlife.",
     "humane-world-care-resources", "https://www.humaneworld.org/en/animal-care-resources"),
    ("website", "Best Friends Pet Care Resources", "A free library from Best Friends Animal Society on pet health, training, behavior, adoption and rescue, written by vets and behavior specialists.",
     "best-friends-pet-care", "https://bestfriends.org/pet-care-resources"),
    ("video", "How To Teach Your Dog The Basics", "Training your dog is important, and there are some basics every dog should know. In this video I show you how to train your dog the basic commands.",
     "dog-training-basics", "https://www.youtube.com/watch?v=lUzcA9qa_P8"),
]

# ----------------------------------------------------------------------
# ICONS (inline SVG, lucide-style)
# ----------------------------------------------------------------------
def icon(name, extra=""):
    paths = {
        "arrow-right": '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
        "arrow-left": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
        "chevron-right": '<path d="m9 18 6-6-6-6"/>',
        "chevron-down": '<path d="m6 9 6 6 6-6"/>',
        "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
        "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
        "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
        "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
        "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
        "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V20a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9.5"/>',
        "globe": '<circle cx="12" cy="12" r="10"/><path d="M21.54 15H17a2 2 0 0 0-2 2v4.54"/><path d="M7 3.34V5a3 3 0 0 0 3 3a2 2 0 0 1 2 2c0 1.1.9 2 2 2a2 2 0 0 0 2-2c0-1.1.9-2 2-2h3.17"/><path d="M11 21.95V18a2 2 0 0 0-2-2a2 2 0 0 1-2-2v-1a2 2 0 0 0-2-2H2.05"/>',
        "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4"/><path d="M8 2v4"/><path d="M3 10h18"/>',
        "gender": '<circle cx="10" cy="14" r="5"/><path d="M13.5 10.5 20 4"/><path d="M15 4h5v5"/>',
        "pin": '<path d="M20 10c0 4.99-5.54 10.19-7.4 11.8a1 1 0 0 1-1.2 0C9.54 20.19 4 14.99 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
        "send": '<path d="M14.54 21.69a.5.5 0 0 0 .94-.03l6.5-19a.5.5 0 0 0-.64-.64l-19 6.5a.5.5 0 0 0-.03.94l7.93 3.18a2 2 0 0 1 1.11 1.11z"/><path d="m21.85 2.15-10.94 10.94"/>',
        "clipboard": '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/>',
        "book": '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
        "paw": '<circle cx="11" cy="4" r="2"/><circle cx="18" cy="8" r="2"/><circle cx="20" cy="16" r="2"/><path d="M9 10a5 5 0 0 1 5 5v3.5a3.5 3.5 0 0 1-6.84 1.045Q6.52 17.48 4.46 16.84A3.5 3.5 0 0 1 5.5 10Z"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
        "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',
        "eye": '<path d="M2.06 12.35a1 1 0 0 1 0-.7 10.75 10.75 0 0 1 19.88 0 1 1 0 0 1 0 .7 10.75 10.75 0 0 1-19.88 0"/><circle cx="12" cy="12" r="3"/>',
        "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>',
        "lock": '<rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
        "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>',
        "external": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    }
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"%s>%s</svg>') % (extra, paths[name])

e = html.escape

# ----------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------
NAV = [("about", "About"), ("pets", "Pet Profiles"), ("resources", "Resources"), ("quiz", "Quiz"), ("contact", "Contact")]


def layout(path, title, description, body, active="", extra_head="", extra_scripts="", body_class="", page=""):
    depth = len([p for p in path.split("/") if p])
    p = "../" * depth or "./"

    def nav_items(cls_icon=False):
        out = []
        for slug, label in NAV:
            cur = ' aria-current="page"' if slug == active else ""
            chev = icon("chevron-right") if cls_icon else ""
            out.append(f'<li><a href="{p}{slug}/"{cur}>{label}{chev}</a></li>')
        return "\n          ".join(out)

    full_title = f"{title} | {SITE_NAME}" if title != SITE_NAME else f"{SITE_NAME} — Every Pet Deserves a Loving Home"
    cls = f' class="{body_class}"' if body_class else ""
    cls += f' data-base="{p}"' + (f' data-page="{page}"' if page else "")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(full_title)}</title>
  <meta name="description" content="{e(description)}">
  <meta name="theme-color" content="#ffffff">
  <meta property="og:title" content="{e(full_title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:type" content="website">
  <link rel="icon" href="{p}assets/img/favicon-32.png" type="image/png" sizes="32x32">
  <link rel="icon" href="{p}assets/img/favicon.png" type="image/png" sizes="64x64">
  <link rel="apple-touch-icon" href="{p}assets/img/apple-touch-icon.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300..900;1,300..900&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{p}assets/css/style.css">{extra_head}
</head>
<body{cls}>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{p}" aria-label="{SITE_NAME} home">
        <img src="{p}assets/img/logo.webp" alt="" width="36" height="36">
        <span>{SITE_NAME}</span>
      </a>
      <nav class="main-nav" aria-label="Main">
        <ul>
          {nav_items()}
        </ul>
      </nav>
      <div class="header-actions" data-auth="out">
        <a class="btn btn-outline" href="{p}signup/">Sign Up</a>
        <a class="btn btn-primary" href="{p}login/">Login</a>
      </div>
      <div class="account-menu" data-auth="in" hidden>
        <button class="avatar-btn" type="button" aria-haspopup="true" aria-expanded="false" aria-label="Account menu">
          <span class="avatar" data-user-avatar>{icon('user')}</span>
          <span class="account-name" data-user-first>Account</span>
          {icon('chevron-down')}
        </button>
        <div class="account-dropdown" hidden>
          <div class="account-who"><span class="avatar avatar-sm" data-user-avatar>{icon('user')}</span><span><strong data-user-name>My account</strong><small data-user-email></small></span></div>
          <a href="{p}profile/">{icon('user')}My profile</a>
          <a href="{p}profile/#favorites">{icon('heart')}Favorite pets</a>
          <a href="{p}profile/#quizzes">{icon('clipboard')}Quiz history</a>
          <button type="button" data-signout>{icon('logout')}Log out</button>
        </div>
      </div>
      <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="mobile-menu" aria-label="Open menu">
        <span class="bars"><span></span><span></span><span></span></span>
      </button>
    </div>
  </header>

  <div class="mobile-menu" id="mobile-menu" aria-hidden="true">
    <nav aria-label="Mobile">
      <ul>
          {nav_items(True)}
      </ul>
    </nav>
    <div class="mobile-actions" data-auth="out">
      <a class="btn btn-outline" href="{p}signup/">Sign Up</a>
      <a class="btn btn-primary" href="{p}login/">Login</a>
    </div>
    <div class="mobile-account" data-auth="in" hidden>
      <a class="mobile-account-card" href="{p}profile/">
        <span class="avatar" data-user-avatar>{icon('user')}</span>
        <span><strong data-user-name>My account</strong><small data-user-email></small></span>
        {icon('chevron-right')}
      </a>
      <button class="btn btn-outline btn-block mobile-logout" type="button" data-signout>Log out</button>
    </div>
    <p class="mobile-contact">Questions? <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  </div>

  <main id="main">
{body}
  </main>

  <footer class="site-footer">
    <div class="container">
      <div class="footer-grid">
        <div class="footer-brand">
          <a class="brand" href="{p}">
            <img src="{p}assets/img/logo.webp" alt="" width="36" height="36">
            <span>{SITE_NAME}</span>
          </a>
          <p>{TAGLINE}</p>
        </div>
        <div>
          <h3>Explore</h3>
          <ul>
            {"".join(f'<li><a href="{p}{s}/">{l}</a></li>' for s, l in NAV)}
          </ul>
        </div>
        <div>
          <h3 class="caps">Contact</h3>
          <ul class="footer-contact">
            <li><a href="mailto:{EMAIL}">{icon('mail')}<span>{EMAIL}</span></a></li>
            <li><a href="{INSTAGRAM_URL}" target="_blank" rel="noopener">{icon('instagram')}<span>@{INSTAGRAM_HANDLE}</span></a></li>
          </ul>
        </div>
      </div>
      <p class="copyright">&copy; {SITE_NAME}. All Rights Reserved.</p>
    </div>
  </footer>

  <script src="{p}assets/js/main.js"></script>{extra_scripts}
  <script type="module" src="{p}assets/js/account.js"></script>
</body>
</html>
"""


def pet_card(pet, p):
    search = " ".join([pet["name"], pet["breed"], pet["type"], pet["age"], pet["sex"], pet["characteristics"],
                       pet["shelter"], pet["location"], pet["color"]]).lower()
    meta = " · ".join(x for x in [pet["age"], pet["sex"], pet["location"]] if x)
    return f"""        <div class="pet-card-wrap" data-search="{e(search)}" data-type="{pet['type'].lower()}" data-age="{e(pet['age'].lower())}" data-shelter="{slugify(pet['shelter'])}">
        <a class="pet-card" href="{p}pets/{pet['slug']}/">
          <div class="thumb"><img src="{p}{pet_img(pet)}" alt="{e(pet['name'])}, {e(pet['breed'])}" loading="lazy" width="577" height="577"></div>
          <div class="body">
            <div class="row"><h3>{e(pet['name'])}</h3><span class="tag">{e(pet['type'])}</span></div>
            <p class="breed">{e(pet['breed'])}</p>
            <p class="pet-meta">{e(meta)}</p>
          </div>
        </a>
        <button class="card-fav" type="button" data-fav="{pet['slug']}" data-name="{e(pet['name'])}" aria-pressed="false" aria-label="Save {e(pet['name'])} to favorites">{icon('heart')}</button>
        </div>"""


def write(path, content):
    out = os.path.join(ROOT, path, "index.html") if path else os.path.join(ROOT, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(content)
    print("wrote", os.path.relpath(out, ROOT))


# ----------------------------------------------------------------------
# PAGES
# ----------------------------------------------------------------------
def home():
    p = "./"
    featured = "\n".join(pet_card(x, p) for x in PETS if x.get("featured"))[:]
    body = f"""    <section class="hero" style="background-image:url('assets/img/hero.webp')">
      <div class="container">
        <img class="hero-logo" src="assets/img/logo.webp" alt="" width="44" height="44">
        <h1>Every Pet Deserves a Loving Home</h1>
        <p>Browse pet profiles from local shelters, read their stories, and find your perfect companion.</p>
        <div class="hero-actions">
          <a class="btn btn-primary" href="pets/">Meet our pets {icon('arrow-right')}</a>
          <a class="btn btn-outline-light" href="about/">Learn more</a>
        </div>
      </div>
    </section>

    <section class="stats" aria-label="PetRadius in numbers">
      <div class="container stats-grid">
        <div class="stat">{icon('home')}<strong>12+</strong><span>Partner Shelters</span></div>
        <div class="stat">{icon('heart')}<strong>340+</strong><span>Pets Profiles Listed</span></div>
        <div class="stat">{icon('globe')}<strong>3</strong><span>Countries</span></div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>Featured Pets</h2>
          <p>Meet some of the wonderful animals waiting to meet you.</p>
        </div>
        <div class="pet-grid">
{featured}
        </div>
        <div class="center mt-32">
          <a class="btn btn-ghost" href="pets/">View all pets {icon('arrow-right')}</a>
        </div>
      </div>
    </section>

    <section class="cta">
      <div class="container">
        <h2>Ready to Change a Life?</h2>
        <p>Whether you are looking to adopt, foster, or volunteer, there is a place for you in our community.</p>
        <div class="cta-actions">
          <a class="btn btn-light" href="contact/">Get in touch</a>
          <a class="btn btn-outline-light" href="resources/">Adoption Guide</a>
        </div>
      </div>
    </section>"""
    write("", layout("", SITE_NAME, "Browse pet profiles from local shelters, read their stories, and find your perfect companion.", body))


def about():
    p = "../"
    values = [
        ("heart", "Compassion First", "Every animal deserves dignity, care, and love. We put the wellbeing of pets at the center of everything we do."),
        ("shield", "Trust & Transparency", "We believe in honest communication between shelters and adopters. No hidden details, no surprises."),
        ("users", "Community Driven", "Our platform is built by animal lovers, for animal lovers. Together we create a stronger network of care."),
        ("leaf", "Sustainable Impact", "We work toward reducing shelter overcrowding and promoting responsible, lifelong pet ownership."),
    ]
    cards = "\n".join(f'          <div class="value-card">{icon(i)}<h3>{t}</h3><p>{d}</p></div>' for i, t, d in values)
    body = f"""    <section class="page-hero wide">
      <div class="container">
        <h1>Our Mission</h1>
        <p>PetRadius was born from a simple belief: every pet deserves a loving home, and every home deserves a loving pet. We partner with local shelters to showcase their wonderful animals, share their unique stories, and make the adoption process as warm and welcoming as possible.</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <div class="section-head">
          <h2>What We Stand For</h2>
          <p>The values that guide our work every single day.</p>
        </div>
        <div class="values-grid">
{cards}
        </div>
      </div>
    </section>

    <section class="section band">
      <div class="container">
        <div class="section-head"><h2 style="font-size:clamp(28px,4.4vw,36px)">Our Team</h2></div>
        <article class="team-card">
          <div class="person">
            <img src="{p}assets/img/avatar.webp" alt="Ryan Choi" width="130" height="130" loading="lazy">
            <h3>Ryan Choi</h3>
            <span>Founder &amp; CEO</span>
          </div>
          <p class="bio">Growing up, I always loved animals, so adopting a dog was something my family had always wanted to do. When we decided to adopt our dog from Korea, I realized how difficult and confusing the process could be. Information about shelters, available pets, and adoption requirements was often scattered across different websites, making it hard to find trustworthy and up-to-date information. That experience inspired me to create PetRadius, a website designed to make pet adoption easier by connecting people with shelters and adoptable pets in one place. My goal is to help more animals find loving homes while making the adoption process simpler, faster, and more accessible for families everywhere.</p>
        </article>
      </div>
    </section>"""
    write("about", layout("about", "About", "Our mission: every pet deserves a loving home, and every home deserves a loving pet.", body, active="about"))


def pets_index():
    p = "../"
    cards = "\n".join(pet_card(x, p) for x in PETS)
    ages = [a for a in ["Puppy", "Young", "Adult", "Senior"] if any(x["age"] == a for x in PETS)]
    shelters = sorted({x["shelter"] for x in PETS if x["shelter"]})
    age_opts = "".join(f'<option value="{a.lower()}">{a}</option>' for a in ages)
    sh_opts = "".join(f'<option value="{slugify(n)}">{e(n)}</option>' for n in shelters)
    n_dogs = sum(1 for x in PETS if x["type"] == "Dog")
    n_cats = len(PETS) - n_dogs
    body = f"""    <section class="page-hero">
      <div class="container">
        <h1>Pet Profiles</h1>
        <p>Meet the wonderful animals waiting to find their forever families.</p>
        <form class="search" id="pet-search" role="search">
          <label class="visually-hidden" for="pet-q">Search pets</label>
          <input id="pet-q" type="search" placeholder="Search name, breed or personality" autocomplete="off">
          <button type="submit" aria-label="Search">{icon('search')}</button>
        </form>
      </div>
    </section>

    <section class="section pets-section">
      <div class="container">
        <div class="pet-filters" id="pet-filters">
          <div class="type-chips" role="group" aria-label="Filter by type">
            <button type="button" class="filter-chip" data-type-filter="" aria-pressed="true">All <span>{len(PETS)}</span></button>
            <button type="button" class="filter-chip" data-type-filter="dog" aria-pressed="false">Dogs <span>{n_dogs}</span></button>
            <button type="button" class="filter-chip" data-type-filter="cat" aria-pressed="false">Cats <span>{n_cats}</span></button>
          </div>
          <div class="filter-selects">
            <label class="visually-hidden" for="f-age">Age</label>
            <select id="f-age"><option value="">Any age</option>{age_opts}</select>
            <label class="visually-hidden" for="f-shelter">Shelter</label>
            <select id="f-shelter"><option value="">All shelters</option>{sh_opts}</select>
          </div>
        </div>
        <p class="results-count" id="results-count" aria-live="polite">Showing {len(PETS)} pets</p>
        <div class="pet-grid">
{cards}
        </div>
        <div class="show-more-wrap">
          <button type="button" class="btn btn-ghost show-more" id="show-more" hidden>Show more pets {icon('chevron-down')}</button>
        </div>
        <div class="empty-state" id="no-results" role="status">
          <p>No pets match those filters.</p>
          <button type="button" class="btn btn-ghost" id="clear-filters">Clear filters</button>
        </div>
      </div>
    </section>"""
    write("pets", layout("pets", "Pet Profiles", "Meet the wonderful animals waiting to find their forever families.", body, active="pets"))


def story_html(text):
    paras = [x.strip() for x in re.split(r"\n\s*\n", text or "") if x.strip()]
    return "".join("<p>" + "<br>".join(e(line.strip()) for line in para.split("\n") if line.strip()) + "</p>" for para in paras)


def pet_detail(pet):
    path = f"pets/{pet['slug']}"
    p = "../../"
    chips = []
    if pet["age"]: chips.append(f'<span class="chip">{icon("calendar")}{e(pet["age"])}</span>')
    if pet["sex"]: chips.append(f'<span class="chip">{icon("gender")}{e(pet["sex"])}</span>')
    if pet["location"]: chips.append(f'<span class="chip">{icon("pin")}{e(pet["location"])}</span>')
    chips_html = f'<div class="chips">{"".join(chips)}</div>' if chips else '<div style="height:4px"></div>'

    info = [("Breed", pet["breed"]), ("Medical", pet["medical"]), ("Color", pet["color"]), ("Weight", pet["weight"])]
    info_html = "".join(f"<li><b>{k}:</b> {e(v)}</li>" for k, v in info if v)

    blocks = f'<div class="block"><h2>Medical Information</h2><ul>{info_html}</ul></div>'
    if pet["characteristics"]:
        blocks += f'<div class="block"><h2>Characteristics</h2><p>{e(pet["characteristics"])}</p></div>'
    story = story_html(pet["story"]) or f'<p>Contact {e(pet["shelter"] or "the shelter")} to learn more about {e(pet["name"])}.</p>'
    blocks += f'<div class="block story"><h2>Story</h2>{story}</div>'

    if pet["shelter"]:
        hours = f'<p>{e(pet["hours"])}</p>' if pet["hours"] else ""
        blocks += (f'<div class="shelter-box"><h2>Currently at</h2><p>{e(pet["shelter"])}</p>'
                   f'<p>{e(pet["shelter_location"])}</p>{hours}</div>')
    if pet["shelter_url"]:
        cta = f'<a class="btn btn-primary btn-block" href="{e(pet["shelter_url"])}" target="_blank" rel="noopener">Visit shelter</a>'
    else:
        cta = f'<a class="btn btn-primary btn-block" href="{p}contact/">Ask about {e(pet["name"])}</a>'

    body = f"""    <div class="container">
      <a class="back-link" href="{p}pets/">{icon('arrow-left')}Back to all pets</a>
      <article class="pet-detail">
        <div class="photo{' no-photo' if not pet['photo'] else ''}"><img src="{p}{pet_img(pet)}" alt="{e(pet['name'])}, {e(pet['breed'])}" width="800" height="800"></div>
        <div>
          <span class="tag">{e(pet['type'])}</span>
          <div class="pet-title">
            <h1>{e(pet['name'])}</h1>
            <button class="fav-btn" type="button" data-fav="{pet['slug']}" data-name="{e(pet['name'])}" aria-pressed="false" aria-label="Save {e(pet['name'])} to favorites">{icon('heart')}</button>
          </div>
          {chips_html}
          {blocks}
          {cta}
        </div>
      </article>
    </div>"""
    desc = f"Meet {pet['name']}, a {pet['breed']} at {pet['shelter']} looking for a forever home."
    write(path, layout(path, pet["name"], desc, body, active="pets", body_class="pet-detail-page"))


def resources():
    p = "../"
    sections = [("guide", "Guides"), ("website", "Websites"), ("video", "Videos")]
    out = []
    for key, label in sections:
        cards = []
        for sec, title, desc, img, url in RESOURCES:
            if sec != key:
                continue
            cards.append(f"""          <a class="res-card" href="{e(url)}" target="_blank" rel="noopener">
            <div class="thumb"><img src="{p}assets/img/resources/{img}.webp" alt="" loading="lazy" width="780" height="512"></div>
            <div class="body">
              <h3>{e(title)}</h3>
              <p>{e(desc)}</p>
              <span class="read-more">Read more {icon('arrow-right')}</span>
            </div>
          </a>""")
        out.append(f"""        <section class="res-section" aria-labelledby="res-{key}">
          <h2 id="res-{key}">{label}</h2>
          <div class="res-grid">
{chr(10).join(cards)}
          </div>
        </section>""")
    body = f"""    <section class="page-hero">
      <div class="container">
        <h1>Resources</h1>
        <p>Whether you are a first-time adopter or a seasoned pet parent, our guides help you give your companion the best life possible.</p>
      </div>
    </section>

    <div class="section">
      <div class="container">
{chr(10).join(out)}
      </div>
    </div>"""
    write("resources", layout("resources", "Resources", "Guides, websites and videos to help you give your companion the best life possible.", body, active="resources"))


QUIZZES = [
    {"slug": "are-you-ready", "key": "readiness", "icon": "clipboard", "short": "Dog Readiness",
     "title": "Are You Ready for a Dog?",
     "intro": "Are you ready for a dog? Let\u2019s find out",
     "blurb": "Test whether you\u2019re prepared for the time, money and care that come with owning a dog.",
     "meta": "15 questions \u00b7 about 3 min"},
    {"slug": "pet-care-knowledge", "key": "pet-care", "icon": "book", "short": "Pet Care Knowledge",
     "title": "Pet Care Knowledge Quiz",
     "intro": "How much do you know about keeping pets healthy and happy?",
     "blurb": "Exercise, nutrition, vaccines, dental care and body language \u2014 see how your pet-care knowledge stacks up.",
     "meta": "10 questions \u00b7 about 2 min"},
    {"slug": "breed-match", "key": "breed-match", "icon": "paw", "short": "Breed Match",
     "title": "Which Dog Breed Matches Your Personality?",
     "intro": "Choose the answer that sounds most like you \u2014 we\u2019ll tally up your match.",
     "blurb": "A just-for-fun personality quiz that pairs you with a breed that shares your energy and style.",
     "meta": "10 questions \u00b7 just for fun"},
]


def quiz_hub():
    p = "../"
    tiles = "\n".join(f"""          <a class="quiz-tile" href="{q['slug']}/">
            <span class="tile-icon">{icon(q['icon'])}</span>
            <div class="tile-body">
              <span class="meta">{e(q['meta'])}</span>
              <h2>{e(q['title'])}</h2>
              <p>{e(q['blurb'])}</p>
            </div>
            <span class="tile-cta">Start quiz {icon('arrow-right')}</span>
          </a>""" for q in QUIZZES)
    body = f"""    <section class="page-hero">
      <div class="container">
        <h1>Quiz</h1>
        <p>Are you ready for a dog? Test your pet-care knowledge or find the breed that matches your personality.</p>
      </div>
    </section>

    <section class="quiz-section">
      <div class="container">
        <div class="quiz-hub">
{tiles}
        </div>
      </div>
    </section>"""
    write("quiz", layout("quiz", "Quiz", "Three PetRadius quizzes: dog readiness, pet care knowledge, and which breed matches your personality.", body,
                         active="quiz", extra_head=f'\n  <link rel="stylesheet" href="{p}assets/css/quiz.css">'))


def quiz_page(q):
    path = f"quiz/{q['slug']}"
    p = "../../"
    body = f"""    <section class="page-hero compact">
      <div class="container">
        <h1>{e(q['title'])}</h1>
        <p>{e(q['intro'])}</p>
      </div>
    </section>

    <section class="quiz-section has-back">
      <div class="container">
        <div class="quiz-wrap quiz-back"><a class="back-link" href="{p}quiz/">{icon('arrow-left')}All quizzes</a></div>
        <div id="petradius-quiz-widget" data-quiz="{q['key']}" data-slug="{q['slug']}" data-title="{e(q['title'])}" data-base="{p}">
          <div class="quiz-card" id="quizCard">
            <div class="progress-bar-container"><div class="progress-bar" id="progressBar"></div></div>
            <div class="question-counter" id="questionCounter" aria-live="polite">Question 1</div>
            <div class="question-title" id="questionTitle" tabindex="-1">Loading question...</div>
            <div class="options-list" id="optionsList"></div>
            <div class="quiz-footer">
              <button class="next-btn" id="nextBtn" type="button">Next Question</button>
            </div>
            <noscript><p>Please turn on JavaScript to take this quiz.</p></noscript>
          </div>
          <div class="quiz-card results-container" id="resultsContainer" tabindex="-1" aria-live="polite">
            <h2>Quiz Complete! \U0001F389</h2>
            <div class="results-score" id="resultsScore"></div>
            <p class="results-message" id="resultsMessage"></p>
            <div id="resultsExtra"></div>
            <p class="results-saved" id="resultsSaved" aria-live="polite"></p>
            <div class="quiz-actions">
              <button class="btn-solid" id="restartBtn" type="button">Retake Quiz</button>
              <a class="btn-link" href="{p}quiz/">Try another quiz</a>
            </div>
          </div>
        </div>
      </div>
    </section>"""
    write(path, layout(path, q["title"], q["blurb"], body, active="quiz",
                       extra_head=f'\n  <link rel="stylesheet" href="{p}assets/css/quiz.css">',
                       extra_scripts=f'\n  <script src="{p}assets/js/quizzes.js"></script>\n  <script src="{p}assets/js/quiz.js"></script>'))


def contact():
    body = f"""    <section class="page-hero">
      <div class="container">
        <h1>Contact</h1>
        <p>Have questions about a pet, want to volunteer, or just want to say hello? We would love to hear from you.</p>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <form class="form-card" id="contact-form" data-public-email="{EMAIL}" novalidate>
          <h2>Send a message</h2>
          <div class="form-grid">
            <div class="field"><label for="c-name">Name</label><input id="c-name" name="name" type="text" autocomplete="name" required></div>
            <div class="field"><label for="c-email">Email</label><input id="c-email" name="email" type="email" autocomplete="email" required></div>
            <div class="field full"><label for="c-subject">Subject</label><input id="c-subject" name="subject" type="text" required></div>
            <div class="field full"><label for="c-message">Message</label><textarea id="c-message" name="message" rows="5" required></textarea></div>
            <input type="text" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true" class="visually-hidden">
          </div>
          <button class="btn btn-primary btn-block" type="submit">Send message {icon('send')}</button>
          <p class="form-note" id="contact-note" role="status"></p>
          <p class="form-alt">Or email us at <a href="mailto:{EMAIL}">{EMAIL}</a></p>
        </form>
      </div>
    </section>"""
    write("contact", layout("contact", "Contact", "Questions about a pet, volunteering, or just want to say hello? Get in touch with PetRadius.", body, active="contact"))


GOOGLE_G = ('<svg viewBox="0 0 48 48" aria-hidden="true" width="18" height="18">'
            '<path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/>'
            '<path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>'
            '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/>'
            '<path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.4-.4-3.5z"/></svg>')

PREVIEW_NOTE = ('<p class="preview-note" data-preview-note hidden>'
                '<strong>Preview mode.</strong> Firebase isn’t connected yet, so accounts are saved only in this browser.</p>')


def auth(kind):
    p = "../"
    is_login = kind == "login"
    title = "Login" if is_login else "Sign Up"
    if is_login:
        heading, sub = "Welcome back", "Log in to your PetRadius account."
        fields = f"""
            <div class="field"><label for="a-email">Email</label>
              <div class="input-icon">{icon('mail')}<input id="a-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required></div></div>
            <div class="field">
              <div class="label-row"><label for="a-pass">Password</label><button class="link-btn" id="forgot-btn" type="button">Forgot password?</button></div>
              <div class="input-icon has-toggle">{icon('lock')}<input id="a-pass" name="password" type="password" autocomplete="current-password" placeholder="Your password" required>
                <button class="pw-toggle" type="button" aria-label="Show password" aria-pressed="false">{icon('eye')}</button></div></div>"""
        alt = f'New to PetRadius? <a href="{p}signup/">Create an account</a>'
        legal = ""
        demo = ('\n            <div class="demo-box" data-preview-note hidden>'
                '<div><strong>Demo account</strong><span>demo@petradius.com &middot; demo1234</span></div>'
                '<button class="btn btn-outline" id="demo-btn" type="button">Use demo account</button></div>')
    else:
        demo = ""
        heading, sub = "Create your account", "Join PetRadius to save pets and track your quizzes."
        fields = f"""
            <div class="field"><label for="a-name">Full name</label>
              <div class="input-icon">{icon('user')}<input id="a-name" name="name" type="text" autocomplete="name" placeholder="Your name" required></div></div>
            <div class="field"><label for="a-email">Email</label>
              <div class="input-icon">{icon('mail')}<input id="a-email" name="email" type="email" autocomplete="email" placeholder="you@example.com" required></div></div>
            <div class="field"><label for="a-pass">Password</label>
              <div class="input-icon has-toggle">{icon('lock')}<input id="a-pass" name="password" type="password" autocomplete="new-password" placeholder="At least 6 characters" minlength="6" required>
                <button class="pw-toggle" type="button" aria-label="Show password" aria-pressed="false">{icon('eye')}</button></div></div>"""
        alt = f'Already have an account? <a href="{p}login/">Log in</a>'
        legal = '<p class="auth-legal">By creating an account you agree to use PetRadius responsibly and kindly.</p>'

    body = f"""    <section class="auth-page">
      <div class="container">
        <div class="auth-shell">
          <div class="auth-panel">
            <img class="auth-logo" src="{p}assets/img/logo.webp" alt="" width="52" height="52">
            <h1>{heading}</h1>
            <p class="auth-sub">{sub}</p>
            {PREVIEW_NOTE}{demo}
            <button class="btn-google" id="google-btn" type="button">{GOOGLE_G}<span>Continue with Google</span></button>
            <div class="auth-divider"><span>or</span></div>
            <form id="auth-form" class="auth-form" novalidate>{fields}
              <button class="btn btn-primary btn-block" type="submit">{title}</button>
              <p class="form-note" id="auth-note" role="status"></p>
            </form>
            {legal}
            <p class="form-alt">{alt}</p>
          </div>
        </div>
      </div>
    </section>"""
    write(kind, layout(kind, title, f"{title} to PetRadius to save favorite pets and track your quiz results.", body, page=kind))


def profile():
    p = "../"
    body = f"""    <section class="section profile-gate" id="profile-gate">
      <div class="container">
        <div class="gate-card">
          <span class="gate-icon">{icon('user')}</span>
          <h1>Your PetRadius profile</h1>
          <p>Log in to edit your details, see your favorite pets and review your quiz results.</p>
          <div class="gate-actions">
            <a class="btn btn-primary" id="gate-login" href="{p}login/">Log in</a>
            <a class="btn btn-outline" href="{p}signup/">Create an account</a>
          </div>
        </div>
      </div>
    </section>

    <div id="profile-app" hidden>
      <section class="profile-hero">
        <div class="container profile-head">
          <span class="avatar avatar-xl" id="pf-avatar">{icon('user')}</span>
          <div class="profile-id">
            <h1 id="pf-name">Welcome!</h1>
            <p id="pf-email"></p>
            <div class="profile-chips"><span class="chip" id="pf-provider"></span><span class="chip" id="pf-since"></span></div>
          </div>
          <button class="btn btn-ghost profile-signout" type="button" data-signout>{icon('logout')}Log out</button>
        </div>
      </section>

      <section class="profile-body">
        <div class="container">
          {PREVIEW_NOTE}
          <div class="tabs" role="tablist" aria-label="Profile sections">
            <button class="tab" role="tab" id="t-info" aria-controls="tab-info" data-tab="info" aria-selected="true">Profile</button>
            <button class="tab" role="tab" id="t-favorites" aria-controls="tab-favorites" data-tab="favorites" aria-selected="false" tabindex="-1">Favorites <span class="count" data-count="favorites">0</span></button>
            <button class="tab" role="tab" id="t-quizzes" aria-controls="tab-quizzes" data-tab="quizzes" aria-selected="false" tabindex="-1">Quiz history <span class="count" data-count="quizzes">0</span></button>
          </div>

          <div class="tab-panel" id="tab-info" role="tabpanel" aria-labelledby="t-info">
            <form class="profile-card" id="profile-form" novalidate>
              <div class="profile-card-head"><h2>Basic info</h2><p>This helps shelters get to know you when you reach out about a pet.</p></div>
              <div class="form-grid">
                <div class="field"><label for="pf-displayName">Full name</label><input id="pf-displayName" name="displayName" type="text" autocomplete="name" maxlength="120" required></div>
                <div class="field"><label for="pf-email-input">Email</label><input id="pf-email-input" name="email" type="email" readonly aria-describedby="email-hint"><small class="hint" id="email-hint">Your sign-in email can’t be changed here.</small></div>
                <div class="field"><label for="pf-location">Location</label><input id="pf-location" name="location" type="text" autocomplete="address-level2" placeholder="City, State" maxlength="120"></div>
                <div class="field"><label for="pf-phone">Phone <span class="optional">(optional)</span></label><input id="pf-phone" name="phone" type="tel" autocomplete="tel" maxlength="40"></div>
                <div class="field full"><label for="pf-bio">About me</label><textarea id="pf-bio" name="bio" rows="4" maxlength="600" placeholder="Your home, schedule, experience with pets…"></textarea><small class="hint"><span id="bio-count">0</span>/600</small></div>
              </div>
              <div class="pw-row" id="pw-row"><div><strong>Password</strong><span>We’ll email you a secure link to change it.</span></div><button class="btn btn-ghost" id="pf-reset" type="button">Change password</button></div>
              <div class="profile-actions">
                <p class="form-note" id="profile-note" role="status"></p>
                <button class="btn btn-primary" type="submit">Save changes</button>
              </div>
            </form>
          </div>

          <div class="tab-panel" id="tab-favorites" role="tabpanel" aria-labelledby="t-favorites" hidden>
            <div class="pet-grid" id="fav-grid"></div>
            <div class="empty-card" id="fav-empty" hidden>
              <span class="gate-icon">{icon('heart')}</span>
              <h2>No favorites yet</h2>
              <p>Tap the heart on any pet to save them here.</p>
              <a class="btn btn-primary" href="{p}pets/">Browse pets</a>
            </div>
          </div>

          <div class="tab-panel" id="tab-quizzes" role="tabpanel" aria-labelledby="t-quizzes" hidden>
            <div class="summary-grid" id="quiz-summary"></div>
            <h2 class="panel-title">History</h2>
            <ul class="history-list" id="quiz-list"></ul>
            <div class="empty-card" id="quiz-empty" hidden>
              <span class="gate-icon">{icon('clipboard')}</span>
              <h2>No quiz results yet</h2>
              <p>Finish a quiz while logged in and your results will appear here.</p>
              <a class="btn btn-primary" href="{p}quiz/">Take a quiz</a>
            </div>
          </div>
        </div>
      </section>
    </div>"""
    write("profile", layout("profile", "My Profile", "Your PetRadius profile, favorite pets and quiz history.", body, page="profile"))


def site_data():
    import json
    pets = [{"slug": x["slug"], "name": x["name"], "breed": x["breed"], "type": x["type"], "img": pet_img(x),
             "meta": " \u00b7 ".join(v for v in [x["age"], x["sex"], x["location"]] if v)} for x in PETS]
    quizzes = []
    for q in QUIZZES:
        quizzes.append({"key": q["key"], "slug": q["slug"], "title": q["title"], "short": q["short"],
                        "type": "personality" if q["key"] == "breed-match" else "scored",
                        "total": 15 if q["key"] == "readiness" else 10})
    out = os.path.join(ROOT, "assets", "js", "site-data.js")
    with open(out, "w", encoding="utf-8") as f:
        f.write("/* Generated by scripts/build.py — do not edit by hand. */\n")
        f.write("export const PETS = " + json.dumps(pets, ensure_ascii=False, indent=2) + ";\n")
        f.write("export const QUIZ_META = " + json.dumps(quizzes, ensure_ascii=False, indent=2) + ";\n")
    print("wrote assets/js/site-data.js")


if __name__ == "__main__":
    home()
    about()
    pets_index()
    for pet in PETS:
        pet_detail(pet)
    resources()
    quiz_hub()
    for q in QUIZZES:
        quiz_page(q)
    contact()
    auth("login")
    auth("signup")
    profile()
    site_data()
