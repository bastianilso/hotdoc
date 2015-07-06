import argparse, os, re

from xml.etree import ElementTree as ET
from giscanner.transformer import Transformer
from giscanner import ast
import logging

class NameFormatter(object):
    def __init__(self, language='python'):
        if language == 'C':
            self.__make_node_name = self.__make_c_node_name
        elif language == 'python':
            self.__make_node_name = self.__make_python_node_name

    def get_full_node_name(self, node):
        return self.__make_node_name (node)

    def __make_python_node_name (self, node):
        out = ""
        if type (node) in (ast.Namespace, ast.DocSection):
            return node.name

        if type (node) in (ast.Signal, ast.VFunction, ast.Property, ast.Field):
            out = "%s.%s-%s" % (node.namespace.name, node.parent.name,
                    node.name)

        if type (node) == ast.Function:
            while node:
                if out:
                    out = "%s.%s" % (node.name, out)
                else:
                    out = node.name

                if hasattr (node, "parent"):
                    node = node.parent
                else:
                    node = None

        elif type (node) in (ast.Class, ast.Enum):
            out = "%s.%s" % (node.namespace.name, node.name)

        return out

    def __make_c_node_name (self, node):
        out = ""
        if type (node) in (ast.Namespace, ast.DocSection):
            return node.name

        if type (node) in (ast.Signal, ast.VFunction, ast.Property, ast.Field):
            out = "%s%s-%s" % (node.namespace.name, node.parent.name,
                    node.name)

        if type (node) == ast.Function:
            while node:
                if out:
                    out = "%s_%s" % (node.name.lower(), out)
                else:
                    out = node.name

                if hasattr (node, "parent"):
                    node = node.parent
                else:
                    node = None

        elif type (node) in (ast.Class, ast.Enum):
            out = "%s%s" % (node.namespace.name, node.name)

        return out


class DocScanner(object):
    def __init__(self):
        specs = [
            ('!alpha', r'[a-zA-Z0-9_]+'),
            ('!alpha_dash', r'[a-zA-Z0-9_-]+'),
            ('!anything', r'.*'),
            ('note', r'\>\s*<<note_contents:anything>>\s*\n'),
            ('new_paragraph', r'\n\n'),
            ('new_line', r'\n'),
            ('code_start_with_language',
                r'\|\[\<!\-\-\s*language\s*\=\s*\"<<language_name:alpha>>\"\s*\-\-\>'),
            ('code_start', r'\|\['),
            ('code_end', r'\]\|'),
            ('property', r'#<<type_name:alpha>>:(<<property_name:alpha_dash>>)'),
            ('signal', r'#<<type_name:alpha>>::(<<signal_name:alpha_dash>>)'),
            ('type_name', r'#(<<type_name:alpha>>)'),
            ('enum_value', r'%(<<member_name:alpha>>)'),
            ('parameter', r'@<<param_name:alpha>>'),
            ('function_call', r'<<symbol_name:alpha>>\(\)'),
            ('include', r'{{\s*<<include_name:anything>>\s*}}'),
            ('heading', r'#+\s+<<heading:anything>>'),
        ]
        self.specs = self.unmangle_specs(specs)
        self.regex = self.make_regex(self.specs)

    def unmangle_specs(self, specs):
        mangled = re.compile('<<([a-zA-Z_:]+)>>')
        specdict = dict((name.lstrip('!'), spec) for name, spec in specs)

        def unmangle(spec, name=None):
            def replace_func(match):
                child_spec_name = match.group(1)

                if ':' in child_spec_name:
                    pattern_name, child_spec_name = child_spec_name.split(':', 1)
                else:
                    pattern_name = None

                child_spec = specdict[child_spec_name]
                # Force all child specs of this one to be unnamed
                unmangled = unmangle(child_spec, None)
                if pattern_name and name:
                    return '(?P<%s_%s>%s)' % (name, pattern_name, unmangled)
                else:
                    return unmangled

            return mangled.sub(replace_func, spec)

        return [(name, unmangle(spec, name)) for name, spec in specs]

    def make_regex(self, specs):
        regex = '|'.join('(?P<%s>%s)' % (name, spec) for name, spec in specs
                         if not name.startswith('!'))
        return re.compile(regex)

    def get_properties(self, name, match):
        groupdict = match.groupdict()
        properties = {name: groupdict.pop(name)}
        name = name + "_"
        for group, value in groupdict.iteritems():
            if group.startswith(name):
                key = group[len(name):]
                properties[key] = value
        return properties

    def scan(self, text):
        pos = 0
        while True:
            match = self.regex.search(text, pos)
            if match is None:
                break

            start = match.start()
            if start > pos:
                yield ('other', text[pos:start], None)

            pos = match.end()
            name = match.lastgroup
            yield (name, match.group(0), self.get_properties(name, match))

        if pos < len(text):
            yield ('other', text[pos:], None)



