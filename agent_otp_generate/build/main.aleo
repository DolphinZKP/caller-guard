program agent_otp_generate.aleo;

function generate_otp:
    input r0 as field.private;
    input r1 as field.private;
    input r2 as u64.private;
    input r3 as field.private;
    cast r2 into r4 as field;
    add r0 r3 into r5;
    hash.bhp256 r5 into r6 as field;
    add r1 r6 into r7;
    hash.bhp256 r7 into r8 as field;
    add r4 r8 into r9;
    hash.bhp256 r9 into r10 as field;
    cast r10 into r11 as u128;
    rem r11 1000000u128 into r12;
    cast r12 into r13 as u32;
    output r13 as u32.private;
