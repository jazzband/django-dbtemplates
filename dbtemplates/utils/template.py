from django import VERSION
from django.template import (Template, TemplateDoesNotExist,
                             TemplateSyntaxError)
from django.utils.importlib import import_module


def get_loaders():
    if VERSION[:2] < (1, 8):
        from django.template.loader import template_source_loaders
        if template_source_loaders is None:
            try:
                from django.template.loader import find_template as finder
            except ImportError:
                from django.template.loader import find_template_source as finder  # noqa
            try:
                source, name = finder('test')
            except TemplateDoesNotExist:
                pass
            from django.template.loader import template_source_loaders
        return template_source_loaders or []
    else:
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
    except TemplateSyntaxError as e:
        return (False, e)
    return (True, None)
