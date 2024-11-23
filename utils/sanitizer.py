import re
import html


def sanitize(value: str) -> str:
    value = re.sub(r'<[^>]+>', '', value)

    value = html.escape(value)

    value = re.sub(r'\s+', ' ', value)
    value = value.strip()

    value = re.sub(r'(<script.*?>.*?</script>)', '', value, flags=re.DOTALL)

    return value
