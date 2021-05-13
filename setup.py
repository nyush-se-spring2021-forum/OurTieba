from setuptools import find_packages, setup

setup(
    name='ourtieba',
    version='0.1-alpha',
    packages=find_packages(),
    license='MIT',
    description='simple blog implementation',
    url='https://github.com/nyush-se-spring2021-forum/OurTieba',
    download_url='https://github.com/nyush-se-spring2021-forum/OurTieba/archive/refs/tags/v0.1-alpha.tar.gzz',
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
