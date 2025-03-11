pip uninstall -y services_communication && python setup.py sdist && pip install dist/services_communication-*.tar.gz

rm -rf build/* && rm -rf dist/* && python setup.py sdist bdist_wheel
twine upload dist/*
