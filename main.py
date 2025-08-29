from client import Client

if __name__ == "__main__":
    auto_mode = False
    game_client = Client()
    if auto_mode:
        game_client.server_ip = "localhost"
        game_client.state = "join_server"
    game_client.run()