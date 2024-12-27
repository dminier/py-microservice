#!/bin/bash

# Étape 1 : Récupérer l'access token
RESPONSE=$(curl -s -X POST http://localhost:8024/realms/pymicroservice/protocol/openid-connect/token \
-H "Content-Type: application/x-www-form-urlencoded" \
-d "grant_type=password" \
-d "client_id=myclient" \
-d "client_secret=BtkZhTjSkOVgxRknWvZV6f0fQx26PkIH" \
-d "username=test_user" \
-d "password=test")

# Extraire l'access token de la réponse JSON
ACCESS_TOKEN=$(echo "$RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

# Vérification si l'ACCESS_TOKEN a été récupéré
if [ -z "$ACCESS_TOKEN" ]; then
  echo "Erreur : Impossible de récupérer l'access token."
  echo "Réponse : $RESPONSE"
  exit 1
fi

echo "Access Token récupéré avec succès : $ACCESS_TOKEN"
echo "Résultat :"
# Étape 2 : Faire une requête GET protégée avec le token
curl -X GET http://localhost:8000/api/v1/protected \
-H "Authorization: Bearer $ACCESS_TOKEN"
