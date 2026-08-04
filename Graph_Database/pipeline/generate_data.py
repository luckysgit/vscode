import csv
import random

NUM_USERS = 100000       # 100,000 Nodes
NUM_EDGES = 500000        # 500,000 Relationships

print("Generating users.csv...")
with open('users.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'name', 'age'])
    for i in range(NUM_USERS):
        writer.writerow([i, f"User_{i}", random.randint(18, 65)])

print("Generating follows.csv...")
with open('follows.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['source_id', 'target_id', 'since'])
    for _ in range(NUM_EDGES):
        src = random.randint(0, NUM_USERS - 1)
        tgt = random.randint(0, NUM_USERS - 1)
        if src != tgt:
            writer.writerow([src, tgt, random.randint(2015, 2024)])

print("Data generation complete!")
