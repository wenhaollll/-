import RPi.GPIO as GPIO
import serial
import time

# ==================== Configuration ====================
IR_DETECT_PIN = 17  # PIR OUT -> Raspberry Pi GPIO17
SERIAL_PORT = "/dev/serial0"  # Hardware serial port
BAUD_RATE = 9600  # Same as PC serial assistant
SEND_MSG = "Person detected\r\n"  # Message to PC

# Global variable: mark if program is running
running = True

# ==================== Cleanup Function for Exit ====================
def cleanup_and_exit():
    """Cleanup resources when exit (Ctrl+C)"""
    global running
    running = False
    print("\n\n=== Exiting Program ===")
    # Close serial port if open
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial port closed successfully")
    # Cleanup GPIO
    GPIO.cleanup()
    print("GPIO resources released successfully")
    print("=== Program Exited Safely ===\n")
    exit(0)

# ==================== Initialization ====================
# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(IR_DETECT_PIN, GPIO.IN)

# Serial setup
try:
    ser = serial.Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=0.1
    )
    print(f"Serial port opened: {SERIAL_PORT}, Baud rate: {BAUD_RATE}")
except Exception as e:
    print(f"Failed to open serial port: {e}")
    GPIO.cleanup()
    exit(1)

# Flag to avoid repeated sending
is_detected = False

# ==================== Main Logic ====================
print("System started! Waiting for PIR detection...")
print("PC Serial Assistant config: 9600 baud, 8N1, no flow control")
print("Press Ctrl + C to exit program safely\n")

try:
    while running:
        ir_level = GPIO.input(IR_DETECT_PIN)
        
        # Detect person (high level) and not sent yet
        if ir_level == GPIO.HIGH and not is_detected:
            print("Person detected! Sending to PC: Person detected")
            ser.write(SEND_MSG.encode("utf-8"))
            is_detected = True
        
        # Person left (low level), reset flag
        elif ir_level == GPIO.LOW and is_detected:
            print("Person left, reset detection state")
            is_detected = False
        
        time.sleep(0.2)  # Anti-shake

# Catch Ctrl+C (KeyboardInterrupt)
except KeyboardInterrupt:
    cleanup_and_exit()

# Catch other exceptions
except Exception as e:
    print(f"\nProgram error: {e}")
    cleanup_and_exit()
