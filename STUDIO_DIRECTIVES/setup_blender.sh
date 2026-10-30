#!/usr/bin/env bash
# Installs the studio's Blender build (5.2.3 LTS as a Python module) for headless use.
set -euo pipefail

VENV="${BLENDER_VENV:-$HOME/.blender-venv}"

if [ ! -x "$VENV/bin/python" ]; then
  python3 -m venv "$VENV"
fi
"$VENV/bin/pip" install -q bpy==5.2.3

# Software EGL lets EEVEE and Workbench render without a GPU.
if ! ldconfig -p | grep -q libEGL.so.1; then
  apt-get update -qq
  apt-get install -y -qq libegl1 libegl-mesa0 libgl1-mesa-dri
fi

"$VENV/bin/python" -c "import bpy; print('Blender', bpy.app.version_string)"
echo "Run scripts with: EGL_PLATFORM=surfaceless $VENV/bin/python your_script.py"
