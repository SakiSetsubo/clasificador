import cv2
import os

def capture_photos(output_folder, num_photos=30):
    # Crear la carpeta de salida si no existe
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Inicializar la captura de video (cámara por defecto)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    print("Presiona 'q' para salir en cualquier momento.")
    
    photo_count = 0
    while photo_count < num_photos:
        # Captura frame por frame
        ret, frame = cap.read()
        if not ret:
            print("No se pudo capturar la imagen.")
            break

        # Mostrar el frame
        cv2.imshow('Captura de Foto', frame)

        # Esperar por una tecla
        key = cv2.waitKey(1)
        if key == ord('q'):
            # Salir si la tecla 'q' es presionada
            break

        # Guardar la foto en la carpeta especificada
        photo_filename = os.path.join(output_folder, f'photo_{photo_count + 1}.jpg')
        cv2.imwrite(photo_filename, frame)
        print(f'Foto {photo_count + 1} guardada como {photo_filename}')

        photo_count += 1

    # Liberar la captura y cerrar las ventanas
    cap.release()
    cv2.destroyAllWindows()
    print("Captura completada.")

if __name__ == "__main__":
    output_folder = "fotos_capturadas"  # Carpeta donde se guardarán las fotos
    capture_photos(output_folder)
