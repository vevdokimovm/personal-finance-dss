"""Б-04, второй проход: насколько ДАЛЕКО уезжает план при ошибке во входе."""
import sys, random, statistics
sys.path.insert(0, "/Users/vasyaevdokimov/repos/personal-finance-dss")
from app.core.alternatives import generate_alternatives, evaluate_alternative
from app.core.filtering import filter_alternatives
from app.core.ranking import rank_alternatives
R_BENCH = 0.14

def best_shares(income, expense, obls, goals, bliq, profile):
    pay = sum(o["monthly_payment"] for o in obls)
    rt = income - expense - pay
    if rt <= 0: return None
    goals_total = sum(g.get("target_amount", 0) for g in goals)
    alts = generate_alternatives(rt, pay, goals_total)
    ev = [evaluate_alternative(dict(a), income, expense, obls, goals, R_BENCH, bliq) for a in alts]
    ok, _ = filter_alternatives(ev, dt_current=(pay/income if income else 0))
    if not ok: return None
    ranked = rank_alternatives(ok, risk_tolerance=profile)
    b = max(ranked, key=lambda a: (a.get("floor_level",0), a.get("utility",0)))
    tot = b.get("x_obligations",0)+b.get("x_reserve",0)+b.get("x_goals",0)
    if tot <= 0: return None
    return (b["x_obligations"]/tot, b["x_reserve"]/tot, b["x_goals"]/tot)

def make(rng):
    income = rng.choice([45000,70000,95000,130000,180000,250000])
    expense = income*rng.uniform(0.45,0.80)
    obls=[]
    for i in range(rng.randint(1,3)):
        amt=rng.uniform(40000,900000); rate=rng.choice([0.055,0.09,0.12,0.155,0.19,0.24,0.35])
        obls.append({"id":f"o{i}","name":f"К{i}","amount":round(amt,2),"interest_rate":rate,
                     "monthly_payment":round(amt*rng.uniform(0.02,0.05),2)})
    goals=[{"id":f"g{j}","name":f"Ц{j}","target_amount":round(rng.uniform(50000,700000),2),
            "current_amount":0.0,"category":rng.choice(["safety","material","income","emotional"]),
            "deadline_months":rng.randint(4,48)} for j in range(rng.randint(1,2))]
    return income, round(expense,2), obls, goals, round(income*rng.uniform(0.2,4.0),2)

rng=random.Random(20260922)
shifts={0.005:[],0.02:[],0.05:[]}
valid=0
for _ in range(400):
    income,expense,obls,goals,bliq=make(rng); prof=rng.randint(1,5)
    base=best_shares(income,expense,obls,goals,bliq,prof)
    if base is None: continue
    valid+=1
    for e in shifts:
        worst=0.0
        for sign in (1,-1):
            w=best_shares(income,round(expense*(1+sign*e),2),obls,goals,bliq,prof)
            if w is None: continue
            d=sum(abs(a-b) for a,b in zip(base,w))/2   # доля потока, ушедшая в другое русло
            worst=max(worst,d)
        shifts[e].append(worst)
print(f"портретов: {valid}")
print(f"{'ошибка расходов':>16} | {'медиана сдвига':>15} | {'p90':>7} | {'макс':>7} | {'сдвиг ≥10 пп':>13}")
for e,v in shifts.items():
    if not v: continue
    v_sorted=sorted(v); p90=v_sorted[int(len(v_sorted)*0.9)]
    big=sum(1 for x in v if x>=0.10)/len(v)*100
    print(f"{e*100:>14.1f}% | {statistics.median(v)*100:>13.1f} пп | {p90*100:>5.1f} пп | {max(v)*100:>5.1f} пп | {big:>11.1f}%")
