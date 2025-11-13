from django import template

register = template.Library()

@register.filter
def youtube_id(url):
    """Extrae el ID de video de YouTube de una URL"""
    if not url:
        return None
    
    # Formato: https://www.youtube.com/watch?v=VIDEO_ID
    if 'youtube.com/watch?v=' in url:
        return url.split('v=')[1].split('&')[0]
    
    # Formato: https://youtu.be/VIDEO_ID
    if 'youtu.be/' in url:
        return url.split('youtu.be/')[1].split('?')[0]
    
    return None

