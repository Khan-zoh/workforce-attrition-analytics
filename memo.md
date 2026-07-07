---
title: "Where the Next Retention Dollar Should Go"
subtitle: "Workforce attrition — diagnostic, predictive, and prescriptive findings"
author: "Zohair Khan, Analytics"
date: "July 7, 2026"
---

**To:** HR Director
**Re:** Attrition drivers and a targeted retention plan
**Basis:** Company workforce snapshot, n = 1,470 employees *(method demonstration on IBM's public synthetic HR dataset; every number below is real output of the analysis, but describes that dataset, not a real company)*

---

## The headline

**237 of 1,470 employees (16.1%) left in the period analyzed — roughly $3.6M a year at a conservative $15K replacement cost per leaver.** That cost is not spread evenly: it concentrates in overtime workers, first-year employees, the lowest pay quartile, and one specific role. A predictive model built on this data can put **49% of future leavers inside a watch list covering just 10% of the workforce** — meaning a retention budget aimed with this list works about five times harder than one spread evenly.

## What is actually driving attrition

Out of 30 candidate factors tested (with corrections so chance findings don't slip through), the survivors cluster into **four driver themes** — several of the significant variables are the same underlying signal (tenure, seniority, and pay travel together), so we report themes rather than inflating the count:

**1. Overtime — the loudest signal, and the most directly testable lever.** Employees working overtime leave at **30.5% vs 10.4%** for everyone else. Controlling for pay, role, tenure, and satisfaction, overtime is still associated with roughly **6× higher odds** of leaving. This is not "busy people happen to leave" — the association holds after adjusting for everything else we measure (though only an actual intervention can prove the policy fixes it).

**2. The first two years.** Attrition is **34.9% in year 0–1**, falling to 18.4% in years 2–3 and 8.1% past year ten. Half the battle is getting people through year one.

**3. Low pay, specifically the bottom quartile.** The lowest-paid quartile leaves at **29.3%** vs **10.3%** in the top quartile. In the model, every additional $1,000/month of income is associated with measurably lower exit odds — and the cliff sits between Q1 and Q2, which makes the bottom quartile the natural first test for a targeted comp review.

**4. The Sales Representative role.** Nearly **4 in 10 Sales Reps left (39.8%)** — the worst rate of any role, in the role with the lowest median pay. Even after controlling for that pay, the role carries the single largest risk multiplier in the model, which suggests something about the job itself — quota structure, travel load (frequent travelers show 6× odds), career path — beyond compensation. The data can't say which; it says where to look.

Worth naming what *didn't* survive testing: gender, education field, commute distance, and pay-raise percentage show no dependable relationship with leaving. Several "obvious" factors are significant only on paper, with effects too small to justify spend — the analysis flags these explicitly so budget doesn't chase them.

## Where the next dollar goes

These are prioritized, testable interventions — the analysis identifies where risk concentrates; each program should be piloted and measured (ideally with a control group) before scaling:

1. **Cap or compensate overtime, starting in Sales and the lab-technician group.** Largest adjusted association, most directly controllable lever. The exposure is material: 416 overtime employees carrying a 20-point excess attrition rate represents on the order of $1M/year at the $15K cost assumption — the upper bound on what a successful overtime intervention could recover.
2. **Build a year-one program: structured onboarding, a 6-month check-in, and a first-year manager touchpoint.** The 0–1 year cohort (215 people, ~35% attrition) is the cheapest group to test because interventions are process, not payroll.
3. **Targeted comp review for the bottom pay quartile — not an across-the-board raise.** The attrition-pay association is concentrated in Q1 (29.3%); above the median the data shows almost no relationship, so that's where a raise dollar has the least evidence behind it.
4. **Redesign the Sales Representative job before backfilling it again.** At ~40% attrition, the company is paying to refill this role continuously, and the role effect persists after controlling for pay.

## Using the watch list responsibly

The watch list scores every employee 0–1 for exit risk (a calibrated logistic-regression probability — the same model behind every number in this memo) and annotates each person with their top risk pattern (e.g., "overtime") from a companion model. Two ground rules: **it targets support, not surveillance** — the output should trigger a manager conversation about workload or growth, never a preemptive write-off; and **it's a probability, not a verdict** — half the people on the list would have stayed anyway. Used that way, the top-decile list reaches ~49% of true leavers with 10% of the outreach effort.

## Caveats

- Everything here is an **association measured in observational snapshot data** — the recommendations are prioritized hypotheses with the strongest evidence behind them, not proven causal effects. That's why each intervention should ship with a measurement plan.
- The underlying dataset is synthetic (IBM's public HR sample) and this memo demonstrates the method; magnitudes are illustrative, direction and approach are transferable.
- The $15K/leaver cost is a deliberately conservative flat parameter (industry estimates for professional roles run 50–200% of salary); the dashboard exposes it as a slider so you can price scenarios yourself.
- The data is a snapshot: it distinguishes leavers within the period, and a production deployment would revalidate on a time split.

*Full analysis, dashboard, and reproducible code: github.com/Khan-zoh/workforce-attrition-analytics*
