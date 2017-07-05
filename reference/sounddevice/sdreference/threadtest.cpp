/*
*   file:       threadtest.cpp
*   author:     Conner Brown
*   date:       5/9/2017
*   update:     5/9/2017
*   brief:      use thread library to share variables across processes, specifically timing information to be used in onbeat.py (and eventually to onbeat.cpp)
*/

#include <thread>
#include <atomic>
#include <iostream>
#include <unistd.h>
using namespace std;
atomic<bool> button(false);

void trigger() {
int x=0;
cin >> x;
if (x>0) {
    button=true;
    }
}


void response() {
//atomic<bool> button=false;
while (!button) {
    cout << "don't press the button" << endl;
    usleep(1000000);
    }
cout << "you pressed the button...." << endl;
}


int main() {
thread t1(trigger);
thread t2(response);
t1.join();
t2.join();
return 0;
}
