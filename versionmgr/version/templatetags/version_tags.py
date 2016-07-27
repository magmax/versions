from django.template.defaulttags import register
import markdown

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def md(text):
    if text.startswith(('http://', 'https://')):
        return "<a href={url}>{url}</a>".format(url=text)
    return markdown.markdown(text)