# Long name is long
def get_sorted_symbols_from_sections (sections, symbols):
    for element in sections:
        if element.tag == "SYMBOL":
            symbols.append (element.text)
        get_sorted_symbols_from_sections (element, symbols)


class AggregatedClass(object):
    def __init__(self, class_node, section_node):
        self.class_node = class_node
        self.__formatter = NameFormatter()
        self.__section_node = section_node
        self.signals = {}
        self.methods = {}
        self.properties = {}
        self.virtual_functions = {}

    def add_aggregated_node (self, node):
        name = self.__formatter.get_full_node_name (node)
        if type (node) == ast.Signal:
            self.signals[name] = node
        elif type (node) == ast.Function:
            self.methods[name] = node
        elif type (node) == ast.VFunction:
            self.virtual_functions[name] = node
        elif type (node) == ast.Property:
            self.properties[name] = node
        else:
            raise NotImplementedError

    def __sort_symbols (self, nodes):
        sorted_symbols = []
        for symbol in self.__section_node:
            try:
                node = nodes.pop (symbol.text)
                sorted_symbols.append (node)
            except KeyError:
                continue
        return sorted_symbols

    def sort (self):
        self.methods = self.__sort_symbols (self.methods)
        self.signals = self.__sort_symbols (self.signals)
        self.properties = self.__sort_symbols (self.properties)
        self.virtual_functions = self.__sort_symbols (self.virtual_functions)

