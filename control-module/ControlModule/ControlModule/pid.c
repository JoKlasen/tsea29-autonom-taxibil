#include <stdio.h>

int ConstantP, ConstantI, ConstantD;
int PTerm, ITerm, DTerm;
int CurrentI, MaxI, MinI;
int dTemp = 0;

// Set up PID variables from external source.
void PIDSetup(int InputP, int InputI, int InputD) {
    ConstantP = InputP;
    ConstantI = InputI;
    ConstantD = InputD;
}

// Returns amount of steering to counteract error.
int PIDIteration(int Error) {
    PTerm = (Error * ConstantP);
    
    CurrentI += Error;
    if (CurrentI > MaxI) {
        CurrentI = MaxI;
    }
    else if (CurrentI < MinI) {
        CurrentI = MinI;
    }
    ITerm = (ConstantI * CurrentI);

    DTerm = ConstantD * (dTemp - Error);
    dTemp = Error;

    return (PTerm + ITerm + DTerm);
}

int main() {
    PIDSetup(10, 2, 2);
    
    int steering = PIDIteration(10);
    printf("Steering: %d\n", steering);
}
