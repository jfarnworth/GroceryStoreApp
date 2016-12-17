from django import template
from django.utils.safestring import mark_safe
from smiths_app.models import Customers, Reservations, Products
# import markdown2

register = template.Library()


@register.filter('get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter('closing_slash')
def get_slash(id=None):
    if id:
        return '{}/'.format(id)
    else:
        return ''

# @register.simple_tag
# def newest_course():
#     ''' Gets the most recent course that was added to the library. '''
#     return Course.objects.latest('created_at')
#
#
# @register.inclusion_tag('courses/course_nav.html')
# def nav_courses_list():
#     ''' Returns dictionary of courses to display as navigation pane. '''
#     courses = Course.objects.all()
#     return {'courses': courses}
#
#
# @register.filter('time_estimate')
# def time_estimate(wordcount):
#     ''' Estimates the number of minutes it will take to complete a step based on wordcount. '''
#     minutes = round(wordcount/20)
#     return minutes
#
#
# @register.filter('markdown_to_html')
# def markdown_to_html(markdown_text):
#     ''' Converts markdown text to html. '''
#     html_body = markdown2.markdown(markdown_text)
#     return mark_safe(html_body)