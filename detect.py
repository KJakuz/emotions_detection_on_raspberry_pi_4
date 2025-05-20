from fer import FER
from time import sleep
import time
import webcam as wc
import servo as srv
import RPi.GPIO as GPIO
from lcd import LcdScreen

if __name__ == "__main__":

    #red led delete
    
    #pin numeration mode (by GPIO names)
    GPIO.setmode(GPIO.BCM)
    green_diode = 16 #init pin for green diode
    GPIO.setup(green_diode,GPIO.OUT)
    #red_diode = 27 
    #GPIO.setup(red_diode,GPIO.OUT)

    #lcd init
    happy_people_counter = 125
    sad_people_counter = 74
    lcd=LcdScreen(rs = 25,e = 24,d4 = 23,d5 = 18,d6 = 15,d7 = 14)
    lcd.display("spoko goscie "+str(happy_people_counter),1)
    lcd.display("smutne ludki "+str(sad_people_counter),2)

    
    # create and run videostream from camera
    # src = 0 for default first connected camera (by usb)
    
    vs = wc.WebcamVideoStream(src=0).start()

    #servo init
    servo_upper_start = 0 #swap this to make servo move diffrent values
    servo_upper = srv.ServoController(pin = 12, starting_value= servo_upper_start)
    neutral_move = servo_upper_start
    happy_move = neutral_move - 0.6
    sad_move = neutral_move + 0.6

    #servo_lower_start = -1 #swap this to make servo move diffrent values
    #servo_lower = srv.ServoController(pin = 13, starting_value= servo_lower_start)
    #last_lower_move = servo_lower_start 
    #move_lower_first = -1 * servo_lower_start
    #move_lower_second = servo_lower_start

    # skip first few frames
    print("[INFO] Kamera uruchomiona, czekam 1 sekundę...")
    time.sleep(1.0)

    # check if program connected with camera (are there frames given to program)
    if vs.stopped or vs.frame is None:
         print("[ERROR] Nie udało się uruchomić strumienia wideo..")
         exit()

    #fps viewer - not used by default
    print("[INFO] Rozpoczynam przetwarzanie klatek...")
    fps_start_time = time.time()
    fps_counter = 0
    
    #init face detector (not emotion recognition)
    detector = FER(mtcnn=True)
    
    frame_counter = 0
    
    #frequency of detections
    process_every_n_frames = 5  # Process every xth frame
    output_interval = 0.7 # Output results every x seconds
    last_output_time = time.time()

    #init for two emotions prevention
    person_present = False
    ready_for_new_person = True
    last_time_with_person = time.time()
    no_face_timeout = 2 # seconds

    #main loop of program
    try:
        while True:

            # get most recent frame from camera
            frame = vs.read()

            # check if frames given by camera are not empty
            if frame is None:
                print("[WARNING] Otrzymano pustą klatkę.")
                time.sleep(0.1)
                continue

            frame_counter += 1
            
            
            # only process every nth frame
            if frame_counter % process_every_n_frames == 0:
                
                # init emotion recognition via FER library
                emotions = detector.detect_emotions(frame)
                
                current_time = time.time()

                # print results at specified interval
                if current_time - last_output_time >= output_interval:
                    #menu
                    print("\n" + "="*50)
                    print(f"Emotion Detection Results ({time.strftime('%H:%M:%S')})")
                    print("="*50)
                    
                    #face not detected
                    if not emotions:
                        GPIO.output(green_diode,GPIO.LOW)
                        print("No faces detected")
                        servo_upper.move_to_value(neutral_move)
                        person_present = False
                        #after no_face_timout seconds allow item hand out
                        if current_time - last_time_with_person > no_face_timeout:
                            ready_for_new_person = True
                    #face detected
                    else:

                        #diode GREEN expressing that the face was found and emotions are recognised
                        
                        GPIO.output(green_diode,GPIO.HIGH)

                        #person_present = True
                        #last_time_with_person = current_time
                        
                        for i, emotion in enumerate(emotions):
                            dominant_emotion = emotion["emotions"]
                            # Sort emotions by confidence (highest first)
                            sorted_emotions = sorted(dominant_emotion.items(), key=lambda x: x[1], reverse=True)
                            
                            print(f"\nFace #{i+1}:")
                            # Print top 3 emotions with confidence scores
                            for emotion_name, score in sorted_emotions[:3]:
                                print(f"  {emotion_name}: {score:.2f}")
                            
                            #when happy emotion detected hand out item by moving servo
                            if sorted_emotions[0][0] == 'happy' or sorted_emotions[0][0] == 'suprise':
                                #if ready_for_new_person:
                                print("[INFO] Happy person detected")
                                
                                #increment lcd screen counter
                                if ready_for_new_person:
                                    happy_people_counter += 1
                                    lcd.clear()
                                    lcd.display("spoko goscie "+str(happy_people_counter),1)
                                    lcd.display("smutne ludki "+str(sad_people_counter),2)

                                #servo showing happy face
                                servo_upper.move_to_value(happy_move)
                                ready_for_new_person = False

                            if sorted_emotions[0][0] == 'neutral':
                                print("[INFO] neutral person detected")
                                                                
                                #increment lcd screen counter
                                #if ready_for_new_person:
                                    #lcd.display("spoko goscie "+str(happy_people_counter),1)
                                    #lcd.display("smutne ludki "+str(sad_people_counter),2)

                                #servo showing happy face
                                servo_upper.move_to_value(neutral_move)
                            
                            if sorted_emotions[0][0] == 'sad' or sorted_emotions[0][0] == 'disgusted' or sorted_emotions[0][0] == 'angry':
                                print("[INFO] sad person detected")
                                                                
                                #increment lcd screen counter
                                if ready_for_new_person:
                                    sad_people_counter += 1
                                    lcd.clear()
                                    lcd.display("spoko goscie "+str(happy_people_counter),1)
                                    lcd.display("smutne ludki "+str(sad_people_counter),2)

                                #servo showing happy face
                                servo_upper.move_to_value(sad_move)
                                ready_for_new_person = False
                        
                        last_output_time = current_time
                        
                

    #zakonczenie dzialania programu/uwolnienie zasobow
    except KeyboardInterrupt:
        print("\n[STOPPING]Stopping emotion detection...")
    finally:
        GPIO.cleanup()
        vs.stop()
        print("[STOPPING]Resources released. Program terminated.")
