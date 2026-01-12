from setuptools import find_packages, setup


setup(name="ep_report_generator",
      version="0.1.19",
      description="Library for generating reports for board objects from epcore.elements library",
      url="https://github.com/EPC-MSU/ep_report_generator",
      author="EPC MSU",
      author_email="info@physlab.ru",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=[
          "Mako==1.1.5",
          'matplotlib<=3.3.0; python_version=="3.6"',
          'matplotlib; python_version>"3.6"',
          'numpy==1.18.1; python_version=="3.6"',
          'numpy; python_version>"3.6"',
          'Pillow==8.0.1; python_version=="3.6"',
          'Pillow; python_version>"3.6"',
          'PyQt5>=5.8.2, <=5.15.0; python_version=="3.6"',
          'PyQt5; python_version>"3.6"',
          # "epcore @ git+https://github.com/EPC-MSU/epcore#egg=epcore",
          # "ivviewer @ git+https://github.com/EPC-MSU/ivviewer@dev-1.0#egg=ivviewer",
      ],
      package_data={"report_generator": ["locales/en/LC_MESSAGES/translation.mo",
                                         "locales/en/LC_MESSAGES/translation.po"],
                    "report_templates": ["*"]},
      )
