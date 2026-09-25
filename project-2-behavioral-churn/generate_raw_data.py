import random, csv
random.seed(11)

N = 8400
THIRDS = ['Weak', 'Average', 'Strong']
THIRD_N = N // 3  # 2800 each, exact
ROW_N = {'neg': 3238, 'nonneg': N - 3238}  # 5162
ROW_CANCEL = {'neg': 1328, 'nonneg': 464}  # sums to 1792, matches col total below
COL_CANCEL = {'Weak': 952, 'Average': 532, 'Strong': 308}  # 34%/19%/11% of 2800 exactly

# 1) Build 6-cell population sizes (row x col), independence assumption, integer-exact via largest remainder
cells = {}
raw = {}
for r, rn in ROW_N.items():
    for c in THIRDS:
        raw[(r, c)] = rn * THIRD_N / N
floor_sum = 0
for k, v in raw.items():
    cells[k] = int(v)
    floor_sum += cells[k]
remainder = N - floor_sum
# distribute remainder to largest fractional parts
fracs = sorted(raw.items(), key=lambda kv: (kv[1] - int(kv[1])), reverse=True)
for i in range(remainder):
    cells[fracs[i][0]] += 1
assert sum(cells.values()) == N

# 2) IPF on cancel counts within cells to hit both row and column cancel totals
# start proportional to population, then rescale rows, then columns, iterate
prob = {k: ROW_CANCEL['neg']/ROW_N['neg'] if k[0]=='neg' else ROW_CANCEL['nonneg']/ROW_N['nonneg'] for k in cells}
cell_cancel = {k: prob[k]*cells[k] for k in cells}
for _ in range(60):
    # rescale to row targets
    for r in ROW_N:
        cur = sum(cell_cancel[(r,c)] for c in THIRDS)
        if cur > 0:
            f = ROW_CANCEL[r]/cur
            for c in THIRDS: cell_cancel[(r,c)] *= f
    # rescale to col targets
    for c in THIRDS:
        cur = sum(cell_cancel[(r,c)] for r in ROW_N)
        if cur > 0:
            f = COL_CANCEL[c]/cur
            for r in ROW_N: cell_cancel[(r,c)] *= f

# round to integers, clip to population size, patch rounding drift onto largest cell
cell_cancel_int = {k: min(cells[k], round(v)) for k,v in cell_cancel.items()}
drift = sum(ROW_CANCEL.values()) - sum(cell_cancel_int.values())
if drift != 0:
    biggest = max(cell_cancel_int, key=lambda k: cells[k])
    cell_cancel_int[biggest] += drift

print('population cells', cells)
print('cancel cells', cell_cancel_int)
row_check = {r: sum(cell_cancel_int[(r,c)] for c in THIRDS)/ROW_N[r] for r in ROW_N}
col_check = {c: sum(cell_cancel_int[(r,c)] for r in ROW_N)/THIRD_N for c in THIRDS}
print('row rates', row_check)
print('col rates', col_check)

# 3) Materialize subscribers
REGIONS = ['Midwest','West','Northeast','South']
PLANS = ['Monthly Essentials','Monthly Plus','Quarterly Bundle']
THIRD_RANGE = {'Weak': (35, 55), 'Average': (55, 75), 'Strong': (75, 100)}

subs = []
sid = 10000
for (row, third), pop in cells.items():
    n_cancel = cell_cancel_int[(row, third)]
    flags = [True]*n_cancel + [False]*(pop-n_cancel)
    random.shuffle(flags)
    for cancelled in flags:
        lo, hi = THIRD_RANGE[third]
        score = round(random.uniform(lo, hi), 1)
        has_neg = (row == 'neg')
        if has_neg:
            days_before = round(random.uniform(0, 14), 1)  # negative ticket WITHIN the 14-day pre-renewal window
        else:
            days_before = None  # no negative ticket in that window (may have had one much earlier, or none)
        region = random.choice(REGIONS)
        plan = random.choice(PLANS)
        tenure_months = random.randint(1, 24)
        monthly_price = {'Monthly Essentials': 39, 'Monthly Plus': 59, 'Quarterly Bundle': 149}[plan]
        total_spent = round(monthly_price * tenure_months * random.uniform(0.9, 1.1), 2)
        subs.append({
            'SubscriberID': f"S-{sid}", 'Region': region, 'Plan': plan,
            'OnboardingScore': score, 'HasNegativeTicketPreRenewal': has_neg,
            'Cancelled': cancelled, 'TotalSpent': total_spent,
            'DaysBeforeRenewalLastNegativeTicket': days_before,
        })
        sid += 1

random.shuffle(subs)
print('generated', len(subs))

# ---- write messy raw CSV: duplicate orders, free-text cancellation reasons,
# mixed currency, missing sentiment (handled via ticket table concept -> here as
# blank negative-ticket day field, already None=missing), inconsistent bools ----
def messy_bool(b):
    r = random.random()
    if r < 0.4: return 'Yes' if b else 'No'
    if r < 0.6: return '1' if b else '0'
    return str(b)

def messy_money(v):
    r = random.random()
    if r < 0.3: return f"${v:,.2f}"
    if r < 0.5: return f"USD {v:.2f}"
    return f"{v:.2f}"

CANCEL_REASONS = ['too expensive','found alternative','no longer needed','poor quality','bad support experience',
                   'shipping issues','moving/relocating','paused indefinitely','']

raw_header = ['subscriber_id','region','plan','onboarding_score','negative_ticket_pre_renewal',
              'cancelled','total_spent','days_before_renewal_negative_ticket','cancellation_reason']
raw_rows=[]
dup=0
for s in subs:
    reason = random.choice(CANCEL_REASONS) if s['Cancelled'] else ''
    row = [s['SubscriberID'], s['Region'], s['Plan'], s['OnboardingScore'],
           messy_bool(s['HasNegativeTicketPreRenewal']), messy_bool(s['Cancelled']),
           messy_money(s['TotalSpent']),
           '' if s['DaysBeforeRenewalLastNegativeTicket'] is None else s['DaysBeforeRenewalLastNegativeTicket'],
           reason]
    raw_rows.append(row)
    if random.random() < 0.015 and dup < 90:  # duplicate retried-checkout order rows
        raw_rows.append(row)
        dup += 1

with open('solmere_churn_raw.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(raw_header)
    w.writerows(raw_rows)
print('raw csv written, rows incl dup:', len(raw_rows), 'dups:', dup)