class Renderer(object):
    def __init__ (self, transformer, include_directories, sections,
            do_class_aggregation=False):
        self.__transformer = transformer
        self.__include_directories = include_directories
        self.__sections = sections
        self.__do_class_aggregation = do_class_aggregation

        self.__handlers = self.__create_handlers ()
        self.__doc_renderers = self.__create_doc_renderers ()
        self.__doc_scanner = DocScanner()
        self.__name_formatter = NameFormatter()

        # Used to aggregate the class with its members
        self.__current_class = None
        self.__aggregated_classes = []

        # Used to avoid parsing code as doc
        self.__processing_code = False

        # Used to create the index file if required
        self.__created_pages = []

    def render (self, output):
        self.__walk_node(output, self.__transformer.namespace, [])
        self.__transformer.namespace.walk(lambda node, chain:
                self.__walk_node(output, node, chain))
        if self.__do_class_aggregation:
            self.__aggregate_classes (output)

    def __render_section (self, name, output, elements):
        if not elements:
            return ""

        out = ""
        try:
            out += self._render_section (name)
        except AttributeError:
            pass

        for elem in elements:
            with open (self.__make_file_name (output, elem), 'r') as f:
                out += f.read()

        return out

    def __aggregate_classes (self, output):
        for klass in self.__aggregated_classes:
            klass.sort()
            filename = self.__make_file_name (output, klass.class_node)
            with open (filename, 'a') as f:
                out = ""
                out += self.__render_section ('Properties', output,
                        klass.properties)
                out += self.__render_section ('Methods', output, klass.methods)
                out += self.__render_section ('Signals', output, klass.signals)
                out += self.__render_section ('Virtual Functions', output,
                        klass.virtual_functions)
                f.write (out)

    def render_index (self, output):
        out = ""

        try:
            out += self._start_index (self.__transformer.namespace.name)
        except AttributeError:
            pass

        filenames = [os.path.splitext(os.path.basename (filename))[0] for
                filename in self.__created_pages]
        try:
            out += self._render_index (filenames, self.__sections)
        except AttributeError:
            pass

        try:
            out += self._end_index ()
        except AttributeError:
            pass

        extension = self._get_extension ()
        filename = os.path.join (output, "index.%s" % extension)
        if out:
            with open (filename, 'w') as f:
                f.write (out)

    def __create_handlers (self):
        return {
                ast.Function: self.__handle_function,
                ast.Class: self.__handle_class,
                ast.Signal: self.__handle_signal,
                ast.VFunction: self.__handle_virtual_function,
                ast.DocSection: self.__handle_doc_section,
               }

    def __create_doc_renderers (self):
        return {
            'other': self.__render_other,
            'property': self.__render_property,
            'signal': self.__render_signal,
            'type_name': self.__render_type_name,
            'enum_value': self.__render_enum_value,
            'parameter': self.__render_parameter,
            'function_call': self.__render_function_call,
            'code_start': self.__render_code_start,
            'code_start_with_language': self.__render_code_start_with_language,
            'code_end': self.__render_code_end,
            'new_line': self.__render_new_line,
            'new_paragraph': self.__render_new_paragraph,
            'include': self.__render_include,
            'note': self.__render_note,
            'heading': self.__render_heading
        }

    def __render_other (self, node, match, props):
        try:
            return self._render_other (node, match)
        except AttributeError:
            return ""

    def __render_property (self, node, match, props):
        type_node = self.__resolve_type(props['type_name'])
        if type_node is None:
            return match

        try:
            prop = self._find_thing(type_node.properties, props['property_name'])
        except (AttributeError, KeyError):
            return self.__render_other (node, match, props)

        try:
            return self._render_property (node, prop)
        except AttributeError:
            return ""

    def __resolve_type(self, ident):
        try:
            matches = self.__transformer.split_ctype_namespaces(ident)
        except ValueError:
            return None

        for namespace, name in matches:
            node = namespace.get(name)
            if node:
                return node

        return None

    def __resolve_symbol(self, symbol):
        try:
            matches = self.__transformer.split_csymbol_namespaces(symbol)
        except ValueError:
            return None
        for namespace, name in matches:
            node = namespace.get_by_symbol(symbol)
            if node:
                return node

        if not node:
            for namespace, name in matches:
                node = namespace.get(name)
                if node:
                    return node
        return None

    def __render_signal (self, node, match, props):
        raise NotImplementedError

    def __render_type_name (self, node, match, props):
        ident = props['type_name']
        type_ = self.__resolve_type(ident)
        if not type_:
            return self.__render_other (node, match, props)

        type_name = self.__name_formatter.get_full_node_name (type_)
        try:
            return self._render_type_name (type_name)
        except AttributeError:
            return ""

    def __render_enum_value (self, node, match, props):
        raise NotImplementedError

    def __render_parameter (self, node, match, props):
        try:
            parameter = node.get_parameter(props['param_name'])
        except (AttributeError, ValueError):
            return self.__render_other (node, match, props)

        try:
            return self._render_parameter (node, parameter)
        except AttributeError:
            return ""

    def __render_function_call (self, node, match, props):
        func = self.__resolve_symbol(props['symbol_name'])
        if func is None:
            return self.__render_other (node, match, props)

        function_name = self.__name_formatter.get_full_node_name (func)
        try:
            return self._render_function_call (function_name)
        except AttributeError:
            return ""

    def __render_code_start (self, node, match, props):
        self.__processing_code = True
        try:
            return self._render_code_start ()
        except AttributeError:
            return ""

    def __render_code_start_with_language (self, node, match, props):
        self.__processing_code = True
        try:
            return self._render_code_start_with_language (props["language_name"])
        except AttributeError:
            return ""

    def __render_code_end (self, node, match, props):
        self.__processing_code = False
        try:
            return self._render_code_end ()
        except AttributeError:
            return ""

    def __render_new_line (self, node, match, props):
        try:
            return self._render_new_line ()
        except AttributeError:
            return ""

    def __render_new_paragraph (self, node, match, props):
        try:
            return self._render_new_paragraph ()
        except AttributeError:
            return ""

    def __render_include (self, node, match, props):
        filename = props["include_name"].strip()
        f = None

        try:
            f = open(filename, 'r')
        except IOError:
            for dir_ in self.__include_directories:
                try:
                    f = open(os.path.join(dir_, filename), 'r')
                    break
                except:
                    continue
        if f:
            contents = f.read()
            if self.__processing_code:
                return contents
            else:
                out = self.__render_doc_string(node, contents)
            f.close()
        else:
            logging.warning("Could not find file %s" % (props["include_name"], ))
            out = match

        return out

    def __render_note (self, node, match, props):
        if self.__processing_code:
            return self.__render_other (node, match, props)

        try:
            return self._render_note (props["note_contents"])
        except AttributeError:
            return ""

    def __render_heading (self, node, match, props):
        raise NotImplementedError

    def __get_class_symbols (self, root, node):
        formatter = NameFormatter ()
        node_name = formatter.get_full_node_name (node)
        return_next = False
        for element in root:
            if return_next:
                return element

            if element.text == node_name:
                return_next = True
                continue

            res = self.__get_class_symbols (element, node)
            if res is not None:
                return res
        return None

    def __do_aggregation (self, node):
        if type(node) == ast.Namespace:
            return False

        if type (node) == ast.Class:
            symbol = self.__get_class_symbols (self.__sections, node)
            self.__current_class = AggregatedClass (node, symbol)
            self.__aggregated_classes.append (self.__current_class)
            return False
        elif self.__current_class and node.parent is self.__current_class.class_node:
            self.__current_class.add_aggregated_node (node)
            return True
        else:
            self.__current_class = None
            return False

    def __make_file_name (self, output, node):
        extension = self._get_extension ()
        name = self.__name_formatter.get_full_node_name (node)
        return os.path.join (output, "%s.%s" % (name, extension))

    def __walk_node(self, output, node, chain):
        filename = self.__make_file_name (output, node)

        try:
            handler = self.__handlers[type (node)]
        except KeyError:
            return True

        with open (filename, 'w') as f:
            f.write (handler (node))

        if not self.__do_aggregation (node):
            self.__created_pages.append (filename)

        return True

    def _get_extension (self):
        raise NotImplementedError

    def __render_doc_string (self, node, docstring):
        if not docstring:
            return ""

        out = ""
        tokens = self.__doc_scanner.scan (docstring)
        for tok in tokens:
            kind, match, props = tok
            rendered_token = self.__doc_renderers[kind](node, match, props)
            if rendered_token:
                out += rendered_token
        return out

    def __render_doc (self, node):
        return self.__render_doc_string (node, node.doc)

    def __handle_parameter (self, node):
        out = ""
        try:
            out += self._start_parameter (node.argname)
        except AttributeError:
            pass

        logging.debug ("handling parameter %s" % node.argname)
        out += self.__render_doc (node)

        try:
            out += self._end_parameter ()
        except AttributeError:
            pass

        return out

    def __handle_class (self, node):
        out = ""
        try:
            out += self._start_class (self.__name_formatter.get_full_node_name (node))
        except AttributeError:
            pass

        logging.debug ("handling class %s" % self.__name_formatter.get_full_node_name (node))
        out += self.__render_doc (node)

        try:
            out += self._end_class ()
        except AttributeError:
            pass
        return out

    def __handle_parameters (self, node):
        out = ""
        if node.all_parameters:
            try:
                out += self._start_parameters ()
            except AttributeError:
                pass

            for param in node.all_parameters:
                out += self.__handle_parameter (param)

            try:
                out += self._end_parameters ()
            except AttributeError:
                pass

        return out

    def __handle_signal (self, node):
        out = ""
        try:
            out += self._start_signal (self.__name_formatter.get_full_node_name (node))
        except AttributeError:
            pass

        out += self.__handle_parameters (node)

        logging.debug ("handling signal %s" % self.__name_formatter.get_full_node_name (node))
        out += self.__render_doc (node)

        try:
            out += self._end_signal ()
        except AttributeError:
            pass

        return out

    def __handle_function (self, node):
        out = ""
        param_names = []
        for param in node.all_parameters:
            param_names.append (param.argname)
        try:
            out += self._start_function (self.__name_formatter.get_full_node_name (node), param_names)
        except AttributeError:
            pass

        out += self.__handle_parameters (node)

        logging.debug ("handling function %s" % self.__name_formatter.get_full_node_name (node))
        out += self.__render_doc (node)

        try:
            out += self._end_function ()
        except AttributeError:
            pass
        return out

    def __handle_virtual_function (self, node):
        out = ""
        try:
            out += self._start_virtual_function (self.__name_formatter.get_full_node_name (node))
        except AttributeError:
            pass

        out += self.__handle_parameters (node)

        logging.debug ("handling virtual function %s" % self.__name_formatter.get_full_node_name (node))
        out += self.__render_doc (node)

        try:
            out += self._end_virtual_function ()
        except AttributeError:
            pass
        return out

    def __handle_doc_section (self, node):
        out = ""
        try:
            out += self._start_doc_section (node.name)
        except AttributeError:
            pass

        logging.debug ("handling doc section %s" % node.name)
        out += self.__render_doc (node)

        try:
            out += self._end_doc_section ()
        except AttributeError:
            pass
        return out


