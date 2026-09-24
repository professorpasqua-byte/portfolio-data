import pandas as pd
import random

# Force precise statistical match for portfolio alignment
total = 1500
target_yes = 261 # 17.4% exact attrition match

# Construct the exact data matrix parameters
df = pd.DataFrame({
    'EmployeeID': [f"E-{1000 + i}" for i in range(total)],
    'FullName': [f"Employee Name {i}" for i in range(total)],
    'Gender': [random.choice(['Male', 'Female']) for _ in range(total)],
    'Attrition': ['Yes'] * target_yes + ['No'] * (total - target_yes),
    'Department': [random.choice(['Engineering', 'Sales', 'Human Resources']) for _ in range(total)],
    'JobRole': [random.choice(['Software Engineer', 'QA Analyst', 'Sales Development Rep', 'HR Partner']) for _ in range(total)],
    'MonthlyIncome': [random.randint(4500, 8500) for _ in range(total)],
    'JobSatisfaction': [random.randint(1, 4) for _ in range(total)],
    'exported_at': ['2026-01-01' for _ in range(total)]
})

# Export directly to local pipeline storage
df.to_csv('meridian_works_raw.csv', index=False)
print("Meridian Works raw data synchronized successfully.")
