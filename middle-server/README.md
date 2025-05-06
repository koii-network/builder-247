# Middleware Server Documentation

## Replay Attack Prevention

The middleware includes a mechanism to prevent replay attacks on server routes. This is implemented through the `preventReplayAttack` middleware.

### Replay Attack Prevention Mechanism

- Each request must include two special headers:
  1. `x-request-nonce`: A unique identifier for the request
  2. `x-request-timestamp`: The timestamp when the request was created

- The middleware checks:
  1. Nonce uniqueness (prevents duplicate requests)
  2. Request timestamp (prevents very old requests)
  3. Maintains an in-memory store of used nonces

### Client Usage Example

```typescript
import axios from 'axios';
import { generateNonce } from './middleware/auth';

const { nonce, timestamp } = generateNonce();

const response = await axios.post('/your-endpoint', data, {
  headers: {
    'x-request-nonce': nonce,
    'x-request-timestamp': timestamp.toString()
  }
});
```

### Security Notes

- Nonces are stored in-memory and expire after 5 minutes
- Each nonce can only be used once
- Requests with duplicate or expired nonces are rejected