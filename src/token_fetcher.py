def get_token() -> str:
    with open("bot_token.txt", 'r') as file:
        token = file.read()
    return token