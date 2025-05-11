program main.aleo;

record Agent:
    owner as address.private;
    commit as field.private;
    status as u8.private;
    perm_hash as field.private;

function mint_agent:
    input r0 as field.private;
    input r1 as field.private;
    cast self.caller r0 1u8 r1 into r2 as Agent.record;
    output r2 as Agent.record;

function revoke_agent:
    input r0 as Agent.record;
    assert.eq r0.owner self.caller;
    cast r0.owner r0.commit 0u8 r0.perm_hash into r1 as Agent.record;
    output r1 as Agent.record;

function has_permission:
    input r0 as Agent.record;
    input r1 as field.private;
    hash.bhp256 r1 into r2 as field;
    is.eq r2 r0.perm_hash into r3;
    output r3 as boolean.private;
