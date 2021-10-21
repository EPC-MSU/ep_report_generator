from setuptools import find_packages, setup


setup(name="ep_report_generator",
      version="0.1.0",
      description="Library for generating reports for board objects from epcore.elements library",
      long_description=open("README.md", "r", encoding="utf-8").read(),
      long_description_content_type="text/markdown",
      url="https://github.com/EPC-MSU/ep_report_generator",
      author="EPC MSU",
      author_email="info@physlab.ru",
      packages=find_packages(),
      install_requires=[
          "Mako==1.1.5",
          "matplotlib==3.3.4",
          "numpy==1.18.1",
          "Pillow==8.0.1",
          "PyQt5<=5.15.0",
          "PyQt5-stubs",
          "epcore @ hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/epcore@dev-0.1#egg=epcore",
          "ivviewer @ hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/ivviewer@dev-0.1#egg=ivviewer",
      ],
      dependency_links=[
          "hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/epcore@dev-0.1#egg=epcore",
          "hg+https://anonymous:anonymous@hg.ximc.ru/eyepoint/ivviewer@dev-0.1#egg=ivviewer",
      ],
      package_data={"report_templates": ["*"]},
      python_requires=">=3.6",
      )
