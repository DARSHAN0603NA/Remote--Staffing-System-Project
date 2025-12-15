/* =========================================================
   FIREBASE SETUP
========================================================= */
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import {
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  onAuthStateChanged
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

import {
  getFirestore,
  doc,
  setDoc
} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyCbrwCaaQYEFCF1FJto_O3OYi68qTOqGQc",
  authDomain: "beyondmatch-a714f.firebaseapp.com",
  projectId: "beyondmatch-a714f",
  storageBucket: "beyondmatch-a714f.firebasestorage.app",
  messagingSenderId: "16758090560",
  appId: "1:16758090560:web:89f207139970c97592a8a5"
};

const firebaseApp = initializeApp(firebaseConfig);
const auth = getAuth(firebaseApp);
const db = getFirestore(firebaseApp);

/* =========================================================
   BACKEND API CONFIG
========================================================= */
const API_BASE = "https://l46kikh65i.execute-api.eu-north-1.amazonaws.com/prod";
const API_KEY  = "BknqNazYXca23JWFpNXic6dqN8M4ox6XafyKBdUg";

/* =========================================================
   AUTH MODAL STATE
========================================================= */
let authMode = "login";

function openAuth(mode) {
  authMode = mode;
  updateAuth();
  clearAuthMessage();
  document.getElementById("authOverlay").style.display = "block";
  document.getElementById("authCard").style.display = "block";
}

function closeAuth() {
  document.getElementById("authOverlay").style.display = "none";
  document.getElementById("authCard").style.display = "none";
}

function toggleAuth() {
  authMode = authMode === "login" ? "signup" : "login";
  updateAuth();
  clearAuthMessage();
}

function updateAuth() {
  document.getElementById("authTitle").innerText =
    authMode === "login" ? "Login" : "Sign Up";

  document.getElementById("authText").innerText =
    authMode === "login"
      ? "Don’t have an account?"
      : "Already have an account?";
}

/* =========================================================
   AUTH UI HELPERS
========================================================= */
function showAuthMessage(message, type = "error") {
  const box = document.getElementById("authMessage");
  if (!box) return;

  box.textContent = message;
  box.className = `auth-message ${type}`;
}

function clearAuthMessage() {
  const box = document.getElementById("authMessage");
  if (!box) return;

  box.textContent = "";
  box.className = "auth-message";
}

/* =========================================================
   FIREBASE AUTH HANDLER (LOGIN / SIGNUP)
========================================================= */
document.addEventListener("DOMContentLoaded", () => {
  const emailInput = document.querySelector('.auth-card input[type="email"]');
  const passwordInput = document.querySelector('.auth-card input[type="password"]');
  const continueBtn = document.querySelector(".auth-btn");

  if (!continueBtn) return;

  emailInput.addEventListener("input", clearAuthMessage);
  passwordInput.addEventListener("input", clearAuthMessage);

  continueBtn.addEventListener("click", async () => {
    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();

    if (!email || !password) {
      showAuthMessage("Please enter both email and password to continue.");
      return;
    }

    try {
      if (authMode === "signup") {
        const userCred = await createUserWithEmailAndPassword(auth, email, password);

        await setDoc(doc(db, "users", userCred.user.uid), {
          email,
          createdAt: new Date().toISOString()
        });

        showAuthMessage("Account created successfully. Redirecting…", "success");
        setTimeout(() => window.location.href = "index.html", 800);
      } else {
        await signInWithEmailAndPassword(auth, email, password);
        showAuthMessage("Login successful. Redirecting…", "success");
        setTimeout(() => window.location.href = "index.html", 800);
      }
    } catch (err) {
      let msg = "Unable to continue. Please try again.";

      switch (err.code) {
        case "auth/invalid-credential":
          msg = "Incorrect email or password. Please try again.";
          break;
        case "auth/user-not-found":
          msg = "No account found with this email. Please sign up first.";
          break;
        case "auth/email-already-in-use":
          msg = "This email is already registered. Please log in.";
          break;
        case "auth/weak-password":
          msg = "Password must be at least 6 characters long.";
          break;
        case "auth/invalid-email":
          msg = "Please enter a valid email address.";
          break;
      }

      showAuthMessage(msg, "error");
    }
  });
});

/* =========================================================
   AUTO REDIRECT IF LOGGED IN (LANDING PAGE)
========================================================= */
onAuthStateChanged(auth, (user) => {
  if (user && window.location.pathname.includes("landing")) {
    window.location.href = "index.html";
  }
});

/* =========================================================
   API FETCH WRAPPER
========================================================= */
async function apiFetch(path, opts = {}) {
  const url = API_BASE.replace(/\/$/, "") + path;
  const headers = Object.assign(
    { "Content-Type": "application/json", "x-api-key": API_KEY },
    opts.headers || {}
  );

  const res = await fetch(url, Object.assign({ headers }, opts));
  const text = await res.text().catch(() => "");

  try {
    const outer = JSON.parse(text || "{}");
    if (outer && typeof outer.body === "string") {
      return JSON.parse(outer.body);
    }
    return outer;
  } catch {
    return { status: res.status, raw: text };
  }
}

/* =========================================================
   API FUNCTIONS
========================================================= */
async function uploadJD(formData) {
  return apiFetch("/upload-jd", { method: "POST", body: JSON.stringify(formData) });
}

async function uploadCandidate(formData) {
  return apiFetch("/upload-candidate", { method: "POST", body: JSON.stringify(formData) });
}

async function getMatches({ job_id, top_n = 10 } = {}) {
  if (!job_id) throw new Error("job_id required");

  return apiFetch("/get-matches", {
    method: "POST",
    body: JSON.stringify({ job_id, top_n })
  });
}

/* =========================================================
   UI HELPERS
========================================================= */
function showJSON(elSelector, obj) {
  const el = document.querySelector(elSelector);
  if (el) el.textContent = JSON.stringify(obj, null, 2);
}

/* =========================================================
   PAGE-SPECIFIC LOGIC (DASHBOARD FORMS)
========================================================= */
document.addEventListener("DOMContentLoaded", () => {

  const jdForm = document.getElementById("uploadJDForm");
  if (jdForm) {
    jdForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const get = id => document.getElementById(id)?.value;

      const payload = {
        COMPANY_NAME: get("companyName"),
        JOB_TITLE: get("jobTitle"),
        ROLES_AND_RESPONSIBILITIES: get("roles"),
        SOURCE: "frontend"
      };

      const res = await uploadJD(payload);
      if (res?.job_id) {
        localStorage.setItem("job_id", res.job_id);
        alert("JD uploaded successfully");
      }

      showJSON("#uploadJDResult", res);
    });
  }

  const candForm = document.getElementById("uploadCandidateForm");
  if (candForm) {
    candForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const get = id => document.getElementById(id)?.value;

      const payload = {
        FULL_NAME: get("fullName"),
        EMAIL: get("email"),
        RESUME_TEXT: get("resumeText")
      };

      const res = await uploadCandidate(payload);
      showJSON("#uploadCandidateResult", res);
    });
  }
});

/* =========================================================
   EXPOSE FUNCTIONS FOR INLINE HTML
========================================================= */
window.openAuth = openAuth;
window.closeAuth = closeAuth;
window.toggleAuth = toggleAuth;
