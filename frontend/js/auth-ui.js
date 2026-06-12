/**
 * Authentication UI Components
 * Handles rendering sign-in/sign-up UI and user info
 */

// ════════════════════════════════════════════════════
// Auth Page
// ════════════════════════════════════════════════════

/**
 * Render the authentication page (sign-in/sign-up)
 */
function renderAuthPage() {
  const appContainer = document.getElementById('app-container');
  const authContainer = document.getElementById('auth-container');

  if (!authContainer) return;

  // Hide app container
  appContainer.style.display = 'none';

  // Show Clerk sign-in component
  authContainer.style.display = 'flex';
  authContainer.innerHTML = `
    <div class="auth-card">
      <h2 class="auth-title">Welcome to My Notes</h2>
      <p class="auth-subtitle">Sign in or create an account to get started</p>
      <div id="clerk-sign-in"></div>
    </div>
  `;

  // Mount Clerk sign-in component
  if (window.Clerk) {
    window.Clerk.mountSignIn(document.getElementById('clerk-sign-in'));
  }
}

/**
 * Hide the authentication page
 */
function hideAuthPage() {
  const appContainer = document.getElementById('app-container');
  const authContainer = document.getElementById('auth-container');

  if (authContainer) {
    authContainer.style.display = 'none';
  }
  if (appContainer) {
    appContainer.style.display = 'block';
  }
}

// ════════════════════════════════════════════════════
// User Header
// ════════════════════════════════════════════════════

/**
 * Update the header to show user info and logout button
 */
function updateUserHeader() {
  const headerElement = document.getElementById('app-header');
  if (!headerElement) return;

  const user = getClerkUser();
  if (!user) {
    removeUserInfo();
    return;
  }

  // Find or create user info container
  let userInfoEl = headerElement.querySelector('.user-info');
  if (!userInfoEl) {
    userInfoEl = document.createElement('div');
    userInfoEl.className = 'user-info';
    headerElement.appendChild(userInfoEl);
  }

  const userName = getUserName() || getUserEmail() || 'User';

  userInfoEl.innerHTML = `
    <div class="user-details">
      <span class="user-name">${escapeHtml(userName)}</span>
      <button class="btn-logout" aria-label="Sign out">Sign out</button>
    </div>
  `;

  // Add logout handler
  const logoutBtn = userInfoEl.querySelector('.btn-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', handleLogout);
  }
}

/**
 * Remove user info from header
 */
function removeUserInfo() {
  const userInfoEl = document.querySelector('.user-info');
  if (userInfoEl) {
    userInfoEl.remove();
  }
}

/**
 * Handle logout action
 */
async function handleLogout() {
  try {
    await signOut();
    redirectToSignIn();
  } catch (error) {
    console.error('Logout failed:', error);
    showToast('Logout failed', 'error');
  }
}

// ════════════════════════════════════════════════════
// Auth State Handlers
// ════════════════════════════════════════════════════

/**
 * Handle authentication state changes
 */
function setupAuthStateListener() {
  onAuthStateChange((isSignedIn, user) => {
    if (isSignedIn) {
      hideAuthPage();
      updateUserHeader();
      // Reload notes when user changes
      loadNotes();
    } else {
      renderAuthPage();
      removeUserInfo();
    }
  });
}

/**
 * Ensure user is authenticated or redirect
 */
async function ensureAuthenticated() {
  if (!isUserSignedIn()) {
    renderAuthPage();
    return false;
  }
  return true;
}
