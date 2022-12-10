SRC_DIR = 'src'
TEST_DIR = 'test'
VSCODE_DIR = '.vscode'

README_FILE = 'README.md'
LICENSE_FILE = 'LICENSE'
GITIGNORE_FILE = '.gitignore'
PYPROJECT_FILE = 'pyproject.toml'
REQUIREMENTS_FILE = 'requirements{group}.txt'
VSCODE_FILE = 'settings.json'

ALL_GROUP_NAME = 'all'

EXTRA_REGEX = r'(.*)?extra == "(.*?)"'
VERSION_REGEX = r'^(\s*)(\d+).(\d+)(?:.(\d+))?$'
REQUIRES_PYTHON_REGEX = r'^(\d+.\d+)?(?:.\d)?$'


README_TPL = '''\
# Example Package

This is a simple example package. You can use
[Github-flavored Markdown](https://guides.github.com/features/mastering-markdown/)
to write your content.
'''


LICENSE_TPL = '''\
MIT License

Copyright (c) {year} {fullname}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


GITIGNORE_TPL = '''\
__pycache__
*.log
*.gz
*.egg-info
.pytest_cache
.python-version
.vscode
pyvenv.cfg
bin
dist
include
lib
lib64
share
'''


PYPROJECT_TPL = '''\
[build-system]
requires = ['setuptools']
build-backend = 'setuptools.build_meta'

[project]
name = ''
version = '0.1.0'
description = ''
readme = 'README.md'
requires-python = ''
license = {text = 'MIT License'}
authors = []
keywords = []
classifiers = []
dependencies = []
[project.optional-dependencies]
'''

VSCODE_TPL = '''\
{
    "files.exclude": {
        ".vscode": true,
        ".python-version": true,
        ".gitignore": true,
        "pyvenv.cfg": true,
        "**/.pytest_cache": true,
        "**/*.egg-info": true,
        "**/__pycache__": true,
        "**/.git": true
    },
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": [
        "--skip-string-normalization"
    ],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
'''
