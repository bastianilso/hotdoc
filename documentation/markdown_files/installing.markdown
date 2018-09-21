---
short-description: Detailed instructions for installing hotdoc
...

# Installing

## System-wide dependencies

### lxml

Hotdoc uses lxml, which depends on libxml2 and libxslt.

### cmake

For now, hotdoc bundles its own version of [libcmark](https://github.com/jgm/cmark) as a submodule, and builds it using cmake, which thus needs to be installed on the system.

### pyyaml

Hotdoc uses pyyaml to parse yaml ‘front-matter’ metadata in markdown pages, it depends on libyaml.

### flex

flex is an optional dependency, which enables the C and GI extensions. See [][Build options] for more info.

### clang and llvm-config

Clang and llvm-config are runtime dependencies for the C extension. 

### Command-line install

On Fedora you can install all these dependencies with:

```
dnf install python3-devel libxml2-devel libxslt-devel cmake libyaml-devel
```

And on ubuntu / debian:

```
apt-get install python3-dev libxml2-dev libxslt1-dev cmake libyaml-dev
```

We'll be happy to merge updates to this list if you have successfully built hotdoc on another platform.

## Creating a virtualenv

It is highly recommended to use a virtual env to try out any new python project, and hotdoc is no exception. You can however skip this step if you really do not
mind installing hotdoc system-wide.

> Assuming [pip](https://pip.pypa.io/en/stable/) is installed

```
python3 -m pip install virtualenv
python3 -m venv hotdoc_env
. hotdoc_env/bin/activate
```

You are now in a virtual environment, to exit it you may call `deactivate`, to enter it again simply call `. hotdoc_env/bin/activate` from the directory in which the environment was created.


## Installing HotDoc

To install HotDoc for regular usage (writing/editing docs), use pip to get the last released version of hotdoc:
  ```
  python3 -m pip install hotdoc
  ```

Alternatively you can install HotDoc from a from a github clone:
  ```
  git clone https://github.com/hotdoc/hotdoc.git
  cd hotdoc
  python3 setup.py install
  ```
  
If you wish to modify HotDoc's code, you can install an editable version from a github clone:
  ```
  git clone https://github.com/hotdoc/hotdoc.git
  cd hotdoc
  python3 -m pip install -e .[dev]
  ```
  
### Build options

To ensure that extensions with optional dependencies are enabled when installing hotdoc, the setup script will look at the following environment variables:

- `HOTDOC_BUILD_C_EXTENSION`: one of `enabled`, `disabled` or `auto`. Default is `auto`

This awkward way of passing options is due to setuptools' limitations.

