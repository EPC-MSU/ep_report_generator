import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt


class Analyzer:
    """
    Class for analyzing the distribution of time spent generating reports.
    """

    LABELS: Dict[str, str] = {"DRAW BOARD WITH PINS": "Плата с пинами",
                              "DRAW IVC FOR PIN": "ВАХи на пинах",
                              "DRAW FAULT HISTOGRAM": "Гистограмма неисправностей",
                              "DRAW PIN": "Пины",
                              "GENERATE REPORT": "Генерация отчета",
                              "SAVE BOARD": "Плата"}

    def __init__(self) -> None:
        self._times: Dict[str, Any] = {"DRAW BOARD WITH PINS": [],
                                       "DRAW IVC FOR PIN": [],
                                       "DRAW FAULT HISTOGRAM": [],
                                       "DRAW PIN": [],
                                       "GENERATE REPORT": [],
                                       "SAVE BOARD": []}
        self._total_time: float = None
        self._total_time_from_log = None
        self._total_times: Dict[str, float] = dict()

    def _analyze(self, lines: List[str]) -> None:
        """
        :param lines: list of messages to be analyzed.
        """

        start_time, finish_time = None, None
        for line in lines:
            if "Board drawing..." in line:
                start_time = self._get_datetime(line)
            elif "Generating a report..." in line:
                finish_time = self._get_datetime(line)
            elif "[TIME_SPENT]" in line:
                self._analyze_time(line)

        self._sum_times()

        if self._total_time is not None:
            print(f"Total time from analysis: {self._total_time:.3f} sec")
        if None not in (start_time, finish_time):
            self._total_time_from_log = finish_time - start_time
            print(f"Total time from log file: {self._total_time_from_log.seconds} sec")

    def _analyze_time(self, line: str) -> None:
        """
        :param line: message to be analyzed.
        """

        for key in self._times:
            if f"'{key}'" in line:
                self._times[key].append(self._get_time(line))
                break

    @staticmethod
    def _get_datetime(line: str) -> Optional[datetime]:
        """
        :param line: a string from which to get the time and date.
        :return: date and time object.
        """

        result = re.match(r"^\[(?P<time>\d+-\d+-\d+ \d+:\d+:\d+) INFO\] .*$", line)
        if result:
            return datetime.strptime(result["time"], "%Y-%m-%d %H:%M:%S")
        return None

    @staticmethod
    def _get_time(line: str) -> Optional[float]:
        """
        :param line: a string from which to get spent time in sec.
        :return: time in sec.
        """

        result = re.match(r"^.*: (?P<time>\d+\.\d+) sec$", line)
        if result:
            return float(result["time"])
        return None

    def _plot(self) -> None:
        _, ax = plt.subplots()
        labels = []
        values = []
        for key, value in self._total_times.items():
            if value > 0:
                labels.append(f"{Analyzer.LABELS[key]} ({len(self._times[key])} шт.)")
                values.append(value)
        if self._total_time_from_log.seconds > self._total_time:
            total_time = self._total_time_from_log.seconds
            labels.append("Остальное")
            values.append(self._total_time_from_log.seconds - self._total_time)
        else:
            total_time = self._total_time

        wedges, _, autotexts = ax.pie(values, labels=labels, textprops=dict(color="w"),
                                      autopct=lambda x: f"{x:.2f}%\n{x * total_time / 100:.3f} сек")
        ax.set_title(f"Полное затраченное время {self._total_time_from_log.seconds} сек")
        ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.setp(autotexts, size=8)
        plt.show()

    @staticmethod
    def _read_log_file(file_name: str) -> List[str]:
        """
        :param file_name: file name with report generator logs.
        :return: list of messages from file.
        """

        with open(file_name, "r", encoding="utf-8") as file:
            content = file.read()
        return content.split("\n")

    def _sum_times(self) -> None:
        for key, values in self._times.items():
            self._total_times[key] = sum(values)
        self._total_time = sum(self._total_times.values())

    def run(self, log_file: str) -> None:
        lines = self._read_log_file(log_file)
        self._analyze(lines)
        self._plot()
