import pygame
import jkrc

pygame.quit()
pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
done = False
ABS = 0  # 绝对运动
INCR = 1  # 增量运动

robot = jkrc.RC("10.5.5.100")  # ip address
if robot.login():
    print("Successfully login!")
    
robot.set_user_frame_id(1)# xqj的问题1：这个id是随便设的吗
robot.set_tool_id(1)

ret = robot.get_tcp_position()
ret_end_pos = ret[1]

robot.linear_move(end_pos=ret_end_pos, move_mode=ABS, is_block=False, speed=50)  #
usr_end_pos = ret_end_pos

usr_joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]


# robot.logout() #登出

res = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
res_hat = 0
res_jhat = 0

while not done:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

        if event.type == pygame.JOYBUTTONDOWN:
            if joystick.get_button(0):  # A键connect
                if robot.login():
                    # print("A")
                    # home = [112, 311, 255, 3.14, -0, 0]
                    home = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    ret_end_pos = home
                    robot.linear_move(end_pos=ret_end_pos, move_mode=ABS, is_block=True, speed=50)
                    usr_end_pos = ret_end_pos
                    if robot.linear_move(end_pos=ret_end_pos, move_mode=ABS, is_block=True, speed=50):
                        print("Successfully Back to Home!")

            if joystick.get_button(2):
                if robot.power_on():
                    print(robot.get_tcp_position())
                    print(robot.get_joint_position())
                    print(robot.get_robot_state())

            if joystick.get_button(3):
                if robot.enable_robot():
                    print(robot.get_robot_state())

            if joystick.get_button(1):  # B键disconnect
                # robot.power_off()
                # robot.disable_robot()
                # if(robot.logout()):
                #     print("Successfully logout!")
                robot.motion_abort()
                ret_stop = robot.get_tcp_position()
                usr_end_pos = ret_stop[1]
                # done = True
                # break

        # if event.type == pygame.JOYHATMOTION:
        hat = joystick.get_hat(0)  # 左右控制第六关节旋转，是左右按键
        res_hat = hat[0] / 50
        res_jhat = hat[1] / 50
 
        # axes = joystick.get_numaxes()
        pygame.time.wait(10)
        for i in range(6):  # 左右摇杆(右上下为2，左右为3)
            axis = joystick.get_axis(i)
            if i < 2:
                if abs(axis) > 0.5:
                    res[i] = axis * 10
                else:
                    res[i] = 0
            if (i == 2) | (i == 3):
                if abs(axis) > 0.5:
                    res[i] = axis / 200
                else:
                    res[i] = 0
                # print(axis)
            if (i == 4) | (i == 5):
                # print(axis)
                if axis > -0.5:
                    res[i] = (axis+5) / 2
                else:
                    res[i] = 0
        # print(res)
        if res == [0, 0, 0, 0, 0, 0] and hat[0] == 0 and hat[1] == 0 :
            robot.motion_abort()
            ret_stop = robot.get_tcp_position()
            usr_end_pos = ret_stop[1]
        pygame.time.wait(1)
        break

    usr_end_pos[0] += res[0]
    usr_end_pos[1] += res[1]
    usr_end_pos[2] += res[4]
    usr_end_pos[2] -= res[5]
    usr_end_pos[3] += res[3]
    usr_end_pos[4] += res[2]
    usr_end_pos[5] += res_hat

    # res_hat = 0
    res == [0, 0, 0, 0, 0, 0]
    
    pygame.time.wait(1)
    # print(usr_joint_pos)
    try:
        ret = robot.linear_move(end_pos=usr_end_pos, move_mode=ABS, is_block=False,
                                speed=10)
    except ValueError:
        print('Out of range')
               
    # usr_joint_pos[5] = res_jhat
    # ret_j = robot.joint_move(joint_pos=usr_joint_pos, move_mode=INCR, is_block=False,
    #                     speed=10)
    # pygame.time.wait(5)
    
    # ret_jtcp = robot.get_tcp_position()
    # usr_end_pos = ret_jtcp[1]
    
    # usr_joint_pos[5] = 0
    # print(usr_end_pos)
    # print("the return value is :",ret)

pygame.quit()
