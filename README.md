# ep_report_generator
Библиотека для создания отчетов для плат типа **Board** из библиотеки **epcore.elements**.

## Применение

1. Установите библиотеки **ep_report_generator**, **epcore** и **ivviewer**:

   ```bash
   python -m pip install --upgrade pip
   python -m pip install git+https://github.com/EPC-MSU/ep_report_generator
   python -m pip install git+https://github.com/EPC-MSU/epcore@dev-0.1 git+https://github.com/EPC-MSU/ivviewer@dev-0.1
   ```

2. В вашем python-скрипте импортируйте из библиотеки следующие классы:

   ```python
   from report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator, ScalingTypes
   ```

3. С помощью библиотеки **epcore.elements** создайте плату типа **Board**, для которой будет сгенерирован отчет:

   ```python
   board = функция_которая_каким-то_образом_создает_плату()
   ```
   
4. Библиотека **ep_report_generator** может создать отчет как для всей платы целиком, так и для некоторых элементов и/или пинов на плате. Если вам нужно создать отчет только для некоторых элементов и/или пинов на плате, каким-либо образом определите индексы требуемых элементов и/или пинов.

   С определением индексов требуемых элементов не должно возникнуть проблем: в плате типа **Board** имеется атрибут **elements**, представляющий собой список элементов платы. Вам нужно определить индексы требуемых элементов в этом списке. Каждый элемент - это объект типа **Element**, у которого есть атрибут **pins** - список пинов на элементе. Индексы требуемых пинов нужно определить относительно одного общего списка пинов, объединяющего все пины на плате. Список всех пинов на плате получается последовательным объединением списков пинов на каждом элементе платы.

5. Создайте словарь-конфиг, по которому будет создан отчет. Для задания полей словаря-конфига используйте класс **ConfigAttributes**. Для задания объектов, которые должны быть включены в отчет, используйте класс **ObjectsForReport**. Для выбора типа масштабирования графиков ВАХ используйте класс **ScalingTypes**. Пример словаря-конфига:

   ```python
   config = {ConfigAttributes.BOARD: board,
   		  ConfigAttributes.DIRECTORY: путь к папке, в которой нужно сохранить отчет,
             ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: нужно ли создать отчет для всей платы целиком True или False,
                                        ObjectsForReport.ELEMENT: [индексы элементов, которые должны быть включены в отчет],
                                        ObjectsForReport.PIN: [индексы пинов, которые должны быть включены в отчет]},
             ConfigAttributes.THRESHOLD_SCORE: пороговое значение score,
             ConfigAttributes.PIN_SIZE: высота изображения пина в пикселях для отчета,
             ConfigAttributes.OPEN_REPORT_AT_FINISH: если True, то по завершении создания отчета отчет будет открыт,
             ConfigAttributes.REPORTS_TO_OPEN: список отчетов, которые нужно открыть в браузере по завершении создания отчетов,
             ConfigAttributes.APP_NAME: название приложения (например, EyePoint P10), которое использует генератор отчетов,
             ConfigAttributes.APP_VERSION: версия приложения, которое использует генератор отчетов,
             ConfigAttributes.TEST_DURATION: длительность тестирования (тип значения datetime.timedelta),
             ConfigAttributes.NOISE_AMPLITUDES: список с амлитудами шумов графиков ВАХ,
             ConfigAttributes.SCALING_TYPE: тип масштабирования графиков ВАХ (например, ScalingTypes.EYEPOINT_P10),
             ConfigAttributes.USER_DEFINED_SCALES: список с масштабами графиков ВАХ, если ConfigAttributes.SCALING_TYPE == ScalingTypes.USER_DEFINED,
             ConfigAttributes.ENGLISH: если True, то отчет будет создан на английском языке}
   ```
   
6. Создайте объект типа **ReportGenerator** и запустите его, передав в качестве аргумента словарь-конфиг:

   ```python
   report_generator = ReportGenerator()
   report_generator.run(config)
   ```

7. После окончания работы в указанной вами папке появится отчет.

## Запуск примера

1. Склонируйте репозиторий и перейдите в папку репозитория **ep_report_generator**:

   ```bash
   git clone https://github.com/EPC-MSU/ep_report_generator
   cd ep_report_generator
   ```

2. Установите необходимые зависимости, перейдя в папку **scripts** и выполнив скрипт:

   - **install.bat**, если Вы работаете в *Windows*;

   - **install.sh**, если Вы работаете в *Linux*:

     ```bash
     bash install.sh
     ```

3. Перейдите в папку **scripts** и запустите скрипт:

   - **run_example.bat**, если Вы работаете в *Windows*;

   - **run_example.sh**, если Вы работаете в *Linux*:

     ```bash
     bash run_example.sh
     ```

   В папке репозитория появится папка **examples**, в которой будут находиться четыре новые папки **report_for_empty_board**, **report_for_manual_board**, **report_for_manual_board_with_user_defined_scales** и **report_for_p10_board с отчетами для соответствующих плат.

## Запуск тестов

1. Установите необходимые зависимости, перейдя в папку **scripts** и выполнив скрипт:

   - **install.bat**, если Вы работаете в *Windows*;

   - **install.sh**, если Вы работаете в *Linux*:

     ```bash
     bash install.sh
     ```

2. Перейдите в папку **scripts** и запустите скрипт:

   - **run_tests.bat**, если Вы работаете в *Windows*;

   - **run_tests.sh**, если Вы работаете в *Linux*:

     ```bash
     bash run_tests.sh
     ```

## Выпуск релиза

1. Задайте версию X.X.X выпускаемого релиза в файле **report_generator/version.py**.
2. Запушьте соответствующий коммит.
3. Повесьте тег vX.X.X на коммит.

## Добавление перевода

1. Добавьте перевод в файл **translation/locales/en/LC_MESSAGES/translation.po**.

2. В Ubuntu 18 скомпилируйте бинарный файл с переводом. Для этого перейдите в папку **translations/locales/en/LC_MESSAGES** и выполните команду:

   ```bash
   msgfmt ./translation.po -o ./translation.mo
   ```

3. Добавьте новый бинарный файл в репозиторий и запушьте изменения.
