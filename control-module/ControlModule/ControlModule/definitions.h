#ifndef DEFINITIONS_F
#define DEFINITIONS_F

//Port Definitions
#define UART_RX PD0 // 14
#define UART_TX PD1 // 15


#define PWM PD5    // 19
#define DIR PA0     // 40
#define BRAKE PA1   // 39
#define SERVO PB6  // 7

//Constants
#define F_CPU 16000000UL
#define USART_BAUDRATE 57600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)

#define MAX_SPEED 4000

#define MAX_STEER_LEFT 2100
#define STEER_NEUTRAL 3046 //Drar aningen åt vänster (välidgt lite)
#define MAX_STEER_RIGHT 4200

#define ONE_THOUSAND_RIGHT ((MAX_STEER_RIGHT - STEER_NEUTRAL) / 1000)

#define  STEER_REGISTER OCR3A
#define  SPEED_REGISTER OCR1A

#define RECEIVE_BUFFER_SIZE 100


void clear_buffer(char* buffer,int size = RECEIVE_BUFFER_SIZE);

void send_data(char * buffer);

unsigned long long millis();

void port_init();

void UART_init();

void pwm_init();

void timer2_init();

void setup();

void send_data(char* data);

void speedlimiter(int speed);

void pid_init(int in_p, int in_i, int in_d);

int pid_loop(int error);

bool parse_handshake();

void handshake();

void parse(char input[]);

int PIDIteration(int Error);

void PIDSetup(int InputP, int InputI, int InputD);

#endif