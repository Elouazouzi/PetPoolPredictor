import random
from collections import defaultdict, Counter

random.seed(42)

# -------------------------
# Talent class (no parent, manifested ignored)
# -------------------------

class Talent:
    def __init__(self, name, rarity, index, manifested=False):
        self.name = name
        self.rarity = rarity
        self.index = index
        self.manifested = manifested  # kept for compatibility, unused

def build_pool(input_dict):
    talents_pool = []
    index = 1
    for talent in input_dict:
        talents_pool.append(Talent(talent, input_dict[talent], index))
        index += 1
    return talents_pool


# -------------------------
# Input pools
# -------------------------

pet1_pool = { 
    "Death-Spear": 2,
    "Plaguebringer": 3,
    "Virulence": 3,
    "Rugged": 1,
    "Fairy-Friend": 1,
    "Death-Boon": 0,
    "Death-Ward": 3,
    "Death-Assailant": 4,
    "Black-Mantle": 3,
    "Armor-Breaker": 4
}

pet2_pool = { 
    "Sharp-Shot":       3,
    "Pain-Bringer":     2,
    "Pain-Giver":       3,
    "Spell-Proof":      4,
    "Fairy-Friend":     1,
    "Critical-Striker": 4,
    "Death-Dealer":     3,
    "Death-Giver":      1,
    "Mighty":           3,
    "Armor-Breaker":    4
}

# -------------------------
# Masked offspring pool
# -------------------------

masked_rarities = [3, 2, 3, 3, 4, 0, 3, 4, 3, 4]

# -------------------------
# Combine pools
# -------------------------

alpha_pool = build_pool(pet1_pool)
beta_pool  = build_pool(pet2_pool)

combined = {}
for t in alpha_pool + beta_pool:
    if t.name not in combined:
        combined[t.name] = t

talents = list(combined.values())

talent_names = []
talents_dict = {}

print("Combined Parents Pool:")
for i, t in enumerate(talents, 1):
    print(f"{i}. {t.name} ({t.rarity})")
    talents_dict[t.name] = t.rarity
    talent_names.append(t.name)

by_rarity = defaultdict(list)
for t in talents:
    by_rarity[t.rarity].append(t)

# -------------------------
# Parameters
# -------------------------

BASE_W = 1.0
CHAIN_W = 2.5
DISTANCE_PENALTY = 0.35

# -------------------------
# Chain scoring
# -------------------------

def chain_bonus(candidate, placed):
    bonus = 0
    for prev in reversed(placed):
        if prev is None:
            break
        if candidate.index == prev.index + 1:
            bonus += CHAIN_W
        else:
            break
    return bonus

def distance_penalty(candidate, slot):
    return DISTANCE_PENALTY * (candidate.index - (slot + 1)) ** 2

# -------------------------
# Monte Carlo
# -------------------------

SIMS = 5000
full_counts = Counter()

for _ in range(SIMS):
    chosen = [None] * 10
    used = set()

    for i, rarity in enumerate(masked_rarities):
        candidates = [t for t in by_rarity[rarity] if t.name not in used]

        weights = {}
        for t in candidates:
            w = BASE_W
            w += chain_bonus(t, chosen)
            w -= distance_penalty(t, i)
            weights[t] = max(w, 0.01)

        total = sum(weights.values())
        r = random.uniform(0, total)
        acc = 0

        for t, w in weights.items():
            acc += w
            if acc >= r:
                chosen[i] = t
                used.add(t.name)
                break

    full_counts[tuple(t.name for t in chosen)] += 1

# -------------------------
# Output
# -------------------------

best_pool, count = full_counts.most_common(1)[0]

max_len = max(len(name) for name in talent_names)

best_pool_names = []
print("\nPredicted Pool:")
for i, name in enumerate(best_pool):
    best_pool_names.append(name)
    print(f"[{i+1:<2}] {name:<{max_len}} ({talents_dict[name]})")

print(f"Confidence: {round(100 * count / SIMS, 2)}%")
print("-------------")
print("Lost talents:")
for t in talent_names:
    if t not in best_pool_names:
        print(f"{'':<5} {t:<{max_len}} ({talents_dict[t]})")
