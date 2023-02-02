token="55cde...403157"
endpoint="https://elab.example.org/api/v1"
# get experiment with id 42
json=$(curl -s -H "Authorization: $token" ${endpoint}/experiments/42)
echo $json
