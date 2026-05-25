# Adaptive VM Automation

A Python-based automation toolkit for Voicemeeter Potato focused on realtime mixer control, adaptive DSP behavior, and workflow automation.

---

# Features

## Adaptive Smile EQ

Dynamically adjusts EQ curves based on realtime output loudness.

The current implementation:

* Reads live output bus levels from Voicemeeter
* Converts raw meter amplitudes into dBFS values
* Smooths loudness changes to avoid jitter
* Interpolates EQ gain values dynamically
* Applies realtime EQPro-G6 updates through the Voicemeeter API

This creates a loudness compensation system similar in spirit to classic “loudness” processing, while remaining configurable and lightweight.

---

## Linked Gain Compensation

Allows buses or strips to compensate against another control automatically.

Example use case:

* Raise a master listening bus
* Automatically lower selected channels (Discord, voice chat, etc.)
* Preserve relative balance without manual readjustment

Supports:

* Manual UI slider movement
* MIDI-controlled changes
* Live synchronization through Voicemeeter parameter dirty-state tracking

---


# Planned Features

* Lightweight local web UI
* Configurable automation routing
* User-defined EQ profiles
* Preset/profile management
* Generic strip-to-strip or bus-to-strip automation bindings

---


# Requirements

* Python 3.11+
* Voicemeeter Potato
* Voicemeeter Remote API
* Windows

---

# Current Status

This project is actively experimental.

The current focus is:

* stable synchronization behavior
* automation architecture
* clean parameter abstractions


