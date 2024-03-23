// 定义电机和开关引脚
#define ENA 10
#define IN1 9
#define IN2 8
#define ENB 7
#define IN3 6
#define IN4 5


#define SWITCH1 1
#define SWITCH2 2
#define SWITCH3 3
#define SWITCH4 4

void setup() {
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);

  pinMode(SWITCH1, INPUT);
  pinMode(SWITCH2, INPUT);
  pinMode(SWITCH3, INPUT);
  pinMode(SWITCH4, INPUT);
}

void loop() {
  // 读取开关状态
  int switch1 = digitalRead(SWITCH1);
  int switch2 = digitalRead(SWITCH2);
  int switch3 = digitalRead(SWITCH3);
  int switch4 = digitalRead(SWITCH4);
  // 根据开关状态控制电机
  if (switch1 == HIGH && switch2 == LOW && switch3 == LOW && switch4 == LOW) {
    // 开关1开启，A正传
    digitalWrite(IN1, HIGH);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
  } else if (switch2 == HIGH && switch1 == LOW && switch3 == LOW && switch4 == LOW) {
    // 开关2开启，A电机反转
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, HIGH);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, LOW);
  } else if (switch3 == HIGH && switch2 == LOW && switch1 == LOW && switch4 == LOW) {
    // 开关3开启，B电机正转
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, HIGH);
    digitalWrite(IN4, LOW);
  } else if(switch4 == HIGH && switch2 == LOW && switch3 == LOW && switch1 == LOW) {
    // 开关四开启，B电机反转
    digitalWrite(IN1, LOW);
    digitalWrite(IN2, LOW);
    digitalWrite(IN3, LOW);
    digitalWrite(IN4, HIGH);
  }
}
