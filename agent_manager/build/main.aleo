program agent_manager.aleo;

record Agent:
    owner as address.private;
    rep_id as field.private;
    bank_name as field.private;
    status as u8.private;

function mint_agent:
    input r0 as field.private;
    input r1 as field.private;
    cast self.caller r0 r1 1u8 into r2 as Agent.record;
    output r2 as Agent.record;

function revoke_agent:
    input r0 as Agent.record;
    assert.eq r0.owner self.caller;
    cast r0.owner r0.rep_id r0.bank_name 0u8 into r1 as Agent.record;
    output r1 as Agent.record;

function is_agent_active:
    input r0 as Agent.record;
    is.eq r0.status 1u8 into r1;
    output r1 as boolean.private;
