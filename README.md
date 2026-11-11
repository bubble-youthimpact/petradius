# PetRadius

Static website for PetRadius — connecting loving families with pets in need of a forever home.

## Structure
Every page lives in its own folder as `index.html`, so URLs are clean (`/about/`, `/pets/aj/`, …).

```
index.html            Home
about/                About / mission / team
pets/                 Pet profiles (searchable)
pets/<slug>/          One page per pet
resources/            Guides, websites, videos
quiz/                 Quiz hub
quiz/<slug>/          are-you-ready, pet-care-knowledge, breed-match
contact/              Contact form (sends through FormSubmit)
login/  signup/       Email + Google sign-in
profile/              Edit profile, favorite pets, quiz history
assets/               CSS, JS, images
scripts/build.py      Regenerates every page from the data at the top of the file
```

## Editing content
**Pets** come from `scripts/data/pets.csv` (export the "Pets" Google Sheet as CSV and replace this file).
**Resources** are listed near the top of `scripts/build.py`. After any change, run:

```
python3 scripts/build.py
```

Pet photos: save a square image as `assets/img/pets/<slug>.webp` (or .jpg/.png), where the slug is the
pet's name in lowercase with dashes (e.g. `mary-celeste`, `harley-and-remi`). Pets without a photo show
a "Photo coming soon" placeholder. Shelter websites and cities are set in `SHELTERS` in `build.py`.

## Editing quizzes
All quiz questions, answers and results live in `assets/js/quizzes.js` — edit that file directly, no rebuild needed.

## Contact form (FormSubmit)
Messages are sent with [FormSubmit](https://formsubmit.co). The form only uses FormSubmit's private
random code, so no inbox address appears in the site's code. Paste that code into `FORMSUBMIT_ID`
near the bottom of `assets/js/main.js`. Until it's set, the form asks visitors to use the public email.

## Accounts (Firebase)
Until Firebase is connected the site runs in **preview mode**: accounts, favorites and quiz
results are stored only in the visitor's browser. To go live:

1. Create a project at https://console.firebase.google.com and add a **Web app**.
2. Copy its config into `assets/js/firebase-config.js`.
3. **Authentication → Sign-in method:** enable **Email/Password** and **Google**.
4. **Authentication → Settings → Authorized domains:** add `your-username.github.io`
   (and any custom domain).
5. **Firestore Database → Create database** (production mode), then paste `firestore.rules`
   into the **Rules** tab and publish.

Data is stored as `users/{uid}` (profile + `favorites` array) and
`users/{uid}/quizResults/{id}` (one document per finished quiz).

## Deploying to GitHub Pages
Push to a repo, then **Settings → Pages → Deploy from a branch → main / (root)**.
All links are relative, so it works on both `username.github.io` and `username.github.io/repo/`.
