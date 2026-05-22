curl -X POST http://127.0.0.1:8080/api/v1/offer/rand \
  -H "Content-Type: application/json" \
  -H "X-API-Key:ac!0pOS4%s_-a+210saOIpsl;+asq21_szxc-IOSvp" \
  -d '{
    "user_id": 2,
    "min_rel":70,
    "city": "Москва",
    "user_flags": {
      "pets":"none",
      "smoking":true
    }
  }'