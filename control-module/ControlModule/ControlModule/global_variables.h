#ifndef GLOBAL_VARIABLES
#define GLOBAL_VARIABLES
extern volatile unsigned steering;

extern volatile bool manual_mode;

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

extern volatile int P;
extern volatile int I;
extern volatile int D;
extern volatile int velocity;
extern volatile int steering_from_pi;
extern volatile int error;
extern volatile int detection;

#endif