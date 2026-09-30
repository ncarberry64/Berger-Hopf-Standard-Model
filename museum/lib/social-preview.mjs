export const museumPublicURL =
  'https://ncarberry64.github.io/Berger-Hopf-Standard-Model/';
export const socialImageFile = 'bhsm-museum-social-2026-09-30.png';
export const freshSharePath = 'visit/2026-09-30/';
export const freshShareURL = `${museumPublicURL}${freshSharePath}`;

// A distinct HTML URL with its own canonical/og:url avoids pointing a new
// Facebook share straight back at the homepage's previously cached object.
// Serve the complete museum, not a redirect; assets resolve at the site root.
export function makeFreshShareHTML(html) {
  return html
    .replace('<head>', `<head><base href="${museumPublicURL}"/>`)
    .replace(
      /<link rel="canonical" href="[^"]*"\s*\/?\s*>/,
      `<link rel="canonical" href="${freshShareURL}"/>`,
    )
    .replace(
      `property="og:url" content="${museumPublicURL}"`,
      `property="og:url" content="${freshShareURL}"`,
    );
}
