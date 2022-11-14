/*
 * ControlModule.cpp
 *
 * Created: 06/11/2022 20:57:21
 * Author : Johan, Hannes
 */ 

#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <stdio.h>
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
#define USART_BAUDRATE 57600
#define BAUD_PRESCALE (((F_CPU / (USART_BAUDRATE * 16UL))) - 1)	

#define MAX_SPEED 4000

#define MAX_STEER_LEFT 2100
#define STEER_NEUTRAL 3046 //Drar aningen åt vänster (välidgt lite)
#define MAX_STEER_RIGHT 4200

#define  STEER_REGISTER OCR3A
#define  SPEED_REGISTER OCR1A

#define RECEIVE_BUFFER_SIZE 100

volatile unsigned steering = STEER_NEUTRAL;

volatile bool manual_mode = true;

volatile bool man_left = false;
volatile bool man_right = false;
volatile bool man_forward = false;
volatile bool man_back = false;
volatile unsigned long long old_millis=0;

volatile bool update = false;

volatile unsigned long long milliseconds =0;

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
    /* Set frame format: 8data, 1stop bit */
    UCSR0C = (0<<USBS0)|(3<<UCSZ00)|(0<<UPM00)|(0<<UPM01);
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

/*
void timer0_init()
{
	// Set Output Compare Register to 160 which is 10 us at 16MHz
	OCR0A = 250; // 1 millisecond
	
	//CTC-mode with 64 prescaler, COM0 in normal operation OC0A/B disabled
	TCCR0A = (0<<COM0A1) | (0<<COM0A1) | (1<<WGM01) | (0<<WGM00);
	TCCR0B = (0<<WGM02)	 | (1<<CS00)|(1<<CS01);
	
	// Enable Output Compare A Match Interrupt Enable
	TIMSK0 = (1<<OCIE0A);
}



ISR(TIMER0_COMPA_vect)
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
}*/
void clear_buffer(char* buffer,int size = RECEIVE_BUFFER_SIZE);

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
		if (data[counter] == '\0')
		{
			break;
		}
		UDR0 = data[counter];

		counter++;
	}
}

void receive_data(char* receive_buffer)
{
	bool receiving = true;
	int counter = 0;
	
	while (receiving) {
		while (!(UCSR0A & (1<<RXC0)));
		
		unsigned char from_receive_buffer = UDR0;
		receive_buffer[(counter)++] = from_receive_buffer;
		
		receiving = !((from_receive_buffer == '\0') || ((counter) == RECEIVE_BUFFER_SIZE-2) || (from_receive_buffer == '\n'));
	}

	
	send_data("Tog emot detta från UART:\n");
	send_data(receive_buffer);
	send_data("\n");
	
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

void parse(char input[])
{
	char command[20];
	char value_name[20];
	
	bool findcommand = true;
	bool pid = false;
	bool switchmode = false;
	bool keys = false;
	
	int label_end = 0;
	int value_separator = 0;
	
	//send_data(" I parsern\n");
	
	//for (int i = 0; *(input+i) != NULL; i++)
	for (int i = 0; input[i] != '\0'; i++)
	{
		if (findcommand) 
		{
			//send_data(" in find command\n");
			//if (*(input+i) == ':') 
			if (input[i] == ':') 
			{
				strlcpy(&command[0], input, i+1);
				label_end = i;
				//send_data(" found label end\n");
				//send_data("Command=");
				//send_data(&command[0]);
				//send_data("A\n");
				if (!strcmp(&command[0], "keyspressed")) 
				{
				//	send_data(" I Keyspressed\n");
					keys = true;
					findcommand = false;
				} 
				else if (!strcmp(&command[0], "switchmode")) 
				{
					switchmode = true;
					findcommand = false;
				} 
				else if (!strcmp(&command[0], "sendpid")) 
				{
					pid = true;
					findcommand = false;
				}
			}
		}
		else
		{
			if (keys)
			{
	//			send_data("k e keys\n");
				if (input[i] == '=')
				{
					clear_buffer(&value_name[0], 20);
					strlcpy(&value_name[0], &input[label_end+1], ((i) - label_end));
					value_separator = i;
			//		send_data("found key\n");
				}
				//else if (*(input+i) == ':')
				else if (input[i] == ':')
				{	
				//	send_data("comparing keys\n");
					char text_value[10];
					clear_buffer(&text_value[0], 10);
					strlcpy(&text_value[0], &input[value_separator+1], ((i) - value_separator) );
			//		send_data(&value_name[0]);
				//	send_data("\n");
					if (!strcmp(&value_name[0], "forward"))
					{
				//		send_data(" I forward\n");
						man_forward = atoi(&text_value[0]);
				//		if(man_forward) {send_data(" man_forward = 1\n");}
					} 
					else if (!strcmp(&value_name[0], "left")) 
					{
						//send_data(" I left\n");

						//send_data(&text_value[0]);
						man_left = atoi(&text_value[0]);
					//	if(man_left) {send_data(" man_left = 1\n");}
					} 
					else if (!strcmp(&value_name[0], "back")) 
					{
			//			send_data(" I back\n");

						man_back = atoi(&text_value[0]);
				//		if(man_back) {send_data(" man_back = 1\n");}
					} 
					else if (!strcmp(&value_name[0], "right")) 
					{
//						send_data(" I right\n");

						man_right = atoi(&text_value[0]);
	//					if(man_right) {send_data(" man_right = 1\n");}
					}
					char debugstring[50];
					label_end = i;
		//			sprintf(&debugstring[0],"labe_lend=%d value_separator=%d\n",label_end,value_separator);
		//			send_data(&debugstring[0]);
				}
			}
				
			if (switchmode) 
			{
					
			}
				
			if (pid) 
			{
			}	
		}	 
	}
	
	char value_msg[50];

	sprintf(&value_msg[0], "Received forward:%d left:%d back:%d right:%d\n", man_forward, man_left, man_back, man_right );
	send_data(&value_msg[0]);
	
}

int P, I, D;
void pid_init(int in_p, int in_i, int in_d) {
    P = in_p;
    I = in_i;
    D = in_d;
}

int pid_loop(int error) {
    int steering = 0;
    
    steering -= error*P;

    return steering;
}

int main(void)
{
    setup();
    
    char* welcome_msg = "Hello World! :)\n";
    send_data(welcome_msg);
	char receive_buffer[RECEIVE_BUFFER_SIZE];
	//clear_buffer(&receive_buffer[0]);	
	memset(receive_buffer,0,sizeof receive_buffer);
	while (1)
	{
		
		//Busy waits for data
		receive_data(&receive_buffer[0]);
		//char* input = "keyspressed:forward=0:left=1:back=0:right=0:";
		parse(receive_buffer);
	
		// char value_msg[50];
		// sprintf(&value_msg[0], "\nReceived forward:%d left:%d back:%d right:%d\n", man_forward, man_left, man_back, man_right );
		// send_data(&value_msg[0]);
		// steering
		if (man_left)
			steering = MAX_STEER_LEFT;
		else if (man_right)
			steering = MAX_STEER_RIGHT;
		else
			steering = STEER_NEUTRAL;
		STEER_REGISTER = steering;
			
 		if (man_forward)
		 
 			SPEED_REGISTER = MAX_SPEED;	
 		else
 			SPEED_REGISTER = 0;
		
		//old_millis = millis();	
		//clear_buffer(receive_buffer);
		memset(receive_buffer,0,sizeof receive_buffer);

    }
}

