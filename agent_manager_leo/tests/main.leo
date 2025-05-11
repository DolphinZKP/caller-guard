program main.aleo {
    import main;

    function test_mint_grant_revoke_cycle() {
        // Precompute a salted commit and a permission hash
        let commit     = Poseidon::hash(["mysalt", "Acme Bank", "E8938"]);
        let perm_hash  = Poseidon::hash(["CanOpenAccount"]);

        // 1) Cannot revoke a non-existent agent (uncomment to assert failure)
        // let _ = callerguard::revoke_agent(Agent { owner: address("aleo1..."), commit, status:1u8 });

        // 2) Mint agent successfully
        let agent1 = callerguard::mint_agent(private commit);
        assert(agent1.status == 1u8);
        assert(agent1.commit == commit);

        // 3) Duplicate mint should fail (uncomment to assert failure)
        // let _ = callerguard::mint_agent(private commit);

        // 4) Grant a permission
        let ok1 = callerguard::grant_permission(agent1, private perm_hash);
        assert(ok1 == true);
        assert(Mapping::contains(callerguard::agent_permissions, (commit, perm_hash)));

        // 5) Revoke that permission
        let ok2 = callerguard::revoke_permission(agent1, private perm_hash);
        assert(ok2 == true);
        assert(!Mapping::contains(callerguard::agent_permissions, (commit, perm_hash)));

        // 6) Revoke (deactivate) the agent
        let agent2 = callerguard::revoke_agent(agent1);
        assert(agent2.status == 0u8);

        // 7) Remint after revoke restores active status
        let agent3 = callerguard::mint_agent(private commit);
        assert(agent3.status == 1u8);

        // 8) Previous permissions cleared upon remint
        assert(!Mapping::contains(callerguard::agent_permissions, (commit, perm_hash)));
    }
}
