# API Documentation

## Authentication
- Most endpoints require authentication via Django session or token.
- Example header:
  ```http
  Authorization: Token <your-token>
  ```

## Main Endpoints

### Example: Player Ranking
- `GET /api/lineage/top-level/?limit=10`
- Response:
  ```json
  [
    {"char_name": "Hero", "level": 80, "clan_name": "Lendas", ...},
    ...
  ]
  ```

### Example: Castle Status
- `GET /api/lineage/siege/`
- Response:
  ```json
  [
    {"castle": "Aden", "owner": "ClanX", "siege_date": "2024-06-01"},
    ...
  ]
  ```

## Error Formats
- Error responses follow the pattern:
  ```json
  {"error": "Error message"}
  ```

## Notes
- See the code in `apps/lineage/server/views/` for more endpoint examples. 