class MarkdownRenderer (Renderer):
    def __render_local_link (self, name):
        return "#%s" % name

    def __render_title (self, title, level=1):
        return "%s%s%s" % ("#" * level, title, self._render_new_paragraph ())

    def _render_line (self, line):
        return "%s%s" % (line, self._render_new_line ())

    def _render_paragraph (self, paragraph):
        return "%s%s" % (paragraph, self._render_new_paragraph ())

    def _get_extension (self):
        return "md"

    def _start_parameter (self, param_name):
        return "+ %s: " % param_name

    def _end_parameter (self):
        return self._render_new_line ()

    def _end_parameters (self):
        return self._render_new_line ()

    def _start_function (self, function_name, param_names):
        prototype = "%s (" % function_name
        for i, param_name in enumerate (param_names):
            if (i != 0):
                prototype += ", "
            prototype += param_name
        prototype += ")"
        return self.__render_title (prototype, level=3)

    def _render_section (self, section_name):
        return self.__render_title ("%s:" % section_name, level=2)

    def _end_function (self):
        return self._render_new_paragraph ()

    def _start_virtual_function (self, function_name):
        return self.__render_title (function_name, level=3)

    def _end_virtual_function (self):
        return self._render_new_paragraph ()

    def _start_signal (self, signal_name):
        return self.__render_title (signal_name, level=3)

    def _end_signal (self):
        return self._render_new_paragraph ()

    def _start_class (self, class_name):
        return self.__render_title (class_name, level=2)

    def _end_class (self):
        return self._render_new_paragraph ()

    def _start_doc_section (self, doc_section_name):
        return self.__render_title (doc_section_name, level=1)

    def _end_doc_section (self):
        return self._render_new_paragraph ()

    def _render_other (self, node, other):
        return other

    def _render_property (self, node, prop):
        print "rendering property"

    def _render_signal (self, node, signal):
        print "rendering signal"

    def _render_type_name (self, type_name):
        return "[%s](%s)" % (type_name, self.__render_local_link (type_name))

    def _render_enum_value (self, node, enum):
        print "rendering enum value"

    def _render_parameter (self, node, parameter):
        if isinstance(parameter.type, ast.Varargs):
            return "*...*"
        else:
            return "*%s*" % parameter.argname

    def _render_function_call (self, function_name):
        return "[%s](%s)" % (function_name, self.__render_local_link (function_name))

    def _render_code_start (self):
        return "```%s" % self._render_new_line ()

    def _render_code_start_with_language (self, language):
        return "```%s%s" % (language, self._render_new_line ())

    def _render_code_end (self):
        return "```%s" % self._render_new_line ()

    def _render_new_line (self):
        return "\n"

    def _render_new_paragraph (self):
        return "\n\n"

    def _render_note (self, note):
        return "> %s%s" % (note, self._render_new_paragraph ())

    def _render_heading (self, node, title, level):
        print "rendering heading"


