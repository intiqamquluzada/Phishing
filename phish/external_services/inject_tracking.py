TRACKING_PIXEL_URL = "https://localhost:8000/track/{template_id}?uuid={unique_uuid}"


def inject_tracking_pixel(body: str, template_id: int, uuid: str) -> str:
    pixel_url = TRACKING_PIXEL_URL.format(template_id=template_id, unique_uuid=uuid)
    pixel_html = f'<img src="{pixel_url}" alt="" style="display:none;width:1px;height:1px;">'
    return body + pixel_html
