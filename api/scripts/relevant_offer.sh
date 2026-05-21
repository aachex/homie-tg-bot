curl -X POST http://127.0.0.1:8080/api/v1/offer/relevance \
  -H "Content-Type: application/json" \
  -H "X-API-Key:ac!0pOS4%s_-a+210saOIpsl;+asq21_szxc-IOSvp" \
  -d '{
    "offer_id": 4,
    "user_id": 5297482606,
    "user_flags": {
      "smoking": true,
      "sex": "male",
      "children": "none",
      "pets": "dogs",
      "occupants_count": 10,
      "noise_lvl": "quiet",
      "works_from_home": false,
      "alcohol": "never",
      "age_min": 32,
      "age_max": 46
    }
  }'