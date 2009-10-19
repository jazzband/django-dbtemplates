__test__ = {"doctest": """

>>> from django.contrib.sites.models import Site
>>> from django.conf import settings
>>> from dbtemplates.models import Template
>>> Site(domain="example.com", name="example.com").save()
>>> Template(name="test_template.html")
<Template: test_template.html>
>>> from django.template import loader, Context
>>> t1 = Template(name='base.html', content="<html><head></head><body>{% block content %}Welcome at {{ title }}{% endblock %}</body></html>")
>>> t1.save()
>>> Site.objects.get_current()
<Site: example.com>
>>> t1.sites.all()
[<Site: example.com>]
>>> t1
<Template: base.html>
>>> "Welcome at" in t1.content
True
>>> t2 = Template(name='sub.html', content='{% extends "base.html" %}{% block content %}This is {{ title }}{% endblock %}')
>>> t2.save()
>>> test_site2 = Site(domain="example.org", name="example.org")
>>> test_site2.save()
>>> t2.sites.add(test_site2)
>>> t2
<Template: sub.html>
>>> test_site = Site.objects.get_current()
>>> Template.objects.filter(sites=test_site)
[<Template: base.html>, <Template: sub.html>]
>>> t2.sites.all()
[<Site: example.com>, <Site: example.org>]
>>> from dbtemplates.loader import load_template_source
>>> loader.template_source_loaders = [load_template_source]
>>> loader.get_template("base.html").render(Context({'title':'MainPage'}))
u'<html><head></head><body>Welcome at MainPage</body></html>'
>>> loader.get_template("sub.html").render(Context({'title':'SubPage'}))
u'<html><head></head><body>This is SubPage</body></html>'
>>> from django.core.management import call_command
>>> call_command('create_error_templates', force=True)
Created database template for 404 errors.
Created database template for 500 errors.
>>> Template.objects.filter(sites=test_site)
[<Template: 404.html>, <Template: 500.html>, <Template: base.html>, <Template: sub.html>]
>>> settings.DBTEMPLATES_ADD_DEFAULT_SITE = False
>>> t3 = Template(name='footer.html', content='ohai')
>>> t3.save()
>>> t3
<Template: footer.html>
>>> t3.sites.all()
[]
"""}
