program agent_manager.aleo {
  // Agent record for call center employees
  record Agent {
    owner: address,         // HR admin address who created this record
    private rep_id: field,  // Made private to protect agent identity
    private bank_name: field, // Made private to protect institutional association
    status: u8              // Public to allow verification of active status
  }

  // Mint a new agent record (removed unused permissions parameter)
  transition mint_agent(
    private rep_id: field,
    private bank_name: field
  ) -> Agent {
    // Return the agent record
    return Agent {
      owner: self.caller,
      rep_id: rep_id,
      bank_name: bank_name,
      status: 1u8
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
      status: 0u8
    };
  }

  // Added: Check if an agent is active
  transition is_agent_active(agent: Agent) -> bool {
    return agent.status == 1u8;
  }
}