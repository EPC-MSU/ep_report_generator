<%def name="create_component_table(pins_info)">
    % if len(pins_info) == 0:
        <% return "" %>
    % endif

    <table id="report" cellspacing="0" cellpadding="0">
        <thead>
            <tr>
                <th class="column_name"><span>Имя</span></th>
            % if board_img_width is not None:
                <th class="column_image"><span>Компонент</span></th>
            % endif
                <th class="column_plot"><span>ВАХ</span></th>
            </tr>
        </thead>
        <tbody>
        <%
            prev_element_index = None
        %>
        % for pin in pins_info:
            % if pin.element_index != prev_element_index:
            <%
                prev_element_index = pin.element_index
            %>
            <tr>
                <td class="element_name" colspan="3">
                    <h2>#${pin.element_index} - ${pin.element_name}</h2>
                </td>
            </tr>
            % endif
            % if pin.measurements or board_img_width is not None:
            <tr>
                <td class="align_left">
                    <a class="anchor" id="top" name="point_${pin.x}_${pin.y}"></a>
                    <span>#${pin.total_pin_index}</span><br>
                    <span>Название элемента: ${pin.element_name}</span><br>
                    <span>Индекс элемента: ${pin.element_index}</span><br>
                    <span>Индекс пина: ${pin.pin_index}</span><br>
                % if mm_per_px:
                    <span>X = ${round(pin.x * mm_per_px, 2)} мм</span><br>
                    <span>Y = ${round(pin.y * mm_per_px, 2)} мм</span><br>
                % else:
                    <span>X = ${round(pin.x, 2)} пк</span><br>
                    <span>Y = ${round(pin.y, 2)} пк</span><br>
                % endif
                % if pin.score is not None:
                    <span>score = ${round(pin.score, 2)}%}</span><br>
                % endif
                % if pin.multiplexer_output:
                    <button class="collapsible" onclick="handle_click(this)">Выход мультиплексора</button>
                    <div class="hidden_options">
                        <span>Номер модуля = ${pin.multiplexer_output.module_number}</span><br>
                        <span>Номер канала = ${pin.multiplexer_output.channel_number}</span><br>
                    </div><br>
                % endif
                % if pin.measurements:
                    <button class="collapsible" onclick="handle_click(this)">Параметры измерения</button>
                    <div class="hidden_options">
                        <span>Частота = ${pin.measurements[0].settings.probe_signal_frequency} Гц</span><br>
                        <span>Напряжение = ${pin.measurements[0].settings.max_voltage} В</span><br>
                        <span>Внутреннее сопротивление = ${pin.measurements[0].settings.internal_resistance} Ом</span><br>
                    </div><br>
                    <%
                        comments = [measurement.comment for measurement in pin.measurements if measurement.comment]
                        comment = "<br>".join(comments)
                    %>
                    % if comment:
                    <button class="collapsible" onclick="handle_click(this)">Комментарий к измерению</button>
                    <div class="hidden_options">
                        <span>${comment}</span>
                    </div><br>
                    % endif
                    <%
                        legend_for_iv_img = ""
                        for measurement in pin.measurements:
                            if measurement.is_reference:
                                legend_for_iv_img += '<font color="#00f">ВАХ эталона</font>\n'
                            else:
                                legend_for_iv_img += '<font color="#f00">Тестовая (текущая) ВАХ</font>\n'
                    %>
                    <button class="collapsible" onclick="handle_click(this)">Легенда ВАХ</button>
                    <div class="hidden_options">
                        <span style="white-space: pre-line">${legend_for_iv_img}</span>
                    </div><br>
                % endif
                % if pin.comment:
                    <button class="collapsible" onclick="handle_click(this)">Комментарий к пину</button>
                    <div class="hidden_options">
                        <span>${pin.comment}</span>
                    </div>
                % endif
                </td>
                % if board_img_width is not None:
                <td>
                    <a class="img_pin">
                        <canvas data-pin-data="${pin.x},${pin.y},${pin.pin_type}"></canvas>
                        <span>
                            <img src="static/img/board_clear.jpeg" width="300px" style="position:fixed; top:50px; left:50px">
                                <div class="pin" style="top:${50 + pin.y * 300 / board_img_width - 2}px; left:${50 + pin.x * 300 / board_img_width - 2}px;"></div>
                            </img>
                        </span>
                    </a>
                </td>
                % endif
                <td>
                % if pin.measurements:
                    <img src="static/img/${pin.element_index}_${pin.pin_index}_iv.png" height="${pin_img_size}" alt="Изображение ВАХ" title="${legend_for_iv_img}">
                % else:
                    <span>ВАХ нет</span>
                % endif
                </td>
            </tr>
            % endif
        % endfor
        </tbody>
    </table>
