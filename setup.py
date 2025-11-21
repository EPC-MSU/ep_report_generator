from setuptools import find_packages, setup


setup(name="ep_report_generator",
      version="0.1.18",
      description="Library for generating reports for board objects from epcore.elements library",
      url="https://github.com/EPC-MSU/ep_report_generator",
      author="EPC MSU",
      author_email="info@physlab.ru",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=[
          "Mako==1.1.5",
          "matplotlib",
          "numpy",
          "Pillow",
          "PyQt5",
          "PyQt5",
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
