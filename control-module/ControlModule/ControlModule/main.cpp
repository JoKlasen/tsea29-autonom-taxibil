
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

#include "definitions.h"


volatile unsigned steering = STEER_NEUTRAL;

volatile bool manual_mode = true;

volatile bool man_left = false;
volatile bool man_right = false;
volatile bool man_forward = false;
volatile bool man_back = false;
volatile unsigned long long old_millis=0;

volatile bool update = false;
volatile unsigned long long milliseconds =0;

volatile bool received = false;
char receive_buffer[RECEIVE_BUFFER_SIZE];
char working_buffer[RECEIVE_BUFFER_SIZE];
volatile int receive_buffer_index = 0;

volatile int P;
volatile int I;
volatile int D;
volatile int velocity;
volatile int steering_from_pi;
volatile int error;
volatile int detection;

int main(void)
{
	setup();
	
	memset(receive_buffer,0,sizeof receive_buffer);
	memset(working_buffer,0,sizeof working_buffer);
	
	handshake();
	while (1)
	{

		//"keyspressed:forward=0:left=1:back=0:right=0:";
		//"emergencystop:"
		//"switchmode:mode=1:" == manual "switchmode:mode=0:" == autonomous
		//"telemetry:velocity=2:steering=2:error=2:detection=2:"
		//"sendpid:p=4:i=3:d=23:"
		if(received)
		{
			received = false;
			parse(working_buffer);

			if(manual_mode)
			{
				send_data("In manual mode :) \n");
				if (man_left)
				{
					steering = MAX_STEER_LEFT;
				}
				else if (man_right)
				{
					steering = MAX_STEER_RIGHT;
				}
				else
				{
					steering = STEER_NEUTRAL;
				}
				STEER_REGISTER = steering;
				if (man_forward)
				{
					SPEED_REGISTER = MAX_SPEED;
				}
				else
				{
					SPEED_REGISTER = 0;
				}
				old_millis = millis();
				
			}
			else
			{
				send_data("In autonomous mode xD\n");
				
				//PID LOOP/FUNCTION for speed
				
				//PID LOOP/FUNCTION for steerring
				
			}
		}
	}
	
}
