program agent_otp_generate.aleo;

closure internal_generate_otp:
    input r0 as u64;
    rem r0 1000000u64 into r1;
    cast r1 into r2 as u32;
    div r0 60u64 into r3;
    rem r3 100u64 into r4;
    rem r4 10u64 into r5;
    cast r5 into r6 as u8;
    cast r6 into r7 as u32;
    pow 10u32 r7 into r8;
    rem r2 r8 into r9;
    div 1000000u32 r8 into r10;
    mul r9 r10 into r11;
    div r2 r8 into r12;
    add r11 r12 into r13;
    rem r13 1000000u32 into r14;
    output r14 as u32;

function generate_otp:
    input r0 as field.private;
    input r1 as field.private;
    input r2 as u64.private;
    input r3 as field.private;
    call internal_generate_otp r2 into r4;
    output r4 as u32.private;

function prove_otp_generation:
    input r0 as field.private;
    input r1 as field.private;
    input r2 as field.private;
    input r3 as u64.public;
    input r4 as u32.public;
    call internal_generate_otp r3 into r5;
    is.eq r5 r4 into r6;
    assert.eq r6 true;
    output true as boolean.private;
