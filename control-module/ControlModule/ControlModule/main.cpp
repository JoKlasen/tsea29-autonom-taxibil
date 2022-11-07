/*
 * ControlModule.cpp
 *
 * Created: 06/11/2022 20:57:21
 * Author : Johan, Hannes
 */ 

#include <avr/io.h>

//Port Definitions
#define UART_RX RXD0 // 14
#define UART_TX TXD0 // 15

#define PWM OC1A    // 19
#define DIR PA0     // 40
#define BRAKE PA1   // 39
#define SERVO OC3A  // 7

//Constants
#define F_CPU 16000000UL
#define USART_BAUDRATE 9600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)	

#define MAX_SPEED_CONST = 0;


void port_init()
{
    PORTA = (1 << DIR) | (0 << BRAKE); // Testa om DIR = 1 Eller 0 blir frammåt
    DDRA = (1 << DIR) | (1 << BRAKE);

    PORTB = (0 << SERVO);
    DDRB = (1 << SERVO);

    PORTD = (0 << PWM) | (1 << TXD0) | (1 << RXD0);
    // output == 1 input == 0
    DDRD = (1 << PWM) | (1 << TXD10) | (0 << RXD0);
}

void UART_init()
{
    /* Set baud rate */
    UBRR0H = (BAUD_PRESCALE>>8);
    UBRR0L = BAUD_PRESCALE;
    
    /* Enable receiver and transmitter */
    UCSR0B = (1<<RXEN0)|(1<<TXEN0);
    /* Set frame format: 8data, 2stop bit */
    UCSR0C = (1<<USBS0)|(3<<UCSZ00)|(0<<UPM00)|(0<<UPM01);
}

void pwm_init()
{
	// Motor-timer 2000Hz (0.5ms) 1-2ms
	// Set Output Compare Register to 16000 which is 1 ms at 16MHz
	OCR1A = 8000; // == 0x1F40
	// CTC = Clear Timer on Compare-mode with no prescaler
	TCCR1A = (0<<WGM11)|(0<<WGM10); // COM1 in normal operation OC1A/B disabled
	TCCR1B = (1<<WGM12)|(1<<CS10);
	// Enable Output Compare A Match Interrupt Enable
	TIMSK1 = (1<<OCIE1A);
	
	// Servo-timer 50Hz (20ms) with 1-2ms PW
	// Set Output Compare Register to 16000 which is 1 ms at 16MHz
	OCR3A = 20*2000; // == 0x9C40
	// CTC = Clear Timer on Compare-mode with 1/8 prescaler
	TCCR3A = (0<<WGM31)|(0<<WGM30); // COM1 in normal operation OC1A/B disabled
	TCCR3B = (1<<WGM32)|(1<<CS31);
	// Enable Output Compare A Match Interrupt Enable
	TIMSK3 = (1<<OCIE3A);
}

void setup()
{
    port_init();
    UART_init();
}

void forward() {
	
}

void reverse() {
	
}

void left() {
	
}

void right() {
	
}

void speedlimiter(int speed) {
	if (speed > MAX_SPEED_CONST) {
		speed = MAX_SPEED_CONST;
	}
}

int main(void)
{
    setup();
    
    char* welcome_msg= "Hello World! :)\n";
    send_data(welcome_msg);
	
    while (1) 
    {
		int input;
		if (input = 1)
    }
}

