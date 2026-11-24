#!/usr/bin/env bash
set -euo pipefail
site=/home/cpjsirwin/public_html/doitformedash.com
source_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/website
release=/home/cpjsirwin/apps/doitformedash-releases/$(date -u +%Y%m%dT%H%M%SZ)
test "$(id -u)" = 0 || { echo 'Run as root.'; exit 1; }
test -d "$site" && test ! -L "$site" || { echo 'Expected website folder is missing or is a symlink.'; exit 1; }
test -f "$source_dir/index.html" && test -f "$source_dir/downloads/DoItForMeDash_Setup_1.4.5.exe" || { echo 'Website or installer is missing from checkout.'; exit 1; }
mkdir -p "$release/staging"
cp -a "$source_dir/." "$release/staging/"
(cd "$release/staging/downloads" && sha256sum -c SHA256SUMS.txt)
tar -C "$site" -czf "$release/previous-website.tar.gz" .
for directory in assets downloads; do
  test ! -L "$site/$directory" || { echo 'Refusing to replace a symlink.'; exit 1; }
  install -d -o cpjsirwin -g cpjsirwin -m 755 "$site/$directory"
done
for file in assets/site.css assets/site.js assets/favicon.svg assets/banner.png downloads/release.json downloads/SHA256SUMS.txt downloads/DoItForMeDash_Setup_1.4.5.exe .htaccess index.html; do
  test ! -L "$site/$file" || { echo "Refusing to replace symlink: $file"; exit 1; }
  install -o cpjsirwin -g cpjsirwin -m 644 "$release/staging/$file" "$site/$file"
done
echo "Website installed. Previous content backed up at: $release/previous-website.tar.gz"
curl --fail --silent --show-error --max-time 30 -I https://doitformedash.com/
curl --fail --silent --show-error --max-time 30 -I https://doitformedash.com/downloads/DoItForMeDash_Setup_1.4.5.exe
