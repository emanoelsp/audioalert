"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import {
  onAuthStateChanged,
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
  signOut,
  sendPasswordResetEmail,
  updateProfile,
  updatePassword,
  EmailAuthProvider,
  reauthenticateWithCredential,
  type User,
} from "firebase/auth"
import { doc, setDoc, getDoc, updateDoc, serverTimestamp } from "firebase/firestore"
import { getFirebaseAuth, getFirebaseDb, getFirebaseError, isFirebaseConfigured, COLLECTIONS } from "@/lib/firebase"

interface UserData {
  uid: string
  email: string | null
  displayName: string | null
  photoURL: string | null
  phone: string | null
  company: string | null
  role: "admin" | "operator" | "viewer"
  plantAccess: string[]
  createdAt: Date
  updatedAt?: Date
}

interface AuthContextType {
  user: User | null
  userData: UserData | null
  loading: boolean
  isConfigured: boolean
  configError: Error | null
  signIn: (email: string, password: string) => Promise<void>
  signUp: (email: string, password: string, displayName: string) => Promise<void>
  logout: () => Promise<void>
  resetPassword: (email: string) => Promise<void>
  updateUserProfile: (data: { displayName?: string; phone?: string; company?: string }) => Promise<void>
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [userData, setUserData] = useState<UserData | null>(null)
  const [loading, setLoading] = useState(true)
  const [configError, setConfigError] = useState<Error | null>(null)

  useEffect(() => {
    const auth = getFirebaseAuth()
    const error = getFirebaseError()
    
    if (error) {
      setConfigError(error)
      setLoading(false)
      return
    }
    
    if (!isFirebaseConfigured || !auth) {
      setLoading(false)
      return
    }

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser)
      
      const db = getFirebaseDb()
      if (firebaseUser && db) {
        try {
          const userDocRef = doc(db, COLLECTIONS.USERS, firebaseUser.uid)
          const userDoc = await getDoc(userDocRef)
          
          if (userDoc.exists()) {
            setUserData(userDoc.data() as UserData)
          }
        } catch (error) {
          console.error("[v0] Error fetching user data:", error)
        }
      } else {
        setUserData(null)
      }
      
      setLoading(false)
    })

    return () => unsubscribe()
  }, [])

  const signIn = async (email: string, password: string) => {
    const auth = getFirebaseAuth()
    if (!auth) throw new Error("Firebase nao configurado")
    await signInWithEmailAndPassword(auth, email, password)
  }

  const signUp = async (email: string, password: string, displayName: string) => {
    const auth = getFirebaseAuth()
    const db = getFirebaseDb()
    if (!auth || !db) throw new Error("Firebase nao configurado")
    
    const userCredential = await createUserWithEmailAndPassword(auth, email, password)
    
    await updateProfile(userCredential.user, { displayName })
    
    const userDocRef = doc(db, COLLECTIONS.USERS, userCredential.user.uid)
    await setDoc(userDocRef, {
      uid: userCredential.user.uid,
      email,
      displayName,
      photoURL: null,
      phone: null,
      company: null,
      role: "viewer",
      plantAccess: [],
      createdAt: serverTimestamp(),
    })
  }

  const logout = async () => {
    const auth = getFirebaseAuth()
    if (!auth) throw new Error("Firebase nao configurado")
    await signOut(auth)
  }

  const resetPassword = async (email: string) => {
    const auth = getFirebaseAuth()
    if (!auth) throw new Error("Firebase nao configurado")
    await sendPasswordResetEmail(auth, email)
  }

  const updateUserProfile = async (data: { displayName?: string; phone?: string; company?: string }) => {
    const auth = getFirebaseAuth()
    const db = getFirebaseDb()
    if (!auth || !db || !user) throw new Error("Usuario nao autenticado")
    
    if (data.displayName) {
      await updateProfile(user, { displayName: data.displayName })
    }
    
    const userDocRef = doc(db, COLLECTIONS.USERS, user.uid)
    await updateDoc(userDocRef, {
      ...data,
      updatedAt: serverTimestamp(),
    })
    
    // Refresh user data
    const userDoc = await getDoc(userDocRef)
    if (userDoc.exists()) {
      setUserData(userDoc.data() as UserData)
    }
  }

  const changePassword = async (currentPassword: string, newPassword: string) => {
    const auth = getFirebaseAuth()
    if (!auth || !user || !user.email) throw new Error("Usuario nao autenticado")
    
    const credential = EmailAuthProvider.credential(user.email, currentPassword)
    await reauthenticateWithCredential(user, credential)
    await updatePassword(user, newPassword)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        userData,
        loading,
        isConfigured: isFirebaseConfigured,
        configError,
        signIn,
        signUp,
        logout,
        resetPassword,
        updateUserProfile,
        changePassword,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
