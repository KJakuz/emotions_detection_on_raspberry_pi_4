from fer import FER
from time import sleep
import time
import webcam as wc
import servo as srv

if __name__ == "__main__":
    
    # create and run videostream from camera
    # src = 0 for default first connected camera (by usb)
    
    vs = wc.WebcamVideoStream(src=0).start()

    #servo init
    servo_start = -1 #swap this to make servo move diffrent values
    #by default servo is on pin 18
    servo = srv.ServoController(pin = 18, starting_value= servo_start)
    last_move = servo_start 
    move_first = -1 * servo_start
    move_second = servo_start

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
    process_every_n_frames = 5  # Process every 1th frame
    output_interval = 0.3 # Output results every x seconds
    last_output_time = time.time()

    #init for twice item gifting prevention system
    person_present = False
    ready_for_new_person = True
    last_time_with_person = time.time()
    no_face_timeout = 2 # seconds

    #main loop of program
    try:
        while True:

            #TODO!
            #diode X expressing that emotion recognition started
            #GPIO.setmode(GPIO.BCM)
            #GPIO.setup(17,GPIO.OUT)
            #GPIO.output(17,GPIO.HIGH)
            #GPIO.output(17,GPIO.LOW)
            #GPIO.cleanup()

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
                        print("No faces detected")
                        person_present = False
                        #after no_face_timout seconds allow item hand out
                        if current_time - last_time_with_person > no_face_timeout:
                            ready_for_new_person = True
                    #face detected
                    else:
                        person_present = True
                        last_time_with_person = current_time
                        
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
                                if ready_for_new_person:
                                    print("[INFO] Happy person detected")

                                    #TODO!
                                    #diode Y expressing that the item is being given
                                    #GPIO.setmode(GPIO.BCM)
                                    #GPIO.setup(17,GPIO.OUT)
                                    #GPIO.output(17,GPIO.HIGH)
                                    #GPIO.output(17,GPIO.LOW)
                                    #GPIO.cleanup()
                                    
                                    servo.move_to_value(move_first)
                                    last_move = move_first
                                    
                                    
                                    #TODO!
                                    #increment number on display
                                    
                                    time.sleep(2) #time to get item through hole

                                    servo.move_to_value(move_second)
                                    last_move = move_second

                                    #TODO!
                                    #end lightning up diode Y
                                    

                                    #wait a x seconds after happy person detected to prevent giving item twice to the same person
                                    ready_for_new_person = False
                                    #sleep for x seconds to give a moment to change person
                                    #time.sleep(5)





                        last_output_time = current_time
                        
                
    #zakonczenie dzialania programu/uwolnienie zasobow
    except KeyboardInterrupt:
        print("\n[STOPPING]Stopping emotion detection...")
    finally:
        vs.stop()
        print("[STOPPING]Resources released. Program terminated.")