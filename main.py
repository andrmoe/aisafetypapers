from ai_safety_rss import create_html

def main() -> int:
    try:
        content = create_html()
        #send_email(MIMEText(content, "html"))
    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            pass
            #send_email(MIMEText(traceback.format_exc(), "plain"))
        raise
    return 0


if __name__ == "__main__":
    exit(main())