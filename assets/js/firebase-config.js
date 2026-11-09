/*
 * PetRadius — Firebase settings
 * ------------------------------------------------------------
 * 1. Firebase console → Project settings → General → Your apps → Web app
 * 2. Copy the values from "firebaseConfig" into the object below.
 *
 * These values are safe to commit: they identify your project but do not
 * grant access. Access is controlled by Authentication + firestore.rules.
 *
 * If apiKey is empty (or Firebase can't load) the site runs in PREVIEW MODE: accounts, favourites
 * and quiz results are stored only in the visitor's browser (localStorage).
 */
export const firebaseConfig = {
  apiKey: "AIzaSyBguKMt0DmkoCW8U9U-nZUeCu9ZtkJ89zs",
  authDomain: "petradius-1ba0a.firebaseapp.com",
  projectId: "petradius-1ba0a",
  storageBucket: "petradius-1ba0a.firebasestorage.app",
  messagingSenderId: "68800192802",
  appId: "1:68800192802:web:ad03ca8906fd8b215e857b"
};

// Firebase JS SDK version loaded from Google's CDN.
export const FIREBASE_SDK_VERSION = "12.19.0";
