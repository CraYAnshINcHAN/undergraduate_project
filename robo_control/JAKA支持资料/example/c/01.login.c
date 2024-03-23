#include <jakaAPI.h>

int main()
{
    JKHD hd;
    create_handler("192.168.137.162", &hd);
    destory_handler(&hd);
    return 0;
}