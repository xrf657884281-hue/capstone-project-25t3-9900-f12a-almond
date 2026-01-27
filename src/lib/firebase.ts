import { initializeApp, getApps, getApp } from "firebase/app";
import {
  getAuth,
  GoogleAuthProvider,
  GithubAuthProvider,
} from "firebase/auth";

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "dummy-key",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "dummy-project.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "dummy-project",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "dummy-app-id",
};

// Only initialize Firebase if API key is provided
let app;
let auth;
let googleProvider;
let githubProvider;

try {
  if (import.meta.env.VITE_FIREBASE_API_KEY && import.meta.env.VITE_FIREBASE_API_KEY !== "dummy-key") {
    app = getApps().length ? getApp() : initializeApp(firebaseConfig);
    auth = getAuth(app);
    googleProvider = new GoogleAuthProvider();
    githubProvider = new GithubAuthProvider();
  } else {
    // Create dummy auth object to prevent errors
    console.warn("Firebase API key not configured. OAuth login will not work.");
    auth = null as any;
    googleProvider = null as any;
    githubProvider = null as any;
  }
} catch (error) {
  console.error("Firebase initialization failed:", error);
  auth = null as any;
  googleProvider = null as any;
  githubProvider = null as any;
}

export { auth, googleProvider, githubProvider };
