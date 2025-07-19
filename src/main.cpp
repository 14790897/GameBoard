#include <JoystickShield.h>

// 创建 JoystickShield 对象
JoystickShield joystickShield;

void setup() {
    // 初始化串口通信
    Serial.begin(115200);
    
    // 等待串口准备就绪
    delay(1000);
    
    Serial.println("=== JoystickShield 测试程序 ===");
    Serial.println("正在校准摇杆...");
    
    // 校准摇杆中心位置
    joystickShield.calibrateJoystick();
    
    Serial.println("校准完成！");
    Serial.println("开始检测摇杆和按钮状态...");
    Serial.println();
    
    // 硬件连接说明（默认引脚配置）：
    // 摇杆 X 轴 -> A0
    // 摇杆 Y 轴 -> A1  
    // 摇杆按键 -> 引脚 8
    // 上按钮   -> 引脚 2
    // 右按钮   -> 引脚 3
    // 下按钮   -> 引脚 4
    // 左按钮   -> 引脚 5
    // E 按钮   -> 引脚 6
    // F 按钮   -> 引脚 7
    
    // 如果使用不同的引脚，可以取消下面的注释并修改：
    // joystickShield.setJoystickPins(0, 1);  // X轴, Y轴
    // joystickShield.setButtonPins(8, 2, 3, 4, 5, 7, 6); // K,A,B,C,D,F,E
}

void loop() {
    // 处理摇杆和按钮事件
    joystickShield.processEvents();
    
    // 检测摇杆方向（8个方向）
    if (joystickShield.isUp()) {
        Serial.println("摇杆：上");
    }
    
    if (joystickShield.isRightUp()) {
        Serial.println("摇杆：右上");
    }
    
    if (joystickShield.isRight()) {
        Serial.println("摇杆：右");
    }
    
    if (joystickShield.isRightDown()) {
        Serial.println("摇杆：右下");
    }
    
    if (joystickShield.isDown()) {
        Serial.println("摇杆：下");
    }
    
    if (joystickShield.isLeftDown()) {
        Serial.println("摇杆：左下");
    }
    
    if (joystickShield.isLeft()) {
        Serial.println("摇杆：左");
    }
    
    if (joystickShield.isLeftUp()) {
        Serial.println("摇杆：左上");
    }
    
    // 检测摇杆按键
    if (joystickShield.isJoystickButton()) {
        Serial.println("摇杆按键按下");
    }
    
    // 检测方向按钮
    if (joystickShield.isUpButton()) {
        Serial.println("上按钮按下");
    }
    
    if (joystickShield.isRightButton()) {
        Serial.println("右按钮按下");
    }
    
    if (joystickShield.isDownButton()) {
        Serial.println("下按钮按下");
    }
    
    if (joystickShield.isLeftButton()) {
        Serial.println("左按钮按下");
    }
    
    // 检测功能按钮
    if (joystickShield.isEButton()) {
        Serial.println("E 按钮按下");
    }
    
    if (joystickShield.isFButton()) {
        Serial.println("F 按钮按下");
    }
    
    // 检测摇杆是否不在中心位置
    if (joystickShield.isNotCenter()) {
        Serial.println("摇杆偏离中心");
    }
    
    // 显示摇杆位置数据（-100 到 100）
    int xPos = joystickShield.xAmplitude();
    int yPos = joystickShield.yAmplitude();
    
    // 只在摇杆移动时显示位置信息
    if (xPos != 0 || yPos != 0) {
        Serial.print("摇杆位置 -> X: ");
        Serial.print(xPos);
        Serial.print(", Y: ");
        Serial.println(yPos);
    }
    
    // 延迟避免输出过快
    delay(100);
}
