import random, datetime
random.seed(42)

DEPTS = [
  ('Human Resources', [
    ('HR Partner', 48, 11, [2.61,2.72,2.54,2.93,2.90]),
    ('HR Manager', 12, 2, [3.05,2.88,2.81,2.52,2.90]),
  ]),
  ('Engineering', [
    ('Software Engineer', 280, 40, [2.78,2.71,2.80,2.68,2.70]),
    ('QA Analyst', 250, 58, [2.52,2.66,2.58,2.62,2.55]),
    ('Data Engineer', 150, 16, [2.92,2.75,2.71,2.74,2.79]),
    ('Support Engineer', 130, 18, [2.74,2.70,2.66,2.70,2.73]),
    ('Engineering Lead', 85, 8, [2.81,2.84,2.68,2.83,2.77]),
    ('Engineering Manager', 65, 5, [2.90,2.86,2.72,2.88,2.84]),
  ]),
  ('Sales', [
    ('Account Executive', 330, 68, [2.66,2.70,2.74,2.71,2.79]),
    ('Sales Development Rep', 100, 32, [2.58,2.53,2.50,2.57,2.88]),
    ('Sales Manager', 50, 3, [2.64,2.72,2.77,2.85,2.76]),
  ]),
]
AGE = [('18-25',90,55),('26-33',300,80),('34-41',360,60),('42-49',270,40),('50-57',150,18),('58+',69,8)]
SEN = [('0-1',150,110),('2-3',240,70),('4-5',300,40),('6-7',210,20),('8-10',170,12),('11-15',110,6),('16+',59,3)]
FEMALE = {'Human Resources':(62,69),'Engineering':(41,38),'Sales':(52,49)}
INCOME = {'Human Resources':(5120,4380),'Engineering':(6940,5870),'Sales':(6210,5690)}

def age_bracket_range(b):
    if b=='58+': return (58,65)
    lo,hi=b.split('-'); return (int(lo),int(hi))
def sen_bracket_range(b):
    if b=='16+': return (16,22)
    lo,hi=b.split('-'); return (int(lo),int(hi))

# 1. build employee skeleton per role
emps=[]
eid=1000
for dept,roles in DEPTS:
    for role,total,term,scores in roles:
        for i in range(total):
            terminated = i < term
            emps.append({'id':eid,'dept':dept,'role':role,'terminated':terminated,'scores_target':scores})
            eid+=1
random.shuffle(emps)

# 2. assign age brackets: split active pool and term pool per AGE counts
active=[e for e in emps if not e['terminated']]
term=[e for e in emps if e['terminated']]
assert len(active)==1239 and len(term)==261, (len(active),len(term))
random.shuffle(active); random.shuffle(term)
ai=0
for label,acount,tcount in AGE:
    for e in active[ai:ai+acount]:
        lo,hi=age_bracket_range(label); e['age']=random.randint(lo,hi)
    ai+=acount
ti=0
for label,acount,tcount in AGE:
    for e in term[ti:ti+tcount]:
        lo,hi=age_bracket_range(label); e['age']=random.randint(lo,hi)
    ti+=tcount

# 3. tenure brackets same way (reshuffle pools independently)
random.shuffle(active); random.shuffle(term)
ai=0
for label,acount,tcount in SEN:
    for e in active[ai:ai+acount]:
        lo,hi=sen_bracket_range(label); e['tenure']=round(random.uniform(lo,hi),2)
    ai+=acount
ti=0
for label,acount,tcount in SEN:
    for e in term[ti:ti+tcount]:
        lo,hi=sen_bracket_range(label); e['tenure']=round(random.uniform(lo,hi),2)
    ti+=tcount

# 4. gender per dept, active/term split
by_dept={}
for e in emps: by_dept.setdefault(e['dept'],[]).append(e)
for dept,elist in by_dept.items():
    a=[e for e in elist if not e['terminated']]; t=[e for e in elist if e['terminated']]
    fa_pct,ft_pct=FEMALE[dept]
    random.shuffle(a); random.shuffle(t)
    n_fa=round(len(a)*fa_pct/100); n_ft=round(len(t)*ft_pct/100)
    for e in a[:n_fa]: e['gender']='Female'
    for e in a[n_fa:]: e['gender']='Male'
    for e in t[:n_ft]: e['gender']='Female'
    for e in t[n_ft:]: e['gender']='Male'

# 5. income per dept active/term, normal around target mean
for dept,elist in by_dept.items():
    ia,it_=INCOME[dept]
    for e in elist:
        base = ia if not e['terminated'] else it_
        e['income']=max(2500, round(random.gauss(base, base*0.08)))

# 6. survey scores: for each role, generate per-employee ints 1-4 hitting target mean per metric
by_role={}
for e in emps: by_role.setdefault((e['dept'],e['role']),[]).append(e)
def make_scores(n, target_mean):
    lo=int(target_mean); hi=lo+1
    if hi>4: hi=4; lo=4
    frac=target_mean-lo
    n_hi=round(frac*n)
    vals=[hi]*n_hi + [lo]*(n-n_hi)
    random.shuffle(vals)
    return vals
