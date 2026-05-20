// ================= CONFIG =================
// Define your base address just once
const API_BASE_URL = "https://medicosync-backend.onrender.com";

// ================= UI TOGGLE =================
const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container   = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => container.classList.add("sign-up-mode"));
sign_in_btn.addEventListener("click", () => container.classList.remove("sign-up-mode"));

// ================= TOKEN (UPDATED TO PRODUCTION STANDARD) =================
const token = {
    set : (t)  => localStorage.setItem("access_token", t),
    get : ()   => localStorage.getItem("access_token"),
    clear: ()  => localStorage.removeItem("access_token"),
};

// ================= UI FEEDBACK =================
function showError(formId, message) {
    const existing = document.querySelector(`#${formId} .error-msg`);
    if (existing) existing.remove();

    const el = document.createElement("p");
    el.className = "error-msg";
    el.style.cssText = "color:red; font-size:0.85rem; margin-top:8px;";
    el.textContent = message;
    document.querySelector(`#${formId}`).appendChild(el);
}

function clearError(formId) {
    const existing = document.querySelector(`#${formId} .error-msg`);
    if (existing) existing.remove();
}

// ================= LOGIN =================
document.querySelector("#login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError("login-form");

    const email    = document.querySelector("#login-email").value.trim();
    const password = document.querySelector("#login-password").value;

    try {
        // FIXED: Added /api prefix
        const res  = await fetch(`${API_BASE_URL}/api/auth/login`, {
            method  : "POST",
            headers : { "Content-Type": "application/json" },
            body    : JSON.stringify({ email, password }),
        });

        const data = await res.json();

        if (!res.ok) {
            showError("login-form", data.detail || "Login failed");
            return;
        }

        // Save token to 'access_token' via the helper abstraction
        token.set(data.access_token);

        // FIXED: Redirects directly to Netlify's dashboard.html file
        window.location.href = "/dashboard.html";

    } catch (err) {
        console.error(err);
        showError("login-form", "Cannot reach server. Is it running?");
    }
});

// ================= SIGNUP =================
document.querySelector("#signup-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError("signup-form");

    const full_name = document.querySelector("#signup-fullname").value.trim();
    const email     = document.querySelector("#signup-email").value.trim();
    const password  = document.querySelector("#signup-password").value;

    try {
        // FIXED: Added /api prefix
        const res  = await fetch(`${API_BASE_URL}/api/auth/register`, {
            method  : "POST",
            headers : { "Content-Type": "application/json" },
            body    : JSON.stringify({ full_name, email, password }),
        });

        const data = await res.json();

        if (!res.ok) {
            showError("signup-form", data.detail || "Signup failed");
            return;
        }

        container.classList.remove("sign-up-mode");
        showError("login-form", "✅ Account created. Please sign in.");

    } catch (err) {
        console.error(err);
        showError("signup-form", "Cannot reach server. Is it running?");
    }
});

// ================= LOGOUT (FIXED FALLBACK) =================
function logout() {
    token.clear();
    // FIXED: Bounces safely back to Netlify's index landing page layout
    window.location.href = "/index.html";
}
