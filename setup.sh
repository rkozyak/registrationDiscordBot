requests_file="saved_requests.json"
touch $requests_file
echo "[]" > $requests_file

token_file="bot_token.txt"
touch $token_file
echo -n $1 > $token_file