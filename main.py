import sys
import os
import random
from collections import defaultdict, Counter
import json
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QComboBox, QGridLayout, QVBoxLayout, QGroupBox,
    QTextEdit, QHBoxLayout
)

random.seed(42)

# -------------------------
# Talent class (no parent, manifested ignored)
# -------------------------

class Talent:
    def __init__(self, name, rarity, index, manifested=False):
        self.name = name
        self.rarity = rarity
        self.index = index
        self.manifested = manifested  # unused

def build_pool(input_pool):
    talents_pool = []
    index = 1
    for t, r in input_pool:
        talents_pool.append(Talent(t, r, index))
        index += 1

    return talents_pool

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

talents_data_file = './data/talents.json'
TALENT_DB = {}
if os.path.exists(talents_data_file):
        try:
            with open(talents_data_file, 'r') as f:
                TALENT_DB = json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: {talents_data_file} was empty or corrupted.")

RARITIES = ["0", "1", "2", "3", "4"]


class TalentRow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        self.talent_box = QComboBox()
        self.rarity_box = QComboBox()

        self.talent_box.addItem("???")
        self.talent_box.addItems(sorted(TALENT_DB.keys()))

        self.rarity_box.addItems(RARITIES)

        self.talent_box.currentTextChanged.connect(self.on_talent_changed)

        layout.addWidget(self.talent_box)
        layout.addWidget(self.rarity_box)
        self.setLayout(layout)

    def on_talent_changed(self, talent):
        if talent == "???":
            self.rarity_box.setEnabled(True)
        else:
            rarity = TALENT_DB[talent]
            self.rarity_box.setCurrentText(str(rarity))
            self.rarity_box.setEnabled(False)

    def get_value(self):
        return (
            self.talent_box.currentText(),
            int(self.rarity_box.currentText())
        )



class PetInput(QWidget):
    def __init__(self, title):
        super().__init__()
        box = QGroupBox(title)
        layout = QGridLayout()

        self.rows = []

        for i in range(10):
            row = TalentRow()
            self.rows.append(row)
            layout.addWidget(QLabel(str(i+1)), i, 0)
            layout.addWidget(row, i, 1)

        box.setLayout(layout)

        main = QHBoxLayout()
        main.addWidget(box)
        self.setLayout(main)

    def get_pool(self):
        return [row.get_value() for row in self.rows]



class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wizard101 Pet Talent Predictor")

        main_layout = QVBoxLayout()

        # Parents
        parents_layout = QGridLayout()
        self.pet_a = PetInput("Parent A")
        self.pet_b = PetInput("Parent B")
        parents_layout.addWidget(self.pet_a, 0, 0)
        parents_layout.addWidget(self.pet_b, 0, 1)

        # Masked offspring
        mask_box = QGroupBox("Offspring Masked Rarities")
        mask_layout = QGridLayout()
        self.mask_boxes = []

        for i in range(10):
            box = QComboBox()
            box.addItems(RARITIES)
            self.mask_boxes.append(box)
            mask_layout.addWidget(QLabel(str(i+1)), 0, i)
            mask_layout.addWidget(box, 1, i)

        mask_box.setLayout(mask_layout)

        # Run button
        run_btn = QPushButton("Run Prediction")
        run_btn.clicked.connect(self.run_prediction)

        # Output
        self.output = QTextEdit()
        self.output.setReadOnly(True)

        main_layout.addLayout(parents_layout)
        main_layout.addWidget(mask_box)
        main_layout.addWidget(run_btn)
        main_layout.addWidget(self.output)

        self.setLayout(main_layout)

    def run_prediction(self):
        pet_a = self.pet_a.get_pool()
        pet_b = self.pet_b.get_pool()
        masked = [int(b.currentText()) for b in self.mask_boxes]

        # -------------------------
        # Combine pools
        # -------------------------

        alpha_pool = build_pool(pet_a)
        beta_pool  = build_pool(pet_b)

        combined = {}
        for t in alpha_pool + beta_pool:
            if t.name not in combined:
                combined[t.name] = t

        talents = list(combined.values())

        talent_names = []
        talents_dict = {}

        for i, t in enumerate(talents, 1):
            talents_dict[t.name] = t.rarity
            talent_names.append(t.name)

        by_rarity = defaultdict(list)
        for t in talents:
            by_rarity[t.rarity].append(t)

        # -------------------------
        # Monte Carlo
        # -------------------------

        SIMS = 5000
        full_counts = Counter()

        for _ in range(SIMS):
            chosen = [None] * 10
            used = set()

            for i, rarity in enumerate(masked):
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

            try:
                full_counts[tuple(t.name for t in chosen)] += 1
            except:
                self.output.clear()
                self.output.append("Error: Input data is invalid, please check the talents and masked rarities for errors and try again.")
                break




        # -------------------------
        # Output
        # -------------------------

        output_string = "" 
        best_pool, count = full_counts.most_common(1)[0]

        max_len = max(len(name) for name in talent_names)

        best_pool_names = []
        output_string += "Predicted Pool:\n" 
        for i, name in enumerate(best_pool):
            best_pool_names.append(name)
            output_string += f"[{i+1:<2}] {name:<{max_len}} ({talents_dict[name]})\n"

        output_string += f"Confidence: {round(100 * count / SIMS, 2)}%\n"
        output_string +="-------------\n"
        output_string += "Lost talents:\n"
        for t in talent_names:
            if t not in best_pool_names:
                output_string += f"{'':<5} {t:<{max_len}} ({talents_dict[t]})\n" 


        self.output.clear()
        self.output.append(output_string)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(600, 900)
    win.show()
    sys.exit(app.exec())
