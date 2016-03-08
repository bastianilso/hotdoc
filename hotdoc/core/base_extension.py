# -*- coding: utf-8 -*-
#
# Copyright © 2015,2016 Mathieu Duponchelle <mathieu.duponchelle@opencreed.com>
# Copyright © 2015,2016 Collabora Ltd
#
# This library is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 2.1 of the License, or (at your option)
# any later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

"""
Utilities and baseclasses for extensions
"""

import os

from collections import defaultdict

from hotdoc.core.doc_tree import DocTree
from hotdoc.formatters.html_formatter import HtmlFormatter
from hotdoc.utils.utils import OrderedSet
from hotdoc.utils.configurable import Configurable
from hotdoc.utils.loggable import debug, info, warn, error


# pylint: disable=too-few-public-methods
class ExtDependency(object):
    """
    Represents a dependency on another extension.

    If not satisfied, the extension will not be instantiated.

    See the `BaseExtension.get_dependencies` static method documentation
    for more information.

    Attributes:
        dependency_name: str, the name of the extension depended on.
        is_upstream: bool, if set to true hotdoc will arrange for
            the extension depended on to have its `BaseExtension.setup`
            implementation called first. Circular dependencies will
            generate an error.
    """

    def __init__(self, dependency_name, is_upstream=False):
        """
        Constructor for `BaseExtension`.

        Args:
            dependency_name: str, see `ExtDependency.dependency_name`
            is_upstream: bool, see `ExtDependency.is_upstream`
        """
        self.dependency_name = dependency_name
        self.is_upstream = is_upstream


