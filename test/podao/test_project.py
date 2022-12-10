import os
import shutil
import tempfile

import pytest

from podao.constant import (
    GITIGNORE_FILE,
    LICENSE_FILE,
    PYPROJECT_FILE,
    README_FILE,
    REQUIREMENTS_FILE,
    SRC_DIR,
    TEST_DIR,
    VSCODE_DIR,
    VSCODE_FILE,
)
from podao.main import Package, Project


def test_package():
    p = Package('requests [security] >= 2.8.1, == 2.8.* ; python_version < "2.7"')
    assert p.name == 'requests'
    assert p.extras == {'security'}
    assert str(p.marker) == 'python_version < "2.7"'
    assert p.line_name == 'requests[security]==2.8.*,>=2.8.1; python_version < "2.7"'

    p = Package('cchardet; python_version < "3.10" and extra=="speedups"')
    assert p.name == 'cchardet'
    assert str(p.marker) == 'python_version < "3.10" and extra == "speedups"'


@pytest.fixture(scope='module')
def project():
    prefix = 'podao-'
    suffix = '-project'
    odir = os.getcwd()
    pdir = tempfile.mkdtemp(suffix, prefix)
    os.chdir(pdir)
    p = Project(pdir)
    yield p
    del p
    os.chdir(odir)
    shutil.rmtree(pdir)


def test_create_venv(project):
    for s in project.create_venv('3.10.4'):
        print(s)
    assert os.path.isfile(os.path.join(project.root, 'pyvenv.cfg'))


@pytest.mark.depends(on=['test_create_venv'])
def test_create_structure(project):
    for s in project.create_structure('vscode'):
        print(s)
    assert os.path.exists(os.path.join(project.root, SRC_DIR))
    assert os.path.exists(os.path.join(project.root, TEST_DIR))
    assert os.path.exists(os.path.join(project.root, README_FILE))
    assert os.path.exists(os.path.join(project.root, LICENSE_FILE))
    assert os.path.exists(os.path.join(project.root, GITIGNORE_FILE))
    assert os.path.exists(os.path.join(project.root, PYPROJECT_FILE))
    assert os.path.exists(os.path.join(project.root, VSCODE_DIR))
    assert os.path.exists(os.path.join(project.root, VSCODE_DIR, VSCODE_FILE))


@pytest.mark.depends(on=['test_create_structure'])
def test_install(project):
    pack_req = 'requests>=2.0.0,<3.0.0'
    for s in project.install([pack_req]):
        print(s)
    packages = [Package(p) for p in project.config['project']['dependencies']]
    assert Package(pack_req) in packages

    pack_pyt = 'pytest>=7.1.0'
    for s in project.install([pack_pyt], 'test'):
        print(s)
    packages = [
        Package(p) for p in project.config['project']['optional-dependencies']['test']
    ]
    assert Package(pack_pyt) in packages

    packages = [Package(p) for p in project.pip('freeze').splitlines()]
    assert Package(pack_req) in packages
    assert Package(pack_pyt) in packages


@pytest.mark.depends(on=['test_install'])
def test_freeze(project):
    pack_req = 'requests>=2.0.0,<3.0.0'
    req_file = REQUIREMENTS_FILE.format(group='')
    for s in project.freeze():
        print(s)
    assert os.path.isfile(os.path.join(project.root, req_file))

    with open(os.path.join(project.root, req_file)) as f:
        packages = [Package(p) for p in f.read().splitlines()]
    assert Package(pack_req) in packages


@pytest.mark.depends(on=['test_freeze'])
def test_uninstall(project):
    pack_req = 'requests>=2.0.0,<3.0.0'
    for s in project.uninstall([pack_req]):
        print(s)
    packages = [Package(p) for p in project.config['project']['dependencies']]
    assert Package(pack_req) not in packages

    packages = [Package(p) for p in project.pip('freeze').splitlines()]
    assert Package(pack_req) not in packages


if __name__ == '__main__':
    pytest.main(['-s', '-q'])
