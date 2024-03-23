def show_tcp_position():
    ret = robot.get_tcp_position()
    ret_end_pos = ret[1]
    print(ret_end_pos)
    
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

vel_ang = 0.3
vel_lin = 50/vel_ang
del_lin = 0.1*vel_lin#线速度增量系数
del_ang = 1*vel_ang#角度增量系数
del_ang_6 = 1#六轴角速度增量系数


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
usr_end_pos_vel = usr_end_pos
usr_end_pos_ang = usr_end_pos

usr_joint_pos = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
#screen = pygame.display.set_mode((640, 240))

# # robot.logout() #登出


res_hat = 0
res_jhat = 0


while not done:


    usr_end_pos_vel = usr_end_pos
    usr_end_pos_ang = usr_end_pos

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
                show_tcp_position()

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
    hat = joystick.get_hat(0)  # 左右控制第六关节旋转，是左右按键
    #print(hat)
    res_hat = hat[0] * del_ang
    res_jhat = hat[1] * del_ang
    #print(res_hat)
    #print(res_jhat)

    # axes = joystick.get_numaxes()
    res = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    for i in range(6):  # 左右摇杆(右上下为2，左右为3)
        axis = joystick.get_axis(i)
        if i < 2:#左摇杆上下控制x，左右控制y
            if abs(axis) > 0.99:
                res[i] = axis * del_lin
            else:
                res[i] = 0
        if (i == 3):#右摇杆上下控制z，左右控制Rx
            if abs(axis) > 0.9:
                res[2] = axis * del_lin
            else:
                res[2] = 0
            # print(axis)
        if (i == 2): #右摇杆左右控制Rx
            if abs(axis) > 0.5:
                res[3] = axis * del_ang
            else:
                res[3] = 0
        if (i == 4) | (i == 5):#左右肩键控制Ry
            # print(axis)
            if axis > 0:
                res[i] = (axis + 1)/2 * del_ang
            else:
                res[i] = 0
    print(res)
    if res == [0, 0, 0, 0, 0, 0] and hat[0] == 0 and hat[1] == 0 :
        #robot.motion_abort()
        ret_stop = robot.get_tcp_position()
        usr_end_pos = ret_stop[1]
    pygame.time.wait(1)

    ret = robot.get_tcp_position()
    usr_end_pos = ret[1]

    if res != [0, 0, 0, 0, 0, 0] or hat[0] != 0 or hat[1] != 0 :
        usr_end_pos[0] += res[0]
        usr_end_pos[1] += res[1]
        usr_end_pos[2] += res[2]
        usr_end_pos[3] += res[3]
        usr_end_pos[4] += res[4]
        usr_end_pos[4] -= res[5]
        usr_end_pos[5] += res_hat
        usr_end_pos[5] -= res_jhat

        # usr_end_pos_vel[0] += res[0]
        # usr_end_pos_vel[1] += res[1]
        # usr_end_pos_vel[2] += res[2]


        # res_hat = 0
        res = [0, 0, 0, 0, 0, 0]
        # print(usr_joint_pos)
        # show_tcp_position()
        # print(usr_end_pos)
        try:
            print("expected:")
            print(usr_end_pos)
            robot.set_rapidrate(vel_ang)
            ret = robot.linear_move(end_pos=usr_end_pos, move_mode=ABS, is_block=False,
                                    speed=vel_lin)
            print("real:")
            ret = robot.get_tcp_position()
            ret_end_pos_real = ret[1]
            print(ret_end_pos_real)
 
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


