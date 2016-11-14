from setuptools import setup, find_packages

setup(name='camltex',
        version='0.0.9',
        description='CLI for processing embedded OCaml.',
        url='http://github.com/cs51/camltex',
        author='Sam Green',
        author_email='cs51heads@gmail.com',
        license='MIT',
        packages=find_packages(),
        install_requires=[
            'pygments',
            'pexpect',
            ],
        entry_points={
            'console_scripts': [
                'caml-tex = camltex.command_line:main'
                ]
            },
        zip_safe=False,)

