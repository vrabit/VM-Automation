from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# vm_auto_eq
VM_AUTO_EQ_DIR = ROOT / "vm_auto_eq"

# eq presets
BASE_PRESETS_DIR = VM_AUTO_EQ_DIR / "presets"

# eqpro presets
EQ_PRO_TEMPLATE = 'eqpro_g6_{i}.json'
EQ_PRESETS_DIR = BASE_PRESETS_DIR / "eq_presets"
