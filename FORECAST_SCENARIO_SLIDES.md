# 30-Day Forecast & Scenario Analysis

## Slide 1: What This Section Means

The 30-Day Forecast & Scenarios section helps estimate how much money may be collected soon.

It answers one main question:

> Based on the current customers and their risk levels, how much money can we expect to collect?

Speaker note:
This is not exact cash already collected. It is a projection based on expected weekly payments and customer risk.

---

## Slide 2: Daily Projection

Daily Projection estimates how much money may be collected per day.

The system starts with active customers' weekly payments:

```text
Total Weekly Payments / 7 days
```

Then it reduces the amount depending on how many customers are On Track.

Example:

```text
Weekly Expected = MK 7,000,000
Daily Base = MK 7,000,000 / 7
Daily Base = MK 1,000,000
```

If only 60% of customers are On Track:

```text
Daily Projection = MK 1,000,000 x 60%
Daily Projection = MK 600,000
```

---

## Slide 3: 30-Day Forecast

30-Day Forecast estimates expected collection over the next 30 days.

Formula:

```text
Daily Projection x 30
```

Example:

```text
Daily Projection = MK 600,000
30-Day Forecast = MK 600,000 x 30
30-Day Forecast = MK 18,000,000
```

Speaker note:
This number changes when dashboard filters change, such as contractor, risk, location, state, or due date.

---

## Slide 4: Confidence

Confidence shows how reliable the forecast is.

The system checks how many active customers are High Risk or Critical.

Simple meaning:

```text
More risky customers = lower confidence
More On Track customers = higher confidence
```

Example:

If many customers are High Risk or Critical, the forecast may still show money expected, but confidence will be lower.

Speaker note:
Confidence is a risk signal. It does not guarantee collection. It tells us whether the forecast should be trusted strongly or treated carefully.

---

## Slide 5: Monthly Projection

Monthly Projection estimates a conservative monthly amount.

Formula:

```text
Total Weekly Payments x 4 weeks x 70%
```

Example:

```text
Weekly Expected = MK 7,000,000
Monthly Base = MK 7,000,000 x 4
Monthly Base = MK 28,000,000
Monthly Projection = MK 28,000,000 x 70%
Monthly Projection = MK 19,600,000
```

Speaker note:
The 70% makes this projection conservative, because not every expected payment may come in.

---

## Slide 6: Scenario Analysis

Scenario Analysis shows three possible outcomes:

```text
Conservative
Realistic
Optimistic
```

It separates customers into two groups:

```text
On Track customers
At-risk customers
```

At-risk customers include:

```text
Medium Risk, High Risk, Critical
```

Speaker note:
This helps management understand low, middle, and better-case collection possibilities.

---

## Slide 7: Conservative Scenario

The Conservative scenario is the cautious case.

It assumes:

```text
60% of On Track customers pay
5% of at-risk customers pay
```

Use this when:

```text
Collection performance is weak
Many customers are risky
The team wants a careful estimate
```

---

## Slide 8: Realistic Scenario

The Realistic scenario is the middle estimate.

It assumes:

```text
80% of On Track customers pay
20% of at-risk customers pay
```

Use this when:

```text
Collections are normal
Follow-ups are happening
Risk is manageable
```

---

## Slide 9: Optimistic Scenario

The Optimistic scenario is the best case.

It assumes:

```text
100% of On Track customers pay
30% of at-risk customers pay
```

Use this when:

```text
Collections are strong
Contractors are following up well
At-risk customers are responding
```

---

## Slide 10: Simple Summary

```text
Daily Projection = expected money per day
30-Day Forecast = expected money over 30 days
Confidence = how much we can trust the forecast
Monthly Projection = conservative monthly estimate
Scenario Analysis = low, middle, and high collection possibilities
```

Final explanation:

The forecast tells us what we may collect.

The confidence tells us how risky that estimate is.

The scenarios show what could happen under different collection performance levels.
