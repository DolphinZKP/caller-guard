program agent_manager.aleo {
  // Agent record for call center employees
  record Agent {
    owner: address,         // HR admin address who created this record
    rep_id: field,          // Agent's representative ID
    bank_name: field,       // Bank/institution name  
    status: u8,             // 1 = active, 0 = revoked
    private permissions: field,  // Raw permission string/value
    private seed: field     // Secret seed for OTP generation
  }

  // Mint a new agent record
  transition mint_agent(
    private rep_id: field,
    private bank_name: field,
    private permissions: field,
    private seed: field
  ) -> Agent {
    // Return the agent record
    return Agent {
      owner: self.caller,
      rep_id: rep_id,
      bank_name: bank_name,
      status: 1u8,
      permissions: permissions,
      seed: seed
    };
  }

  // Revoke an agent - changes status to 0 (revoked)
  transition revoke_agent(agent: Agent) -> Agent {
    // Verify the caller is the owner
    assert_eq(agent.owner, self.caller);
    
    // Return new agent with status set to 0 (revoked)
    return Agent {
      owner: agent.owner,
      rep_id: agent.rep_id,
      bank_name: agent.bank_name,
      status: 0u8,
      permissions: agent.permissions,
      seed: agent.seed
    };
  }

  // Check if an agent has a specific permission
  transition has_permission(agent: Agent, permission: field) -> bool {
    // Verify the agent is active
    assert_eq(agent.status, 1u8);
    
    // Direct comparison with the permission field
    return agent.permissions == permission;
  }
}