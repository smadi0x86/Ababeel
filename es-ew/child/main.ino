#define RXD2 16
#define TXD2 17

typedef struct __attribute__((packed)) {
    uint8_t  msg_type;
    uint16_t track_id;
    uint32_t freq_khz;
    int16_t  rssi_scaled;
    int16_t  bearing_scaled;
    uint8_t  threat;
    uint8_t  protocol_id;
    uint32_t timestamp;
    uint8_t padding[15];
} TDL_Track;

void setup() {
  Serial.begin(115200);
  Serial2.begin(115200, SERIAL_8N1, RXD2, TXD2);
}

void loop() {
  if (Serial2.available() >= 32) {
    uint8_t buffer[32];
    size_t len = Serial2.readBytes(buffer, 32);

    if (len == 32) {
      TDL_Track msg;
      memcpy(&msg, buffer, 32);

      if (msg.msg_type == 0x01) {
        float freq_mhz = msg.freq_khz / 1000.0;
        float rssi = msg.rssi_scaled / 10.0;
        float bearing_deg = msg.bearing_scaled / 10.0;

        Serial.printf("TDL Track received - Freq: %.3f MHz | RSSI: %.1f dB | Bearing: %.1f° | Threat: %d\n",
                      freq_mhz, rssi, bearing_deg, msg.threat);

        Serial.printf("Starting terminal homing toward bearing %.1f°\n", bearing_deg);
      }
    }
  }
}
