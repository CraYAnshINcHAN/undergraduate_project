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
else:
    print("no login")
    
robot.set_user_frame_id(1)
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

while True:
    ret = robot.get_tcp_position()
    print(ret[1])
    pygame.time.wait(5000)