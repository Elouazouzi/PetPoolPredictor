# Wizard101 Pet Talent Predictor

A community-driven tool to **predict Wizard101 pet hatching outcomes** by modeling how talent pools are inherited during a hatch.

This project aims to turn long-standing breeder intuition ("talent sticking", "order chunks", manifested bias, etc.) into a **transparent, testable, and extensible prediction engine**.

> ⚠️ Disclaimer: KingsIsle has never published the official hatching algorithm. This tool is a **best-fit statistical model** based on extensive player observations and testing.

---

## ✨ Features

* 🔢 **Rarity-aware prediction** — strictly respects offspring rarity order

* 🔗 **Talent chaining (order preservation)** — contiguous talents strongly prefer to stay together

* 📉 **Distance penalty** — discourages large jumps in ordering

* ⭐ **Manifested talent bias** — manifested talents are more likely to persist

* 🎲 **Monte Carlo simulation** — produces probability-based predictions, not guesses

* 🧪 **Validated against real hatch data** — early tests closely match trained pets

---

## 🧠 Core Idea

This initial release is an **experimental sketch** focused on validating one core hypothesis:

> **Wizard101 pet talents are inherited primarily through order-preserving chains, not independent random draws.**

Early testing shows that when chaining and distance penalties are applied correctly, the predictor can closely reproduce real in-game outcomes — even **without explicit manifested-talent weighting**.

Manifested talents still tend to appear in predicted pools, but as a *natural consequence of order preservation*, not because they are hard-coded to be favored.

This version prioritizes:

* Small changes → small pool differences
* Minimal talent jumps
* In-game-valid pools only

Wizard101 pet hatching is not purely random.

Observed behavior suggests:

* Talents often transfer in **ordered chunks**
* Pools tend to **shift slightly**, not reshuffle
* **Manifested talents** are harder to discard
* When two parents differ by only 1 talent, the offspring pool usually differs by only 1 talent

This tool models hatching as a **sequence alignment problem with soft constraints**, similar to:

* DNA alignment (bioinformatics)
* Token decoding (NLP)
* Hidden Markov Models

---

## 📥 Inputs

The predictor requires:

### 1️⃣ Parent Talent Pools

Each parent provides:

* Talent name
* Rarity (0–4)
* Original pool index (1–10)
* Whether the talent is manifested

Example:

```python
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
    "Armor-Breaker": 4}

```

### 2️⃣ Masked Offspring Pool

The **observed rarity order** of the offspring pool:

```python
masked_rarities = [2, 3, 3, 1, 1, 0, 3, 4, 3, 4]
```

Unknown talents are represented as `???`, but their rarity is known.

---

## 📤 Outputs

The predictor produces:

* 🏆 **Most likely full offspring pool** (in-game valid)
* 📊 Confidence percentage (based on simulation frequency)
* 🧪 Optional: Top N most likely pools

Example output:

```
Predicted Pool:
[1 ] Sharp-Shot       (3)
[2 ] Pain-Bringer     (2)
[3 ] Pain-Giver       (3)
[4 ] Spell-Proof      (4)
[5 ] Spell-Defying    (2)
[6 ] Fairy-Friend     (1)
[7 ] Critical-Striker (4)
[8 ] Death-Boon       (0)
[9 ] Mighty           (3)
[10] Death-Giver      (1)
Confidence: 54.4%
-------------------------
Lost talents:
      Death-Dealer     (3)
      Armor-Breaker    (4)

```

---

## ⚙️ How It Works (High Level)

For each simulation run:

1. Combine parent pools and deduplicate talents
2. Group talents by rarity
3. Fill offspring slots **left-to-right** using weighted sampling
4. Each candidate talent is weighted by:

   * Base probability
   * **Chain continuation bonus** (prefers neighbors from original pool)
   * **Distance penalty** (discourages large index jumps)
5. Duplicate talents are rejected
6. The completed pool is recorded

After thousands of simulations, the **most frequent full pool** is reported as the prediction.

---

## 🧪 Why Monte Carlo?

Because the real system is:

* Probabilistic
* Order-biased
* Partially observable

Monte Carlo allows us to:

* Model uncertainty honestly
* Compare multiple plausible outcomes
* Avoid false certainty

---

## 🔧 Configuration

Key tunable parameters (subject to community testing):

```python
BASE_W = 1.0
MANIFEST_W = 3.5
CHAIN_W = 2.5
DISTANCE_PENALTY = 0.35
SIMS = 5000
```

Adjust these to better match your own hatch logs.

---

## 🚧 Limitations

* This is **not the official KingsIsle algorithm**
* Probabilities are estimates, not guarantees
* Results depend on correct rarity order input
* Derby talents are currently ignored
* Some edge cases (e.g. extreme pool divergence) may be underrepresented

This is an **initial commit** intended to establish a solid, testable baseline.

---

## 🤝 Contributing

Contributions are welcome!

Ideas:

* Add CLI or GUI
* Log real hatch results to tune weights
* Implement deterministic solvers (Viterbi / DP)
* Support multiple offspring rarity patterns
* Visualize talent chains

Please open an issue or PR with:

* Input pools
* Observed offspring
* Any discrepancies

---

## 📜 License

GPL-3.0 license — use it, fork it, improve it.

Happy hatching 🐾
