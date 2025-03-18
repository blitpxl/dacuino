TCCR1B = 0b00000010
WGM12 = 3; CS11 = 1; CS10 = 0


print("bin: {:08b}".format(TCCR1B))
print("let: ABCDEFGH")
print(f"dec: {TCCR1B}")

# TCCR1B = (1 << WGM12) | (1 << CS11) | (1 << CS10); // Prescaler 64