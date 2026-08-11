---
name: cua-driver-linux
description: "Fix cua-driver on Linux: X11 switch, daemon, GNOME pitfalls."
version: 1.0.0
metadata:
  hermes:
    tags: [cua-driver, linux, x11, wayland, gnome, desktop-automation, screenshot]
    category: devops
    related_skills: [computer-use, vision-analysis-fallback]
---

# cua-driver on Linux — Setup & Troubleshooting

The bundled `computer-use` skill covers the cross-platform action vocabulary.
This skill covers the **Linux-specific plumbing** that makes cua-driver actually
work: session type, daemon env, GNOME quirks, and the screenshot field trap.

## The Wayland Wall (read this first)

cua-driver's `get_desktop_state` returns screen size on Wayland, but
`XGetImage` fails with a `Match` error — **screenshots are impossible on
Wayland**. This is Wayland's security model blocking root-window access, not a
bug.

**Fix**: Switch the GNOME session to X11 ("GNOME on Xorg").

### How to switch to X11

1. **AccountsService** (persists across reboots):
   ```bash
   dbus-send --system --print-reply --dest=org.freedesktop.Accounts \
     /org/freedesktop/Accounts/User1000 \
     org.freedesktop.Accounts.User.SetXSession string:"ubuntu-xorg"
   ```

2. **`~/.dmrc`**:
   ```
   [Desktop]
   Session=gnome-xorg
   ```

3. **GDM greeter** (manual, one-time): Click username → gear ⚙️ → "GNOME on
   Xorg" → password.

4. **Verify** after next login:
   ```bash
   cat /proc/$(pgrep -x gnome-shell | head -1)/environ | tr '\0' '\n' | grep XDG_SESSION_TYPE
   # Must show: XDG_SESSION_TYPE=x11
   ```

### ⚠️ Do NOT log the user out to switch sessions

GDM auto-login does **not** re-fire on `systemctl restart gdm3`. After logout,
GDM shows the greeter and waits for a physical click — even with
`AutomaticLoginEnable=true`. The user must click their name at the physical
screen. `systemctl restart gdm3` also needs sudo and fails silently from the
agent session.

**Lesson**: Change AccountsService + dmrc, then ask the user to reboot or
manually log in at the physical screen. Never log them out yourself.

## Starting the daemon

```bash
DISPLAY=:0 XDG_SESSION_TYPE=x11 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus \
  /home/tars/.local/bin/cua-driver serve \
  --socket /home/tars/.cache/cua-driver/cua-driver.sock
```

Run in **background** (`terminal(background=true)`) — it's long-lived.

### Discovering env vars at runtime

If `DISPLAY` or `DBUS_SESSION_BUS_ADDRESS` change (e.g. after reboot):

```bash
cat /proc/$(pgrep -x gnome-shell | head -1)/environ | tr '\0' '\n' \
  | grep -E '(DISPLAY|XDG_SESSION_TYPE|DBUS)'
```

### Disabling telemetry

```bash
/home/tars/.local/bin/cua-driver telemetry disable
```

## MCP config (Hermes config.yaml)

```yaml
mcp_servers:
  cua-driver:
    command: /home/tars/.local/bin/cua-driver
    args: ["mcp"]
    env:
      DISPLAY: ":0"
      XDG_SESSION_TYPE: "x11"
      DBUS_SESSION_BUS_ADDRESS: "unix:path=/run/user/1000/bus"
```

## Screenshot field trap

`get_desktop_state` returns two screenshot-like fields:

| Field | Content |
|---|---|
| `screenshot_png_b64` | ✅ **The actual base64-encoded PNG** |
| `screenshot` | ❌ Empty — NOT the image |

**Always read `screenshot_png_b64`.**

## GNOME desktop icon clicks

GNOME's Desktop Icons extension (`Gjs` process) does **not** expose AT-SPI
elements for individual file icons. Clicking desktop files by element index
is impossible. Workarounds:

1. **`xdg-open` / `gio open`** from terminal — most reliable.
2. **`ffplay`** as lightweight video player (Ubuntu minimal may have no player):
   ```bash
   DISPLAY=:0 ffplay -x 800 -y 450 -autoexit /path/to/video.mp4
   ```
3. Pixel-coordinate clicks on desktop icons may need `delivery_mode:"foreground"`
   to register as double-clicks.

## Screenshot → Vision analysis

After capturing, pipe the screenshot through the `vision-analysis-fallback` skill
(NVIDIA free → OpenRouter Gemini). See that skill's
`references/cua-driver-screenshot-pipeline.md` for the full recipe.

## Quick troubleshooting table

| Symptom | Fix |
|---|---|
| `XGetImage` Match error | Switch to X11 (Wayland blocks screenshots) |
| `get_desktop_state` returns empty screenshot | Read `screenshot_png_b64`, not `screenshot` |
| GDM greeter stuck after logout | Physical login required; don't logout from agent |
| `no on-screen window` on Linux | Check `DISPLAY` env var on daemon; verify X11 session |
| 0 windows with windows in `list_windows` | Desktop Icons Gjs window shows as the only window; open apps via `xdg-open` |
| No video player installed | Use `ffplay` (bundled with ffmpeg) |
| `cua-driver not installed` | `hermes computer-use install` |

## Verified working (Aug 10 2026)

- cua-driver v0.19.2, Ubuntu 24.04, kernel 6.17.0-35-generic
- GNOME on Xorg, DISPLAY=:0, 1680×1050
- Screenshots: 2MB PNG, perfect quality
- AT-SPI: active, accessibility tree functional
- XSendEvent: active (keyboard/mouse input works)
- ffplay video playback: detected, subtitles read via NVIDIA vision
