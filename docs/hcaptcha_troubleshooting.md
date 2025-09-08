# hCaptcha Troubleshooting Guide

## Problem
The application was experiencing Internal Server Errors when trying to verify hCaptcha tokens due to network connectivity issues. The error was:

```
socket.gaierror: [Errno -3] Temporary failure in name resolution
```

This prevented users from registering or logging in when hCaptcha verification was required.

## Solution

### 1. Enhanced Error Handling
- Added comprehensive error handling for network-related issues
- Implemented timeout configuration (10 seconds default)
- Added proper logging for debugging

### 2. Centralized hCaptcha Utility
Created `utils/hcaptcha.py` with:
- `verify_hcaptcha()` function with robust error handling
- `is_hcaptcha_enabled()` function to check configuration
- Proper logging for all error scenarios

### 3. Configuration Options
Added `HCAPTCHA_FAIL_OPEN` setting to control behavior during network failures:

- `False` (default): Fail closed - block registration/login if hCaptcha fails (more secure)
- `True`: Fail open - allow registration/login if hCaptcha fails due to network issues (less secure)

### 4. Environment Configuration
Add to your `.env` file:
```bash
# Comportamento do hCaptcha em caso de falha de rede
# True = permitir registro/login mesmo se hCaptcha falhar (menos seguro)
# False = bloquear registro/login se hCaptcha falhar (mais seguro)
CONFIG_HCAPTCHA_FAIL_OPEN=False
```

## Usage

### For Registration
The registration view automatically uses the enhanced hCaptcha verification.

### For Login
The login form automatically uses the enhanced hCaptcha verification when required.

### Manual Verification
```python
from utils.hcaptcha import verify_hcaptcha

# Verify a token
is_valid = verify_hcaptcha(token)

# Check if hCaptcha is configured
from utils.hcaptcha import is_hcaptcha_enabled
enabled = is_hcaptcha_enabled()
```

## Error Types Handled

1. **ConnectionError**: Network connectivity issues
2. **Timeout**: Request timeout (configurable)
3. **HTTPError**: Bad HTTP status codes
4. **RequestException**: General request errors
5. **ValueError**: JSON parsing errors
6. **Exception**: Any other unexpected errors

## Logging

All hCaptcha verification attempts are logged with appropriate levels:
- `DEBUG`: Successful verifications and attempts
- `WARNING`: Failed verifications
- `ERROR`: Network and configuration errors

## Security Considerations

- **Fail Closed (Default)**: More secure, prevents registration/login during hCaptcha failures
- **Fail Open**: Less secure, allows registration/login during network issues
- Choose based on your security requirements and network reliability

## Network Requirements

Ensure your server can reach:
- `https://hcaptcha.com/siteverify`
- Port 443 (HTTPS)
- DNS resolution for `hcaptcha.com`

## Troubleshooting

1. **Check DNS Resolution**:
   ```bash
   nslookup hcaptcha.com
   ```

2. **Check Network Connectivity**:
   ```bash
   curl -I https://hcaptcha.com/siteverify
   ```

3. **Check Logs**:
   Look for hCaptcha-related error messages in your application logs.

4. **Temporary Solution**:
   Set `CONFIG_HCAPTCHA_FAIL_OPEN=True` to allow registration/login during network issues.
