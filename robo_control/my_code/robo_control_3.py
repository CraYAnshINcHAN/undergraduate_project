import pygame
import jkrc
import time

pygame.quit()
pygame.init()   
joystick = pygame.joystick.Joystick(0)
joystick.init()
done = False
ABS = 0  # 绝对运动
INCR = 1  # 增量运动

vel_ang = 5/180*3.14
vel_lin = 30

flag = [True, True, True, True, True, True]

robot = jkrc.RC("10.5.5.100")  # ip address
while (not robot.login()):
    time.sleep(3)
    robot.login()
if (robot.login()):
    print("login successfully!")
robot.set_user_frame_id(1)
robot.set_tool_id(1)
ret = robot.get_tcp_position()
ret_end_pos = ret[1]
print(ret_end_pos)

# #robot.linear_move(end_pos=ret_end_pos, move_mode=ABS, is_block=False, speed=50)
usr_end_pos = ret_end_pos

usr_joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#screen = pygame.display.set_mode((640, 240))

# # robot.logout() #登出
vel_actual = [0, 0, 0, 0, 0, 0]
vel_total_last = [0, 0, 0, 0, 0, 0, 0]
vel_total = [0, 0, 0, 0, 0, 0]
res_hat = 0
res_jhat = 0
print(usr_end_pos)
usr_end_pos_new = usr_end_pos
j = 0

robot.set_rapidrate(0.1)
while not done:
    print(j)
    j = j + 1
    flag = [True, True, True, True, True, True]
    vel_total_last = vel_total.copy()
    print(vel_total_last)
    pygame.event.get()
#for event in pygame.event.get():
    if joystick.get_button(0):  # A键connect
        if robot.login(): 
                # print("A")
                # home = [112, 311, 255, 3.14, -0, 0]
            home = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
            ret_end_pos = home
            if robot.linear_move(end_pos=ret_end_pos, move_mode=ABS, is_block=True, speed=50):
                usr_end_pos = ret_end_pos
                print("Successfully Back to Home!")

    if joystick.get_button(2): #X
        if robot.power_on():
            print('tcp_position'+str(robot.get_tcp_position()))
            print('joint_position'+str(robot.get_joint_position()))
            print('robot_state'+str(robot.get_robot_state()))

    if joystick.get_button(3): #Y
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
    res_hat = joystick.get_button(4)
    res_jhat = joystick.get_button(5)  # LB、RB控制第六关节旋转
    #print(hat)
    #print(res_hat)
    #print(res_jhat)
    
    # axes = joystick.get_numaxes()
    res = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for i in range(6):  # 左右摇杆(右上下为2，左右为3)
        axis = joystick.get_axis(i)
        if i < 2:#左摇杆左右控制x，上下控制y
            if abs(axis) > 0.5:
                res[i] = axis
            else:
                res[i] = 0
        if (i == 3):#右摇杆上下控制z
            if abs(axis) > 0.5:
                res[2] = axis
            else:
                res[2] = 0
            # print(axis)
        if (i == 2): #右摇杆左右控制Rx
            if abs(axis) > 0.5:
                res[3] = axis
            else:
                res[3] = 0
        if (i == 4) | (i == 5):#左右肩键控制Ry
            # print(axis)
            if axis > 0:
                res[i] = (axis + 1)/2
            else:
                res[i] = 0
    if res == [0, 0, 0, 0, 0, 0] and res_hat == 0 and res_jhat == 0 :
        #robot.motion_abort()
        ret_stop = robot.get_tcp_position()
        usr_end_pos = ret_stop[1]
    pygame.time.wait(1)

    for i in range(4):
        vel_total[i] = res[i] 

    vel_total[4] = res[4] - res[5]
    vel_total[5] = res_hat - res_jhat
    print('127')
    print(vel_total_last)

    print('vel_total:')
    print(vel_total)
    print('vel_total_last:')
    print(vel_total_last)
    
    for i in range(6):
        if (abs(vel_total[i] - vel_total_last[i])) < 0.5:
            vel_total[i] = vel_total_last[i]
            flag[i] = True
        else:
            flag[i] = False
    for i in range(6):
        if (i < 3):
            vel_actual[i] = vel_total[i] * vel_lin
        if(i >= 3):
            vel_actual[i] = vel_total[i] * vel_ang

    ret = robot.get_tcp_position()
    usr_end_pos = ret[1]

    #if res != [0, 0, 0, 0, 0, 0] or hat[0] != 0 or hat[1] != 0 :
        # usr_end_pos[0] += res[0]
        # usr_end_pos[1] += res[1]
        # usr_end_pos[2] += res[2]
        # usr_end_pos[3] += res[3]
        # usr_end_pos[4] += res[4]
        # usr_end_pos[4] -= res[5]
        # usr_end_pos[5] += res_hat
        # usr_end_pos[5] -= res_jhat

        # usr_end_pos_vel[0] += res[0]
        # usr_end_pos_vel[1] += res[1]
        # usr_end_pos_vel[2] += res[2]


        # res_hat = 0
    res = [0, 0, 0, 0, 0, 0]
        # print(usr_joint_pos)
        # show_tcp_position()
        # print(usr_end_pos)
    for i in range(6):
        if (flag[i] == False):
            try:
                print(i)
                robot.jog_stop(-1)
                robot.jog(aj_num = i, move_mode = 0, coord_type = 0, jog_vel = vel_actual[i])
                print(vel_actual)
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
    time.sleep(5)

pygame.quit()




    