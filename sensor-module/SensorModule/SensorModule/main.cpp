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


//Port Definitions
#define UART_RX		 PD0 // 14
#define UART_TX		 PD1 // 15

#define ECHO_OUTPUT	 PB2 // 3
#define ECHO_TRIGGER PB3 // 4
#define HALL_RIGHT	 PD2 // 16
#define HALL_LEFT	 PD3 // 17


// Constants
#define F_CPU 16000000UL
#define USART_BAUDRATE 9600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)	

#define SPEED_PRECISION 1000 // 3 decimalers precision
#define SPEED_FIVETICKS 0.13 * 3.6 * 1000 * SPEED_PRECISION // konvertering till km/h med 0 decimalers shiftning åt vänster


// Timing variables
volatile unsigned short interval_counter = 0;
volatile unsigned long long milliseconds = 0;
volatile unsigned long long echo_start = 0;
volatile unsigned long long	echo_end = 0;
volatile unsigned long long hall_left_latest = 0;
volatile unsigned long long hall_left_old = 0;
volatile unsigned long long hall_right_latest = 0;

// ISR flags
volatile bool echo_updated = false;
volatile bool hall_left_updated = false;
volatile bool hall_right_updated = false;  

//Skicka data med jämnt intervall
volatile bool sendbool = false;


volatile int hall_left_counter = 0;

// Function predeclarations
void portinit();
void UART_init();
void timer0_init();
void timer1_init();
void ext_intr_init();



// ======================
// Help functions
// ======================

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


unsigned long long millis()
{
	cli();
	unsigned long long tempmillis = milliseconds;
	sei();
	return tempmillis;
}


void start_echo_pulse()
{
	cli();
	// Start Timer0
	TCNT0 = 0;
	TCCR0B |= (1<<CS00);
	// Start tigger pulse
	PORTB |= (1<<ECHO_TRIGGER);
	sei();
}



// ======================
// Main program
// ======================

void setup()
{
	portinit();
	UART_init();
	timer0_init();
	timer1_init();
	ext_intr_init();
	sei();
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
	
	volatile unsigned pulse_length = 0;
	volatile unsigned heltal = 0;
	volatile unsigned decimal = 0;
	while(1)
	{
		new_time = millis();
		
		cli();
		localultrasound = echo_updated;
		sei();
		if (localultrasound)
		{
			char test_inital[50];
			char * echo_test = &test_inital[0];
			pulse_length = echo_end - echo_start;
			echo_updated = false;
			//sprintf(echo_test, "start:%u end:%u \n", echo_start, echo_end);
			//send_data(echo_test);
		}
		
		cli();
		localhallsensor = hall_left_updated;
		sei();
		if(localhallsensor)
		{
			unsigned long long diff = hall_left_latest - hall_left_old; // diff in ms for 5 ticks

			unsigned long tmp = SPEED_FIVETICKS / ( diff ); // tmp = hastighet i km/h shiftat med precisionen
			
			heltal = tmp / SPEED_PRECISION;
			decimal = tmp % SPEED_PRECISION;

			hall_left_updated = false;
		}
	
		cli();
		localsend = sendbool;
		sei();
		if(localsend == true)
		{
			if ((new_time - old_time) > 250)
			{
				//send_data_routine();
				sprintf(speed_msg, "telemetry:speed=%u.%03u:detection=%u\n", heltal, decimal, pulse_length );
				send_data(speed_msg);
				cli();
				sendbool = false;
				sei();
			}
		}	
	}
	return 0;
}



// ======================
// Interrupt Service Routines 
// ======================

ISR(TIMER0_COMPA_vect)
{
	// Stop Timer0
	TCCR0B &= ~(1<<CS00);
	// End trigger pulse
	PORTB &= ~(1<<ECHO_TRIGGER);
	echo_start = millis();
}

ISR(TIMER1_COMPA_vect)
{
	milliseconds++;
	interval_counter++;
	if(interval_counter == 250)
	{
		sendbool = true;
		interval_counter = 0;
		
		start_echo_pulse();
	}
}

//HALL_RIGHT
ISR(INT0_vect)
{
	//hall_right_latest = millis();
	//hall_right_updated = true;
	char * data = "Right Hallsensor!\n";
	send_data(data);
}

//HALL_LEFT
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

//ECHO_OUTPUT
ISR(INT2_vect)
{
	echo_end = millis();
	echo_updated = true;
}



// ======================
// Initiation functions
// ======================

void portinit()
{
	PORTD = (0 << HALL_LEFT) | (0 << HALL_RIGHT) | (1 << UART_TX) | (1 << UART_RX); // (0 << PD5) for testing
	// output == 1 input == 0
	DDRD = (0 << HALL_LEFT) | (0 << HALL_RIGHT) | (1 << UART_TX) | (0 << UART_RX); // (1 << DDD5)|(1 << DDD4) for testing
		
	// Flyttar echo_trigger från PA1 till PB3
	//DDRA = (1 << DDA1); 
	//PORTA = (0 << PA1);
		
	PORTD = (0 << ECHO_TRIGGER);
	DDRB = (1 << ECHO_TRIGGER)|(0 << ECHO_OUTPUT);
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


void timer0_init() // PWM variant
{
	// Set Output Compare Register to 160 which is 10 us at 16MHz
	OCR0A = 160; // == 10 us
	
	//CTC-mode with no prescaler, COM0 in normal operation OC0A/B disabled
	TCCR0A = (0<<COM0A1) | (0<<COM0A1) | (1<<WGM01) | (1<<WGM00);
	TCCR0B = (0<<WGM02)	 | (0<<CS00);
	
	// Enable Output Compare A Match Interrupt Enable
	TIMSK0 = (1<<OCIE0A);
}


void timer1_init()
{
	// Set Output Compare Register to 16000 which is 1 ms at 16MHz
	OCR1A = 16000; // == 0x3E80
	
	//CTC = Clear Timer on Compare-mode with no prescaler, COM1 in normal operation OC1A/B disabled
	TCCR1A = (0<<WGM11) | (0<<WGM10); 
	TCCR1B = (1<<WGM12) | (1<<CS10);
	// Enable Output Compare A Match Interrupt Enable
	TIMSK1 = (1<<OCIE1A);
}


void ext_intr_init()
{
	//Set control mode and enable External Interrupt routines
	//Modes: 2 == falling edge // 3 == raising edge // 1 == any change
	
	EICRA = (2 << ISC20) | (3 << ISC10) | (3 << ISC00);
	EIMSK = (1 << INT2) | (1 << INT1) | (1 << INT0);
}