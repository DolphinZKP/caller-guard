# Business Logic for Agent Management System

This document outlines key business logics and considerations for the Aleo-based agent management system, focusing on the `agent_manager.aleo` program.

## Core Functionality (Implemented)

- **Agent Creation (Minting):** HR can create new agent records on the blockchain.
- **Agent Revocation:** HR can revoke an agent's access.
- **Agent Status Check:** Verify if an agent is currently active.

## Additional Business Logics & Considerations

Here are important aspects and potential edge cases to account for:

### 1. Duplicate Agent Prevention

- **Logic:** Ensure that no two agents are created with the same unique identifiers (e.g., `rep_id` and `bank_name`).
- **Implementation:** Primarily needs to be enforced off-chain in the backend system _before_ calling the `mint_agent` transition, as on-chain global lookups are not supported.

### 2. Agent Reactivation

- **Logic:** Allow a previously revoked agent to have their access reinstated.
- **Implementation:** Requires a new transition (e.g., `reactivate_agent`) to change the agent's status back to active (`1u8`).

### 3. Agent Expiry or Time-Limited Access

- **Logic:** Define an expiration date or time for agent validity.

- **Implementation:** Add an `expiry` field to the `Agent` record and update status/verification logic to check against the current time.

### 4. Revocation Reason

- **Logic:** Record why an agent's access was revoked.
- **Implementation:** Add a `revocation_reason` field to the `Agent` record and modify the `revoke_agent` transition to accept this reason.

### 5. Ownership Transfer

- **Logic:** Allow the current owner of an agent record to transfer ownership to another address.
- **Implementation:** Requires a `transfer_ownership` transition.

### 6. Soft Delete (Archiving)

- **Logic:** Mark an agent record as inactive or archived without permanently removing it.
- **Implementation:** Add a `deleted` boolean field or status code.

### 7. Multi-Role or Multi-Department Support

- **Logic:** Associate agents with multiple roles or departments for granular permissions.
- **Implementation:** Can be added as fields (e.g., array, bitmask) in the `Agent` record.

### 8. Rate Limiting / Abuse Prevention

- **Logic:** Limit actions (like OTP generation frequency) to prevent abuse.
- **Implementation:** Primarily handled off-chain in the backend application layer.

### 9. Audit Logging

- **Logic:** Record all significant actions for compliance and security analysis.
- **Implementation:** Log events off-chain in a secure database, potentially using on-chain data as verifiable input.

### 10. Access Control for Transitions

- **Logic:** Restrict who can call sensitive transitions (e.g., only HR admins can mint/revoke).
- **Implementation:** Add `assert_eq(self.caller, admin_address)` checks within the Leo transitions.

### 11. Agent Metadata

- **Logic:** Store additional non-sensitive information about the agent.
- **Implementation:** Can be added as fields in the `Agent` record or managed off-chain.

### 12. On-Chain/Off-Chain Consistency

- **Logic:** Ensure data in the on-chain record matches related off-chain data (like the seed).
- **Implementation:** Use checksums or hashes to cross-verify data during operations.

### 13. Error Handling and User Feedback

- **Logic:** Provide informative messages for failed operations.
- **Implementation:** Use Leo's assert statements, and enhance feedback in the backend Python code based on transaction results.

### 14. Agent Listing and Search

- **Logic:** Allow searching and listing agents based on criteria.
- **Implementation:** Best handled off-chain by indexing agent records retrieved from the blockchain in a database or search index.
