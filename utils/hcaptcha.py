import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def verify_hcaptcha(token, timeout=10):
    """
    Verify hCaptcha token with proper error handling and timeout.
    
    Args:
        token (str): The hCaptcha response token
        timeout (int): Request timeout in seconds (default: 10)
    
    Returns:
        bool: True if verification successful, False otherwise
    """
    if not token:
        logger.warning("hCaptcha verification failed: No token provided")
        return False
    
    secret = getattr(settings, 'HCAPTCHA_SECRET_KEY', None)
    if not secret:
        logger.error("hCaptcha verification failed: HCAPTCHA_SECRET_KEY not configured")
        return False
    
    logger.debug(f"Attempting hCaptcha verification with timeout={timeout}s")
    
    data = {
        'response': token,
        'secret': secret,
    }
    
    try:
        r = requests.post(
            'https://hcaptcha.com/siteverify', 
            data=data, 
            timeout=timeout
        )
        r.raise_for_status()  # Raise an exception for bad status codes
        response_data = r.json()
        success = response_data.get('success', False)
        logger.debug(f"hCaptcha verification result: {success}")
        return success
        
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error during hCaptcha verification: {str(e)}")
        # Check if we should fail open or closed
        fail_open = getattr(settings, 'HCAPTCHA_FAIL_OPEN', False)
        if fail_open:
            logger.warning("hCaptcha connection failed, but HCAPTCHA_FAIL_OPEN=True - allowing verification to pass")
            return True
        return False
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error during hCaptcha verification: {str(e)}")
        # Check if we should fail open or closed
        fail_open = getattr(settings, 'HCAPTCHA_FAIL_OPEN', False)
        if fail_open:
            logger.warning("hCaptcha timeout, but HCAPTCHA_FAIL_OPEN=True - allowing verification to pass")
            return True
        return False
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error during hCaptcha verification: {str(e)}")
        return False
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error during hCaptcha verification: {str(e)}")
        # Check if we should fail open or closed
        fail_open = getattr(settings, 'HCAPTCHA_FAIL_OPEN', False)
        if fail_open:
            logger.warning("hCaptcha request failed, but HCAPTCHA_FAIL_OPEN=True - allowing verification to pass")
            return True
        return False
    except ValueError as e:
        logger.error(f"JSON parsing error during hCaptcha verification: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during hCaptcha verification: {str(e)}")
        return False


def is_hcaptcha_enabled():
    """
    Check if hCaptcha is properly configured.
    
    Returns:
        bool: True if hCaptcha is configured, False otherwise
    """
    site_key = getattr(settings, 'HCAPTCHA_SITE_KEY', None)
    secret_key = getattr(settings, 'HCAPTCHA_SECRET_KEY', None)
    return bool(site_key and secret_key)
