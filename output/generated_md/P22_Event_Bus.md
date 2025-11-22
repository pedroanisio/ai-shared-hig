### P22. Event Bus

**Definition P22:**
$B = (publishers, subscribers, topics, broker)$

- $topics : Set⟨Topic⟩$ is event channels

**Type Definitions:**
```
Publisher := (id: ID, publish: (Topic, Event) → Effect)
Subscriber := (id: ID, handle: Event → Effect)
Topic := String
Event := (type: String, payload: Map⟨String, Value⟩, timestamp: Time)
```

**Properties:**

**P.P22.1 (Decoupling):**
```
Publishers don't know subscribers
Subscribers don't know publishers
```

**P.P22.2 (Many-to-Many):**
```
One event → multiple subscribers
One subscriber → multiple topics
```

**P.P22.3 (Async Delivery):**
```
publish(event) returns immediately
Delivery happens asynchronously
```

**Operations:**

1. **Subscribe:**
   ```
   subscribe(topic: Topic, subscriber: Subscriber) → Effect
   ```
   ```
   subscribe(topic: Topic, subscriber: Subscriber) → Effect
      = subscribers[topic] := subscribers[topic] ∪ {subscriber}
   ```

2. **Publish:**
   ```
   publish(topic: Topic, event: Event) → Effect
   ```
   ```
   publish(topic: Topic, event: Event) → Effect
      = for subscriber in subscribers[topic]:
          async_invoke(subscriber.handle, event)
   ```

3. **Unsubscribe:**
   ```
   unsubscribe(topic: Topic, subscriber: Subscriber) → Effect
   ```
   ```
   unsubscribe(topic: Topic, subscriber: Subscriber) → Effect
      = subscribers[topic] := subscribers[topic] ∖ {subscriber}
   ```

4. **At-Most-Once:**
   ```
   Fire and forget
      Fast but may lose events
   ```

5. **At-Least-Once:**
   ```
   Retry until acknowledged
      May duplicate events
   ```

6. **Exactly-Once:**
   ```
   Deduplication + acknowledgment
      Expensive but reliable
   ```

**Manifestations:**
- UI event system
- Component communication
- Plugin events
- Message queues

---
