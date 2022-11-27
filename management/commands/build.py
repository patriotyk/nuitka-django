import os
import imp
import subprocess
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings


DYNAMIC_IMPORTS=[
    'INSTALLED_APPS',
    'MIDDLEWARE',
    'ROOT_URLCONF',
    'STATICFILES_STORAGE',
    'SERIALIZATION_MODULES',
    'AUTHENTICATION_BACKENDS'
]


def list_packages():
    packages = set()
    for di in DYNAMIC_IMPORTS:
        imports = getattr(settings, di, [])
        if imports:
            if type(imports) == list:
                for im in imports:
                    packages.add(im.split('.')[0])
            else:
                packages.add(imports.split('.')[0])
    return packages


class Command(BaseCommand):
    help = 'Build django application to binary'

    # def __init__(self, *args, **kwargs):
    #     super(Command, self).__init__(*args, **kwargs)
    #     self.themes = None

    def add_arguments(self, parser):
        parser.add_argument('app', nargs='?', type=str, 
                            help='Application entrypoint', default='gunicorn')
    

    def copy_data(self, module, dist):
        _, path, _ = imp.find_module(module)
        patterns = list(Path(path).rglob('locale'))
        patterns.extend(Path(path).rglob('templates'))

        for p in patterns:
            if p.is_dir():
                copy_to = os.path.join(dist, p.relative_to(os.path.dirname(path)))
                print(p.absolute(), copy_to)
                shutil.copytree(p.absolute(),  copy_to, dirs_exist_ok=True, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
          
    
    def handle(self, *args, **options):
        paths = settings.ROOT_URLCONF.split('.')[:-1]
        print(os.path.realpath('/'.join(paths)))
        packages = list_packages()
        out_dir = 'app_dist'
        for p in packages:
            self.copy_data(p, out_dir)
        
        from_static = os.path.realpath(settings.STATIC_ROOT)
        to_static = os.path.join(out_dir, os.path.basename(from_static))
        print(from_static, to_static)
        shutil.copytree(from_static, to_static, dirs_exist_ok=True)
  
        
        nuitka_base_args = ['python3', '-m nuitka',  '--show-progress', '--show-scons', '--remove-output', f'--output-dir="{out_dir}"']
        nuitka_args = nuitka_base_args + ['--module',]
        nuitka_args.extend([f'--include-package="{p}"'  for p in packages ])
        
        nuitka_args.append(os.path.realpath('/'.join(paths)))
        # subprocess.run(' '.join(nuitka_args), shell=True)

        nuitka_gunicorn_args = nuitka_base_args + ['--standalone', '--onefile', '--include-package=gunicorn',  '--include-package=gunicorn.app', '--include-package=gevent']
        _, npath, _ = imp.find_module('nuitka_django')
        gunicorn_entrypoint = os.path.join(npath, 'entrypoints/gunicorn.py')
        subprocess.run((' '.join(nuitka_gunicorn_args))+f'  {gunicorn_entrypoint}', shell=True)
        #shutil.copytree('gunicorn.dist', out_dir, dirs_exist_ok=True)




        
