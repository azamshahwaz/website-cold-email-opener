"""Application errors. Every error carries a message that is safe to show to users."""
from __future__ import annotations


class AppError(Exception):
    user_message = "Something went wrong. Please try again."

    def __init__(self, user_message: str | None = None):
        self.user_message = user_message or self.user_message
        super().__init__(self.user_message)


# --- URL / website errors -------------------------------------------------
class InvalidURLError(AppError):
    user_message = "Please enter a valid website URL, for example https://company.com."


class UnsafeURLError(AppError):
    user_message = "This URL points to a private or internal address and cannot be fetched."


class WebsiteFetchError(AppError):
    user_message = "The website could not be fetched."


class WebsiteTimeoutError(WebsiteFetchError):
    user_message = "The website took too long to respond. Try again or use a different page."


class WebsiteSSLError(WebsiteFetchError):
    user_message = "The website has an invalid or untrusted SSL certificate."


class WebsiteBlockedError(WebsiteFetchError):
    user_message = "The website blocked our request (it may block automated access)."


class WebsiteUnavailableError(WebsiteFetchError):
    user_message = "The website is unavailable or returned an error."


class EmptyContentError(AppError):
    user_message = "No meaningful text could be extracted from this website."


class JavaScriptRenderedError(EmptyContentError):
    user_message = (
        "This website renders its content with JavaScript, so no readable text was "
        "found in the HTML. Try a more static page (for example /about)."
    )


# --- AI errors ------------------------------------------------------------
class AIError(AppError):
    user_message = "The AI service failed to generate an opener."


class MissingAPIKeyError(AIError):
    user_message = "No Gemini API key is configured. Add GEMINI_API_KEY to your .env file, or use Demo mode."


class InvalidAPIKeyError(AIError):
    user_message = "The Gemini API key was rejected. Check GEMINI_API_KEY."


class ModelNotFoundError(AIError):
    user_message = "The configured Gemini model was not found. Update GEMINI_MODEL in your .env file."


class RateLimitError(AIError):
    user_message = "Gemini rate limit reached. Wait a minute and try again."


class QuotaExceededError(AIError):
    user_message = "Gemini quota exceeded. Wait for the quota to reset or check your plan."


class AIUnavailableError(AIError):
    user_message = "The Gemini API is temporarily unavailable. Please try again shortly."


class InvalidOutputError(AIError):
    user_message = "The AI did not return a valid three-line opener, even after a retry. Please try again."
