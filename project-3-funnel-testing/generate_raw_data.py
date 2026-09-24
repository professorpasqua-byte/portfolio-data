import pandas as pd
import numpy as np
import random

np.random.seed(101)
random.seed(101)

total_users = 1000  # Structured cohort scale
sub_ids = [f"S-{10000 + i}" for i in range(total_users)]

df = pd.DataFrame({
    'SubscriberID': sub_ids,
    'Region': [random.choice(['South', 'Midwest', 'West', 'Northeast']) for _ in range(total_users)],
    'Plan': [random.choice(['Monthly Essentials', 'Monthly Plus', 'Quarterly Bundle']) for _ in range(total_users)],
    'OnboardingScore': [round(random.uniform(40.0, 100.0), 1) for _ in range(total_users)],
    'HasNegativeTicketPreRenewal': [random.choice([True, False]) for _ in range(total_users)]
})

# Behavioral Economics logic insertion: Bad experiences drive cancellations
cancelled = []
days_before = []
for idx, row in df.iterrows():
    if row['HasNegativeTicketPreRenewal']:
        # High likelihood of churn due to bad memory (Peak-End Rule)
        cancelled.append(random.choices([True, False], weights=[0.78, 0.22])[0])
        days_before.append(round(random.uniform(1.0, 14.0), 0))
    else:
        # Low likelihood of churn with standard account health
        cancelled.append(random.choices([True, False], weights=[0.12, 0.88])[0])
        days_before.append(None)

df['Cancelled'] = cancelled
df['TotalSpent'] = [round(random.uniform(150.0, 1300.0), 2) for _ in range(total_users)]
df['DaysBeforeRenewalLastNegativeTicket'] = days_before

df.to_csv('solmere_churn_raw.csv', index=False)
print("🎯 Project 2: 'solmere_churn_raw.csv' synthesized successfully.")
