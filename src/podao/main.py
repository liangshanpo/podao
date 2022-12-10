import getpass
import os
import re

from datetime import datetime
from importlib.metadata import requires

import sh
import tomlkit

from packaging.requirements import Requirement

from podao.constant import (
    EXTRA_REGEX,
    GITIGNORE_FILE,
    GITIGNORE_TPL,
    LICENSE_FILE,
    LICENSE_TPL,
    PYPROJECT_FILE,
    PYPROJECT_TPL,
    README_FILE,
    README_TPL,
    REQUIREMENTS_FILE,
    REQUIRES_PYTHON_REGEX,
    SRC_DIR,
    TEST_DIR,
    VERSION_REGEX,
    VSCODE_DIR,
    VSCODE_FILE,
    VSCODE_TPL,
)
from podao.util import atomic_write, create_dir, singleton


@singleton
class Project:
    def __init__(self, dir):
        self.root = self._ensure_root(dir)
        self.config = self._ensure_config()

    @property
    def pip(self):
        sh.cd(self.root)
        return sh.Command('./bin/pip')

    def _ensure_root(self, dir):
        dir = os.path.normpath(os.path.abspath(dir or '.'))
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir

    def _ensure_config(self):
        pyproject = os.path.join(self.root, PYPROJECT_FILE)
        if os.path.exists(pyproject):
            with open(pyproject) as p:
                config = tomlkit.load(p)
        else:
            config = tomlkit.loads(PYPROJECT_TPL)

        if not (
            config.get('build-system', None) and isinstance(config['build-system'], dict)
        ):
            config['build-system'] = tomlkit.table()
            config['build-system']['requires'] = ['setuptools']
            config['build-system']['build-backend'] = 'setuptools.build_meta'

        if not (config.get('project', None) and isinstance(config['project'], dict)):
            config['project'] = tomlkit.table()

        if not config['project'].get('name', None):
            config['project']['name'] = os.path.basename(self.root)

        if not config['project'].get('authors', None):
            config['project']['authors'] = []
            config['project']['authors'].append({'name': getpass.getuser(), 'email': ''})

        if not (
            config['project'].get('optional-dependencies', None)
            and isinstance(config['project']['optional-dependencies'], dict)
        ):
            config['project']['optional-dependencies'] = tomlkit.table()

        return config

    def _purify_depends(self, package, group=None, purge=False):
        depends = {Package(p) for p in self.get_dependencies(group)}
        package = {Package(package)}
        depends = (depends - package) if purge else ((depends - package) | package)
        return depends

    def _gen_pyproject(self):
        with atomic_write(os.path.join(self.root, PYPROJECT_FILE), overwrite=True) as p:
            p.write(tomlkit.dumps(self.config).replace('"', '\''))
        yield f'    {PYPROJECT_FILE} refreshed'

    def _gen_readme(self):
        with atomic_write(os.path.join(self.root, README_FILE), overwrite=False) as p:
            if not p:
                yield f'    {README_FILE} already exists, skipping'
                return
            p.write(README_TPL)
        yield f'    {README_FILE} created'

    def _gen_license(self):
        year = datetime.today().year
        name = getpass.getuser()
        with atomic_write(os.path.join(self.root, LICENSE_FILE), overwrite=False) as p:
            if not p:
                yield f'    {LICENSE_FILE} already exists, skipping'
                return
            p.write(LICENSE_TPL.format(year=year, fullname=name))
        yield f'    {LICENSE_FILE} created'

    def _gen_gitignore(self):
        with atomic_write(os.path.join(self.root, GITIGNORE_FILE), overwrite=False) as p:
            if not p:
                yield f'    {GITIGNORE_FILE} already exists, skipping'
                return
            p.write(GITIGNORE_TPL)
        yield f'    {GITIGNORE_FILE} created'

    def _gen_vscode(self):
        yield from create_dir(self.root, VSCODE_DIR)
        with atomic_write(
            os.path.join(self.root, VSCODE_DIR, VSCODE_FILE), overwrite=False
        ) as p:
            if not p:
                yield f'    {VSCODE_FILE} already exists, skipping'
                return
            p.write(VSCODE_TPL)
        yield f'    {VSCODE_FILE} created'

    def _gen_requirements(self, data, req_file):
        with atomic_write(os.path.join(self.root, req_file)) as p:
            p.write(data)

    def create_venv(self, python):
        available_python = [
            v.strip()
            for v in sh.pyenv('install', '--list').splitlines()
            if re.match(VERSION_REGEX, v)
        ]
        if not python or python not in available_python:
            python = available_python[-1]

        if not python:
            yield 'Can not find available python, specify a python version number please'
        self.python = python

        yield f'Working on {self.root}'
        yield f'Preparing project environment with python {python}'
        sh.pyenv('install', '-s', python)
        sh.pyenv('local', python)
        sh.python('-m', 'venv', '.')
        self.config['project'][
            'requires-python'
        ] = f'>={re.match(REQUIRES_PYTHON_REGEX, self.python)[1]}'

    def create_structure(self, ide):
        yield f'Preparing project directories: {SRC_DIR} {TEST_DIR}'
        yield from create_dir(self.root, SRC_DIR)
        yield from create_dir(self.root, TEST_DIR)

        yield f'Preparing project files: {PYPROJECT_FILE} {README_FILE} {LICENSE_FILE} {GITIGNORE_FILE}'
        yield from self._gen_pyproject()
        yield from self._gen_readme()
        yield from self._gen_license()
        yield from self._gen_gitignore()
        if ide:
            yield from self._gen_vscode()

    def install(self, packages, group=None):
        for k in packages:
            yield f'Installing {k}'
            self.pip('install', '-U', k)
            self.add_package(k, group)
        yield from self._gen_pyproject()

    def uninstall(self, packages):
        for k in packages:
            yield f'Uninstalling {k}'
            self.pip('uninstall', '-y', k)
            self.del_package(k)
        yield from self._gen_pyproject()

    def freeze(self, group=None):
        req_file = REQUIREMENTS_FILE.format(group="-" + group if group else "")
        yield f'Creating snapshot to {req_file}'
        self._gen_requirements(
            '\n'.join(sorted([p.line_name for p in self.snap_packages(group)])), req_file
        )

    def snap_packages(self, group=None):
        packages = {
            Package(p)
            for p in self.pip('freeze').splitlines()
            if not (p.startswith('#') or p.startswith('-e'))
        }

        depends = {Package(p) for p in self.get_dependencies()}
        if group == 'all':
            for g in self.get_optional_groups():
                depends |= {Package(p) for p in self.get_dependencies(g)}
        elif group:
            depends |= {Package(p) for p in self.get_dependencies(group)}

        requirements = set()
        for d in depends:
            if d.extras:
                requirements |= {
                    Package(p)
                    for p in requires(d.name)
                    if (x := re.match(EXTRA_REGEX, str(Package(p).marker)))
                    and x[2] in d.extras
                }
            else:
                requirements |= {
                    Package(p)
                    for p in requires(d.name)
                    if not re.match(EXTRA_REGEX, str(Package(p).marker))
                }

        depends |= requirements
        packages &= depends
        return packages

    def add_package(self, package, group=None):
        depends = self._purify_depends(package, group)
        if group:
            self.config['project']['optional-dependencies'][group] = [
                p.line_name for p in depends
            ]
        else:
            for g in self.get_optional_groups():
                self.config['project']['optional-dependencies'][g] = [
                    p.line_name for p in self._purify_depends(package, g, purge=True)
                ]
            self.config['project']['dependencies'] = [p.line_name for p in depends]

    def del_package(self, package):
        self.config['project']['dependencies'] = [
            p.line_name for p in self._purify_depends(package, purge=True)
        ]
        self.config['project']['optional-dependencies'] = {
            g: depends
            for g in self.get_optional_groups()
            if (
                depends := [
                    p.line_name for p in self._purify_depends(package, g, purge=True)
                ]
            )
        }

    def get_optional_groups(self):
        optional = self.config['project']['optional-dependencies']
        return optional.keys()

    def get_dependencies(self, group=None):
        project = self.config.get('project', {})
        if group:
            optional = project.get('optional-dependencies', {})
            return optional.get(group, [])
        else:
            return project.get('dependencies', [])


class Package:
    def __init__(self, line):
        req = Requirement(self._normalize_line(line))
        self.name = req.name
        self.extras = req.extras
        self.marker = req.marker
        self.line_name = str(req)

    def _normalize_line(self, line):
        return line

    def __hash__(self):
        return hash((self.__class__.__name__, str(self.name)))

    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.line_name
