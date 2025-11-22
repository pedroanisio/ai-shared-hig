### P25. Streaming Protocol

**Definition P25:**
$S = (producer, consumer, buffer, backpressure, state)$

- $state : \{\text{flowing}, \text{paused}, \text{ended}, \text{error}\}$ is stream state

**Type Definitions:**
```
Producer := (generate: () → Chunk | EndOfStream, pause: () → Effect, resume: () → Effect)
Consumer := (consume: Chunk → Effect)
Chunk := Sequence⟨Byte⟩ | Value
```

**Properties:**

**P.P25.1 (Flow Control):**
```
buffer full → pause producer → wait → resume producer
```

**P.P25.2 (Chunk Ordering):**
```
Chunks consumed in order produced
```

**P.P25.3 (Graceful Termination):**
```
Producer sends EndOfStream → consumer processes remaining chunks → close
```

**Operations:**

1. **Produce:**
   ```
   produce() → Effect
   ```
   ```
   produce() → Effect
      = while state = flowing:
          chunk := producer.generate()
          if chunk = EndOfStream:
            state := ended
            consumer.close()
          else:
            buffer := enqueue(buffer, chunk)
            if buffer.size ≥ highWaterMark:
              state := paused
              producer.pause()
   ```

2. **Consume:**
   ```
   consume() → Effect
   ```
   ```
   consume() → Effect
      = while ¬empty(buffer):
          chunk := dequeue(buffer)
          consumer.consume(chunk)
          if buffer.size < lowWaterMark ∧ state = paused:
            state := flowing
            producer.resume()
   ```

3. **Readable Stream:**
   ```
   Data source (file, network)
      Can only read from
   ```

4. **Writable Stream:**
   ```
   Data sink (file, response)
      Can only write to
   ```

5. **Transform Stream:**
   ```
   Readable + Writable
      Transforms data in flight
      Example: compression, encryption
   ```

6. **Duplex Stream:**
   ```
   Independent readable and writable
      Example: WebSocket
   ```

**Manifestations:**
- WebSocket
- Live updates
- Progressive rendering
- File uploads/downloads
- Video streaming

---
