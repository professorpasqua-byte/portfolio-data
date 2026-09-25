import random, csv, datetime
random.seed(21)

N_A, N_B = 20000, 20000
CR_A, CR_B = 0.342, 0.516
completed_A = round(N_A * CR_A)   # 6840
completed_B = round(N_B * CR_B)   # 10320
dropped_A = N_A - completed_A     # 13160

# Variant A's 12 fields, three named in the portfolio at fixed shares of ALL
# Variant-A abandonment, the remaining nine sharing the rest.
FIELD_SHARE = {
    'Bank routing number': 0.27, 'Employer name': 0.19, 'Phone verification': 0.16,
    'Full name': 0.02, 'Email address': 0.02, 'Date of birth': 0.03,
    'Home address': 0.04, 'Job title': 0.03, 'Annual income': 0.05,
    'Bank account number': 0.08, 'Government ID number': 0.06, 'Password creation': 0.05,
}
assert abs(sum(FIELD_SHARE.values()) - 1.0) < 1e-9
assert round(sum(v for k,v in FIELD_SHARE.items() if k not in
    ('Bank routing number','Employer name','Phone verification')), 2) == 0.38

field_counts = {k: round(v*dropped_A) for k,v in FIELD_SHARE.items()}
drift = dropped_A - sum(field_counts.values())
field_counts['Bank account number'] += drift  # absorb rounding drift into a mid-size bucket
assert sum(field_counts.values()) == dropped_A

print('completed_A', completed_A, 'dropped_A', dropped_A)
print('field_counts', field_counts, 'sum', sum(field_counts.values()))

DEVICES = ['iOS', 'Android']

subs = []
uid = 500000

def make_session(variant, completed, dropoff_field):
    global uid
    device = random.choice(DEVICES)
    if variant == 'Variant A':
        duration = round(random.uniform(4, 15), 1) if completed else round(random.uniform(1.5, 9), 1)
    else:
        duration = round(random.uniform(1.5, 5), 1) if completed else round(random.uniform(0.5, 3), 1)
    ts = datetime.datetime(2026, random.randint(1,9), random.randint(1,28),
                            random.randint(0,23), random.randint(0,59))
    subs.append({
        'SessionID': f"U-{uid}", 'AssignedVariant': variant, 'DeviceType': device,
        'CompletedSignup': completed, 'DropoffField': dropoff_field,
        'DurationMin': duration, 'EventTimestampUTC': ts,
    })
    uid += 1

for _ in range(completed_A):
    make_session('Variant A', True, None)
for field, cnt in field_counts.items():
    for _ in range(cnt):
        make_session('Variant A', False, field)
for _ in range(completed_B):
    make_session('Variant B', True, None)
for _ in range(N_B - completed_B):
    make_session('Variant B', False, None)

random.shuffle(subs)
print('generated', len(subs))
E_A = sum(1 for s in subs if s['AssignedVariant']=='Variant A')
E_B = sum(1 for s in subs if s['AssignedVariant']=='Variant B')
print('A', E_A, 'B', E_B)

# ---- write messy raw CSV ----
# Timestamps arrive in 3 different client time zones (need normalizing to UTC).
TZ_OFFSETS = [('+00:00', 0), ('-05:00', -5), ('+05:30', 5.5)]

def local_ts(utc_dt):
    label, off = random.choice(TZ_OFFSETS)
    local = utc_dt + datetime.timedelta(hours=off)
    return local.strftime('%Y-%m-%dT%H:%M:%S') + label

def messy_bool(b):
    return random.choice(['TRUE','FALSE']) if False else ('true' if b else 'false')

raw_header = ['session_id','assigned_variant','device_type','completed_signup','dropoff_field','duration_min','event_timestamp']
raw_rows = []
for s in subs:
    raw_rows.append([
        s['SessionID'], s['AssignedVariant'], s['DeviceType'],
        messy_bool(s['CompletedSignup']),
        s['DropoffField'] or '',
        s['DurationMin'],
        local_ts(s['EventTimestampUTC']),
    ])

# Inject sessions with a broken/missing variant flag (must be dropped, not guessed)
n_broken = 380
for i in range(n_broken):
    global_uid = 900000 + i
    raw_rows.append([f"U-{global_uid}", random.choice(['', 'NULL', 'Unassigned']), random.choice(DEVICES),
                      messy_bool(random.random()<0.3), '', round(random.uniform(1,10),1), local_ts(datetime.datetime(2026,5,10,12,0,0))])

# Inject bot sessions: completed the full 12-field form in under 2 seconds (non-human).
# duration_min is in MINUTES, so "under 2 seconds" is under 2/60 = 0.033 minutes.
n_bots = 210
for i in range(n_bots):
    global_uid = 950000 + i
    raw_rows.append([f"U-{global_uid}", 'Variant A', random.choice(DEVICES), 'true', '',
                      round(random.uniform(0.005, 0.03), 4), local_ts(datetime.datetime(2026,6,1,3,0,0))])

random.shuffle(raw_rows)
with open('tallywell_funnel_raw.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(raw_header)
    w.writerows(raw_rows)
print('raw csv written, rows:', len(raw_rows), '(includes', n_broken, 'broken-flag +', n_bots, 'bot rows to be cleaned out)')
