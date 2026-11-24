# DoItForMe Dash

Windows desktop companion for recording and replaying Geometry Dash spacebar patterns, with a matching project website for **https://doitformedash.com**.

## Download for players

Use the compiled Windows installer in [`website/downloads/DoItForMeDash_Setup_1.4.5.exe`](website/downloads/DoItForMeDash_Setup_1.4.5.exe). Click **View raw** / **Download raw file** on GitHub to download it. The public website links directly to this installer after deployment.

Users do **not** need Python, a compiler, or build tools. Install Setup, open the desktop shortcut, and open Geometry Dash through Steam. The app opens its dashboard locally in the browser. This release targets Windows 10/11, 64-bit, and is unsigned.

The installer ships a Nuitka-compiled application, required runtime components, dashboard HTML, images, and third-party license notices. No Python source, Python bytecode files, source archives, or build scripts are included. Browser assets remain inspectable. Compilation does not prevent reverse engineering.

The original source ZIP and `BUILD_AND_INSTALL.md` remain for maintainers; they are **not** player downloads and should **not** be copied into the public website directory.

## Deploy from PuTTY on the VPS

The domain is already configured in cPanel/Apache with document root:

```text
/home/cpjsirwin/public_html/doitformedash.com
```

As root, run the following for the first deployment:

```bash
git clone https://github.com/copernicus99/DoItForMeDash.git /home/cpjsirwin/apps/DoItForMeDash
bash /home/cpjsirwin/apps/DoItForMeDash/deploy-vps.sh
```

If that checkout already exists, update it instead of cloning again:

```bash
git -C /home/cpjsirwin/apps/DoItForMeDash pull --ff-only
bash /home/cpjsirwin/apps/DoItForMeDash/deploy-vps.sh
```

The deployment script checks the installer SHA-256 checksum, backs up existing website content outside the public folder, copies the website with the correct owner and permissions, and checks the home page and installer over HTTPS. It does not edit Apache or other sites. Only `website/` is published.

Backups and staged releases live under:

```text
/home/cpjsirwin/apps/doitformedash-releases/<UTC timestamp>/
```

Requirements on the server: Bash, Git, tar, curl, sha256sum, and the existing `cpjsirwin` account and domain folder.

## What was verified

- Nuitka standalone compilation with explicit recording/playback worker inclusion.
- Packaged worker dispatch with no Python on the child process search path.
- Local dashboard HTML, banner, idle status, and recording/playback arming and stopping.
- Installer payload installed under an isolated test identity: **41 files, zero Python source/bytecode or build scripts**; the installed application passed the same integration checks and the test copy uninstalled successfully.
- Website mobile and desktop layout, navigation, help disclosures, and local asset loading.

Actual Geometry Dash recording/playback timing still needs an end-to-end test with the game running. Testing here is not a clean Windows VM certification. The installer is not code-signed, and Windows may show a publisher or reputation warning.

## Use

For recording: name the pattern, arm recording, focus the level-selection screen, press **F8**, play with Space, then press **F9** to save. **F10** cancels recording.

For playback: select the pattern, arm playback, return to the same level-selection screen, and press **F8**. **F9** stops playback. Matching level, speed, and frame-rate settings matter; synchronization is based on a visible scene transition and is not guaranteed to be frame-perfect.

Patterns remain local in `Documents\DoItForMe Dash\patterns`.

This is an unofficial community utility, not affiliated with or endorsed by RobTop Games or Steam.
