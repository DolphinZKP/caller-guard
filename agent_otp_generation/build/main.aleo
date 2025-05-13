program agent_otp_generate.aleo;

function generate_otp:
    input r0 as field.private;
    input r1 as field.private;
    input r2 as u64.private;
    input r3 as field.private;
    rem r2 1000000u64 into r4;
    cast r4 into r5 as u32;
    div r2 60u64 into r6;
    rem r6 100u64 into r7;
    rem r7 10u64 into r8;
    cast r8 into r9 as u8;
    cast r9 into r10 as u32;
    pow 10u32 r10 into r11;
    rem r5 r11 into r12;
    div 1000000u32 r11 into r13;
    mul r12 r13 into r14;
    div r5 r11 into r15;
    add r14 r15 into r16;
    rem r16 1000000u32 into r17;
    output r17 as u32.private;
