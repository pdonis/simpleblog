#!/usr/bin/env python
"""
Sub-Package SIMPLEBLOG.EXTENSIONS
Copyright (C) 2012 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""

from operator import attrgetter

from plib.stdlib.decotools import cached_property, wraps_class
from plib.stdlib.iters import prefixed_items

from simpleblog import (
    extension_types, extension_map, extend_attributes,
    BlogEntries, html_newline)


class NamedEntries(BlogEntries):
    """Named container for a set of blog entries.
    """
    
    typename = None
    prefix = None
    
    def __init__(self, blog, name):
        BlogEntries.__init__(self, blog)
        self.name = self.title = self.sortkey = name
        self.heading = "{0}: {1}".format(self.typename, name)
        if self.prefix:
            self.urlshort = "/{0}/{1}/".format(self.prefix, name)
        else:
            self.urlshort = "/{}/".format(name)
    
    @cached_property
    def prev_next_suffix(self):
        return self.name


def get_links(containers, reverse=False):
    """Return HTML links to containers.
    """
    # FIXME make this configurable
    return html_newline.join(
        '<a href="{0}">{1}</a>&nbsp;({2})'.format(c.urlshort, c.title, len(c.entries))
        for c in sorted(containers, key=attrgetter('sortkey'), reverse=reverse)
    )


class BlogExtension(object):
    """Base class for extension mechanism.
    """
    
    def __init__(self, config):
        self.config = config
        
        # Register this extension in the appropriate places
        attr_tmpl = '{}_'
        mixin_tmpl = '{}_mixin'
        for etype in extension_types:
            # Check for methods that extend a known attribute
            if any(
                item for item in prefixed_items(dir(self), attr_tmpl.format(etype))
                if not item.endswith('mixin')
            ):
                extension_map[etype].append(self)
            # Check for extensions that declare mixins
            mixin = getattr(self, mixin_tmpl.format(etype), None)
            if mixin:
                mixin.extension_type = etype
                extend_attributes(mixin)
                oldcls = extension_types[etype]
                @wraps_class(oldcls)
                class Extended(mixin, oldcls):
                    pass
                extension_types[etype] = Extended
        
        # Allow for post-init processing in subclasses
        self.post_init()
    
    def post_init(self):
        pass
