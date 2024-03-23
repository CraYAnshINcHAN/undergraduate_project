#include <jakaAPI.h>
#include <stdio.h>

#define STR_RES(ret) ((ret)==ERR_SUCC?"SUCC":"FAIL")
#define STR_INPOS(ret) ((ret)?"True":"False")

int main()
{
    JKHD hd;
    errno_t ret = ERR_SUCC;
    int i = 4;
    JointValue cur_jval;
    BOOL inpos = 0, last_inpos = 0;
    double thresholding;

    printf("===========================\n");

    ret = create_handler("192.168.137.173", &hd);
    printf("create_handler: %s\n", STR_RES(ret));

    ret = power_on(&hd);
    printf("power_on: %s\n", STR_RES(ret));

    get_in_pos_thresholding(&hd, &thresholding);
    printf("thresholding: %lf.\n", thresholding);

    set_in_pos_thresholding(&hd, 0.001);
    
    get_in_pos_thresholding(&hd, &thresholding);
    printf("after - thresholding: %lf.\n", thresholding);

    while (1)
    {
        get_joint_position(&hd, &cur_jval);
        is_in_pos(&hd, &inpos);
        if (inpos != last_inpos)
        {
            printf("jval is {%lf, %lf, %lf, %lf, %lf, %lf}.", cur_jval.jVal[0], cur_jval.jVal[1], cur_jval.jVal[2],
                cur_jval.jVal[3], cur_jval.jVal[4], cur_jval.jVal[5]);
            printf("{%s, %s}\n", STR_INPOS(inpos), STR_INPOS(last_inpos));
        }
        last_inpos = inpos;
    }


    ret = destory_handler(&hd);
    printf("destory_handler: %s\n", STR_RES(ret));

    printf("\n");

    return 0;
}