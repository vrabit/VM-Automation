from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# vm_auto_eq
VM_AUTO_EQ_DIR = ROOT / "vm_auto_eq"

# eq presets
BASE_PRESETS_DIR = VM_AUTO_EQ_DIR / "presets"

# eqpro presets
EQ_PRO_TEMPLATE = 'eqpro_g6_{i}.json'
EQ_PRESETS_DIR = BASE_PRESETS_DIR / "eq_presets"


# settings
SETTINGS_DIR = VM_AUTO_EQ_DIR / "settings"

# auto_eq settings
AUTO_EQ_SETTINGS_DIR = SETTINGS_DIR / "auto_eq"
AUTO_EQ_FILENAME = "auto_eq_{i}.json"

# gain_compensation
GAIN_COMP_SETTINGS_DIR = SETTINGS_DIR / "gain_compensation"
GAIN_COMP_CONFIG_FILENAME = "CompensationConfig.json"

# ui_assets
UI_DIR = VM_AUTO_EQ_DIR / "ui"
UI_ASSETS_DIR = UI_DIR / "assets"
TRAY_ICON_24 = UI_ASSETS_DIR / "tray_icon_24.png"
TRAY_ICON_32 = UI_ASSETS_DIR / "tray_icon_32.png"
TRAY_ICON_256 = UI_ASSETS_DIR / "tray_icon_256.png"