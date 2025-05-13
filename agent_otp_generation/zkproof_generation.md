# ZK Proof Generation for OTP – Documentation

## Overview

This document describes how to generate and prove the correctness of one-time passwords (OTPs) using zero-knowledge (ZK) proofs with the Aleo blockchain. The ZK proof demonstrates that an OTP was generated using authorized, private agent data and a public timestamp, without revealing the sensitive data itself.

---

## Steps for ZK Proof Generation

### 1. Generate the OTP

Use the public transition to compute the OTP for given inputs:

```sh
leo run generate_otp "<rep_id>" "<bank_name>" "<timestamp>u64" "<seed>"
```

**Example:**

```sh
leo run generate_otp "1233field" "5678field" "1747100401u64" "123field"
```

Example output:

```
• 100401u32
```

### 2. Generate the ZK Proof

Use the ZK-SNARK transition with the private agent data and the public OTP/timestamp:

```sh
leo run prove_otp_generation "<rep_id>" "<bank_name>" "<seed>" "<timestamp>u64" "<otp>u32"
```

**Example:**

```sh
leo run prove_otp_generation "1233field" "5678field" "123field" "1747100401u64" "100401u32"
```

On success, you will see:

```
➡️  Output

 • true

       Leo ✅ Finished 'agent_otp_generate.aleo/prove_otp_generation'
```

---

## What Does Success Mean?

- The output `true` confirms that the ZK circuit constraints were satisfied.
- This means the proof was successfully generated: **The provided OTP is valid for the given timestamp and was generated using the correct (private) agent data.**
- The proof can now be exported and verified by any party using the corresponding verifier, without revealing the agent's secret data.

---

## Example

**Inputs:**

- rep_id: `1233field`
- bank_name: `5678field`
- seed: `123field`
- timestamp: `1747100401u64`
- otp: `100401u32`

**Proof Generation Command:**

```sh
leo run prove_otp_generation "1233field" "5678field" "123field" "1747100401u64" "100401u32"
```

**Expected Output:**

```
➡️  Output

 • true

       Leo ✅ Finished 'agent_otp_generate.aleo/prove_otp_generation'
```

---

## Next Steps

- The generated proof and public inputs can be shared with a verifier (e.g., a bank or client app).
- The verifier can use the corresponding Aleo verifier program to check the proof's validity and the authenticity of the OTP.

---

**This process ensures secure, privacy-preserving, and verifiable OTP authentication using zero-knowledge proofs on Aleo.**
