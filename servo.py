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
from time import sleep

if __name__=="__main__":
    print("[TEST] Uruchamianie testu serwa...")

    servo_upper_start = -1 #swap this to make servo move diffrent values
    last_upper_move = servo_upper_start 
    move_upper_first = -1 * servo_upper_start
    move_upper_second = servo_upper_start

    servo_lower_start = -1 #swap this to make servo move diffrent values
    last_lower_move = servo_lower_start 
    move_lower_first = -1 * servo_lower_start
    move_lower_second = servo_lower_start

    servo_upper=ServoController(pin=12,starting_value=servo_upper_start)
    servo_lower=ServoController(pin=13,starting_value=servo_lower_start)

    try:
        while True:
            print("\n[MENU TESTOWE]")
            print("1 - Ruch górnego serwa: ")
            print("2 - Ruch dolnego serwa: ")
            print("3 - Ruch obu serw jak w wydawaniu przedmiotu")
            print("4 - ruch dowolny serwo upper")
            print("5 - ruch dowolny serwo lower")

            opcja=input("Wybierz opcję: ").strip()
            if opcja=="1":
                servo_upper.move_to_value(move_upper_first)
                last_move = move_upper_first
                sleep(1) #time to get item through first servo
                servo_upper.move_to_value(move_upper_second)
                last_move = move_upper_second

            elif opcja=="2":
                servo_lower.move_to_value(move_lower_first)
                last_move = move_lower_first
                sleep(2) #time to get item through second servo
                servo_lower.move_to_value(move_lower_second)
                last_move = move_lower_second

            elif opcja=="3":
                servo_upper.move_to_value(move_upper_first)
                last_move = move_upper_first
                sleep(1) #time to get item through first servo
                servo_upper.move_to_value(move_upper_second)
                last_move = move_upper_second
                sleep(1.5) #time between first servo closing tube and second servo opening it
                servo_lower.move_to_value(move_lower_first)
                last_move = move_lower_first
                sleep(2) #time to get item through second servo
                servo_lower.move_to_value(move_lower_second)
                last_move = move_lower_second

            elif opcja=="4":
                value = input("podaj liczbe od -1 do 1: ")
                servo_upper.move_to_value(float(value))
            
            elif opcja=="5":
                value = input("podaj liczbe od -1 do 1: ")
                servo_lower.move_to_value(float(value))

            else:
                print("Niepoprawna opcja.")

    except KeyboardInterrupt:
        print("\n[INFO] Przerwano przez użytkownika.")

    finally:
        print("[CLEANUP] Zatrzymywanie serw...")
        servo_upper.stop()
        servo_lower.stop()
        print("[KONIEC TESTU] Serwa wyłączone.")
