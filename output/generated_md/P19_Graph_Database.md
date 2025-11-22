### P19. Graph Database

**Definition P19:**
$G = (nodes, edges, props, traversal)$

- $nodes : Set⟨Node⟩$ is entities
- $edges : Set⟨Edge⟩$ is relationships
- $props : (Node | Edge) → Map⟨String, Value⟩$ is properties

**Type Definitions:**
```
Node := (id: ID, labels: Set⟨String⟩)
Edge := (id: ID, from: Node, to: Node, type: String)
Path := Sequence⟨(Node | Edge)⟩
Query := pattern matching query (Cypher, SPARQL, etc.)
```

**Properties:**

**P.P19.1 (Efficient Traversal):**
```
traverse(node, depth) in O(k·d) where k = avg degree, d = depth
```

**P.P19.2 (Property Graph Model):**
```
Both nodes and edges can have properties
```

**Operations:**

1. **Match Pattern:**
   ```
   MATCH (a:Person)-[:KNOWS]->(b:Person) WHERE a.name = "Alice"
      RETURN b
   ```

2. **Shortest Path:**
   ```
   shortest_path(node1, node2) → Path | null
   ```
   ```
   shortest_path(node1, node2) → Path | null
   ```

**Manifestations:**
- Knowledge graphs
- Dependency graphs
- Citation networks
- Social networks

---
