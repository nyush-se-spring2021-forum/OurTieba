from setuptools import find_packages, setup

setup(
    name='ourtieba',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'sqlalchemy',
        'flask-moment',
        'flask_apscheduler',
        'requests_html'
    ]
)
