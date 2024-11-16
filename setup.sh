pip install -r requirements.txt

token_file="bot_token.txt"
touch $token_file
echo -n $1 > $token_file