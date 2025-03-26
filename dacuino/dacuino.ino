#define BUFFER_SIZE 1024

#define BUFFER_FILL_REQUEST 1
#define BUFFER_FILL_RESPONSE 2
#define DEVICE_SET_SAMPLE_REQUEST 3

volatile uint8_t buffer_1[BUFFER_SIZE] = {0};
volatile uint8_t buffer_2[BUFFER_SIZE] = {0};
volatile uint8_t* front_buffer = buffer_1;
volatile uint8_t* back_buffer = buffer_2;
volatile unsigned int sample_pos = 0;
volatile bool buffer_ready = false;

void setup() {
  pinMode(9, OUTPUT);
  pinMode(10, OUTPUT);
  Serial.begin(0);  // Leonardo and its equivalent uses USB CDC, baud rate will be ignored
  cli();

  // Setup Timer1 for SPK PWM output (8Bit Fast PWM)
  // Reset Timer
  TCCR1A = 0;
  TCCR1B = 0;

  TCCR1A |= (1 << WGM10);
  TCCR1B |= (1 << WGM12) | (1 << CS10);  // no prescaling
  TCCR1A |= (1 << COM1A1);  // clear OC1A (pin 9) on compare match
  TCCR1A |= (1 << COM1B1);  // clear OC1B (pin 10) on compare match

  // Setup Timer3 for sample fetch and playback (16Bit CTC)
  TCCR3A = 0;
  TCCR3B = 0;
  TCCR3B |= (1 << WGM32) | (1 << CS30);

  OCR3A = F_CPU / 37500;

  TIMSK3 |= (1 << OCIE3A);  // enable interrupt on compare match

  sei();
}

ISR(TIMER3_COMPA_vect) {
  OCR1A = front_buffer[sample_pos++];
  OCR1B = front_buffer[sample_pos++];
  if (sample_pos >= BUFFER_SIZE) {
    sample_pos = 0;
    if (buffer_ready) {
      // swap buffers
      uint8_t* temp = front_buffer;
      front_buffer = back_buffer;
      back_buffer = temp;
      buffer_ready = false;
      Serial.write(BUFFER_FILL_REQUEST);
    }
  }
}

void buffer_fill() {
  Serial.readBytes((char*)back_buffer, BUFFER_SIZE);
  buffer_ready = true;
}

void loop() {
  if (!buffer_ready && Serial.available() > 0) {
    buffer_fill();
  }
}