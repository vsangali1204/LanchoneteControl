from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, 0)

@register.filter
def get_default(dictionary, key):
    """Retorna valor do dict ou 0 se não existir (para abertura_qtd no fechamento)."""
    return dictionary.get(key, 0)

@register.filter
def split(value, delimiter):
    return value.split(delimiter)
