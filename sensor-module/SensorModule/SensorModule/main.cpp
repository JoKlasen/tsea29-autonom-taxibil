/*
 * SensorModule.cpp
 *
 * Created: 2022-11-02 08:26:16
 * Author : johkl473
 */ 

#include <avr/io.h>

#define F_CPU 16000000UL
#define USART_BAUDRATE 9600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)	

void setup()
{
	PORTD = (0 << PD5) |(0 << PD3) | (0 << PD2) | (1 << PD1) | (1 << PD0);
	// output == 1 input == 0
	DDRD = (1 << DDD5)|(1 << DDD4)| (0 << DDD3) | (0 << DDD2) | (1 << DDD1) | (0 << DDD0);
	
	//UART
	
	/* Set baud rate */ 
	
	UBRR0H = (BAUD_PRESCALE>>8);
	UBRR0L = BAUD_PRESCALE;
	/* Enable receiver and transmitter */
	UCSR0B = (1<<RXEN0)|(1<<TXEN0);
	/* Set frame format: 8data, 2stop bit */
	UCSR0C = (1<<USBS0)|(3<<UCSZ00);

}

int main()
{
	setup();
	volatile int a= 0;
    /* Replace with your application code */
    while (1) 
	{
		/*
		volatile int i = PIND;
		
		if( ((i & 0b100) >> 2) == 1)
		{
			PORTD |= (1 << PORTD4);
		}
		else if ( ((i & 0b100 ) >> 2) == 0)
		{
			PORTD &= (0 << PORTD4);
		}*/
		
	}
}

