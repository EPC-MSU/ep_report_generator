import argparse
import re
import sys
from collections import namedtuple
from typing import Dict, List
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import utils as ut


class MemoryLeakAnalyzer:

    COLORS = ["#0000CD", "#DC143C", "#008000"]
    PATTERN = re.compile(r"^\[(?P<time>\d+-\d+-\d+ \d+:\d+:\d+) INFO\] Report #(?P<index>\d+), memory = "
                         r"(?P<memory>\d+\.\d+).+$")
    ReportInfo = namedtuple("ReportInfo", ["index", "time", "memory"])

    def __init__(self) -> None:
        self._data: Dict[str, List[MemoryLeakAnalyzer.ReportInfo]] = dict()

    def _analyze(self, lines: List[str]) -> List["ReportInfo"]:
        """
        :param lines: list of messages to be analyzed.
        """

        data = []
        for line in lines:
            if "Start" in line:
                data = []
            else:
                result = MemoryLeakAnalyzer.PATTERN.match(line)
                if result:
                    index = int(result.group("index"))
                    time_ = ut.convert_to_datetime(result.group("time"))
                    memory = float(result.group("memory"))
                    data.append(self.ReportInfo(index, time_, memory))
        return data

    @staticmethod
    def _get_color(i: int) -> str:
        """
        :param i: index of the curve for which to get the color.
        :return: color.
        """

        return MemoryLeakAnalyzer.COLORS[i % len(MemoryLeakAnalyzer.COLORS)]

    def _plot(self) -> None:
        _, ax = plt.subplots()
        for i, (log_file, data) in enumerate(self._data.items()):
            indeces = [int(item.index) for item in data]
            memories = [float(item.memory) for item in data]
            ax.scatter(indeces, memories, marker="o", facecolors="none", edgecolors=self._get_color(i), label=log_file)
        plt.xlabel("Номер отчета")
        plt.ylabel("Память, MB")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.legend()
        plt.show()

    def run(self, *log_files: str) -> None:
        """
        :param log_files: list of file names with logs that needs to be analyzed and from which to obtain information
        about the memory allocated for generating reports.
        """

        self._data = dict()
        for log_file in log_files:
            lines = ut.read_log_file(log_file)
            self._data[log_file] = self._analyze(lines)
        self._plot()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log_files", nargs="+", default=[], help="Files with logs about memory used")
    parsed_args = parser.parse_args(sys.argv[1:])

    analyzer = MemoryLeakAnalyzer()
    analyzer.run(*parsed_args.log_files)
