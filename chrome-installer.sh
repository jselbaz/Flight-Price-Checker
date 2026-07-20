#!/bin/bash
set -euo pipefail

latest_stable_json="https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
json_data=$(curl -s "$latest_stable_json")

latest_chrome_linux_download_url="$(echo "$json_data" | jq -r '.channels.Stable.downloads["chrome-headless-shell"][] | select(.platform=="linux64") | .url')"
latest_chrome_driver_linux_download_url="$(echo "$json_data" | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url')"

download_path_chrome_linux="/opt/chrome-linux.zip"
download_path_chrome_driver_linux="/opt/chrome-driver-linux.zip"

mkdir -p "/opt/chrome"
curl -fLo $download_path_chrome_linux $latest_chrome_linux_download_url
unzip -q $download_path_chrome_linux -d "/opt/chrome"
rm -rf $download_path_chrome_linux

mkdir -p "/opt/chrome-driver"
curl -fLo $download_path_chrome_driver_linux $latest_chrome_driver_linux_download_url
unzip -q $download_path_chrome_driver_linux -d "/opt/chrome-driver"
rm -rf $download_path_chrome_driver_linux

find /opt/chrome -type f -name "chrome-headless-shell" -exec chmod +x {} \;
find /opt/chrome-driver -type f -name "chromedriver" -exec chmod +x {} \;

echo "=== Chrome headless shell binary ==="
find /opt/chrome -type f -name "chrome-headless-shell"
echo "=== Chromedriver binary ==="
find /opt/chrome-driver -type f -name "chromedriver"