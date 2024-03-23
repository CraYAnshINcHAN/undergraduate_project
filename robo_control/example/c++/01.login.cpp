#include <JAKAZuRobot.h>

int main()
{
    JAKAZuRobot robot;
    robot.login_in("192.168.137.162");
    robot.login_out();
    return 0;
}