METRIC_NAMES=['EnvironmentSatisfaction','JobInvolvement','JobSatisfaction','RelationshipSatisfaction','WorkLifeBalance']
for (dept,role),elist in by_role.items():
    scores_target = elist[0]['scores_target']
    n=len(elist)
    cols=[make_scores(n,t) for t in scores_target]
    for idx,e in enumerate(elist):
        for m,col in zip(METRIC_NAMES,cols):
            e[m]=col[idx]

today = datetime.date(2026,9,25)
for e in emps:
    hire = today - datetime.timedelta(days=round(e['tenure']*365.25))
    e['hire_date']=hire
    e['term_date']= hire+datetime.timedelta(days=round(e['tenure']*365.25)) if e['terminated'] else None

random.shuffle(emps)
print('generated', len(emps))


# ---- write messy raw CSV ----
import csv
random.seed(7)

FIRST=['Maria','Tomas','Li','Priya','James','Okafor','Anna','David','Sofia','Wei','John','Fatima','Carlos','Emma','Noah','Aisha','Lucas','Mei','Omar','Grace','Ivan','Nina','Paul','Rosa','Sven','Talia','Umar','Vera','Yusuf','Zoe','Hana','Igor','Julia','Kenji','Lara','Miguel','Nadia','Oscar','Petra','Quinn']
LAST=['Silva','O\'Brien','Wei','Nair','Okafor','Garcia','Chen','Smith','Kowalski','Andersson','Diallo','Popescu','Haddad','Nakamura','Ivanov','Santos','Kim','Novak','Duarte','Weber','Osei','Rossi','Kaur','Farah','Lindgren']

def messy_name(fn,ln):
    r=random.random()
    if r<0.2: return f"  {fn.lower()} {ln.upper()} "
    if r<0.4: return f"{fn.upper()} {ln}"
    if r<0.6: return f"{fn} {ln}"
    return f"{fn.title()} {ln}"

DEPT_TYPO = {
  'Human Resources': ['HR','Human Resources','human resources '],
  'Engineering': ['Eng.','engineering','Engineering '],
  'Sales': ['Sal3s','sales ','Sales'],
}

def fmt_date(d):
    y,m,dd = d.year, d.month, d.day
    r=random.random()
    if r<0.25: return f"{dd:02d}/{m:02d}/{y}"
    if r<0.5: return f"{y}-{m:02d}-{dd:02d}"
    if r<0.75:
        months=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        return f"{dd} {months[m-1]} {y}"
    return f"{y}/{m:02d}/{dd:02d}"

def fmt_income(v):
    r=random.random()
    if r<0.15: return f"${v:,}"
    if r<0.3: return f"{v:,}.00"
    if r<0.4: return "-1"  # impossible income
    return str(v)

def fmt_score(v):
    r=random.random()
    if r<0.06: return {1:'low',2:'medium',3:'high',4:'very high'}[v]
    if r<0.1: return 'n/a'
    if r<0.13: return str(random.choice([0,5,6]))  # out of range
    return str(v)

rows=[]
header=['emp_id','full_name','department','job_role','hire_date','term_date','monthly_income','age','gender','tenure_years',
        'environment_satisfaction','job_involvement','job_satisfaction','relationship_satisfaction','work_life_balance']

dup_count=0
for e in emps:
    fn=random.choice(FIRST); ln=random.choice(LAST)
    dept_variant = random.choice(DEPT_TYPO[e['dept']])
    term_date = e['term_date']
    if term_date is None:
        term_str = random.choice(['','NULL','N/A'])
    else:
        term_str = fmt_date(term_date)
    row = {
        'emp_id': f"E-{e['id']}",
        'full_name': messy_name(fn,ln),
        'department': dept_variant,
        'job_role': e['role'],
        'hire_date': fmt_date(e['hire_date']),
        'term_date': term_str,
        'monthly_income': fmt_income(e['income']),
        'age': e['age'],
        'gender': e['gender'],
        'tenure_years': e['tenure'],
        'environment_satisfaction': fmt_score(e['EnvironmentSatisfaction']),
        'job_involvement': fmt_score(e['JobInvolvement']),
        'job_satisfaction': fmt_score(e['JobSatisfaction']),
        'relationship_satisfaction': fmt_score(e['RelationshipSatisfaction']),
        'work_life_balance': fmt_score(e['WorkLifeBalance']),
    }
    rows.append(row)
    # inject ~2% exact duplicate rows (different casing) to mirror the RAW example
    if random.random() < 0.02 and dup_count < 30:
        dup = dict(row)
        dup['full_name'] = dup['full_name'].upper()
        rows.append(dup)
        dup_count += 1

with open('meridian_works_raw.csv','w',newline='') as f:
    w=csv.DictWriter(f, fieldnames=header)
    w.writeheader()
    for r in rows: w.writerow(r)

print('rows written (incl dups):', len(rows), 'dups injected:', dup_count)
