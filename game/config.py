

#
# ---------- Central configuration constants ----------

# Money & economics
STARTING_CASH   = 100.0
WAGE_MULTIPLIER = 10           # wage = capacity * multiplier ± variation
MAX_AD_BUDGET   = 500          # daily advertising cap

# UI / formatting
CLEAR_DIVIDER     = "=" * 40
MAX_QUEUE_DISPLAY = 20         # max bar length for queue display

# Time system
MINUTES_PER_TURN = 15
TURNS_PER_DAY    = int((8 * 60) / MINUTES_PER_TURN)   # 08:00‑16:00 → 32 turns