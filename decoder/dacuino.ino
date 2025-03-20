#define BUFFER_SIZE 2300

uint8_t data[BUFFER_SIZE];

// using doc: https://ww1.microchip.com/downloads/en/devicedoc/atmel-7766-8-bit-avr-atmega16u4-32u4_datasheet.pdf

volatile unsigned int sample_pos = 0;
volatile uint8_t last = 0;

void setup() {
  pinMode(9, OUTPUT);
  Serial.begin(9600);
  cli();

  // setup Timer1 to be on 8 bit Fast PWM mode
  TCCR1A = 0;
  TCCR1B = 0;
  TCCR1A |= (1 << WGM10);
  TCCR1B |= (1 << WGM12) | (1 << CS10);
  TCCR1A |= (1 << COM1A1);

  // setup Timer3 to be on 16 bit CTC mode
  TCCR3A = 0;
  TCCR3B = 0;
  TCCR3B |= (1 << WGM32) | (1 << CS30);

  OCR3A = F_CPU / 16000;

  TIMSK3 |= (1 << OCIE3A);

  sei();
}

uint8_t buffer[1] = {128};
unsigned int x = 0;

ISR(TIMER3_COMPA_vect) {
  OCR1A = data[sample_pos];
  sample_pos++;
  if (sample_pos >= BUFFER_SIZE) {
    Serial.write(1);
    sample_pos = 0;
  }
}

void loop() {
  if (Serial.available() > 0) {
    Serial.readBytes(data, BUFFER_SIZE);
  }
}