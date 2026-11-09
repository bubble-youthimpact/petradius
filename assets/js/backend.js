/*
 * PetRadius — account data layer
 * One API, two engines:
 *   • Firebase (Auth + Firestore) when firebase-config.js is filled in
 *   • Preview mode (localStorage) otherwise, so the site still works offline
 *
 * Firestore layout
 *   users/{uid}                    profile fields + favorites: [petSlug]
 *   users/{uid}/quizResults/{id}   one document per finished quiz
 */
import { firebaseConfig, FIREBASE_SDK_VERSION } from './firebase-config.js';

export const DEMO_EMAIL = 'demo@petradius.com';
export const DEMO_PASSWORD = 'demo1234';
export const isConfigured = Boolean(firebaseConfig && firebaseConfig.apiKey && firebaseConfig.projectId);

const PROFILE_FIELDS = ['displayName', 'location', 'phone', 'bio'];

function pick(obj, keys) {
  const out = {};
  keys.forEach(k => { if (obj[k] !== undefined) out[k] = String(obj[k]).trim().slice(0, k === 'bio' ? 600 : 120); });
  return out;
}

function friendlyError(err) {
  const code = (err && err.code) || '';
  const map = {
    'auth/invalid-email': 'That email address doesn’t look right.',
    'auth/missing-email': 'Please enter your email address.',
    'auth/missing-password': 'Please enter your password.',
    'auth/invalid-credential': 'Email or password is incorrect.',
    'auth/wrong-password': 'Email or password is incorrect.',
    'auth/user-not-found': 'Email or password is incorrect.',
    'auth/email-already-in-use': 'An account with this email already exists. Try logging in.',
    'auth/weak-password': 'Please use a password with at least 6 characters.',
    'auth/too-many-requests': 'Too many attempts. Please wait a moment and try again.',
    'auth/popup-closed-by-user': 'Google sign-in was closed before finishing.',
    'auth/cancelled-popup-request': 'Google sign-in was cancelled.',
    'auth/network-request-failed': 'Network error. Check your connection and try again.',
    'auth/unauthorized-domain': 'This website isn’t authorised for Google sign-in yet (add it under Firebase → Authentication → Settings → Authorized domains).',
    'auth/operation-not-allowed': 'This sign-in method isn’t enabled in Firebase yet.',
    'auth/requires-recent-login': 'Please log out and log back in, then try again.',
    'permission-denied': 'You don’t have permission to do that.'
  };
  return map[code] || (err && err.friendly) || 'Something went wrong. Please try again.';
}

/* ================================================================
   Firebase engine
   ================================================================ */
