### P24. Request-Response API

**Definition P24:**
$A = (endpoints, handlers, middleware, responses)$

- $endpoints : Set⟨Endpoint⟩$ is API routes
- $middleware : Sequence⟨Middleware⟩$ is request interceptors

**Type Definitions:**
```
Endpoint := (method: Method, path: Path)
Method := GET | POST | PUT | DELETE | PATCH
Handler := Request → Response
Middleware := (Request, Next) → Response
Request := (method: Method, path: Path, headers: Map, body: Value)
Response := (status: ℕ, headers: Map, body: Value)
```

**Properties:**

**P.P24.1 (Stateless):**
```
Each request independent
No server-side session required (often)
```

**P.P24.2 (Idempotency):**
```
GET, PUT, DELETE are idempotent
Multiple identical requests = same result as single request
```

**P.P24.3 (Status Codes):**
```
2xx: Success
3xx: Redirection
4xx: Client error
5xx: Server error
```

**Operations:**

1. **Handle Request:**
   ```
   handle(request: Request) → Response
   ```
   ```
   handle(request: Request) → Response
      = for mw in middleware:
          request := mw(request, next)
        handler := handlers[request.endpoint]
        return handler(request)
   ```

2. **Register Endpoint:**
   ```
   register(endpoint: Endpoint, handler: Handler) → Effect
   ```
   ```
   register(endpoint: Endpoint, handler: Handler) → Effect
      = handlers[endpoint] := handler
   ```

3. **Add Middleware:**
   ```
   add_middleware(mw: Middleware) → Effect
   ```
   ```
   add_middleware(mw: Middleware) → Effect
      = middleware := middleware ++ [mw]
   - Authentication: Verify credentials
   - Logging: Log request/response
   - Rate limiting: Throttle requests
   - CORS: Handle cross-origin requests
   - Compression: Gzip responses
   ```

**Manifestations:**
- REST API
- RPC (gRPC)
- GraphQL
- Internal service APIs

---
