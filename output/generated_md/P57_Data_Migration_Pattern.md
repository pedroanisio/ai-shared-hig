### P57. Data Migration Pattern

**Definition P57:**
$M = (versions, migrations, current, rollback)$

- $versions : Sequence⟨Version⟩$ is schema versions
- $current : Version$ is active version

**Type Definitions:**
```
Version := (number: ℕ, schema: Schema)
Migration := (up: Data → Data, down: Data → Data)
Schema := description of data structure
```

**Properties:**

**P.P57.1 (Bidirectionality):**
```
∀m ∈ migrations: ∃m⁻¹: m⁻¹(m(data)) = data
```

**P.P57.2 (Transactional):**
```
Migration completes fully or rolls back
```

**P.P57.3 (Version Ordering):**
```
versions totally ordered: v₁ < v₂ < v₃ < ...
```

**Operations:**

1. **Migrate Up:**
   ```
   migrate_up(target: Version) → Effect
   ```
   ```
   migrate_up(target: Version) → Effect
      = while current < target:
          migration := migrations[(current, next(current))]
          data := migration.up(data)
          current := next(current)
   ```

2. **Migrate Down:**
   ```
   migrate_down(target: Version) → Effect
   ```
   ```
   migrate_down(target: Version) → Effect
      = while current > target:
          migration := migrations[(prev(current), current)]
          data := migration.down(data)
          current := prev(current)
   ```

3. **Create Migration:**
   ```
   create_migration(from: Version, to: Version, up: Transform, down: Transform) → Migration
   ```
   ```
   create_migration(from: Version, to: Version, up: Transform, down: Transform) → Migration
      = Migration(up, down)
   ```

4. **Additive (Safe):**
   ```
   Add new fields with defaults
      No data loss
      Can roll back easily
   ```

5. **Transformative:**
   ```
   Change field types or structure
      Requires data transformation
      Test rollback carefully
   ```

6. **Destructive (Dangerous):**
   ```
   Remove fields or tables
      Potential data loss
      Ensure backups
   ```

**Manifestations:**
- Database schema migrations
- API version upgrades
- File format conversions
- Configuration updates

---
