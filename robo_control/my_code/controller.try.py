import pygame
pygame.quit()
pygame.init()
joystick = pygame.joystick.Joystick(0)
joystick.init()
done = False
# while not done:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             done = True
#         if event.type == pygame.JOYBUTTONDOWN:
#             if joystick.get_button(0):
#                 print(0)
#             if joystick.get_button(1):
#                 print(1)
#             if joystick.getbutton(2):
#                 print(2)
