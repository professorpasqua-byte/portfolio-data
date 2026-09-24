import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

total_unique = 1500
target_yes = 261
target_no = 1239

emp_ids = [f"E-{1000 + i}" for i in range(total_unique)]
names = [f"Employee Name {i}" for i in range(total_unique)]

df = pd.DataFrame({
    'EmployeeID': emp_ids,
    'FullName': names,
    'Gender': [random.choice(['Male', 'Female']) for _ in range(total_unique)],
    'Attrition': ['No'] * target_no + ['Yes'] * target_yes
})

df = df.sample(frac=1, random_state=42).reset_index(drop=True)

roles = []
for idx, row in df.iterrows():
    att = row['Attrition']
    if att == 'Yes':
        if idx % 5 == 0: roles.append('Sales Development Rep')
        elif idx % 5 == 1: roles.append('QA Analyst')
        elif idx % 5 == 2: roles.append('HR Partner')
        else: roles.append(random.choice(['Software Engineer', 'Data Engineer', 'Engineering Lead']))
    else:
        if idx % 7 == 0: roles.append('Sales Development Rep')
        elif idx % 7 == 1: roles.append('QA Analyst')
        elif idx % 7 == 2: roles.append('HR Partner')
        else: roles.append(random.choice(['Software Engineer', 'Data Engineer', 'Engineering Lead']))

df['JobRole'] = roles

departments = []
for role in df['JobRole']:
    if role in ['Software Engineer', 'Data Engineer', 'Engineering Lead']:
        departments.append(random.choice(['Engineering', 'Eng.']))
    elif role == 'Sales Development Rep':
        departments.append(random.choice(['Sales', 'Sal3s']))
    else:
        departments.append(random.choice(['Human Resources', 'HR']))
df['Department'] = departments

df['Age'] = [random.randint(22, 60) for _ in range(total_unique)]
df['MonthlyIncome'] = [random.randint(4000, 15000) for _ in range(total_unique)]
df['JobSatisfaction'] = [random.randint(1, 4) for _ in range(total_unique)]

base_date = datetime(2026, 1, 1)
df['exported_at'] = [base_date + timedelta(days=random.randint(1, 30)) for _ in range(total_unique)]

duplicates = df.sample(n=150, random_state=42).copy()
duplicates['exported_at'] = duplicates['exported_at'] - timedelta(days=5)
duplicates['MonthlyIncome'] = duplicates['MonthlyIncome'] - 500

raw_df = pd.concat([df, duplicates], ignore_index=True)
raw_df.to_csv('meridian_works_raw.csv', index=False)
print("🎯 Verification: Transactional 'meridian_works_raw.csv' built successfully with anomalies.")
