#include "jkerr.h"
#include "jktypes.h"
#include <jakaAPI.h>
#include <stdio.h>

#define STR_RES(ret) ((ret)==ERR_SUCC?"SUCC":"FAIL")

int main()
{
    JKHD hd;
    errno_t ret = ERR_SUCC;
    int i = 4;

    while (i--)
    {
        printf("===========================\n");

        ret = create_handler("192.168.137.138", &hd);
        printf("create_handler: %s\n", STR_RES(ret));

        ret = power_on(&hd);
        printf("power_on: %s\n", STR_RES(ret));

        ret = enable_robot(&hd);
        printf("enable_robot: %s\n", STR_RES(ret));

        ret = disable_robot(&hd);
        printf("disable_robot: %s\n", STR_RES(ret));

        ret = power_off(&hd);
        printf("power_off: %s\n", STR_RES(ret));
        
        ret = destory_handler(&hd);
        printf("destory_handler: %s\n", STR_RES(ret));

        printf("\n");
    }

    return 0;
}