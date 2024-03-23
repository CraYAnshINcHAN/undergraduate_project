import pygame
import jkrc

pygame.quit()
pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
while True:
    pygame.event.get()
    print(joystick.get_button(5))
    # print(joystick.get_button(1))
    # pygame.time.wait(1000)


    # pygame.time.wait(10)
    # pygame.event.get()
        # print("start for")
        # if event.type == pygame.JOYBUTTONDOWN:
        #     if joystick.get_button(0):  # A键connect
        #         print("A")
        # print("end for")
        #  # 左右摇杆(右上下为2，左右为3)
    # axis = joystick.get_axis(0)
    # print(str(0)+":"+str(axis))

    # hat = joystick.get_hat(0)
    # print(hat)

    


