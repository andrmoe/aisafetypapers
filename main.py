from email.mime.text import MIMEText
import json
from datetime import datetime, UTC
import traceback
from pathlib import Path

from ai_safety_rss import create_html, filter_for_alignment
from ai_safety_email import send_email
from latest_papers import fetch_papers


def main() -> int:
    try:
        print()
        print(f"Time: {datetime.now(tz=UTC)}")
        
        dir = Path(__file__).parent
        with open(dir / ".env", "r") as f:
            conf = json.loads(f.read())
        receiver_emails = conf["receiver_emails"]
        maintainer_email = conf["maintainer_email"]
        papers = list(filter_for_alignment(fetch_papers()))
        email_content = create_html(papers)
        if not email_content:
            return 0
        for receiver_email in receiver_emails:
            send_email(receiver_email, 
                        subject="New Papers from AI Safety Researchers", 
                        content=MIMEText(email_content, 'html'))
    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            send_email(maintainer_email, 
                       subject="Error in 'ai_safety_papers'", 
                       content=MIMEText(traceback.format_exc(), "plain"))
        raise
    return 0


if __name__ == "__main__":
    exit(main())