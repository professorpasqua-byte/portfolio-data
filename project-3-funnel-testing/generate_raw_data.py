import pandas as pd
import numpy as np
import random

np.random.seed(777)
random.seed(777)

total_traffic = 2000
user_ids = [f"U-{50000 + i}" for i in range(total_traffic)]

variants = ['Control'] * 1000 + ['Experiment'] * 1000
df = pd.DataFrame({
    'UserID': user_ids,
    'AssignedVariant': variants
})

steps = []
completed = []
for idx, row in df.iterrows():
    v = row['AssignedVariant']
    if v == 'Control':
        # Hard manual inputs cause massive ability/friction leaks
        success = random.choices([True, False], weights=[0.342, 0.658])[0]
        completed.append(success)
        steps.append('Completed' if success else random.choice(['Started', 'IdentityVerified', 'BankLinkingAttempted']))
    else:
        # Automated open-banking API links maximize conversion flow
        success = random.choices([True, False], weights=[0.516, 0.484])[0]
        completed.append(success)
        steps.append('Completed' if success else random.choice(['Started', 'IdentityVerified', 'BankLinkingAttempted']))

df['StepReached'] = steps
df['CompletedSignup'] = completed
df['DurationMin'] = [round(random.uniform(2.1, 15.5), 1) for _ in range(total_traffic)]
df['DeviceType'] = [random.choice(['iOS', 'Android']) for _ in range(total_traffic)]

df.to_csv('tallywell_funnel_raw.csv', index=False)
print("🎯 Project 3: 'tallywell_funnel_raw.csv' synthesized successfully.")
