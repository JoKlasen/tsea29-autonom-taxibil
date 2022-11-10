/*
 * ControlModule.cpp
 *
 * Created: 06/11/2022 20:57:21
 * Author : Johan, Hannes
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <string.h>

//Port Definitions
#define UART_RX PD0 // 14
#define UART_TX PD1 // 15


#define PWM PD5    // 19
#define DIR PA0     // 40
#define BRAKE PA1   // 39
#define SERVO PB6  // 7

//Constants
#define F_CPU 16000000UL
#define USART_BAUDRATE 9600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)	

#define MAX_SPEED 0

#define MAX_STEER_LEFT 2100
#define STEER_NEUTRAL 3046 //Drar aningen åt vänster (välidgt lite)
#define MAX_STEER_RIGHT 4200

#define  STEER_REGISTER OCR3A
#define  SPEED_REGISTER OCR1A

volatile unsigned steering = STEER_NEUTRAL;

volatile bool manual_mode = true;

volatile bool man_left = false;
volatile bool man_right = false;
volatile bool man_forward = false;
volatile bool man_back = false;

void port_init()
{
    PORTA = (1 << DIR) | (0 << BRAKE); // Testa om DIR = 1 Eller 0 blir frammåt
    DDRA = (1 << DIR) | (1 << BRAKE);

    PORTB = (0 << SERVO);
    DDRB = (1 << SERVO);

    PORTD = (0 << PWM) | (1 << UART_TX) | (1 << UART_RX);
    // output == 1 input == 0
    DDRD = (1 << PWM) | (1 << UART_TX) | (0 << UART_RX);
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
	SPEED_REGISTER = 3000; // == 0x1F40
	ICR1 = 8000; // Set TOP (total period length) to 20 ms
	// CTC = Clear Timer on Compare-mode with no prescaler
	TCCR1A = (1<<COM1A1)|(0<<COM1A0)|(1<<WGM11)|(0<<WGM10); // COM1 in Clear on CTC, WGM in Fast PWM with ICR1 as TOP
	TCCR1B = (1<<WGM13)|(1<<WGM12)|(1<<CS10);
	// Enable Output Compare A Match Interrupt Enable
	TIMSK1 = (1<<OCIE1A);
	
	// Servo-timer 50Hz (20ms) with 1-2ms PW
	// Set Output Compare Register to 16000 which is 1 ms at 16MHz
	STEER_REGISTER = STEER_NEUTRAL; // == 0x9C40
	ICR3 = 20*2000;
	// CTC = Clear Timer on Compare-mode with 1/8 prescaler
	TCCR3A = (1<<COM3A1)|(0<<COM3A0)|(1<<WGM31)|(0<<WGM30); // COM1 in Clear on CTC, WGM in Fast PWM with ICR1 as TOP
	TCCR3B = (1<<WGM33)|(1<<WGM32)|(1<<CS31);
	// Enable Output Compare A Match Interrupt Enable
	TIMSK3 = (1<<OCIE3A);
}

void setup()
{
    port_init();
    UART_init();
	pwm_init();
}

void send_data(char* data)
{
	int counter=0;
	while(1)
	{
		while(!( UCSR0A & (1<<UDRE0)))
		;
		
		UDR0 = data[counter];
		if (data[counter] == '\0')
		{
			break;
		}
		counter++;
	}
}

void speedlimiter(int speed) {
	if (speed > MAX_SPEED) {
		speed = MAX_SPEED;
	}
}

void parse(char* data)
{
	int i = 0;
	char temp1;
	char temp2;
	char* command;
	
	bool findcommand = true;
	bool pid = false;
	bool switchmode = false;
	bool keys = false;
	
	for (char* c = data; *c != NULL; c++) 
	{
		temp2 = temp1;
		temp1 = *c;
		
		if (findcommand) {
			if (temp1 == ':') {
				strncpy(command, data, i);
				
				if (strcmp(command, "keyspressed")) 
				{
					keys = true;
					findcommand = false;
					i = 0;
				} else if (strcmp(command, "switchmode")) {
					switchmode = true;
					findcommand = false;
					i = 0;
				} else if (strcmp(command, "sendpid")) {
					pid = true;
					findcommand = false;
					i = 0;
				}
			}
		} else 
		{			
			if (temp1 == ':')
			{				
				if (keys)
				{
					if (i == 0)
					man_forward = temp2;
					else if (i == 1)
					man_left = temp2;
					else if (i == 2)
					man_back = temp2;
					else if (i == 3)
					man_right = temp2;
				}
				
				if (switchmode) {
					
				}
				
				if (pid) {
					
				}
			}
		
	
		}
		
		i++;
	}
	
}

int main(void)
{
    setup();
    
    char* welcome_msg= "Hello World! :)\n";
    send_data(welcome_msg);
	
    while (1) 
    {
		char* input = "left1:";
		parse(input);
		if (manual_mode)
		{
			// steering
			if (man_left)
				steering = MAX_STEER_LEFT;
			else if (man_right)
				steering = MAX_STEER_RIGHT;
			else
				steering = STEER_NEUTRAL;
			STEER_REGISTER = steering;
			
			if (man_back)
				//back = 0;
				SPEED_REGISTER = 0;
			else if (man_forward)
				SPEED_REGISTER = MAX_SPEED;
		}
		else
		{
			// autonomt med pid loop
		}

    }
}

