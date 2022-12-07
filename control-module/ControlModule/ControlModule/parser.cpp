
#include "definitions.h"
#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include "global_variables.h"

void parse(char input[])
{
	char command[20];
	char value_name[20];
	char text_value[10];
	
	bool findcommand = true;
	bool pid = false;
	bool switchmode = false;
	bool keys = false;
	bool telemetry = false;
	bool emergencystop = false;
	bool error_b = false;
	int label_end = 0;
	int value_separator = 0;
	
	for (int i = 0; input[i] != '\0'; i++)
	{
		if (findcommand)
		{
			if (input[i] == ':')
			{
				strlcpy(&command[0], input, i+1);
				label_end = i;

				if (!strcmp(&command[0], "kp"))
				{
					keys = true;
					findcommand = false;
				}
				else if (!strcmp(&command[0], "sm"))
				{
					switchmode = true;
					findcommand = false;
				}
				else if (!strcmp(&command[0], "sp"))
				{
					pid = true;
					findcommand = false;
				}
				else if (!strcmp(&command[0], "es"))
				{
					SPEED_REGISTER = 0;
					emergencystop = true;
				}
				else if (!strcmp(&command[0], "telemetry"))
				{
					telemetry = true;
					findcommand = false;
				}else if (!strcmp(&command[0], "er"))
				{
					error_b = true;
					findcommand = false;
				}
			}
		}
		else
		{
			if (keys)
			{
				if (input[i] == '=')
				{
					clear_buffer(&value_name[0], 20);
					strlcpy(&value_name[0], &input[label_end+1], ((i) - label_end));
					value_separator = i;
				}
				else if (input[i] == ':')
				{
					clear_buffer(&text_value[0], 10);
					strlcpy(&text_value[0], &input[value_separator+1], ((i) - value_separator) );
					if (!strcmp(&value_name[0], "f"))
					{
						man_forward = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "l"))
					{
						man_left = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "b"))
					{
						man_back = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "r"))
					{
						man_right = atoi(&text_value[0]);
					}
					label_end = i;

				}
			}
			else if (switchmode)
			{
				if (input[i] == '=')
				{
					clear_buffer(&value_name[0], 20);
					strlcpy(&value_name[0], &input[label_end+1], ((i) - label_end));
					value_separator = i;
				}
				else if (input[i] == ':')
				{
					clear_buffer(&text_value[0], 10);
					strlcpy(&text_value[0], &input[value_separator+1], ((i) - value_separator) );
					if (!strcmp(&value_name[0], "m"))
					{
						manual_mode = atoi(&text_value[0]);
						if (manual_mode == 1)
						{
							send_data("Switched to manual mode\n");
							release_brake();
						}
						else if (manual_mode == 0)
						{
							send_data("Switched to autonomous mode\n");
						}
					}
					label_end = i;
				}
				

			}
			else if(telemetry)
			{
				if (input[i] == '=')
				{
					clear_buffer(&value_name[0], 20);
					strlcpy(&value_name[0], &input[label_end+1], ((i) - label_end));
					value_separator = i;
				}
				else if (input[i] == ':')
				{
					clear_buffer(&text_value[0], 10);
					strlcpy(&text_value[0], &input[value_separator+1], ((i) - value_separator) );
					if (!strcmp(&value_name[0], "velocity"))
					{
						velocity = atoi(&text_value[0]); // TODO: Velocity is NOT sent as an INT, in km/h as xx.xxx
						//velocity = aito [xx.] * 1000 + aito [.xxx] // need to prase textvalue to separate the integer and decimal, separated with '.'
						velocity_received = true;
					}
					
					else if (!strcmp(&value_name[0], "steering")) // Q: What is this??
					{
						steering_from_pi = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "error")) // TODO: Rename to steering error or something... add speed_error or expected_speed
					{
						error = atoi(&text_value[0]);
						turn_error_received = true;
					}
					else if (!strcmp(&value_name[0], "detection"))
					{
						detection = atoi(&text_value[0]);
					}
					label_end = i;
				}
			}
			else if (pid)
			{
				if (input[i] == '=')
				{
					clear_buffer(&value_name[0], 20);
					strlcpy(&value_name[0], &input[label_end+1], ((i) - label_end));
					value_separator = i;
				}
				else if (input[i] == ':')
				{
					clear_buffer(&text_value[0], 10);
					strlcpy(&text_value[0], &input[value_separator+1], ((i) - value_separator) );
					if (!strcmp(&value_name[0], "p"))
					{
						ConstantP = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "i"))
					{
						ConstantI = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "d"))
					{
						ConstantI = atoi(&text_value[0]);
					}
					label_end = i;
				}
			}
			else if (error_b)
			{
				if (input[i] == '=')
				{
					clear_buffer(&value_name[0], 20);
					strlcpy(&value_name[0], &input[label_end+1], ((i) - label_end));
					value_separator = i;
				}
				else if (input[i] == ':')
				{
					clear_buffer(&text_value[0], 10);
					strlcpy(&text_value[0], &input[value_separator+1], ((i) - value_separator) );
					if (!strcmp(&value_name[0], "e"))
					{
						error = atoi(&text_value[0]);
						turn_error_received = true;
					}

					label_end = i;
				}
			}
			
			
			
		}
	}
	/*
	char value_msg[50];
	
	if(keys)
	{
		sprintf(&value_msg[0], "Received forward:%d left:%d back:%d right:%d\n", man_forward, man_left, man_back, man_right );
	}
	else if(switchmode)
	{
		sprintf(&value_msg[0], "Received mode:%d\n", manual_mode );
	}
	else if(pid)
	{
		sprintf(&value_msg[0], "Received p:%d i:%d d:%d\n", ConstantP,ConstantI,ConstantD );
	}
	else if(telemetry)
	{
		//sprintf(&value_msg[0], "Received speed:%d steering:%d error:%d detection:%d\n", velocity,steering_from_pi,error,detection );
		sprintf(&value_msg[0], "Received speed:%d detection:%d\n", velocity,detection );

	}
	else if(emergencystop)
	{
		sprintf(&value_msg[0], "Received EMERGENCYSTOP\n");
	}
	else if (error_b)
	{
		sprintf(&value_msg[0],"Received turnerror e=%d\n",error);
	}
	else
	{
		sprintf(&value_msg[0],"Didnt receive any Parser_Data\n");
	}
	send_data(&value_msg[0]);
	*/
	
	
}
