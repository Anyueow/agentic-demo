"""
Company URL Finder Agent (smolagent + Mistral, no scraping)

This agent finds and fills in the COMPANY_URL column for leads based on COMPANY name,
using (1) direct TLD guesses and (2) a smolagent‐based LLM call to Mistral.

Requirements:
  • smolagent (https://github.com/your‐org/smolagent) installed
  • requests
  • beautiful logging for debugging
  • GoogleSheetsService configured as before
"""

import time
import logging
import requests
from typing import Optional, Dict
from urllib.parse import urlparse

from smolagents import ToolCallingAgent, InferenceClientModel, WebSearchTool
# (Adjust imports if your smolagent API differs.)

from ..services.sheets_service import GoogleSheetsService
from ..core.config import Config

# ─── Logging Setup ───────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(ch)


class CompanyURLFinderAgent:
    def __init__(self, config: Config):
        """
        Initializes:
          • sheets_service: for reading/updating the Google Sheet
          • cache: simple in‐memory cache {company_name_lower: url_or_empty}
          • llm: a smolagent instance configured to use Mistral via Together API
        """
        self.config = config
        self.sheets_service = GoogleSheetsService(config)
        self.cache: Dict[str, str] = {}

        # Set up Together/Mistral via smolagents InferenceClientModel
        together_key = getattr(config, "together_api_key", None)
        if not together_key:
            raise ValueError("A Together API key (config.together_api_key) is required.")
        self.llm_model = InferenceClientModel(
            model_id="mistralai/Mistral-7B-Instruct-v0.2",
            provider="together",
            token=together_key
        )
        # Use WebSearchTool for company URL lookup
        self.web_search_tool = WebSearchTool()
        self.agent = ToolCallingAgent(
            tools=[self.web_search_tool],
            model=self.llm_model
        )
        self.MIN_DELAY = 2.0

    def _validate_url(self, url: str) -> bool:
        """
        Quickly confirm that `url` actually resolves with a HEAD request (status 200–399).
        Returns True if valid, False otherwise.
        """
        try:
            resp = requests.head(url, allow_redirects=True, timeout=5,
                                 headers={"User-Agent": "Mozilla/5.0"})
            return 200 <= resp.status_code < 400
        except Exception as e:
            logger.debug(f"URL validation failed for {url}: {e}")
            return False

    def _direct_domain_guess(self, company_name: str) -> Optional[str]:
        """
        Try common TLDs: .com, .co, .io, .net on a sanitized company name.
        Returns the first valid URL (HEAD passes) or None if none succeeded.
        """
        sanitized = (
            company_name.lower()
            .strip()
            .replace("&", "and")
            .replace(" ", "")
            .replace(",", "")
            .replace(".", "")
        )
        suffixes = [".com", ".co", ".io", ".net"]
        for suffix in suffixes:
            candidate = f"https://{sanitized}{suffix}"
            if self._validate_url(candidate):
                logger.info(f"Direct-guess found: {candidate}")
                return candidate
        return None

    def _mistral_lookup(self, company_name: str) -> Optional[str]:
        """
        Use smolagent + Mistral to ask, "What is the official website URL of <company_name>? Return only the URL."
        Parses and validates the result. Returns the URL if valid, else None.
        """
        prompt = (
            "You are a helpful assistant. "
            f"Given the company name '{company_name}', provide the official website URL (homepage) "
            "and output *only* the URL (e.g., https://www.example.com). Do not add any extra text."
        )
        try:
            request = LLMRequest(
                prompt=prompt,
                max_tokens=32,
                temperature=0.0,   # deterministic
            )
            # Synchronous call to the LLM
            response: LLMResponse = self.llm_agent.generate(request)
            candidate = response.text.strip().split("\n")[0]  # take first line

            # Sometimes the model might prepend "http://" or miss "https://"
            if candidate.startswith("http://") or candidate.startswith("https://"):
                # If there's trailing punctuation, strip it
                candidate = candidate.rstrip(".,;")
            else:
                # If they returned "www.example.com" without scheme, add https://
                candidate = "https://" + candidate.lstrip("/")
            
            if self._validate_url(candidate):
                logger.info(f"Mistral lookup succeeded: {candidate}")
                return candidate
            else:
                logger.warn(f"Mistral returned invalid/non-resolving URL: {candidate}")
        except Exception as e:
            logger.error(f"Mistral lookup error for '{company_name}': {e}")
        return None

    def search_company_url(self, company_name: str) -> str:
        """
        Use the WebSearchTool to find the company website URL.
        """
        try:
            query = f"{company_name} official website"
            result = self.web_search_tool(query)
            # Try to extract the first URL from the result (if available)
            import re
            urls = re.findall(r'https?://\S+', str(result))
            if urls:
                return urls[0]
        except Exception as e:
            logger.error(f"WebSearchTool error for '{company_name}': {e}")
        return ""

    def fill_missing_company_urls(self):
        """
        Reads the Google Sheet, finds rows where COMPANY_URL is blank but COMPANY is non-empty,
        calls search_company_url, and writes back either the URL or "URL not found".
        """
        worksheet = self.sheets_service.worksheet
        headers = worksheet.row_values(1)
        if 'COMPANY' not in headers or 'COMPANY_URL' not in headers:
            logger.error("COMPANY or COMPANY_URL column missing in sheet.")
            return

        company_col = headers.index('COMPANY') + 1
        url_col = headers.index('COMPANY_URL') + 1
        all_rows = worksheet.get_all_values()

        for row_idx, row in enumerate(all_rows[1:], start=2):
            company = row[company_col - 1].strip() if len(row) >= company_col else ""
            current_url = row[url_col - 1].strip() if len(row) >= url_col else ""

            if not company:
                continue  # skip blank company cells
            if current_url:
                continue  # already filled

            logger.info(f"Looking up URL for '{company}' (row {row_idx})")
            found_url = self.search_company_url(company)

            if found_url:
                try:
                    worksheet.update_cell(row_idx, url_col, found_url)
                    logger.info(f"Updated '{company}' → {found_url}")
                except Exception as e:
                    logger.error(f"Error updating sheet at row {row_idx} for '{company}': {e}")
            else:
                try:
                    worksheet.update_cell(row_idx, url_col, "URL not found")
                    logger.warn(f"Marked 'URL not found' for '{company}' (row {row_idx})")
                except Exception as e:
                    logger.error(f"Error marking 'URL not found' at row {row_idx}: {e}")

            # Rate limit between each row
            time.sleep(self.MIN_DELAY)
