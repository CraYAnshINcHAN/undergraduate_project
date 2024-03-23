//定义引脚
int in1 = 8;
int in2 = 7;

void setup() {
//设置引脚模式
pinMode(in1, OUTPUT);
pinMode(in2, OUTPUT);
}

void loop() {
//设置电机顺时针旋转
digitalWrite(in1, HIGH);
digitalWrite(in2, LOW);

//等待一段时间
delay(20000);


}
