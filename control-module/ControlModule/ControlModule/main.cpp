
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


//Ska defaulta true
volatile bool manual_mode = true;
//
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

volatile int velocity;
volatile int steering_from_pi;
volatile int error;
volatile int detection = 10;
volatile bool turn_error_received = false;
volatile bool speed_error_received = false;
volatile bool velocity_received = false;

volatile int ConstantP, ConstantI, ConstantD;
volatile int PTerm, ITerm, DTerm;
volatile int CurrentI, MaxI, MinI;
volatile int dTemp = 0;

void turn_percent(int correction)
{
	if (correction < 0)
	{
		steering += correction;
		if (steering < MAX_STEER_LEFT)
		{
			steering = MAX_STEER_LEFT;
		}
	}
	else if (correction > 0)
	{
		steering += correction;
		if (steering > MAX_STEER_RIGHT)
		{
			steering = MAX_STEER_RIGHT;
		}
	}
	else
	{
		steering = STEER_NEUTRAL;
	}
	STEER_REGISTER = steering;
}

int main(void)
{
	setup();
	
	memset(receive_buffer,0,sizeof receive_buffer);
	memset(working_buffer,0,sizeof working_buffer);
	char debugdata[50];
	memset(debugdata,0,sizeof debugdata);
	int localspeed = 0;
	handshake();
	while (1)
	{

		//"keyspressed:forward=0:left=1:back=0:right=0:";
		//"emergencystop:"
		//"switchmode:mode=1:" == manual "switchmode:mode=0:" == autonomous
		//"telemetry:velocity=2:steering=2:error=800:detection=2:"
		//"sendpid:p=1:i=0:d=0:"
		//error:e=-500:
		if(received)
		{
			received = false;
			parse(working_buffer);

			if(manual_mode)
			{
			
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
			else//Automatic Mode
			{
				
				//Bugg här nånstans
				if(detection <= 3)
				{
					SPEED_REGISTER = 0;
					localspeed = 0;

				}
				int changes = 100;
				
				if(man_forward)
				{
					if((localspeed + changes) > MAX_AUTO_SPEED)
					{
						localspeed = MAX_AUTO_SPEED;
					}
					else
					{
						localspeed += changes;
					}
					SPEED_REGISTER = localspeed;
				}
				else if(man_back)
				{
					if((localspeed - changes) >= 0)
					{
						localspeed -= changes;
					}
					SPEED_REGISTER = localspeed;
				}
				
				//Buggen ovan
				
				// Hårdkodad sålänge

				//sprintf(debugdata,"Speed register = %d",SPEED_REGISTER);
				//send_data(debugdata);
				//memset(debugdata,0,50);

				//PID LOOP/FUNCTION for sterring
				if(turn_error_received)
				{
					int correction = PIDIteration(error);
					sprintf(debugdata,"Correction = %d\n",correction);
					send_data(debugdata);
					memset(debugdata,0,50);
					turn_percent(correction);
					turn_error_received = false;
				}
				//PID LOOP/FUNCTION for speed
				if(velocity_received)
				{
					// variabeln == "velocity"
					//SPEED_REGISTER = 3500;
					velocity_received = false;		
				}
				old_millis = millis();
				
			}
		}
	}
	
}
