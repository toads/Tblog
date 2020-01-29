from setuptools import find_packages, setup

requires = [
    'aniso8601==8.0.0', 'APScheduler==3.6.3', 'argh==0.26.2', 'attrs==19.3.0',
    'blinker==1.4', 'Bootstrap-Flask==1.2.0', 'certifi==2019.11.28',
    'chardet==3.0.4', 'click==6.7', 'coverage==5.0.3', 'dominate==2.4.0',
    'entrypoints==0.3', 'Faker>=3.0.0', 'flake8==3.7.9', 'Flask==1.1.1',
    'Flask-APScheduler==1.11.0', 'Flask-DebugToolbar==0.10.1',
    'Flask-Login==0.4.1', 'Flask-Mail==0.9.1', 'Flask-Moment==0.9.0',
    'Flask-OAuth==0.12', 'Flask-RESTful==0.3.7', 'Flask-SQLAlchemy==2.4.1',
    'Flask-WTF==0.14.2', 'httplib2==0.15.0', 'idna==2.8',
    'importlib-metadata==1.4.0', 'importlib-resources==1.0.2',
    'inflection==0.3.1', 'itsdangerous==1.1.0', 'Jinja2==2.10.3',
    'MarkupSafe==1.1.1', 'mccabe==0.6.1', 'more-itertools==8.1.0',
    'packaging==20.0', 'pathtools==0.1.2', 'pluggy==0.13.1', 'py==1.8.1',
    'pycodestyle==2.5.0', 'pyflakes==2.1.1', 'pyparsing==2.4.6',
    'pytest==5.3.4', 'python-dateutil==2.8.1', 'python-dotenv==0.10.3',
    'pytz==2019.3', 'PyYAML==5.3', 'requests==2.22.0', 'shiv==0.1.0',
    'six==1.13.0', 'SQLAlchemy==1.3.12', 'text-unidecode==1.3',
    'tzlocal==2.0.0', 'urllib3==1.25.7', 'visitor==0.1.3', 'watchdog==0.9.0',
    'wcwidth==0.1.8', 'Werkzeug==0.16.0', 'WTForms==2.2.1', 'yapf==0.29.0',
    'zipp==2.0.0'
]

setup(name='Tblog',
      version='1.0',
      description='A mini blog',
      author='toads',
      author_email='toads@foxmail.com',
      packages=find_packages(),
      install_requires=requires,
      license='MIT')