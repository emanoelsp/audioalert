"use client"

import { initializeApp, getApps, type FirebaseApp } from "firebase/app"
import { getAuth, type Auth } from "firebase/auth"
import { getFirestore, type Firestore } from "firebase/firestore"

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
}

// Check if Firebase config is valid
export const isFirebaseConfigured = Boolean(
  firebaseConfig.apiKey &&
  firebaseConfig.authDomain &&
  firebaseConfig.projectId &&
  firebaseConfig.appId
)

// Collection names with AudioAlert_ prefix
export const COLLECTIONS = {
  USERS: "AudioAlert_users",
  PLANTS: "AudioAlert_plants",
  NODES: "AudioAlert_nodes",
  ANOMALIES: "AudioAlert_anomalies",
  RECORDINGS: "AudioAlert_recordings",
  SETTINGS: "AudioAlert_settings",
  AUDIT_LOGS: "AudioAlert_audit_logs",
} as const

// Lazy initialization to avoid breaking SSR
let _app: FirebaseApp | null = null
let _auth: Auth | null = null
let _db: Firestore | null = null
let _initError: Error | null = null

function initializeFirebase(): { app: FirebaseApp | null; auth: Auth | null; db: Firestore | null; error: Error | null } {
  if (_initError) {
    return { app: null, auth: null, db: null, error: _initError }
  }
  
  if (_app && _auth && _db) {
    return { app: _app, auth: _auth, db: _db, error: null }
  }
  
  if (!isFirebaseConfigured) {
    return { app: null, auth: null, db: null, error: null }
  }
  
  try {
    _app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0]
    _auth = getAuth(_app)
    _db = getFirestore(_app)
    return { app: _app, auth: _auth, db: _db, error: null }
  } catch (error) {
    _initError = error as Error
    console.error("[v0] Firebase initialization error:", error)
    return { app: null, auth: null, db: null, error: _initError }
  }
}

export function getFirebaseAuth(): Auth | null {
  const { auth } = initializeFirebase()
  return auth
}

export function getFirebaseDb(): Firestore | null {
  const { db } = initializeFirebase()
  return db
}

export function getFirebaseApp(): FirebaseApp | null {
  const { app } = initializeFirebase()
  return app
}

export function getFirebaseError(): Error | null {
  const { error } = initializeFirebase()
  return error
}
