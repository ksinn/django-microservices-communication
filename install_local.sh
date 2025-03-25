pip uninstall -y services_communication && python setup.py sdist && pip install dist/services_communication-*.tar.gz

rm -rf build/* && rm -rf dist/* && python -m build
twine upload dist/*
