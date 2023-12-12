import argparse
import re
import sys
from collections import namedtuple
from datetime import datetime
from typing import Any, Dict, Generator, List, Optional, Tuple
import matplotlib.pyplot as plt
import utils as ut


class TimeAnalyzer:
    """
    Class for analyzing the distribution of time spent generating reports.
    """

    LABELS: Dict[str, str] = {"DRAW BOARD WITH PINS": "Плата с пинами",
                              "DRAW IVC FOR PIN": "ВАХи на пинах",
                              "DRAW FAULT HISTOGRAM": "Гистограмма неисправностей",
                              "DRAW PIN": "Пины",
                              "GENERATE REPORT": "Генерация отчета",
                              "SAVE BOARD": "Плата"}
    Data = namedtuple("Data", ["times", "total_times", "total_time", "total_time_from_log"])

    def _analyze(self, lines: List[str]) -> Generator["Data", None, None]:
        """
        :param lines: list of messages to be analyzed.
        :return:
        """

        start_time, finish_time, times = self._init_data()
        there_is_time = False
        for line in lines:
            if "Start report generation" in line:
                if there_is_time:
                    total_time, total_times = self._sum_times(times)
                    print(f"Total time from analysis: {total_time:.3f} sec")
                    if None not in (start_time, finish_time):
                        total_time_from_log = finish_time - start_time
                        print(f"Total time from log file: {total_time_from_log.seconds} sec")
                    else:
                        total_time_from_log = None
                    yield self.Data(times, total_times, total_time, total_time_from_log)

                start_time, finish_time, times = self._init_data()
                there_is_time = False

            if "Start report generation" in line:
                start_time = self._get_datetime(line)
            elif "The full report is saved" in line:
                finish_time = self._get_datetime(line)
            elif "[TIME_SPENT]" in line:
                there_is_time = True
                self._analyze_time(line, times)

    def _analyze_time(self, line: str, times: Dict[str, Any]) -> None:
        """
        :param line: message to be analyzed.
        """

        for key in times:
            if f"'{key}'" in line:
                times[key].append(self._get_time(line))
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

    @staticmethod
    def _init_data() -> Tuple[None, None, Dict[str, Any]]:
        times = {"DRAW BOARD WITH PINS": [],
                 "DRAW IVC FOR PIN": [],
                 "DRAW FAULT HISTOGRAM": [],
                 "DRAW PIN": [],
                 "GENERATE REPORT": [],
                 "SAVE BOARD": []}
        return None, None, times

    @staticmethod
    def _plot(time_data: "Data") -> None:
        _, ax = plt.subplots()
        labels = []
        values = []
        for key, value in time_data.total_times.items():
            if value > 0:
                labels.append(f"{TimeAnalyzer.LABELS[key]} ({len(time_data.times[key])} шт.)")
                values.append(value)

        if time_data.total_time_from_log.seconds > time_data.total_time:
            total_time = time_data.total_time_from_log.seconds
            labels.append("Остальное")
            values.append(time_data.total_time_from_log.seconds - time_data.total_time)
        else:
            total_time = time_data.total_time

        wedges, _, autotexts = ax.pie(values, labels=labels, textprops=dict(color="w"),
                                      autopct=lambda x: f"{x:.2f}%\n{x * total_time / 100:.3f} сек", normalize=True)
        ax.set_title(f"Полное затраченное время {time_data.total_time_from_log.seconds} сек")
        ax.legend(wedges, labels, loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
        plt.setp(autotexts, size=8)
        plt.show()

    @staticmethod
    def _sum_times(times: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        total_times = dict()
        for key, values in times.items():
            total_times[key] = sum(values)
        return sum(total_times.values()), total_times

    def run(self, log_file: str) -> None:
        """
        :param log_file: the name of the log file that needs to be analyzed and from which to obtain information about
        the execution time of individual operations when creating a report.
        """

        lines = ut.read_log_file(log_file)
        for time_data in self._analyze(lines):
            self._plot(time_data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log_file", help="File with logs about time spent")
    parsed_args = parser.parse_args(sys.argv[1:])

    analyzer = TimeAnalyzer()
    analyzer.run(parsed_args.log_file)
