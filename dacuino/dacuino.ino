#define BUFFER_SIZE 1024
#define BUFFER_FILL_REQUEST 1

volatile uint8_t buffer_1[BUFFER_SIZE] = {0};
volatile uint8_t buffer_2[BUFFER_SIZE] = {0};
volatile uint8_t* front_buffer = buffer_1;
volatile uint8_t* back_buffer = buffer_2;
volatile unsigned int sample_pos = 0;
volatile bool buffer_ready = false;
bool sample_rate_set = false;

void setup() {
  pinMode(9, OUTPUT);
  Serial.begin(5000000);
  cli();

  // Setup Timer1 for SPK PWM output (8Bit Fast PWM)
  // Reset Timer
  TCCR1A = 0;
  TCCR1B = 0;

  TCCR1A |= (1 << WGM10);
  TCCR1B |= (1 << WGM12) | (1 << CS10);  // no prescaling
  TCCR1A |= (1 << COM1A1);  // clear OC1A (pin 9) on compare match

  // Setup Timer3 for sample fetch and playback (16Bit CTC)
  TCCR3A = 0;
  TCCR3B = 0;
  TCCR3B |= (1 << WGM32) | (1 << CS30);

  OCR3A = F_CPU / 8000;

  TIMSK3 |= (1 << OCIE3A);  // enable interrupt on compare match

  sei();
}

ISR(TIMER3_COMPA_vect) {
  OCR1A = front_buffer[sample_pos];
  sample_pos++;
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

void loop() {
  if (!buffer_ready && Serial.available() > 0) {
    if (!sample_rate_set) {
      uint16_t sample_rate;
      Serial.readBytes(reinterpret_cast<uint8_t*>(&sample_rate), sizeof(uint16_t));
      OCR3A = F_CPU / sample_rate;
      sample_rate_set = true;
    }

    Serial.readBytes((char*)back_buffer, BUFFER_SIZE);
    buffer_ready = true;
  }
}