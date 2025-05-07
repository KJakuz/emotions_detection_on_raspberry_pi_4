import cv2
from threading import Thread
import time
from queue import Queue

class WebcamVideoStream:
    """
    Klasa do obsługi klatek z kamery w innym watku niz detekcja emocji
    Odczytujemy klatki w tle, aby główny wątek nie był blokowany
    """
    def __init__(self, src=0, name="WebcamVideoStream"):
        """
        Inicjalizacja polaczenia z kamera
        src = Indeks kamery lub ścieżka do pliku wideo. Domyślnie 0 (pierwsza kamera po usb)
        name = nazwa watku(jak by bylo pare to nie moze byc to samo)
        """
        self.stream = cv2.VideoCapture(src)
        if not self.stream.isOpened():
            raise ValueError(f"Nie można otworzyć strumienia wideo z źródła: {src}")

        # Odczyt pierwszej klatki
        (self.grabbed, self.frame) = self.stream.read()
        if not self.grabbed:
            print(f"[WARNING] Nie udało się odczytać pierwszej klatki ze źródła: {src}")
            # moze byc ze pierwsze klatki sie nie odczytaja ale to nic

        # Nazwa wątku
        self.name = name
        # Flaga sygnalizująca zatrzymanie wątku
        self.stopped = False

        # Wątek odczytujący klatki
        self.thread = Thread(target=self.update, name=self.name, args=())
        self.thread.daemon = True # Wątek zakończy się wraz z głównym programem zeby nic nie zostawalo w systemie

    def start(self):
        """Rozpoczyna wątek odczytujący klatki"""
        print(f"[INFO] Uruchamianie wątku {self.name}...")
        self.stopped = False
        self.thread.start()
        return self # mozna takie cos zrobic vs = WebcamVideoStream().start()

    def update(self):
        """Biezace odczytywanie klatek"""
        while not self.stopped:
            # Jeśli webcam daje klatki
            if self.stream.isOpened():
                # Odczytaj następną klatkę
                (grabbed, frame) = self.stream.read()

                # Jeśli nie udało się odczytać klatki
                if not grabbed:
                    print(f"[INFO] Koniec strumienia lub błąd odczytu w wątku {self.name}")
                    self.stop()
                    return # Zakończ pętlę update

                # Zapisz odczytaną klatkę
                self.grabbed = grabbed
                self.frame = frame
                
            else:
                # Jeśli strumień nie jest już otwarty, zatrzymaj wątek
                print(f"[INFO] Strumień zamknięty w wątku {self.name}")
                self.stop()
                return

            # moze byc potrzebne jesli cpu usage wywali duze
            # time.sleep(0.001)


    def read(self):
        """Zwraca najnowszą odczytaną klatkę."""
        return self.frame


    def stop(self):
        """Zatrzymuje wątek i zwalnia zasoby kamery."""
        print(f"[INFO] Zatrzymywanie wątku {self.name}...")
        self.stopped = True
        # Poczekaj chwilę, aby wątek update mógł zakończyć pętlę
        if self.thread.is_alive():
            self.thread.join(timeout=1.0) # Poczekaj max 1 sekundę na zakończenie wątku

        # Zwolnij zasoby kamery
        if self.stream.isOpened():
            self.stream.release()
        print(f"[INFO] Wątek {self.name} zatrzymany, strumień zwolniony.")


#test
if __name__ == '__main__':
    print("[TEST] Uruchamiam test kamery...")
    vs=WebcamVideoStream(src=0).start()
    time.sleep(1.0)  # daj kamerze chwilę na wystartowanie

    try:
        while True:
            frame=vs.read()
            if frame is None:
                print("[WARNING] Brak klatki.")
                continue
            cv2.imshow("Podglad z kamery",frame)
            # Zatrzymaj program po naciśnięciu klawisza 'q'
            if cv2.waitKey(1)&0xFF==ord('q'):
                break
    except KeyboardInterrupt:
        print("\n[STOP] Przerwano przez użytkownika.")
    finally:
        vs.stop()
        cv2.destroyAllWindows()
        print("[TEST] Kamera zatrzymana.")
