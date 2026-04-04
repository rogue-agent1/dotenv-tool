# dotenv_tool

.env file manager — parse, set, diff, merge, validate, and template.

## Usage

```bash
python3 dotenv_tool.py parse .env --json
python3 dotenv_tool.py parse .env -k DB_URL
python3 dotenv_tool.py set .env NEW_KEY value
python3 dotenv_tool.py unset .env OLD_KEY
python3 dotenv_tool.py diff .env .env.production
python3 dotenv_tool.py merge .env .env.local
python3 dotenv_tool.py validate .env -r APP_KEY DB_URL
python3 dotenv_tool.py template .env
```

## Features

- Parse with comment preservation
- Get/set/unset individual variables
- Diff two .env files (added/removed/changed)
- Merge with overlay priority
- Validate with required key checks
- Generate blank templates
- Zero dependencies
