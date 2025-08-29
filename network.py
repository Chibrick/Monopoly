import select
import socket
import pickle
import struct

class Network:
    def __init__(self, server_ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.setblocking(False)
        self.server = server_ip
        self.port = 5555
        self.addr = (self.server, self.port)
        # Установка таймаута для операций сокета
        self.client.settimeout(5.0)  # 5 секунд таймаут
        self.connect()
    
    def connect(self):
        """Подключение к серверу"""
        try:
            self.client.connect(self.addr)
            return True
        except socket.error as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def send(self, data):
        """Отправка данных на сервер"""
        try:
            # Сериализация данных и отправка их размера перед основными данными
            serialized_data = pickle.dumps(data)
            self.client.send(struct.pack('!I', len(serialized_data)))
            self.client.send(serialized_data)
        except socket.error as e:
            print(f"Ошибка отправки данных: {e}")
    
    def receive(self):
        try:
            ready = select.select([self.client], [], [], 0.1)  # Таймаут 100мс
            if ready[0]:
                size_data = self.client.recv(4)
                if not size_data: return None
                data_size = struct.unpack('!I', size_data)[0]
                raw_data = self.recv_all(self.client, data_size)
                return pickle.loads(raw_data)
            return None
        except BlockingIOError:
            return None
    
    def recv_all(self, sock, length):
        data = b''
        while len(data) < length:
            more = sock.recv(length - len(data))
            if not more:
                raise EOFError("Socket closed before receiving all data")
            data += more
        return data

    def close(self):
        """Закрытие соединения"""
        self.client.close()