program callerguard.aleo {
  record Agent {
    owner:    address,      // HR’s account
    commit:   field,        // Poseidon::hash([salt, bank_name, rep_id])
    status:   u8,           // 1 = active, 0 = revoked
  }

  mapping agents: field => bool;
  mapping agent_permissions: (field, field) => bool;

  transition mint_agent(private commit: field) -> Agent {
    assert(!Mapping::contains(agents, commit));
    Mapping::set(agents, commit, true);
    return Agent { owner: self.caller, commit, status: 1u8 };
  }

  transition grant_permission(agent: Agent, private perm_hash: field) -> bool {
    assert_eq(agent.owner, self.caller);
    Mapping::set(agent_permissions, (agent.commit, perm_hash), true);
    true
  }

  transition revoke_permission(agent: Agent, private perm_hash: field) -> bool {
    assert_eq(agent.owner, self.caller);
    Mapping::set(agent_permissions, (agent.commit, perm_hash), false);
    true
  }

  transition revoke_agent(agent: Agent) -> Agent {
    assert_eq(agent.owner, self.caller);
    return Agent { owner: agent.owner, commit: agent.commit, status: 0u8 };
  }
}
