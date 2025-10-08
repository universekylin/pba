// src/utils/check.js
export function startVersionChecker() {
  function checkForUpdate() {
    fetch('/version.json', { cache: 'no-store' })
      .then(res => res.json())
      .then(remote => {
        const current = window.__appVersion;
        if (!current) {
          // Record the current version on first load
          window.__appVersion = remote.version;
        } else if (current !== remote.version) {
          console.log('New version detected, reloading...');
          // Force reload to get the latest assets
          location.reload(true);
        }
      })
      .catch(err => console.error('Version check failed:', err));
  }

  // Run once on page load
  checkForUpdate();
  // Run every 1 minute
  setInterval(checkForUpdate, 60 * 1000);
}
