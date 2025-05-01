from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory


class ServoController:
    def __init__(self,pin=12, starting_value = -1):
        self.pin_factory=PiGPIOFactory()

        self.servo=Servo(pin,
                         min_pulse_width=500/1_000_000,
                         max_pulse_width=2500/1_000_000,
                         pin_factory=self.pin_factory)
        self.move_to_value(starting_value)

    def move_to_value(self,value):
        value=max(-1,min(1,value))
        self.servo.value=value
    
    def move_to_max(self):
        self.servo.value=1

    def move_to_mid(self):
        self.servo.value=0
    
    def move_to_min(self):
        self.servo.value=-1

    def stop(self):
        self.servo.value=None
        self.servo.close()


#test
if __name__=="__main__":
    servo=ServoController()
    try:
        while True:
            val=input("Podaj wartość od -1 do 1: ")
            try:
                num=float(val)
                servo.move_to_value(num)
            except ValueError:
                print("Niepoprawna liczba")
    except KeyboardInterrupt:
        print("\nZatrzymano przez użytkownika")
    finally:
        servo.zamknij()
