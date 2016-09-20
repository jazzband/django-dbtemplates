from django.template import (Template, TemplateDoesNotExist,
                             TemplateSyntaxError)
from importlib import import_module


def get_loaders():
    from django.template.loader import _engine_list
    loaders = []
    for engine in _engine_list():
        loaders.extend(engine.engine.template_loaders)
    return loaders


def get_template_source(name):
    source = None
    for loader in get_loaders():
        if loader.__module__.startswith('dbtemplates.'):
            # Don't give a damn about dbtemplates' own loader.
            continue
        module = import_module(loader.__module__)
        load_template_source = getattr(
            module, 'load_template_source', None)
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
    return None


def check_template_syntax(template):
    try:
        Template(template.content)
    except TemplateSyntaxError as e:
        return (False, e)
    return (True, None)
