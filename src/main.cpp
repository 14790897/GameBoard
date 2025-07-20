#include <JoystickShield.h>

// Create JoystickShield object
JoystickShield joystickShield;

// Variable to track joystick center state
bool wasNotCenter = false;

// Heartbeat variables
unsigned long lastHeartbeat = 0;
const unsigned long heartbeatInterval = 5000; // 5 seconds

void setup() {
    // Initialize serial communication
    Serial.begin(115200);

    // Wait for serial port to be ready
    delay(1000);

    Serial.println("=== JoystickShield Game Controller ===");
    Serial.println("Calibrating joystick...");

    // Calibrate joystick center position
    joystickShield.calibrateJoystick();

    Serial.println("Calibration complete!");
    Serial.println("Starting joystick and button detection...");
    Serial.println();

    // Hardware connection description (default pin configuration):
    // Joystick X-axis -> A0
    // Joystick Y-axis -> A1
    // Joystick button -> Pin 8
    // Up button       -> Pin 2
    // Right button    -> Pin 3
    // Down button     -> Pin 4
    // Left button     -> Pin 5
    // E button        -> Pin 6
    // F button        -> Pin 7

    // If using different pins, uncomment and modify the following:
    // joystickShield.setJoystickPins(0, 1);  // X-axis, Y-axis
    // joystickShield.setButtonPins(8, 2, 3, 4, 5, 7, 6); // K,A,B,C,D,F,E
}

void loop() {
    // Process joystick and button events
    joystickShield.processEvents();

    // Detect joystick directions (8 directions)
    if (joystickShield.isUp()) {
        Serial.println("Joystick Up");
    }

    if (joystickShield.isRightUp()) {
        Serial.println("Joystick RightUp");
    }

    if (joystickShield.isRight()) {
        Serial.println("Joystick Right");
    }

    if (joystickShield.isRightDown()) {
        Serial.println("Joystick RightDown");
    }

    if (joystickShield.isDown()) {
        Serial.println("Joystick Down");
    }

    if (joystickShield.isLeftDown()) {
        Serial.println("Joystick LeftDown");
    }

    if (joystickShield.isLeft()) {
        Serial.println("Joystick Left");
    }

    if (joystickShield.isLeftUp()) {
        Serial.println("Joystick LeftUp");
    }

    // Detect joystick button
    if (joystickShield.isJoystickButton()) {
        Serial.println("Joystick Button Clicked");
    }

    // Detect direction buttons
    if (joystickShield.isUpButton()) {
        Serial.println("Up Button Clicked");
    }

    if (joystickShield.isRightButton()) {
        Serial.println("Right Button Clicked");
    }

    if (joystickShield.isDownButton()) {
        Serial.println("Down Button Clicked");
    }

    if (joystickShield.isLeftButton()) {
        Serial.println("Left Button Clicked");
    }

    // Detect function buttons
    if (joystickShield.isEButton()) {
        Serial.println("E Button Clicked");
    }

    if (joystickShield.isFButton()) {
        Serial.println("F Button Clicked");
    }

    // Detect joystick center state changes
    bool currentNotCenter = joystickShield.isNotCenter();

    if (currentNotCenter) {
        // Joystick is not in center
        if (!wasNotCenter) {
            // Just moved away from center
            Serial.println("Joystick NotCenter");
        }
        wasNotCenter = true;
    } else {
        // Joystick is in center
        if (wasNotCenter) {
            // Just returned to center - send center event
            Serial.println("Joystick Center");
        }
        wasNotCenter = false;
    }

    // Display joystick position data (-100 to 100)
    int xPos = joystickShield.xAmplitude();
    int yPos = joystickShield.yAmplitude();

    // Only display position info when joystick is moved
    if (xPos != 0 || yPos != 0) {
        Serial.print("Joystick Position -> X: ");
        Serial.print(xPos);
        Serial.print(", Y: ");
        Serial.println(yPos);
    }
    static bool wasNotCenter = false;  // 静态变量，保持状态

    bool nowNotCenter = joystickShield.isNotCenter();
    if (wasNotCenter && !nowNotCenter) {
        Serial.println("Joystick Centered");
    }
    wasNotCenter = nowNotCenter;
    // Send heartbeat every 5 seconds to confirm Arduino is running
    unsigned long currentTime = millis();
    if (currentTime - lastHeartbeat >= heartbeatInterval) {
        // Serial.println("Arduino Heartbeat");
        lastHeartbeat = currentTime;
    }

    // Delay to avoid too fast output
    delay(100);
}
