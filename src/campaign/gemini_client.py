import os
import time

from dotenv import load_dotenv
from google import genai


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv(override=True)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)


# ============================================================
# CLIENT
# ============================================================

_client = None

# Once quota is exhausted, don't keep sending requests.
_QUOTA_EXHAUSTED = False


def get_gemini_client():
    """
    Create and return a Gemini client.
    """

    global _client

    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found. "
            "Please add it to the .env file."
        )

    if _client is None:
        _client = genai.Client(
            api_key=GEMINI_API_KEY
        )

    return _client


# ============================================================
# GENERATE TEXT
# ============================================================

def generate_text(prompt, max_retries=2):
    """
    Generate text using Gemini.

    Handles temporary Gemini failures and quota exhaustion.
    """

    global _QUOTA_EXHAUSTED

    # --------------------------------------------------------
    # STOP CALLING GEMINI AFTER QUOTA EXHAUSTION
    # --------------------------------------------------------

    if _QUOTA_EXHAUSTED:
        raise RuntimeError(
            "Gemini API quota exhausted. "
            "Using fallback campaign generation."
        )

    client = get_gemini_client()

    last_error = None

    # --------------------------------------------------------
    # RETRY TEMPORARY FAILURES
    # --------------------------------------------------------

    for attempt in range(max_retries + 1):

        try:

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            if not response or not response.text:

                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as error:

            last_error = error

            error_text = str(error)

            # ------------------------------------------------
            # QUOTA EXHAUSTED
            # ------------------------------------------------

            if (
                "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
                or "quota" in error_text.lower()
            ):

                _QUOTA_EXHAUSTED = True

                print(
                    "\nWARNING - Gemini quota exhausted."
                )

                print(
                    "Switching to fallback campaign "
                    "generation for remaining customers.\n"
                )

                raise RuntimeError(
                    "Gemini API quota exhausted."
                ) from error

            # ------------------------------------------------
            # TEMPORARY SERVICE ERROR
            # ------------------------------------------------

            if (
                "503" in error_text
                or "UNAVAILABLE" in error_text
            ):

                if attempt < max_retries:

                    wait_time = 2 ** attempt

                    print(
                        f"Gemini temporarily unavailable. "
                        f"Retrying in {wait_time}s..."
                    )

                    time.sleep(wait_time)

                    continue

                raise RuntimeError(
                    "Gemini service temporarily unavailable."
                ) from error

            # ------------------------------------------------
            # OTHER ERROR
            # ------------------------------------------------

            raise

    raise RuntimeError(
        f"Gemini generation failed: {last_error}"
    )