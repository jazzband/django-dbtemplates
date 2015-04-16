from django import VERSION
from django.template import (Template, TemplateDoesNotExist,
                             TemplateSyntaxError)
from django.template.loader import find_template_loader
from django.utils.importlib import import_module
from dbtemplates.conf import settings

DBTEMPLATES_TEMPLATE_LOADERS = settings.DBTEMPLATES_TEMPLATE_LOADERS
loader_cache = None

def get_loaders():
    global loader_cache
    if loader_cache is not None:
        return loader_cache
    loader_cache = []
    for loader_name in DBTEMPLATES_TEMPLATE_LOADERS:
        loader = find_template_loader(loader_name)
        if loader is not None:
            loader_cache.append(loader)
    return loader_cache

def get_template_source(name):
    source = None
    for loader in get_loaders():
        if loader.__module__.startswith('dbtemplates.'):
            # Don't give a damn about dbtemplates' own loader or loaders
            # that use the dbtemplates loader
            continue
        module = import_module(loader.__module__)
        load_template_source = getattr(module, 'load_template_source', None)
        if load_template_source is None:
            load_template_source = loader.load_template_source
        try:
            source, origin = load_template_source(name)
            if source:
                return source
        except NotImplementedError:
            pass
        except TemplateDoesNotExist:
            pass
    if source is None and VERSION[:2] < (1, 2):
        # Django supported template source extraction still :/
        try:
            from django.template.loader import find_template_source
            template, origin = find_template_source(name, None)
            if not hasattr(template, 'render'):
                return template
        except (ImportError, TemplateDoesNotExist):
            pass
    return None


def check_template_syntax(template):
    try:
        Template(template.content)
    except TemplateSyntaxError, e:
        return (False, e)
    return (True, None)
