import pandas as pd
import random

total = 1000
target_churn = 68 

df = pd.DataFrame({
    'SubscriberID': [f"S-{10000 + i}" for i in range(total)],
    'Region': [random.choice(['South', 'Midwest', 'West', 'Northeast']) for _ in range(total)],
    'Plan': [random.choice(['Monthly Essentials', 'Monthly Plus', 'Quarterly Bundle']) for _ in range(total)],
    'OnboardingScore': [random.randint(50, 100) for _ in range(total)],
    'HasNegativeTicketPreRenewal': [random.choice([True, False]) for _ in range(total)],
    'Cancelled': [True] * target_churn + [False] * (total - target_churn),
    'TotalSpent': [random.randint(200, 1100) for _ in range(total)],
    'DaysBeforeRenewalLastNegativeTicket': [random.randint(1, 14) for _ in range(total)]
})

df.to_csv('solmere_churn_raw.csv', index=False)
print("🎯 Solmere raw data synchronized!")
