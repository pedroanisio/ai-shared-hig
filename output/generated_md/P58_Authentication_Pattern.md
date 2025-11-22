### P58. Authentication Pattern

**Definition P58:**
$A = (users, credentials, sessions, verify, tokens)$

- $users : Map⟨UserID, User⟩$ is registered users

**Type Definitions:**
```
User := (id: UserID, username: String, email: String, roles: Set⟨Role⟩)
HashedPassword := String  // bcrypt, argon2, etc.
Session := (id: SessionID, user: UserID, created: Time, expires: Time, data: Map⟨String,Value⟩)
Token := String  // JWT, opaque token, etc.
```

**Properties:**

**P.P58.1 (Secure Storage):**
```
Passwords stored as secure hashes, never plaintext
```

**P.P58.2 (Session Expiration):**
```
∀session ∈ sessions: now() > session.expires ⇒ invalid(session)
```

**P.P58.3 (Token Security):**
```
Tokens cryptographically signed and time-limited
```

**Operations:**

1. **Register User:**
   ```
   register(username: String, password: String, email: String) → UserID
   ```
   ```
   register(username: String, password: String, email: String) → UserID
      = user_id := generate_id()
        hashed := hash_password(password)
        users[user_id] := User(user_id, username, email, {})
        credentials[user_id] := hashed
        return user_id
   ```

2. **Authenticate:**
   ```
   authenticate(username: String, password: String) → Session | null
   ```
   ```
   authenticate(username: String, password: String) → Session | null
      = user := find_user_by_username(username)
        if user = null:
          return null
        if verify_password(password, credentials[user.id]):
          session := create_session(user.id)
          sessions[session.id] := session
          return session
        else:
          return null
   ```

3. **Verify Password:**
   ```
   verify_password(plain: String, hashed: HashedPassword) → 𝔹
   ```
   ```
   verify_password(plain: String, hashed: HashedPassword) → 𝔹
      = return hash_function(plain) = hashed
   ```

4. **Create Session:**
   ```
   create_session(user_id: UserID) → Session
   ```
   ```
   create_session(user_id: UserID) → Session
      = session_id := generate_session_id()
        expires := now() + session_duration
        return Session(session_id, user_id, now(), expires, {})
   ```

5. **Validate Session:**
   ```
   validate_session(session_id: SessionID) → 𝔹
   ```
   ```
   validate_session(session_id: SessionID) → 𝔹
      = if session_id ∉ sessions:
          return false
        session := sessions[session_id]
        if now() > session.expires:
          delete sessions[session_id]
          return false
        return true
   ```

6. **Generate Token (JWT):**
   ```
   generate_token(user_id: UserID) → Token
   ```
   ```
   generate_token(user_id: UserID) → Token
      = payload := {
          user_id: user_id,
          issued_at: now(),
          expires_at: now() + token_ttl
        }
        token := sign(payload, secret_key)
        tokens[token] := user_id
        return token
   ```

7. **Session-Based:**
   ```
   Login → Create session → Store session ID in cookie
   ```
   ```
   Login → Create session → Store session ID in cookie
      Subsequent requests send session ID
      Server validates session
   ```

8. **Token-Based (JWT):**
   ```
   Login → Generate JWT → Send to client
   ```
   ```
   Login → Generate JWT → Send to client
      Client includes JWT in Authorization header
      Server validates JWT signature
   ```

9. **OAuth 2.0:**
   ```
   Redirect to OAuth provider → User authorizes
   ```
   ```
   Redirect to OAuth provider → User authorizes
      Provider returns authorization code
      Exchange code for access token
      Use token for API requests
   ```

10. **Multi-Factor (MFA):**
   ```
   Password (something you know)
      + TOTP/SMS code (something you have)
      + Biometric (something you are)
   - Use bcrypt/argon2 for password hashing
   - Implement rate limiting on login attempts
   - Use HTTPS for all authentication traffic
   - Rotate tokens/sessions regularly
   - Implement CSRF protection
   - Use secure cookie flags (HttpOnly, Secure, SameSite)
   ```

**Manifestations:**
- User login systems
- API authentication
- SSO (Single Sign-On)
- Multi-factor authentication

---
