program main.aleo {
  // One simplified record with all fields
  record Agent {
    owner: address,      // HR's account
    commit: field,       // Poseidon::hash([salt, bank_name, rep_id])
    status: u8,          // 1 = active, 0 = revoked
    perm_hash: field,    // Hash of the permission string
  }

  // Mint a new agent
  transition mint_agent(private commit: field, private perm_hash: field) -> Agent {
    // Return the agent record
    return Agent {
      owner: self.caller,
      commit: commit,
      status: 1u8,
      perm_hash: perm_hash
    };
  }

  
  // Revoke an agent - changes status to 0 (revoked)
  transition revoke_agent(agent: Agent) -> Agent {
    // Verify the caller is the owner
    assert_eq(agent.owner, self.caller);
    
    // Return new agent with status set to 0 (revoked)
    return Agent {
      owner: agent.owner,
      commit: agent.commit,
      status: 0u8,
      perm_hash: agent.perm_hash
    };
  }

  // Check if an agent has a specific permission
  transition has_permission(agent: Agent, permission: field) -> bool {
    // Calculate the hash and check if it matches
    return BHP256::hash_to_field(permission) == agent.perm_hash;
  }
}
