program agent_otp_generate.aleo;

function generate_otp:
    input r0 as field.private;
    input r1 as field.private;
    input r2 as u64.private;
    input r3 as field.private;
    add r0 r1 into r4;
    cast r2 into r5 as field;
    add r4 r5 into r6;
    add r6 r3 into r7;
    hash.bhp256 r7 into r8 as field;
    cast r8 into r9 as u32;
    rem r9 1000000u32 into r10;
    output r10 as u32.private;
