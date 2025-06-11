from django.template import (Template, TemplateDoesNotExist,
                             TemplateSyntaxError)


def get_loaders():
    from django.template.loader import _engine_list
    loaders = []
    for engine in _engine_list():
        loaders.extend(engine.engine.template_loaders)
    return loaders


def get_template_source(name):
    source = None
    not_found = []
    for loader in get_loaders():
        if loader.__module__.startswith('dbtemplates.'):
            # Don't give a damn about dbtemplates' own loader.
            continue
        for origin in loader.get_template_sources(name):
            try:
                source = loader.get_contents(origin)
            except (NotImplementedError, TemplateDoesNotExist) as exc:
                if exc.args[0] not in not_found:
                    not_found.append(exc.args[0])
                continue
            else:
                return source
    raise TemplateDoesNotExist(name, chain=not_found)


def check_template_syntax(template):
    try:
        Template(template.content)
    except TemplateSyntaxError as e:
        return (False, e)
    return (True, None)
