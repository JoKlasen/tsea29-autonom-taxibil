/*
 * SensorModule.cpp
 *
 * Created: 2022-11-02 08:26:16
 * Author : johkl473
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

#define F_CPU 16000000UL
#define USART_BAUDRATE 9600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)	

#define SPEED_PRECISION 1000 // 6 decimalers precision
#define SPEED_FIVETICKS 0.13 * 3.6 * 1000 * SPEED_PRECISION // konvertering till km/h med 0 decimalers shiftning åt vänster


// Timing variables
volatile unsigned long long milliseconds = 0;
volatile unsigned long long us_latest = 0;
volatile unsigned long long hall_left_latest = 0;
volatile unsigned long long hall_left_old = 0;
volatile unsigned long long hall_right_latest = 0;

// ISR flags
volatile bool us_updated = false;
volatile bool hall_left_updated = false;
volatile bool hall_right_updated = false;  

//Skicka data med jämnt intervall
volatile bool sendbool = false;


volatile int hall_left_counter = 0;



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

ISR(TIMER1_COMPA_vect)
{
	milliseconds++;
}

unsigned long long millis()
{
	cli();
	unsigned long long tempmillis = milliseconds;
	sei();
	return tempmillis;
}

void portinit()
{
		PORTD = (0 << PD5) |(0 << PD3) | (0 << PD2) | (1 << PD1) | (1 << PD0);
		// output == 1 input == 0
		DDRD = (1 << DDD5)|(1 << DDD4)| (0 << DDD3) | (0 << DDD2) | (1 << DDD1) | (0 << DDD0);
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

void timer1_init()
{
	// Set Output Compare Register to 16000 with is 1 ms at 16MHz
	OCR1A = 16000; // == 0x3E80
	//CTC = Clear Timer on Compare-mode with no prescaler
	TCCR1A = (0<<WGM11)|(0<<WGM10); // COM1 in normal operation OC1A/B disabled
	TCCR1B = (1<<WGM12)|(1<<CS10);
	// Enable Output Compare A Match Interrupt Enable
	TIMSK1 = (1<<OCIE1A);
}

//For interrupt routines
//2 == falling edge // 3 == raising edge // 1 == any change

void INT0_conf()
{
	//Rising edge interrupt mode
	EICRA |=  (3 << ISC00);
	
	//Detta enablar interrupts för INT0
	EIMSK |= (1 << INT0);
}

void INT1_conf()
{
	//Rising edge interrupt mode
	EICRA |=  (3 << ISC10);
	
	//Detta enablar interrupts för INT0
	EIMSK |= (1 << INT1);
}

void INT2_conf()
{
	
	EICRA |= (2 << ISC20);
	
	//Detta enablar interrupts för INT2
	EIMSK |= (1 << INT2);
}

void setup()
{
	portinit();
	UART_init();
	timer1_init();
	INT0_conf();
	INT1_conf();
	INT2_conf();
	
	sei();
}



//Höger Hallsensor
ISR(INT0_vect)
{
	//hall_right_latest = millis();
	//hall_right_updated = true;
	char * data = "Right Hallsensor!\n";
	send_data(data);
}

//vänster hallsensor
ISR(INT1_vect)
{
	hall_left_counter++;
	if(hall_left_counter == 5)
	{
		hall_left_old = hall_left_latest;
		hall_left_latest = millis();


		hall_left_updated = true;
		hall_left_counter = 0;
	}
	//char * data = "Left Hallsensor!\n";
	//send_data(data);
}

//Ultraljudsensor
ISR(INT2_vect)
{
	
}



int main(void)
{
	setup();
	char* Data= "Init Completed! :)\n";
	send_data(Data);
	volatile bool localsend = false;	
	volatile bool localultrasound = false;
	volatile bool localhallsensor = false;
	volatile unsigned long long old_time = 0;
	volatile unsigned long long new_time = 0;
	char initial[50];
	char * speed_msg = &initial[0]; 
	volatile unsigned heltal = 0;
	volatile unsigned decimal =0;
	while(1)
	{
		new_time = millis();
		
		cli();
		localultrasound = us_updated;
		sei();
		if (localultrasound)
		{
			
			
			
		}
		cli();
		localhallsensor = hall_left_updated;
		sei();
		if(localhallsensor)
		{
			unsigned long long diff = hall_left_latest - hall_left_old; // diff in ms for 5 ticks

			unsigned long tmp = SPEED_FIVETICKS / ( diff ); // tmp = hastighet i km/h shiftat med precisionen
			// ett halvt varv * 1000 / skillnaden i tid i ms = hastighet i cm/s*1000
			



			heltal = tmp / SPEED_PRECISION;
			decimal = tmp % SPEED_PRECISION;

			hall_left_updated = false;
			//denna ska sättas i med någon timer i ett rätt intervall.
			sendbool = true;
		}
	
		cli();
		localsend = sendbool;
		sei();
		if(localsend == true)
		{
			if ((new_time - old_time) > 250)
			{
				//send_data_routine();
				sprintf(speed_msg, "telemetry:speed=%u.%03u:detection=none\n", heltal, decimal );
				send_data(speed_msg);
				cli();
				sendbool = false;
				sei();
			}
		}	
	}
	return 0;
}

