import csv
import random
import string

def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters, k=length))

# 1. Generate users.csv with 50 attributes
print("Generating users.csv with 50 fields...")
num_users = 10000
fieldnames = ['id', 'name', 'age'] + [f'attr_{i}' for i in range(1, 51)]

with open('users.csv', mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for i in range(1, num_users + 1):
        row = {
            'id': i,
            'name': f'User_{i}',
            'age': random.randint(18, 70)
        }
        for k in range(1, 51):
            row[f'attr_{k}'] = random_string(10)
        writer.writerow(row)

# 2. Generate follows.csv (100,000 edges)
print("Generating follows.csv...")
num_edges = 100000
with open('follows.csv', mode='w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['source_id', 'target_id', 'since'])
    writer.writeheader()
    for _ in range(num_edges):
        writer.writerow({
            'source_id': random.randint(1, num_users),
            'target_id': random.randint(1, num_users),
            'since': random.randint(2015, 2024)
        })

print("Wide Dataset Generated Successfully!")
