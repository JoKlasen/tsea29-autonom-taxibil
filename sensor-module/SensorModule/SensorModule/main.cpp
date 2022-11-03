/*
 * SensorModule.cpp
 *
 * Created: 2022-11-02 08:26:16
 * Author : johkl473
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>

#define F_CPU 16000000UL
#define USART_BAUDRATE 9600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)	

volatile bool ultrasound = false;
volatile bool hallsensor = false; 
//Skicka data med jämnt intervall
volatile bool sendbool = false;
volatile unsigned long long milliseconds = 0;

void timer1_init()
{
	OCR1A = 16000;
	TCCR1A = 0x00;
	//CTC = clear timer on compare and no prescale
	TCCR1B = (1<<WGM12)|(1<<CS10);
	//ICR1
	TIMSK1 |= (1<<ICIE1);

}


ISR(TIMER1_CAPT_vect)
{
	milliseconds++;
}

unsinged long long millis()
{

}
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
	UCSR0C = (1<<USBS0)|(3<<UCSZ00)|(0<<UPM00)|(0<<UPM01);

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

//vänster hallsensor
/*ISR(INT1_vect)
{

}*/

//Höger Hallsensor
ISR(INT0_vect)
{

}

//Ultraljudsensor
ISR(INT2_vect)
{

}

int main(void)
{

	volatile bool localsend = false;	
	sei();
	while(1)
	{

	cli()
	localsend = sendbool
	sei();
	if(localsend == true)
	{
		//send_data_routine();
	}	


}

/*
int main()
{
	setup();
	volatile int a= 0;
	char* Data= "Hello World! :)";
	send_data(Data);
    while (1) 
	{
		
		volatile int i = PIND;
		
		if( ((i & 0b100) >> 2) == 1)
		{
			PORTD |= (1 << PORTD4);
		}
		else if ( ((i & 0b100 ) >> 2) == 0)
		{
			PORTD &= (0 << PORTD4);
		}
		
	}
}

*/