
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
	bool steering_pid = false;
	bool speed_pid = false;
	bool switchmode = false;
	bool keys = false;
	bool telemetry = false;
	bool emergencystop = false;
	bool error_boolean = false;
	int label_end = 0;
	int value_separator = 0;
	char value_msg[50];
	
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
				else if (!strcmp(&command[0], "stp"))
				{
					steering_pid = true;
					findcommand = false;
				}
				else if (!strcmp(&command[0], "spp"))
				{
					speed_pid = true;
					findcommand = false;
				}
				else if (!strcmp(&command[0], "es"))
				{
					SPEED_REGISTER = 0;
					emergencystop = true;
				}
				else if (!strcmp(&command[0], "tm"))
				{
					telemetry = true;
					findcommand = false;
				}else if (!strcmp(&command[0], "er"))
				{
					error_boolean = true;
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
							release_brake();
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
					if (!strcmp(&value_name[0], "s"))
					{
						velocity = atoi(&text_value[0]);
						Latest_SP = velocity;
						velocity_received = true;
					}
					else if (!strcmp(&value_name[0], "d"))
					{
						detection = atoi(&text_value[0]);
					}
					label_end = i;
				}
			}
			else if (steering_pid)
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
						ConstantD = atoi(&text_value[0]);
					}
					label_end = i;
				}
			}
			else if (speed_pid)
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
						spd_ConstantP = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "i"))
					{
						spd_ConstantI = atoi(&text_value[0]);
					}
					else if (!strcmp(&value_name[0], "d"))
					{
						spd_ConstantD = atoi(&text_value[0]);
					}
					label_end = i;
				}
			}
			else if (error_boolean)
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
					if (!strcmp(&value_name[0], "st"))
					{
						steering_error = atoi(&text_value[0]);
						turn_error_received = true;
					}
					else if (!strcmp(&value_name[0], "sp"))
					{
						target_speed = atoi(&text_value[0]);
						sprintf(&value_msg[0],"target speed == %d\n",target_speed);
						send_data(value_msg);
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
	else if(steering_pid)
	{
		sprintf(&value_msg[0], "Received steering pid p:%d i:%d d:%d\n", ConstantP,ConstantI,ConstantD );
	}
	else if(speed_pid)
	{
		sprintf(&value_msg[0], "Received speed pid p:%d i:%d d:%d\n", spd_ConstantP,spd_ConstantI,spd_ConstantD );
	}
	else if(telemetry)
	{
		sprintf(&value_msg[0], "sspeed:s=%d:d=%d:\n", velocity,detection );

	}
	else if(emergencystop)
	{
		sprintf(&value_msg[0], "Received EMERGENCYSTOP\n");
	}
	else if (error_boolean)
	{
		sprintf(&value_msg[0],"Received errors st=%d sp=%d\n",steering_error, speed_error);
	}
	else
	{
		sprintf(&value_msg[0],"eerrr:e=1:\n");
	}
	send_data(&value_msg[0]);
	*/
	
}
