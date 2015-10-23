import django
from django.template import (Template, TemplateDoesNotExist,
                             TemplateSyntaxError)
from django.utils.importlib import import_module


def get_loaders():
    if django.VERSION < (1, 8):
        from django.template.loader import template_source_loaders
        if template_source_loaders is None:
            try:
                from django.template.loader import (
                    find_template as finder_func)
            except ImportError:
                from django.template.loader import (
                    find_template_source as finder_func)  # noqa
            try:
                # Force django to calculate template_source_loaders from
                # TEMPLATE_LOADERS settings, by asking to find a dummy template
                source, name = finder_func('test')
            except django.template.TemplateDoesNotExist:
                pass
            # Reload template_source_loaders now that it has been calculated ;
            # it should contain the list of valid, instanciated template loaders
            # to use.
            from django.template.loader import template_source_loaders
    else:
        from django.template import engines
        template_source_loaders = []
        for e in engines.all():
            template_source_loaders.extend(e.engine.get_template_loaders(e.engine.loaders))
    loaders = []
    # If template loader is CachedTemplateLoader, return the loaders
    # that it wraps around. So if we have
    # TEMPLATE_LOADERS = (
    #    ('django.template.loaders.cached.Loader', (
    #        'django.template.loaders.filesystem.Loader',
    #        'django.template.loaders.app_directories.Loader',
    #    )),
    # )
    # The loaders will return django.template.loaders.filesystem.Loader
    # and django.template.loaders.app_directories.Loader
    # The cached Loader and similar ones include a 'loaders' attribute
    # so we look for that.
    for loader in template_source_loaders:
        if hasattr(loader, 'loaders'):
            loaders.extend(loader.loaders)
        else:
            loaders.append(loader)
    return loaders


def get_template_source(name):
    source = None
    for loader in get_loaders():
        if loader.__module__.startswith('dbtemplates.'):
            # Don't give a damn about dbtemplates' own loader.
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
    if source is None and django.VERSION[:2] < (1, 2):
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