async function createFirebaseEngine() {
  const base = `https://www.gstatic.com/firebasejs/${FIREBASE_SDK_VERSION}`;
  const [{ initializeApp }, A, F] = await Promise.all([
    import(`${base}/firebase-app.js`),
    import(`${base}/firebase-auth.js`),
    import(`${base}/firebase-firestore.js`)
  ]);

  const app = initializeApp(firebaseConfig);
  const auth = A.getAuth(app);
  const db = F.getFirestore(app);
  const google = new A.GoogleAuthProvider();
  google.setCustomParameters({ prompt: 'select_account' });

  const userRef = uid => F.doc(db, 'users', uid);

  async function ensureUserDoc(user, extra = {}) {
    const ref = userRef(user.uid);
    const snap = await F.getDoc(ref);
    const base = {
      email: user.email || '',
      photoURL: user.photoURL || '',
      lastLoginAt: F.serverTimestamp()
    };
    if (!snap.exists()) {
      await F.setDoc(ref, {
        ...base,
        displayName: extra.displayName || user.displayName || '',
        location: '', phone: '', bio: '',
        favorites: [],
        createdAt: F.serverTimestamp()
      });
    } else {
      await F.setDoc(ref, base, { merge: true });
    }
  }

  const toUser = u => u && ({
    uid: u.uid,
    email: u.email || '',
    displayName: u.displayName || '',
    photoURL: u.photoURL || '',
    provider: (u.providerData[0] && u.providerData[0].providerId) || 'password',
    createdAt: u.metadata && u.metadata.creationTime ? new Date(u.metadata.creationTime) : null
  });

  let current = null;
  const listeners = new Set();
  let resolveReady;
  const readyP = new Promise(r => { resolveReady = r; });

  // Finish a redirect-based Google sign-in if one is pending
  A.getRedirectResult(auth).catch(() => {});

  A.onAuthStateChanged(auth, async u => {
    current = toUser(u);
    if (u) { try { await ensureUserDoc(u); } catch (e) { console.warn('[PetRadius] profile sync failed', e); } }
    resolveReady();
    listeners.forEach(cb => cb(current));
  });

  const need = () => { if (!auth.currentUser) throw { friendly: 'Please log in first.' }; return auth.currentUser; };

  return {
    mode: 'firebase',
    ready: () => readyP,
    current: () => current,
    onChange(cb) { listeners.add(cb); return () => listeners.delete(cb); },

    async signUp(name, email, password) {
      const cred = await A.createUserWithEmailAndPassword(auth, email, password);
      if (name) await A.updateProfile(cred.user, { displayName: name });
      await ensureUserDoc(cred.user, { displayName: name });
      current = toUser(auth.currentUser);
      listeners.forEach(cb => cb(current));
      return current;
    },
    async signIn(email, password) {
      const cred = await A.signInWithEmailAndPassword(auth, email, password);
      return toUser(cred.user);
    },
    async signInGoogle() {
      try {
        const cred = await A.signInWithPopup(auth, google);
        return toUser(cred.user);
      } catch (e) {
        if (e && (e.code === 'auth/popup-blocked' || e.code === 'auth/operation-not-supported-in-this-environment')) {
          await A.signInWithRedirect(auth, google);
          return null;
        }
        throw e;
      }
    },
    signOut: () => A.signOut(auth),
    resetPassword: email => A.sendPasswordResetEmail(auth, email),

    async getProfile() {
      const u = need();
      const snap = await F.getDoc(userRef(u.uid));
      const d = snap.exists() ? snap.data() : {};
      return {
        displayName: d.displayName || u.displayName || '',
        email: u.email || '',
        location: d.location || '', phone: d.phone || '',
        bio: d.bio || '',
        photoURL: d.photoURL || u.photoURL || '',
        createdAt: d.createdAt && d.createdAt.toDate ? d.createdAt.toDate() : toUser(u).createdAt
      };
    },
    async saveProfile(data) {
      const u = need();
      const clean = pick(data, PROFILE_FIELDS);
      await F.setDoc(userRef(u.uid), { ...clean, updatedAt: F.serverTimestamp() }, { merge: true });
      if (clean.displayName !== undefined && clean.displayName !== u.displayName) {
        await A.updateProfile(u, { displayName: clean.displayName });
        current = toUser(auth.currentUser);
        listeners.forEach(cb => cb(current));
      }
    },

    async getFavorites() {
      const u = need();
      const snap = await F.getDoc(userRef(u.uid));
      return (snap.exists() && Array.isArray(snap.data().favorites)) ? snap.data().favorites : [];
    },
    async setFavorite(slug, on) {
      const u = need();
      await F.setDoc(userRef(u.uid), {
        favorites: on ? F.arrayUnion(slug) : F.arrayRemove(slug)
      }, { merge: true });
    },

    async addQuizResult(r) {
      const u = need();
      await F.addDoc(F.collection(db, 'users', u.uid, 'quizResults'), { ...r, takenAt: F.serverTimestamp() });
    },
    async getQuizResults() {
      const u = need();
      const q = F.query(F.collection(db, 'users', u.uid, 'quizResults'), F.orderBy('takenAt', 'desc'), F.limit(50));
      const snap = await F.getDocs(q);
      return snap.docs.map(d => {
        const x = d.data();
        return { id: d.id, ...x, takenAt: x.takenAt && x.takenAt.toDate ? x.takenAt.toDate() : new Date() };
      });
    }
  };
}

/* ================================================================
   Preview engine (localStorage) — for local testing without Firebase
   ================================================================ */
