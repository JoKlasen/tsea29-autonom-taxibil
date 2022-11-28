
#include "definitions.h"
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "global_variables.h"

void port_init()
{
	PORTA = (1 << LED1) | (0 << LED2);
	DDRA = (1 << LED1) | (1 << LED2);
	
	PORTB = (1 << DIR) | (0 << BRAKE) | (0 << SERVO);
	DDRB =	(1 << DIR) | (1 << BRAKE) | (1 << SERVO);

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
	/* Set frame format: 8data, 1stop bit */
	UCSR0C = (0<<USBS0)|(3<<UCSZ00)|(0<<UPM00)|(0<<UPM01);
	
	UCSR0B |= (1 << RXCIE0);
}

ISR (USART0_RX_vect)
{
	
	unsigned char from_receive_buffer = UDR0;
	receive_buffer[(receive_buffer_index)++] = from_receive_buffer;


	if((from_receive_buffer == '\0') || ((receive_buffer_index) == RECEIVE_BUFFER_SIZE-2) || (from_receive_buffer == '\n') || (from_receive_buffer == ';'))
	{
		receive_buffer[receive_buffer_index] = from_receive_buffer;
		strlcpy(working_buffer,receive_buffer,receive_buffer_index);
		memset(receive_buffer,0,receive_buffer_index);
		receive_buffer_index =0;
		received = true;


	}
}

void pwm_init()
{
	// Motor-timer 2000Hz (0.5ms)
	// Set Output Compare Register to 16000 which is 1 ms at 16MHz
	SPEED_REGISTER = 0; // == 0x1F40
	ICR1 = 8000; // Set TOP (total period length) to 20 ms
	// CTC = Clear Timer on Compare-mode with no prescaler
	TCCR1A = (1<<COM1A1)|(0<<COM1A0)|(1<<WGM11)|(0<<WGM10); // COM1 in Clear on CTC, WGM in Fast PWM with ICR1 as TOP
	TCCR1B = (1<<WGM13)|(1<<WGM12)|(1<<CS10);
	// Enable Output Compare A Match Interrupt Enable
	//TIMSK1 = (1<<OCIE1A); -- Får inte ha dessa om vi inte använder interruptsen programmet kommer restarta i en infinite loop
	
	// Servo-timer 50Hz (20ms) with 1-2ms PW
	// Set Output Compare Register to 16000 which is 1 ms at 16MHz
	STEER_REGISTER = STEER_NEUTRAL; // == 0x9C40
	ICR3 = 20*2000;
	// CTC = Clear Timer on Compare-mode with 1/8 prescaler
	TCCR3A = (1<<COM3A1)|(0<<COM3A0)|(1<<WGM31)|(0<<WGM30); // COM1 in Clear on CTC, WGM in Fast PWM with ICR1 as TOP
	TCCR3B = (1<<WGM33)|(1<<WGM32)|(1<<CS31);
	// Enable Output Compare A Match Interrupt Enable
	//TIMSK3 = (1<<OCIE3A); -- får inte ha detta om vi inte använder interrupten programmet kommer restarta i en infinite loop
}


void timer2_init()
{
	// Set Output Compare Register to 160 which is 10 us at 16MHz
	OCR2A = 250; // 1 millisecond
	
	//CTC-mode with 64 prescaler, COM0 in normal operation OC0A/B disabled
	TCCR2A = (1<<COM2A1) | (0<<COM2A0) | (1<<WGM21) | (0<<WGM20);
	TCCR2B = (0<<WGM22)	 | (1<<CS20)|(1<<CS21);
	
	// Enable Output Compare A Match Interrupt Enable
	TIMSK2 = (1<<OCIE2A);
	
}

ISR(TIMER2_COMPA_vect)
{
	
	milliseconds++;
	if(milliseconds - old_millis >= 1000)
	{
		SPEED_REGISTER = 0;
	}
}

unsigned long long millis()
{
	cli();
	unsigned long long temp = milliseconds;
	sei();
	return temp;
}



void setup()
{
	port_init();
	UART_init();
	pwm_init();
	timer2_init();
	PIDSetup(1,0,0);
	sei();
}

void send_data(char* data)
{
	int counter=0;
	while(1)
	{
		while(!( UCSR0A & (1<<UDRE0)))
		;
		if (data[counter] == '\0')
		{
			break;
		}
		UDR0 = data[counter];

		counter++;
	}
}



void speedlimiter(int speed) {
	if (speed > MAX_SPEED) {
		speed = MAX_SPEED;
	}

}

void clear_buffer(char* buffer, int size)
{
	for(int i = 0;i < size ;i++)
	{
		buffer[i] = '\0';
	}
}

bool parse_handshake()
{

	if(!strcmp(&working_buffer[0], "ACK"))
	{
		return true;
	}
	return false;
}

void handshake()
{
	while(1)
	{
		if(millis()-old_millis > 100)
		{
			old_millis = millis();
			//Denna ska va här ---- start
			send_data("control_module\n");
			//Denna ska va här ---- slut
			if(received)
			{
				cli();
				received = false;
				if(parse_handshake()) //ACK
				{
					sei();
					return;
				}
				sei();
				
			}
			
		}
	}
}