# Input format for https://github.com/tripit/slate
class SlateMarkdownRenderer (MarkdownRenderer):
    def _start_index (self, libname):
        out = ""
        out += self._render_line ("---")
        out += self._render_paragraph ("title: %s" % libname)
        out += self._render_line ("language_tabs:")
        out += self._render_paragraph ("  - c")
        out += self._render_line ("toc_footers:")
        out += self._render_paragraph ("""  - <a href='http://github.com/tripit/slate'>Documentation Powered by Slate</a>""")
        out += self._render_line ("includes:")

        return out

    def _end_index (self):
        out = ""
        out += self._render_line ("")
        out += self._render_line ("search: true")
        out += self._render_line ("---")
        return out

    def _render_index (self, filenames, sections):
        out = ""
        symbols = []
        get_sorted_symbols_from_sections (sections, symbols)
        for symbol in symbols:
            if symbol in filenames:
                out += self._render_line ("  - %s" % symbol)
        return out


class SectionsGenerator(object):
    def __init__ (self, transformer):
        self.__transformer = transformer

        self.__name_formatter = NameFormatter ()

        # Used to close the previous section if necessary
        self.__opened_section = False

    def generate (self, output):
        # Three passes but who cares
        filename = os.path.join (output, "%s-sections.txt" %
                self.__transformer.namespace.name)
        with open (filename, 'w') as f:
            f.write ("<SECTIONS>")
            self.__walk_node(output, self.__transformer.namespace, [], f)
            self.__transformer.namespace.walk(lambda node, chain:
                    self.__walk_node(output, node, chain, f))
            if self.__opened_section:
                f.write ("</SYMBOLS>")
                f.write ("</SECTION>")
            f.write ("</SECTIONS>")

        with open (filename, 'r') as f:
            contents = f.read ()
            root = ET.fromstring(contents)
            self.__indent(root)

        with open (filename, 'w') as f:
            f.write(ET.tostring(root))

        return root
    
    def __walk_node(self, output, node, chain, f):
        if type (node) in [ast.Alias, ast.Record]:
            return False

        name = self.__name_formatter.get_full_node_name (node)

        if type (node) in [ast.Namespace, ast.DocSection, ast.Class,
                ast.Interface]:
            if self.__opened_section:
                f.write ("</SYMBOLS>")
                f.write ("</SECTION>")

            f.write ("<SECTION>")
            f.write ("<SYMBOL>%s</SYMBOL>" % name)
            f.write ("<SYMBOLS>")
            self.__opened_section = True
        else:
            f.write ("<SYMBOL>%s</SYMBOL>" % name)

        return True

    def __indent (self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.__indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i


def doc_main (args):
    try:
        debug_level = os.environ["DOCTOOL_DEBUG"]
        if debug_level.lower() == "info":
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.DEBUG)
    except KeyError:
        pass

    parser = argparse.ArgumentParser()

    parser.add_argument("girfile")
    parser.add_argument("-o", "--output",
                      action="store", dest="output",
                      help="Directory to write output to")
    parser.add_argument("-l", "--language",
                      action="store", dest="language",
                      default="c",
                      help="Output language")
    parser.add_argument("-I", "--add-include-path",
                      action="append", dest="include_paths", default=[],
                      help="include paths for other GIR files")
    parser.add_argument("-M", "--markdown-include-path",
                      action="append", dest="markdown_include_paths", default=[],
                      help="include paths for markdown inclusion")
    parser.add_argument("-s", "--write-sections-file",
                      action="store_true", dest="write_sections",
                      help="Generate and write out a sections file")
    parser.add_argument("-u", "--sections-file",
                      action="store", dest="sections_file",
                      help="Sections file to use for ordering")
    parser.add_argument("-O", "--online-links",
                      action="store_true", dest="online_links",
                      help="Generate online links")
    parser.add_argument("-g", "--link-to-gtk-doc",
                      action="store_true", dest="link_to_gtk_doc",
                      help="Link to gtk-doc documentation, the documentation "
                      "packages to link against need to be installed in "
                      "/usr/share/gtk-doc")
    parser.add_argument("-R", "--resolve-implicit-links",
                      action="store_true", dest="resolve_implicit_links",
                      help="All the space and parentheses-separated tokens "
                      "in the comment blocks will be analyzed to see if they "
                      "map to an existing code or symbol. If they do, a link "
                      "will be inserted, for example 'pass that function "
                      "a GList' will resolve the existing GList type and "
                      "insert a link to its documentation")

    args = parser.parse_args(args[1:])
    if not args.output:
        raise SystemExit("missing output parameter")

    if 'UNINSTALLED_INTROSPECTION_SRCDIR' in os.environ:
        top_srcdir = os.environ['UNINSTALLED_INTROSPECTION_SRCDIR']
        top_builddir = os.environ['UNINSTALLED_INTROSPECTION_BUILDDIR']
        extra_include_dirs = [os.path.join(top_srcdir, 'gir'), top_builddir]
    else:
        extra_include_dirs = []
    extra_include_dirs.extend(args.include_paths)
    transformer = Transformer.parse_from_gir(args.girfile, extra_include_dirs)

    if not args.sections_file:
        sections_generator = SectionsGenerator (transformer)
        sections = sections_generator.generate (args.output)
    else:
        sections = ET.parse (args.sections_file).getroot ()

    renderer = SlateMarkdownRenderer (transformer, args.markdown_include_paths,
            sections, do_class_aggregation=True)
    renderer.render (args.output)
    renderer.render_index (args.output)