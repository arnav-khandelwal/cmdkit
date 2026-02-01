#!/bin/sh
set -e

REPO="arnav-khandelwal/cmdkit"
BIN_NAME="cmdkit"

OS="$(uname -s)"

if [ "$OS" = "Darwin" ]; then
  ASSET="cmdkit-macos"
elif [ "$OS" = "Linux" ]; then
  ASSET="cmdkit-linux"
else
  echo "❌ Unsupported OS: $OS"
  exit 1
fi

INSTALL_DIR="/usr/local/bin"
URL="https://github.com/$REPO/releases/latest/download/$ASSET"

echo "⬇️  Downloading cmdkit..."
curl -L "$URL" -o "$BIN_NAME"

echo "🔧 Making executable..."
chmod +x "$BIN_NAME"

echo "📦 Installing to $INSTALL_DIR (may require sudo)..."
sudo mv "$BIN_NAME" "$INSTALL_DIR/$BIN_NAME"

echo "✅ cmdkit installed successfully!"
echo "👉 Run: cmdkit --help"