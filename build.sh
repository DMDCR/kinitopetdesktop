#!/usr/bin/env bash
set -e

APP_NAME="KinitoPET Desktop Pet"
BUNDLE_ID="com.dmdtutorials.KinitoPET"
VERSION="1.1.3"

echo "KinitoPET Desktop Pet Builder (MacOS) [v1.1.3]"
echo
echo "Requires Python 3.10+ (you’re running $(python3 --version))."
read -n1 -s -r -p "Press any key to continue or Ctrl-C to abort..."
echo && echo

echo "Installing/upgrading build tools & dependencies..."
pip3 install --upgrade pip
pip3 install nuitka pillow pygame pystray requests
echo

read -n1 -s -r -p "Dependencies ready. Press any key to build..."
echo && echo

echo "Building Kinito..."
rm -rf build dist
mkdir -p dist
nuitka \
  --standalone \
  --onefile \
  --plugin-enable=tk-inter \
  --output-dir=dist \
  --include-data-files="audio/*,models/*,other/*,icon.ico" \
  kinito.py

# rename the output executable
mv dist/kinito dist/${APP_NAME}

echo
echo "📦 Creating .app bundle structure..."
APP_DIR="dist/${APP_NAME}.app"
rm -rf "${APP_DIR}"
mkdir -p "${APP_DIR}/Contents"/{MacOS,Resources}

# copy the executable
cp dist/${APP_NAME} "${APP_DIR}/Contents/MacOS/${APP_NAME}"
chmod +x "${APP_DIR}/Contents/MacOS/${APP_NAME}"

# copy resources
cp -R audio models other icon.ico "${APP_DIR}/Contents/Resources/"

# write Info.plist
cat > "${APP_DIR}/Contents/Info.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>CFBundleName</key>
  <string>${APP_NAME}</string>
  <key>CFBundleDisplayName</key>
  <string>${APP_NAME}</string>
  <key>CFBundleIdentifier</key>
  <string>${BUNDLE_ID}</string>
  <key>CFBundleVersion</key>
  <string>${VERSION}</string>
  <key>CFBundleExecutable</key>
  <string>${APP_NAME}</string>
  <key>CFBundleIconFile</key>
  <string>icon.ico</string>
  <key>LSUIElement</key>
  <true/>
</dict>
</plist>
EOF

echo
echo "✅ .app bundle created at dist/${APP_NAME}.app"
echo "   Contents:"
echo "     MacOS/${APP_NAME} (your executable)"
echo "     Resources/audio  models  other  icon.ico"
echo
read -n1 -s -r -p "Press any key to finish…"
echo
