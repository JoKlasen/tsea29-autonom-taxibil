/*
 * ControlModule.cpp
 *
 * Created: 06/11/2022 20:57:21
 * Author : johan
 */ 

#include <avr/io.h>

//Portdefinitions
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


void portinit()
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

pwm_init()
{
    // TODO: Se inititering av timer1 i sensormodul
}

void setup()
{
    port_init();
    UART_init();
}

int main(void)
{
    setup();
    /* Replace with your application code */
    char* welcome_msg= "Hello World! :)\n";
    send_data(welcome_msg);
    while (1) 
    {
    }
}

