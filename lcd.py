import pigpio
from time import sleep

class LcdScreen:
    def __init__(self,rs = 25,e = 24,d4 = 23,d5 = 18,d6 = 15,d7 = 14):
        self.pi=pigpio.pi()
        self.RS=rs
        self.E=e
        self.D=[d4,d5,d6,d7]
        for pin in[self.RS,self.E]+self.D:
            self.pi.set_mode(pin,pigpio.OUTPUT)
        self.init()
        
    #tell lcd to read D4-D7 through short impulse on E    
    def pulse(self):
        self.pi.write(self.E,0)
        sleep(0.0005)
        self.pi.write(self.E,1)
        sleep(0.0005)
        self.pi.write(self.E,0)
        sleep(0.0005)

    #set GPIO pins (connected to D4-D7) to data
    def write4(self,data):
        for i in range(4):
            self.pi.write(self.D[i],(data>>i)&1)
        self.pulse()

    #send byte(2x 4bits) to RS in mode=0 or mode=1
    def send(self,val,mode):
        self.pi.write(self.RS,mode)
        self.write4(val>>4)
        self.write4(val&0x0F)
        sleep(0.01)

    #init lcd screen to 4 bit mode
    def init(self):
        sleep(0.05)
        self.send(0x01,0)  # clean screen
        sleep(0.05)
        for _ in range(3):
            self.write4(0x03)
            sleep(0.005)
        self.write4(0x02)
        self.send(0x28,0)   #2 lines 5x8 pixel font
        self.send(0x0C,0)   #cursor migotanie off
        self.send(0x06,0)   #cursor moves to right after writing letter
        self.send(0x01,0)   #cursor on start and clean screen
        sleep(0.01)

    def clear(self):
        sleep(0.02)
        self.send(0x01,0)  # clean screen
        sleep(0.02)
        for _ in range(3):
            self.write4(0x03)
            sleep(0.005)
        self.write4(0x02)
        self.send(0x28,0)   #2 lines 5x8 pixel font
        self.send(0x0C,0)   #cursor migotanie off
        self.send(0x06,0)   #cursor moves to right after writing letter
        self.send(0x01,0)   #cursor on start and clean screen
        sleep(0.01)

    def display(self,text,line=1):
        addr=0x80 if line==1 else 0xC0 #ddram in scrren needs that
        self.send(addr,0)   #sets cursor to line 1 or 2
        for c in text.ljust(16)[:16]:   #ljust adds spaces to 16 letters
            self.send(ord(c),1)         #sends ascii code


#tests
if __name__ == '__main__':
    lcd=LcdScreen(rs = 25,e = 24,d4 = 23,d5 = 18,d6 = 15,d7 = 14)
    happy_people_counter = 0

    lcd.display("WYWOLANYCH",1)
    lcd.display("USMIECHOW:",2)


    for i in range(50):
        happy_people_counter += 1
        lcd.display("WYWOLANYCH",1)
        lcd.display("USMIECHOW: "+str(happy_people_counter),2)
        sleep(1)