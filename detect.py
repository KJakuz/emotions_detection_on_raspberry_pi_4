from fer import FER
import time
import webcam as wc

if __name__ == "__main__":
    
    # Utwórz i uruchom strumien wideo z kamreki
    # Użyj src=0 dla domyślnej kamery USB/wbudowanej
    
    vs = wc.WebcamVideoStream(src=0).start()

    # Czasami pierwszych kilka klatek może być nie poprawnych to je omijamy
    print("[INFO] Kamera uruchomiona, czekam 1 sekundę...")
    time.sleep(1.0)

    # Sprawdź, czy strumień został poprawnie zainicjowany
    if vs.stopped or vs.frame is None:
         print("[ERROR] Nie udało się uruchomić strumienia wideo..")
         exit()

    print("[INFO] Rozpoczynam przetwarzanie klatek...")
    fps_start_time = time.time()
    fps_counter = 0
    
    #TEMP
    detector = FER(mtcnn=True)
    
    #TEMP
    process_every_n_frames = 7  # Process every 1th frame
    frame_counter = 0
    
    #TEMP
    output_interval = 0.3 # Output results every x seconds
    last_output_time = time.time()

    try:
        while True:
            # Pobierz najnowszą klatkę z wątku kamerkowego
            frame = vs.read()

            # Sprawdź, czy klatka istnieje (na wszelki wypadek)
            if frame is None:
                print("[WARNING] Otrzymano pustą klatkę.")
                # Możesz zdecydować, czy kontynuować, czy przerwać
                time.sleep(0.1) # Poczekaj chwilę
                continue
                # break

            # ---------------------------------------------------------------
            # Tutaj umieść kod do przetwarzania klatki (np. detekcja twarzy,
            # ekstrakcja cech, predykcja emocji za pomocą Twojego modelu)
            # Przykład:
            # 1. Konwersja do skali szarości (często wymagana)
            #    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # 2. Detekcja twarzy
            #    faces = face_cascade.detectMultiScale(gray, ...)
            # 3. Dla każdej wykrytej twarzy:
            #    - Wycięcie ROI (Region of Interest)
            #    - Przetworzenie ROI (normalizacja, zmiana rozmiaru)
            #    - Predykcja emocji za pomocą modelu: emotion = model.predict(roi_processed)
            #    - Narysowanie ramki i etykiety z emocją na oryginalnej klatce 'frame'
            # ---------------------------------------------------------------
            
            #TEMP MODEL Z CZATA DO TESTOW
            frame_counter += 1
            
            # Only process every nth frame
            if frame_counter % process_every_n_frames == 0:
                # Use the FER library to detect emotions
                emotions = detector.detect_emotions(frame)
                
                current_time = time.time()
                # Print results at specified interval
                if current_time - last_output_time >= output_interval:
                    print("\n" + "="*50)
                    print(f"Emotion Detection Results ({time.strftime('%H:%M:%S')})")
                    print("="*50)
                    
                    if not emotions:
                        print("No faces detected")
                    
                    for i, emotion in enumerate(emotions):
                        dominant_emotion = emotion["emotions"]
                        # Sort emotions by confidence (highest first)
                        sorted_emotions = sorted(dominant_emotion.items(), key=lambda x: x[1], reverse=True)
                        
                        print(f"\nFace #{i+1}:")
                        # Print top 3 emotions with confidence scores
                        for emotion_name, score in sorted_emotions[:3]:
                            print(f"  {emotion_name}: {score:.2f}")
                    
                    last_output_time = current_time
                    
                    
                    
            #test w GUI        
            # Wyświetl przetworzoną klatkę (lub oryginalną, jeśli nie ma przetwarzania)
            #cv2.imshow("Webcam Stream (Optimized)", frame)

            # Sprawdź, czy naciśnięto klawisz 'q', aby zakończyć
            #key = cv2.waitKey(1) & 0xFF
            #if key == ord('q'):
            #    break
            
    #zakonczenie dzialania programu/uwolnienie zasobow
    except KeyboardInterrupt:
        print("\n[STOPPING]Stopping emotion detection...")
    finally:
        vs.stop()
        print("[STOPPING]Resources released. Program terminated.")