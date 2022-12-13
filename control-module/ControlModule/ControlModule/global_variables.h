#ifndef GLOBAL_VARIABLES
#define GLOBAL_VARIABLES
extern volatile unsigned steering;

extern volatile bool manual_mode;
extern volatile bool velocity_received;
extern volatile bool man_left;
extern volatile bool man_right;
extern volatile bool man_forward;
extern volatile bool man_back;
extern volatile unsigned long long old_millis;

extern volatile bool update;
extern volatile unsigned long long milliseconds;

extern volatile bool received;
extern char receive_buffer[RECEIVE_BUFFER_SIZE];
extern char working_buffer[RECEIVE_BUFFER_SIZE];
extern volatile int receive_buffer_index;

extern volatile int velocity;
extern volatile int steering_error;
extern volatile int target_speed;
extern volatile int detection;
extern volatile bool turn_error_received;
extern volatile bool speed_error_received;
extern volatile bool velocity_received;

extern volatile int ConstantP, ConstantI, ConstantD;
extern volatile int PTerm, ITerm, DTerm;
extern volatile int CurrentI, MaxI, MinI;
extern volatile int dTemp;

extern volatile int spd_ConstantP, spd_ConstantI, spd_ConstantD;
extern volatile int spd_PTerm, spd_ITerm, spd_DTerm;
extern volatile int spd_CurrentI, spd_MaxI, spd_MinI;
extern volatile int spd_dTemp;

extern volatile int Latest_SPerror;
extern volatile int Latest_SP;
extern volatile int Latest_STerror;
extern volatile int Latest_ST;

#endif