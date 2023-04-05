from setuptools import find_packages, setup


setup(name="ep_report_generator",
      version="0.1.9",
      description="Library for generating reports for board objects from epcore.elements library",
      url="https://github.com/EPC-MSU/ep_report_generator",
      author="EPC MSU",
      author_email="info@physlab.ru",
      packages=find_packages(),
      python_requires=">=3.6, <=3.9.13",
      install_requires=[
          "Mako==1.1.5",
          "matplotlib",
          "numpy==1.18.1",
          "Pillow==8.0.1",
          "PyQt5>=5.8.2, <=5.15.2",
          "PyQt5-stubs",
          # "epcore @ hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/epcore#egg=epcore",
          # "ivviewer @ hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/ivviewer#egg=ivviewer",
      ],
      dependency_links=[
          # "hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/epcore#egg=epcore",
          # "hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/ivviewer#egg=ivviewer",
      ],
      package_data={"report_templates": ["*"]},
      )
