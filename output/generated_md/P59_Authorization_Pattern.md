### P59. Authorization Pattern

**Definition P59:**
$Z = (subjects, objects, permissions, policies, check)$

- $subjects : Set⟨Subject⟩$ is actors (users, services)
- $objects : Set⟨Object⟩$ is resources
- $permissions : Set⟨Permission⟩$ is allowed actions

**Type Definitions:**
```
Subject := User | Service | Group
Object := Resource(id: ID, type: Type, owner: Subject)
Permission := (subject: Subject, object: Object, actions: Set⟨Action⟩)
Action := Read | Write | Execute | Delete | Share | Admin
Policy := (condition: Predicate, effect: Allow | Deny)
```

**Properties:**

**P.P59.1 (Least Privilege):**
```
Default deny: access denied unless explicitly allowed
```

**P.P59.2 (Policy Evaluation):**
```
Explicit deny overrides allow
Multiple policies combined with AND
```

**P.P59.3 (Inheritance):**
```
Group permissions inherited by members
Parent resource permissions inherited by children
```

**Operations:**

1. **Check Permission:**
   ```
   check(subject: Subject, object: Object, action: Action) → 𝔹
   ```
   ```
   check(subject: Subject, object: Object, action: Action) → 𝔹
      = policies_applicable := filter(policies, λp: p.applies(subject, object, action))
        // Check for explicit deny
        if ∃p ∈ policies_applicable: p.effect = Deny:
          return false
        // Check for explicit allow
        if ∃p ∈ policies_applicable: p.effect = Allow:
          return true
        // Default deny
        return false
   ```

2. **Grant Permission:**
   ```
   grant(subject: Subject, object: Object, actions: Set⟨Action⟩) → Effect
   ```
   ```
   grant(subject: Subject, object: Object, actions: Set⟨Action⟩) → Effect
      = permission := Permission(subject, object, actions)
        permissions := permissions ∪ {permission}
   ```

3. **Revoke Permission:**
   ```
   revoke(subject: Subject, object: Object) → Effect
   ```
   ```
   revoke(subject: Subject, object: Object) → Effect
      = permissions := permissions ∖ {p : p.subject = subject ∧ p.object = object}
   ```

4. **Evaluate Policy:**
   ```
   evaluate_policy(policy: Policy, context: Context) → Allow | Deny
   ```
   ```
   evaluate_policy(policy: Policy, context: Context) → Allow | Deny
      = if policy.condition(context):
          return policy.effect
        else:
          return NotApplicable
   ```

5. **Role-Based Access Control (RBAC):**
   ```
   Users assigned to roles
      Roles have permissions
      user → roles → permissions → resources
      Example:
        Admin role: can do everything
        Editor role: can read, write
        Viewer role: can read only
   ```

6. **Attribute-Based Access Control (ABAC):**
   ```
   Policies based on attributes of subject, object, environment
      Example:
        Allow if user.department = resource.department
        Allow if time_of_day between 9am and 5pm
   ```

7. **Access Control Lists (ACL):**
   ```
   Each resource has list of allowed subjects and actions
      Example:
        document123.acl = [
          (alice, Read|Write),
          (bob, Read),
          (admin_group, *)
        ]
   ```

8. **Ownership:**
   ```
   Resource owner has full control
      Owner can grant permissions to others
   Policy 1: Owner full access
     condition: subject = object.owner
     effect: Allow all actions
   Policy 2: Department access
     condition: subject.department = object.department
     effect: Allow Read
   Policy 3: Admin access
     condition: subject.role = Admin
     effect: Allow all actions
   Policy 4: Deny deleted users
     condition: subject.status = Deleted
     effect: Deny all actions
   ```

**Manifestations:**
- File permission systems
- API authorization
- Database row-level security
- Cloud resource access (AWS IAM)

---
