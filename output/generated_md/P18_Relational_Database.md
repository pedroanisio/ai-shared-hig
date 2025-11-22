### P18. Relational Database

**Definition P18:**
$R = (tables, schemas, constraints, indices)$

- $tables : Map⟨String, Table⟩$ is data tables

**Type Definitions:**
```
Table := Set⟨Row⟩
Row := Map⟨String, Value⟩  // column → value
Schema := Sequence⟨(name: String, type: Type, constraints: Set⟨Constraint⟩)⟩
Constraint := PrimaryKey | ForeignKey | Unique | NotNull | Check(predicate)
```

**Properties:**

**P.P18.1 (ACID):**
```
Atomicity: Transactions complete fully or not at all
Consistency: Constraints always satisfied
Isolation: Concurrent transactions don't interfere
Durability: Committed changes persist
```

**P.P18.2 (Relational Algebra):**
```
Queries expressed as: SELECT, PROJECT, JOIN, UNION, DIFFERENCE
```

**Operations:**

1. **Insert:**
   ```
   INSERT INTO table VALUES (...)
   ```

2. **Select:**
   ```
   SELECT columns FROM table WHERE predicate ORDER BY columns
   ```

3. **Join:**
   ```
   SELECT * FROM table1 JOIN table2 ON table1.key = table2.foreign_key
   ```

**Manifestations:**
- Content database
- File metadata
- User data
- Application state

---
