#!/bin/bash

RESPONSE=$(curl -s -X POST http://localhost:8024/realms/pymicroservice/protocol/openid-connect/token \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "grant_type=password" \
-d "client_id=myclient" \
-d "client_secret=BtkZhTjSkOVgxRknWvZV6f0fQx26PkIH" \
-d "username=test_user" \
-d "password=test")

 
ACCESS_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')
 
if [ -z "$ACCESS_TOKEN" ]; then
  echo "Unable to get access token"
  echo "Response : $RESPONSE"
  exit 1
fi

echo "Access Token  : $ACCESS_TOKEN"
echo "Result :"
curl -X GET http://localhost:8000/api/v1/protected \
-H "Authorization: Bearer $ACCESS_TOKEN"
