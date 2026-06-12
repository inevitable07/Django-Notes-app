/**
 * Clerk Authentication Utilities
 * Handles token management, user state, and authentication helpers
 */

// ════════════════════════════════════════════════════
// State Management
// ════════════════════════════════════════════════════
let clerkUser = null;
let clerkLoaded = false;

// ════════════════════════════════════════════════════
// Initialization
// ════════════════════════════════════════════════════

/**
 * Initialize Clerk and wait for it to be ready
 * @returns {Promise<void>}
 */
async function initializeClerk() {
  return new Promise((resolve) => {
    if (typeof Clerk === 'undefined') {
      console.error('Clerk SDK not loaded');
      resolve();
      return;
    }

    // Wait for Clerk to be ready
    const checkClerk = setInterval(() => {
      if (window.Clerk && window.Clerk.isReady) {
        clearInterval(checkClerk);
        clerkLoaded = true;
        updateUserState();
        resolve();
      }
    }, 100);

    // Timeout after 5 seconds
    setTimeout(() => {
      clearInterval(checkClerk);
      resolve();
    }, 5000);
  });
}

/**
 * Update the clerkUser state from Clerk SDK
 */
function updateUserState() {
  if (!window.Clerk) return;
  clerkUser = window.Clerk.user;
}

// ════════════════════════════════════════════════════
// User State Queries
// ════════════════════════════════════════════════════

/**
 * Check if a user is currently signed in
 * @returns {boolean}
 */
function isUserSignedIn() {
  if (!clerkLoaded || !window.Clerk) return false;
  return window.Clerk.user !== null && window.Clerk.user !== undefined;
}

/**
 * Get the current signed-in user
 * @returns {Object|null}
 */
function getClerkUser() {
  if (!clerkLoaded || !window.Clerk) return null;
  return window.Clerk.user;
}

/**
 * Get the current user's ID
 * @returns {string|null}
 */
function getUserId() {
  const user = getClerkUser();
  return user ? user.id : null;
}

/**
 * Get the current user's primary email
 * @returns {string|null}
 */
function getUserEmail() {
  const user = getClerkUser();
  if (!user || !user.primaryEmailAddress) return null;
  return user.primaryEmailAddress.emailAddress;
}

/**
 * Get the current user's full name
 * @returns {string|null}
 */
function getUserName() {
  const user = getClerkUser();
  if (!user) return null;
  return user.firstName + (user.lastName ? ' ' + user.lastName : '');
}

// ════════════════════════════════════════════════════
// Token Management
// ════════════════════════════════════════════════════

/**
 * Get a valid JWT token for API calls
 * @returns {Promise<string>}
 */
async function getClerkToken() {
  if (!window.Clerk || !window.Clerk.session) {
    throw new Error('User not authenticated');
  }

  try {
    const token = await window.Clerk.session.getToken();
    return token;
  } catch (error) {
    console.error('Failed to get token:', error);
    throw error;
  }
}

// ════════════════════════════════════════════════════
// API Helpers
// ════════════════════════════════════════════════════

/**
 * Make an authenticated fetch request with Clerk token
 * @param {string} url
 * @param {Object} options
 * @returns {Promise<Response>}
 */
async function authenticatedFetch(url, options = {}) {
  try {
    const token = await getClerkToken();

    const headers = {
      ...options.headers,
      'Authorization': `Bearer ${token}`,
    };

    return fetch(url, {
      ...options,
      headers,
    });
  } catch (error) {
    console.error('Authenticated fetch failed:', error);
    throw error;
  }
}

// ════════════════════════════════════════════════════
// Navigation
// ════════════════════════════════════════════════════

/**
 * Redirect to sign-in flow
 */
function redirectToSignIn() {
  if (window.Clerk) {
    window.Clerk.redirectToSignIn();
  }
}

/**
 * Redirect to sign-up flow
 */
function redirectToSignUp() {
  if (window.Clerk) {
    window.Clerk.redirectToSignUp();
  }
}

/**
 * Sign out the current user
 */
async function signOut() {
  if (window.Clerk) {
    await window.Clerk.signOut();
    updateUserState();
  }
}

// ════════════════════════════════════════════════════
// Session Management
// ════════════════════════════════════════════════════

/**
 * Listen for authentication state changes
 * @param {Function} callback - Called with (isSignedIn, user)
 */
function onAuthStateChange(callback) {
  if (!window.Clerk) return;

  // Check initially
  callback(isUserSignedIn(), getClerkUser());

  // Listen for changes
  window.Clerk.addListener(({ user }) => {
    updateUserState();
    callback(isUserSignedIn(), getClerkUser());
  });
}
