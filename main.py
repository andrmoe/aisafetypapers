

def main() -> int:
    try:
        url = ""
        #content = create_html(url)
        #send_email(MIMEText(content, "html"))
    except BaseException as e:
        if not isinstance(e, KeyboardInterrupt):
            pass
            #send_email(MIMEText(traceback.format_exc(), "plain"))
        raise
    return 0


if __name__ == "__main__":
    exit(main())