function createPreviewEngine() {
  const mem = {};
  const store = {
    get(k, d) { try { const v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return k in mem ? mem[k] : d; } },
    set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) { mem[k] = v; } }
  };
  const USERS = 'petradius-preview-users';
  const SESSION = 'petradius-preview-session';
  const users = () => store.get(USERS, {});
  const saveUsers = u => store.set(USERS, u);
  const listeners = new Set();
  const delay = (ms = 250) => new Promise(r => setTimeout(r, ms));

  const toUser = rec => rec && ({
    uid: rec.uid, email: rec.email, displayName: rec.displayName, photoURL: rec.photoURL || '',
    provider: rec.provider, createdAt: new Date(rec.createdAt)
  });
  // Seed a demo account so the profile page can be explored without signing up
  (function seedDemo() {
    const all = users();
    if (Object.values(all).some(u => u.email === DEMO_EMAIL)) return;
    const day = 86400000, now = Date.now();
    all.p_demo = {
      uid: 'p_demo', email: DEMO_EMAIL, password: DEMO_PASSWORD, provider: 'password',
      displayName: 'Jamie Park', createdAt: now - 42 * day, photoURL: '',
      location: 'Irvine, CA', phone: '(949) 555-0142',
      bio: 'First-time adopter living in a townhouse with a small fenced yard. I work from home three days a week and love weekend hikes.',
      favorites: ['aj', 'poppy', 'peppa-pug'],
      quizResults: [
        { id: 'd4', quizId: 'breed-match', quizSlug: 'breed-match', quizTitle: 'Which Dog Breed Matches Your Personality?', type: 'personality', score: 0, total: 10, result: 'Golden Retriever', takenAt: now - 2 * day },
        { id: 'd3', quizId: 'readiness', quizSlug: 'are-you-ready', quizTitle: 'Are You Ready for a Dog?', type: 'scored', score: 14, total: 15, result: '14/15 \u00b7 Outstanding', takenAt: now - 5 * day },
        { id: 'd2', quizId: 'pet-care', quizSlug: 'pet-care-knowledge', quizTitle: 'Pet Care Knowledge Quiz', type: 'scored', score: 8, total: 10, result: '8/10 \u00b7 Nice work', takenAt: now - 9 * day },
        { id: 'd1', quizId: 'readiness', quizSlug: 'are-you-ready', quizTitle: 'Are You Ready for a Dog?', type: 'scored', score: 11, total: 15, result: '11/15 \u00b7 Good job', takenAt: now - 30 * day }
      ]
    };
    saveUsers(all);
  })();

  let current = toUser(users()[store.get(SESSION, null)]);
  const emit = () => listeners.forEach(cb => cb(current));
  const err = code => { const e = new Error(code); e.code = code; return e; };
  const rec = () => { if (!current) throw { friendly: 'Please log in first.' }; return users()[current.uid]; };
  const update = fn => { const all = users(); fn(all[current.uid]); saveUsers(all); };
  const validEmail = e => /^\S+@\S+\.\S+$/.test(e || '');

  function login(r) { store.set(SESSION, r.uid); current = toUser(r); emit(); return current; }
  function makeUser(fields) {
    return Object.assign({
      uid: 'p_' + Math.random().toString(36).slice(2, 10), createdAt: Date.now(),
      location: '', phone: '', bio: '', photoURL: '',
      favorites: [], quizResults: []
    }, fields);
  }

  return {
    mode: 'preview',
    ready: () => Promise.resolve(),
    current: () => current,
    onChange(cb) { listeners.add(cb); return () => listeners.delete(cb); },

    async signUp(name, email, password) {
      await delay();
      email = (email || '').trim().toLowerCase();
      if (!validEmail(email)) throw err('auth/invalid-email');
      if (!password || password.length < 6) throw err('auth/weak-password');
      const all = users();
      if (Object.values(all).some(u => u.email === email)) throw err('auth/email-already-in-use');
      const r = makeUser({ email, password, displayName: name || '', provider: 'password' });
      all[r.uid] = r; saveUsers(all);
      return login(r);
    },
    async signIn(email, password) {
      await delay();
      email = (email || '').trim().toLowerCase();
      if (!validEmail(email)) throw err('auth/invalid-email');
      const r = Object.values(users()).find(u => u.email === email && u.provider === 'password');
      if (!r || r.password !== password) throw err('auth/invalid-credential');
      return login(r);
    },
    async signInGoogle() {
      await delay(400);
      const all = users();
      let r = Object.values(all).find(u => u.provider === 'google.com');
      if (!r) {
        r = makeUser({ email: 'preview.user@gmail.com', displayName: 'Preview User', provider: 'google.com' });
        all[r.uid] = r; saveUsers(all);
      }
      return login(r);
    },
    async signOut() { store.set(SESSION, null); current = null; emit(); },
    async resetPassword(email) {
      await delay();
      if (!validEmail(email)) throw err('auth/invalid-email');
    },

    async getProfile() {
      const r = rec();
      return { displayName: r.displayName, email: r.email, location: r.location, phone: r.phone,
        bio: r.bio, photoURL: r.photoURL, createdAt: new Date(r.createdAt) };
    },
    async saveProfile(data) {
      await delay();
      rec();
      const clean = pick(data, PROFILE_FIELDS);
      update(r => Object.assign(r, clean));
      current = toUser(users()[current.uid]); emit();
    },
    async getFavorites() { return (rec().favorites || []).slice(); },
    async setFavorite(slug, on) {
      rec();
      update(r => {
        const s = new Set(r.favorites || []);
        on ? s.add(slug) : s.delete(slug);
        r.favorites = Array.from(s);
      });
    },
    async addQuizResult(result) {
      rec();
      update(r => { (r.quizResults = r.quizResults || []).unshift({ id: String(Date.now()), ...result, takenAt: Date.now() }); r.quizResults = r.quizResults.slice(0, 50); });
    },
    async getQuizResults() {
      return (rec().quizResults || []).map(x => ({ ...x, takenAt: new Date(x.takenAt) }));
    }
  };
}

/* ================================================================ */
let enginePromise;
export function getBackend() {
  if (!enginePromise) {
    enginePromise = (isConfigured ? createFirebaseEngine() : Promise.resolve(createPreviewEngine()))
      .catch(e => {
        console.error('[PetRadius] Firebase failed to load — falling back to preview mode.', e);
        return createPreviewEngine();
      });
  }
  return enginePromise;
}

export { friendlyError };
