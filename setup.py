from distutils.util import convert_path
from setuptools import find_packages, setup


data = {}
version_path = convert_path("report_generator/version.py")
with open(version_path) as version_file:
    exec(version_file.read(), data)


setup(name="ep_report_generator",
      version=data["VERSION"],
      description="Library for generating reports for board objects from epcore.elements library",
      url="https://github.com/EPC-MSU/ep_report_generator",
      author="EPC MSU",
      author_email="info@physlab.ru",
      packages=find_packages(),
      python_requires=">=3.6, <=3.9.13",
      install_requires=[
          "Mako==1.1.5",
          "matplotlib<=3.3.0",
          "numpy==1.18.1",
          "Pillow==8.0.1",
          "PyQt5>=5.8.2, <=5.15.2",
          "PyQt5-stubs",
          # "git+https://github.com/EPC-MSU/epcore#egg=epcore",
          # "git+https://github.com/EPC-MSU/ivviewer#egg=ivviewer",
      ],
      dependency_links=[
          # "git+https://github.com/EPC-MSU/epcore#egg=epcore",
          # "git+https://github.com/EPC-MSU/ivviewer#egg=ivviewer",
      ],
      package_data={"report_generator": ["locales/en/LC_MESSAGES/translation.mo",
                                         "locales/en/LC_MESSAGES/translation.po"],
                    "report_templates": ["*"]},
      )
