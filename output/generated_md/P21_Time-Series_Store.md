### P21. Time-Series Store

**Definition P21:**
$T = (series, timestamps, values, aggregations)$

- $series : Map⟨String, TimeSeries⟩$ is named series
- $timestamps : Sequence⟨Time⟩$ is ordered timestamps
- $values : Map⟨Time, Value⟩$ is data points

**Type Definitions:**
```
TimeSeries := Sequence⟨(timestamp: Time, value: Value)⟩
Aggregation := Sum | Avg | Min | Max | Count | ...
```

**Properties:**

**P.P21.1 (Temporal Ordering):**
```
timestamps are sorted: tᵢ < tᵢ₊₁
```

**P.P21.2 (Efficient Range Queries):**
```
range(t1, t2) uses binary search: O(log n + k) where k = result size
```

**Operations:**

1. **Range Query:**
   ```
   range(t1: Time, t2: Time) → TimeSeries
   ```
   ```
   range(t1: Time, t2: Time) → TimeSeries
      = {(t, v) ∈ series : t1 ≤ t ≤ t2}
   ```

2. **Aggregate:**
   ```
   aggregate(t1: Time, t2: Time, window: Duration, func: Aggregation) → TimeSeries
   ```
   ```
   aggregate(t1: Time, t2: Time, window: Duration, func: Aggregation) → TimeSeries
      = group points in windows, apply func to each window
   ```

**Manifestations:**
- Edit history
- Telemetry
- Sensor data
- User activity log
- Stock prices

---
