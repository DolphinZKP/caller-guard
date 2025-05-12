# CallerGuard Encryption Method

## Core Concept

CallerGuard uses a commit hash derived from `Hash([salt, bank_name, rep_id])` to securely represent agents on the blockchain.

## Why This Approach?

- **Massive Pre-image Space**: The pre-image space becomes 2¹²⁸ × |bank| × |rep_id|, making brute-force attacks infeasible even for short 4-6 character codes.
- **No View-Keys Required**: No view-keys or ZK circuits over private strings needed—just standard public mappings.
- **Blockchain Efficiency**: Lightweight on-chain implementation with minimal fields and maps, resulting in low gas usage.

## Off-Chain Flow

### HR Onboards an Agent

1. Generate a random 128-bit salt in your HSM or KMS.
2. Compute: `commit = H(salt || bank_name || rep_id)`
3. Call `leo run mint_agent private commit:<FIELD>` signed by HR.
4. Store `(agent_id, salt, bank_name, rep_id, otp_seed)` encrypted in your DB/HSM.

### Agent Generates OTP

1. Agent's local wallet (or Server B during verification) pulls only its otp_seed.
2. Use standard HMAC-TOTP ±1 window to display a 6-digit code.

### Customer Verifies

1. iOS app captures: bank_name, rep_id, code.
2. Server B recomputes commit from its stored salt, bank_name, and rep_id.
3. Checks on-chain: `leo query agents key:commit` → must be true.
4. Recomputes OTP from otp_seed (hardened in HSM).
5. Returns ✅ only if both on-chain status is active and OTP matches.

## Security & Efficiency

| Property               | Why This Design Wins                               |
| ---------------------- | -------------------------------------------------- |
| Privacy of rep_id      | Protected by salted hash; no short-ID brute force. |
| No on-chain secrets    | All private data (ID, seed, salt) stays off-chain. |
| No view-keys           | Simplifies your contract and node setup.           |
| Audit & revocation     | Instant on-chain revoke; public, tamper-proof.     |
| ZK proof size          | Minimal: no private strings in the circuit.        |
| Operational simplicity | Only need one clan of HSM/KMS and one Aleo node.   |

## Salt Implementation Details

### Why per-agent salt?

Each agent must have a unique salt to prevent rainbow table attacks. If the same salt were used for all agents, an attacker could build a rainbow table of all possible bank_name‖rep_id combinations under that fixed salt.

### How to generate a salt

```python
import os
salt = os.urandom(16)               # 128 bits of randomness
salt_field = int.from_bytes(salt, 'big')
```

### Where to store the salt

Store it in your secure off-chain database (or HSM-backed vault) alongside the agent's record:

```
Table: agents
┌──────────┬────────────────────┬──────────┬─────────────┐
│ agent_id │ salt_encrypted     │ rep_id   │ otp_seed    │
├──────────┼────────────────────┼──────────┼─────────────┤
│ …        │ <AES(salt)>        │ "E8938"  │ <…>         │
└──────────┴────────────────────┴──────────┴─────────────┘
```

Encrypt the salt before writing it to disk so even your DB can't reveal it in plaintext.

### Using the salt

When you need the on-chain commitment, fetch and decrypt the salt, then compute:

```python
commit = poseidon_hash([salt_field, bank_name, rep_id])
```

Pass this commit into your `mint_agent` transition or into your leo query lookup during verification.

### Memory hygiene

Treat the salt like the OTP seed—decrypt it only when needed, immediately zero memory afterward, and discard temporary variables.

## When to Consider Private Fields + View-Keys

If you cannot tolerate any risk of pre-image brute forcing (even 2¹²⁸×36⁶), consider:

1. Making rep_id a private string in your record.
2. Storing only a commitment on-chain.
3. Using Aleo's view-key mechanism so only view-key holders can access that field.

However, this approach comes with drawbacks:

- Larger ZK circuits (private-string handling)
- Complexity of securely managing view-keys/HSMs for every verifier

**Bottom line**: For 4-6 character IDs, salted hashing + off-chain secret management delivers nearly the same privacy as full private fields, while keeping your Aleo program and proof sizes tiny, operations fast, and infrastructure simple.
