#include <stdio.h>

#include "definitions.h"
#include "global_variables.h"
// Set up PID variables from external source.
void PIDSetup(int InputP, int InputI, int InputD) {
    ConstantP = InputP;
    ConstantI = InputI;
    ConstantD = InputD;


    // TODO: Take parameters, add parsing
    spd_ConstantP = 1;
    spd_ConstantI = 0; 
    spd_ConstantD = 0;
}

// Returns amount of steering to counteract error.
int PIDIteration(int Error) {
	
    PTerm = (Error * ConstantP);
    
    // Integration commented out since compiler cant optimize it away

    // CurrentI += Error;
    // if (CurrentI > MaxI) {
    //     CurrentI = MaxI;
    // }
    // else if (CurrentI < MinI) {
    //     CurrentI = MinI;
    // }
    // ITerm = (ConstantI * CurrentI);

    DTerm = ConstantD * (dTemp - Error);
    dTemp = Error;

    return ((PTerm + DTerm) ); // + ITerm 
}

int spd_PIDIteration(int Error) {
	
    spd_PTerm = (Error * spd_ConstantP);
    
    spd_CurrentI += Error;
    if (spd_CurrentI > spd_MaxI) {
        spd_CurrentI = spd_MaxI;
    }
    else if (spd_CurrentI < spd_MinI) {
        spd_CurrentI = spd_MinI;
    }
    spd_ITerm = (spd_ConstantI * spd_CurrentI);

    spd_DTerm = spd_ConstantD * (spd_dTemp - Error);
    spd_dTemp = Error;

    return ((spd_PTerm + spd_ITerm + spd_DTerm) ) / 100;
}

/*
int main() {
    PIDSetup(10, 2, 2);
    
    int steering = PIDIteration(10);
    printf("Steering: %d\n", steering);
}
*/