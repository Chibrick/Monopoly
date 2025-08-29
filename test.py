import subprocess
import time
import sys
import os

def start_server():
    return subprocess.Popen([sys.executable, "run_server.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def start_client():
    return subprocess.Popen([sys.executable, "main.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if __name__ == "__main__":
    print("Запуск сервера...")
    server_process = start_server()
    time.sleep(1)  # подождем немного, чтобы сервер запустился

    print("Запуск клиента 1...")
    client1 = start_client()
    time.sleep(0.5)  # задержка между запусками

    print("Запуск клиента 2...")
    client2 = start_client()

    print("Лобби запущено. Закройте все окна вручную для остановки.")
    
    try:
        # Ожидаем завершения процессов
        client1.wait()
        client2.wait()
    except KeyboardInterrupt:
        print("Прерывание... Остановка всех процессов.")
    finally:
        server_process.terminate()
        client1.terminate()
        client2.terminate()