</%def>


<%def name="create_general_info_table(other_report_file, other_report_name, full_report, board_image_file, pins_info)">
    <table id="general_info" cellspacing="0" cellpadding="0">
        <tbody>
            <tr>
            % if fault_histogram:
                <th colspan="2">
            % else:
                <th>
            % endif
                    <h2>Общая информация</h2>
                </th>
            </tr>

            <tr>
                <td class="align_left">
                % if app_name:
                    <span>Диагностическая система: ${app_name}</span><br>
                % endif
                % if app_version:
                    <span>Версия: ${app_version}</span><br>
                % endif
                    <span>Дата: ${date}</span><br>
                % if computer:
                    <span>Рабочая станция: ${computer}</span><br>
                % endif
                % if operating_system:
                    <span>Операционная система: ${operating_system}</span><br>
                % endif
                % if test_duration:
                    <span>Длительность тестирования: ${test_duration}</span><br>
                % endif
                % if pcb_name:
                    <span>Название платы: ${pcb_name}</span><br>
                % endif
                ${write_component_info(full_report)}
                % if threshold_score:
                    <span>Пороговое значение score: ${round(threshold_score, 2)}%</span><br>
                % endif
                % if pcb_comment:
                    <span>Комментарий: ${pcb_comment}</span><br>
                % endif
                    <span>HTML: v4.01</span><br>
                    <span><a href="${other_report_file}" target="_blank">${other_report_name}</a></span><br>
                % if board_img_width:
                    <span><a href="full_img.html" target="_blank">Изображение платы</a></span><br>
                % endif
                </td>
            % if fault_histogram:
                <td>
                    <img src="static/fault_histogram.jpeg" alt="Гистограмма неисправностей" title="Гистограмма неисправностей" width="600px">
                </td>
            % endif
            </tr>

        % if board_img_width is not None:
            <tr>
            % if fault_histogram:
                <th colspan="2">
            % else:
                <th>
            % endif
                    <h2>Карта неисправных точек тестирования</h2>
                </th>
            </tr>

            <tr>
            % if fault_histogram:
                <td colspan="2">
            % else:
                <td>
            % endif
                    <img id="board" src="static/img/${board_image_file}" usemap="#map" alt="Карта неисправных точек тестирования" title="Карта неисправных точек тестирования">
                    <p>
                        <map name="map">
                        % for pin in pins_info:
                            <area shape="circle" coords="${pin.x},${pin.y},${pin_radius}" href="#point_${pin.x}_${pin.y}" alt="">
                        % endfor
                        </map>
                    </p>
                    <img id="board_clear" src="static/img/board_clear.jpeg" alt="Изображение платы" title="Изображение платы" style="display: none;">
                </td>
            </tr>
        % endif
        </tbody>
    </table>
</%def>


<%def name="write_component_info(full_report)">
    % if full_report:
        <span>Количество компонентов: ${elements_number}</span><br>
        <span>Количество точек тестирования: ${pins_number}</span><br>
    % else:
        <span>Количество неисправных компонентов/количество компонентов: ${bad_elements_number}/${elements_number}</span><br>
        <%
            bad_elements_portion = 0 if not elements_number else round(100 * bad_elements_number / elements_number, 2)
        %>
        <span>Доля неисправных компонентов: ${bad_elements_portion}%</span><br>
        <span>Количество неисправных точек тестирования/количество точек тестирования: ${bad_pins_number}/${pins_number}</span><br>
        <%
            bad_pins_portion = 0 if not pins_number else round(100 * bad_pins_number / pins_number, 2)
        %>
        <span>Доля неисправных точек тестирования: ${bad_pins_portion}%</span><br>
    % endif
</%def>
