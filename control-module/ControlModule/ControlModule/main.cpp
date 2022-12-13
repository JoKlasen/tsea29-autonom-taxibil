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

volatile int velocity = 0;
volatile int steering_error = 0;
volatile int target_speed = 0;
volatile int detection = 10;
volatile bool turn_error_received = false;
volatile bool speed_error_received = false;
volatile bool velocity_received = false;

volatile int ConstantP, ConstantI, ConstantD;
volatile int PTerm, ITerm, DTerm;
volatile int CurrentI, MaxI, MinI = 0;
volatile int dTemp = 0;

volatile int spd_ConstantP, spd_ConstantI, spd_ConstantD;
volatile int spd_PTerm, spd_ITerm, spd_DTerm;
volatile int spd_CurrentI, spd_MaxI, spd_MinI = 0;
volatile int spd_dTemp = 0;
volatile int Latest_SPerror=0;
volatile int Latest_SP =0;
volatile int Latest_STerror = 0;
volatile int Latest_ST =0;

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
	Latest_ST = steering;
}

void drive(int correction)
{
	if ((SPEED_REGISTER + correction)  >= MAX_AUTO_SPEED)
	{
		SPEED_REGISTER = MAX_AUTO_SPEED;
	}
	else
	{
		SPEED_REGISTER = SPEED_REGISTER + correction;
	}
}

void send_debug()
{
	char debugsend[40];
	sprintf(debugsend,"db:esp=%d:sp=%d:est=%d:st=%d:",Latest_SPerror,Latest_SP,Latest_STerror,Latest_ST);
	send_data(debugsend);
	clear_buffer(debugsend,40);
	
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
	PORTA |= (1 << LED2); // Turn on handshake LED
	while (1)
	{

		//"kp:f=1:l=1:b=1:r=1:";
		//"es:"
		//"sm:m=0:" == manual "switchmode:mode=0:" == autonomous
		//"tm:s=3000:d=2:"
		//"spp:p=1:i=2:d=3:"
		//"stp:p=1:i=2:d=3:"
		//"er:st=-500:sp=0:"
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
				Latest_ST = steering;
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
				detection = 100;
				if(detection <= 2)
				{
					brake();
				}
				else
				{
					release_brake();
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
				}
				
				// H�rdkodad s�l�nge

				//sprintf(debugdata,"Speed register = %d",SPEED_REGISTER);
				//send_data(debugdata);
				//memset(debugdata,0,50);

				//PID LOOP/FUNCTION for sterring
				if(turn_error_received)
				{
					int correction = PIDIteration(steering_error);
					sprintf(debugdata,"Correction = %d\n",correction);
					send_data(debugdata);
					memset(debugdata,0,50);
					turn_percent(correction);
					turn_error_received = false;
				}
				//PID LOOP/FUNCTION for speed
				if(velocity_received)
				{
					//int speed = 10000 
					int speederror = (target_speed) - velocity; 
					Latest_SPerror = speederror;
					int speedcorrection = spd_PIDIteration(speederror);
					send_debug();
					drive(speedcorrection);	
					velocity_received = false;
				}
				old_millis = millis();
				
			}
		}
	}
	
}
