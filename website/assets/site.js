'use strict';
// Local release metadata; no analytics or connection to visitors' desktop apps.
fetch('downloads/release.json', {cache: 'no-cache'})
  .then(response => { if (!response.ok) throw new Error('Release information unavailable'); return response.json(); })
  .then(release => {
    if (!/^\d+\.\d+\.\d+$/.test(release.version)) return;
    const button = document.getElementById('download-button');
    const expected = `DoItForMeDash_Setup_${release.version}.exe`;
    if (release.filename !== expected) return;
    button.href = `downloads/${expected}`;
    const size = Number.isFinite(release.bytes) && release.bytes > 0 ? ` · ${(release.bytes / 1048576).toFixed(1)} MB` : '';
    document.getElementById('release-details').textContent = `Version ${release.version}${size} · Windows 10 / 11, 64-bit`;
    if (release.signed === true) document.getElementById('signing-note').hidden = true;
  })
  .catch(() => { /* Keep the versioned, build-time download link available. */ });