class BaseExtension(Configurable):
    """
    All extensions should inherit from this base class

    Attributes:
        EXTENSION_NAME: str, the unique name of this extension, should
            be overriden and namespaced appropriately.
        doc_repo: doc_repo.DocRepo, the DocRepo instance which documentation
            hotdoc is working on.
        formatters: dict, a mapping of format -> `base_formatter.Formatter`
            subclass instances.
    """
    # pylint: disable=unused-argument
    EXTENSION_NAME = "base-extension"

    def __init__(self, doc_repo):
        """Constructor for `BaseExtension`.

        This should never get called directly.

        Args:
            doc_repo: The `doc_repo.DocRepo` instance which documentation
                is being generated.
        """
        self.doc_repo = doc_repo
        self.formatters = {"html": HtmlFormatter([])}
        self.__created_symbols = defaultdict(OrderedSet)
        self.__naive_path = None

    # pylint: disable=no-self-use
    def warn(self, code, message):
        """
        Shortcut function for `loggable.warn`

        Args:
            code: see `utils.loggable.warn`
            message: see `utils.loggable.warn`
        """
        warn(code, message)

    # pylint: disable=no-self-use
    def error(self, code, message):
        """
        Shortcut function for `utils.loggable.error`

        Args:
            code: see `utils.loggable.error`
            message: see `utils.loggable.error`
        """
        error(code, message)

    def debug(self, message, domain=None):
        """
        Shortcut function for `utils.loggable.debug`

        Args:
            message: see `utils.loggable.debug`
            domain: see `utils.loggable.debug`
        """
        if domain is None:
            domain = self.EXTENSION_NAME
        debug(message, domain)

    def info(self, message, domain=None):
        """
        Shortcut function for `utils.loggable.info`

        Args:
            message: see `utils.loggable.info`
            domain: see `utils.loggable.info`
        """
        if domain is None:
            domain = self.EXTENSION_NAME
        info(message, domain)

    def get_formatter(self, output_format):
        """
        Get the `base_formatter.Formatter` instance of this extension
        for a given output format.

        Args:
            output_format: str, the output format, for example `html`
        Returns:
            base_formatter.Formatter: the formatter for this format,
                or `None`.
        """
        return self.formatters.get(output_format)

    def setup(self):
        """
        Extension subclasses should implement this to scan whatever
        source files they have to scan, and connect to the various
        signals they have to connect to.

        Note that this will be called *after* the `doc_tree.DocTree`
        of this instance's `BaseExtension.doc_repo` has been fully
        constructed, but before its `doc_tree.DocTree.resolve_symbols`
        method has been called.
        """
        pass

    def finalize(self):
        """
        This method will be called during the last phase of the generation
        process. The only action taken after this is to persist and close
        some resources, such as the `doc_repo.DocRepo.doc_database` of
        this instance's `BaseExtension.doc_repo`
        """
        pass

    def get_stale_files(self, all_files):
        """
        Shortcut function to `change_tracker.ChangeTracker.get_stale_files`
        for the tracker of this instance's `BaseExtension.doc_repo`

        Args:
            all_files: see `change_tracker.ChangeTracker.get_stale_files`
        """
        return self.doc_repo.change_tracker.get_stale_files(
            all_files,
            self.EXTENSION_NAME)

    @staticmethod
    def get_dependencies():
        """
        Override this to return the list of extensions this extension
        depends on if needed.

        Returns:
            list: A list of `ExtDependency` instances.
        """
        return []

    def get_or_create_symbol(self, *args, **kwargs):
        """
        Extensions that discover and create instances of `symbols.Symbol`
        should do this through this method, as it will keep an index
        of these which can be used when generating a "naive index".

        See `doc_database.DocDatabase.get_or_create_symbol` for more
        information.

        Args:
            args: see `doc_database.DocDatabase.get_or_create_symbol`
            kwargs: see `doc_database.DocDatabase.get_or_create_symbol`

        Returns:
            symbols.Symbol: the created symbol, or `None`.
        """
        sym = self.doc_repo.doc_database.get_or_create_symbol(*args, **kwargs)

        if sym:
            self.__created_symbols[sym.filename].add(sym)

        return sym

    # pylint: disable=no-self-use
    def _get_naive_link_title(self, source_file):
        """
        When a "naive index" is generated by an extension, this class
        generates links between the "base index" and its subpages.

        One subpage is generated per code source file, for example
        if a source file named `my-foo-bar.c` contains documentable
        symbols, a subpage will be created for it, and the label
        of the link in the index will be `my-foo-bar`. Override this
        method to provide a custom label instead.

        Args:
            source_file: The name of the source file to provide a custom
                link label for, for example `/home/user/my-foo-bar.c`

        Returns:
            str: a custom label.
        """
        stripped = os.path.splitext(source_file)[0]
        title = os.path.basename(stripped)
        return title

    def _get_naive_page_description(self, source_file):
        """
        When a "naive index" is generated by an extension, this class
        will preface every subpage it creates for a given source file
        with a description, the default being simply the name of the
        source file, stripped of its extension.

        Override this method to provide a custom description instead.

        Args:
            source_file: The name of the source file to provide a custom
                description for, for example `/home/user/my-foo-bar.c`

        Returns:
            str: a custom description.
        """
        stripped = os.path.splitext(source_file)[0]
        title = os.path.basename(stripped)
        return '## %s\n\n' % title

    def create_naive_index(self, all_source_files):
        """
        This class can generate an index for the documentable symbols
        in a set of source files. To make use of this feature, subclasses
        should call on this method when the well known name they registered
        is encountered by the `DocRepo.doc_repo.doc_tree` of their instance's
        `BaseExtension.doc_repo`.

        This will generate a set of initially empty markdown files, which
        should be populated by calling `BaseExtension.update_naive_index`
        once symbols have been discovered and created through
        `BaseExtension.get_or_create_symbol`.

        Args:
            all_source_files: list, a list of paths, for example
                `[my_foo_bar.c]`.
        Returns: tuple, the arguments expected from a index handler.
        """
        index_name = self.EXTENSION_NAME + "-index.markdown"
        dirname = self.doc_repo.get_generated_doc_folder()
        index_path = os.path.join(dirname, index_name)

        with open(index_path, 'w') as _:
            _.write('## API reference\n\n')
            for source_file in sorted(all_source_files):
                link_title = self._get_naive_link_title(source_file)
                markdown_name = link_title + '.markdown'
                _.write('#### [%s](%s)\n' % (link_title, markdown_name))

        self.__naive_path = index_path
        return index_path, '', self.EXTENSION_NAME

    def update_naive_index(self):
        """
        This method can populate the pages generated by
        `BaseExtension.create_naive_index` with the symbols created through
        `BaseExtension.get_or_create_symbol`.
        """
        subtree = DocTree(self.doc_repo.include_paths,
                          self.doc_repo.get_private_folder())
        dirname = self.doc_repo.get_generated_doc_folder()
        for source_file, symbols in self.__created_symbols.items():
            link_title = self._get_naive_link_title(source_file)
            markdown_path = link_title + '.markdown'
            markdown_path = os.path.join(dirname,
                                         markdown_path)
            with open(markdown_path, 'w') as _:
                _.write(self._get_naive_page_description(source_file))
                for symbol in sorted(symbols, key=lambda s: s.unique_name):
                    # FIXME: more generic escaping
                    unique_name = symbol.unique_name.replace('_', r'\_')
                    _.write('* [%s]()\n' % unique_name)

        subtree.build_tree(self.__naive_path,
                           extension_name=self.EXTENSION_NAME)
        self.doc_repo.doc_tree.pages.update(subtree.pages)

    def format_page(self, page, link_resolver, output):
        """
        Called by `doc_repo.DocRepo.format_page`, to leave full control
        to extensions over the formatting of the pages they are
        responsible of.

        Args:
            page: doc_tree.Page, the page to format.
            link_resolver: links.LinkResolver, object responsible
                for resolving links potentially mentioned in `page`
            output: str, path to the output directory.
        """
        formatter = self.get_formatter('html')
        if page.is_stale:
            debug('Formatting page %s' % page.link.ref, 'formatting')
            page.formatted_contents = \
                self.doc_repo.doc_tree.page_parser.format_page(
                    page, link_resolver, formatter)
            page.format(formatter, link_resolver, output)
        else:
            debug('Not formatting page %s, up to date' % page.link.ref,
                  'formatting')
