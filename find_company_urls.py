from src.core.config import Config
from src.agents.company_url_finder import CompanyURLFinderAgent

def main():
    config = Config()
    agent = CompanyURLFinderAgent(config)
    agent.fill_missing_company_urls()

if __name__ == "__main__":
    main() 