TRACKING_PIXEL_URL = "https://phish.intigam.online/email-templates/track/{template_id}?uuid={unique_uuid}"
TRACKING_LINK_URL = "https://phish.intigam.online/email-templates/click/{template_id}?uuid={unique_uuid}&url={original_url}"


def inject_tracking_pixel_and_links(body: str, template_id: int, uuid: str) -> str:
    pixel_url = TRACKING_PIXEL_URL.format(template_id=template_id, unique_uuid=uuid)
    print("SALAAAAM")
    print(body)
    pixel_html = f'<img src="{pixel_url}" alt="" width="1px" height="1px">'
    print(pixel_html)

    def replace_link(match):
        original_url = match.group(2)
        tracked_url = TRACKING_LINK_URL.format(template_id=template_id, unique_uuid=uuid, original_url=original_url)
        return f'<a href="{tracked_url}"'

    import re
    print(body, "BODY")
    body = re.sub(r'<a\s+(.*?)href="(.*?)"', replace_link, body)

    return pixel_html
