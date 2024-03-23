#include <JAKAZuRobot.h>
#include <chrono>
#include <iostream>
#include <thread>

#define JK_PI (3.141592653589793)

int main()
{
    JAKAZuRobot robot;
    errno_t ret = ERR_SUCC;

    while (true)
    {
        std::cout << "===========================\n";

        ret = robot.login_in("192.168.137.138");
        std::cout << "login: " << (ret == ERR_SUCC ? "SUCC" : "FAIL") << std::endl;

        ret = robot.power_on();
        std::cout << "power_on: " << (ret == ERR_SUCC ? "SUCC" : "FAIL") << std::endl;

        ret = robot.enable_robot();
        std::cout << "enable_robot: " << (ret == ERR_SUCC ? "SUCC" : "FAIL") << std::endl;

        ret = robot.disable_robot();
        std::cout << "disable_robot: " << (ret == ERR_SUCC ? "SUCC" : "FAIL") << std::endl;

        ret = robot.power_off();
        std::cout << "disable_robot: " << (ret == ERR_SUCC ? "SUCC" : "FAIL") << std::endl;

        ret = robot.login_out();
        std::cout << "login_out: " << (ret == ERR_SUCC ? "SUCC" : "FAIL") << std::endl;

        std::cout << "\n";
    }

    return 0;
}