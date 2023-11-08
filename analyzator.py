import re
from datetime import datetime
from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt


class Analyzer:

    def __init__(self) -> None:
        self._times: Dict[str, Any] = {"draw_board_with_pins": [],
                                       "ivcs": [],
                                       "pins": []}

    def _analyze(self, lines: List[str]) -> None:
        start_time, finish_time = None, None
        for line in lines:
            if "Board drawing..." in line:
                start_time = self._get_datetime(line)
            elif "Generating a report..." in line:
                finish_time = self._get_datetime(line)
            elif "[TIME]" in line:
                self._analyze_time(line)

        self._sum_times()
        total = sum(value for key, value in self._times.items() if "total" in key)
        print(total)
        if None not in (start_time, finish_time):
            print(finish_time - start_time)

    def _analyze_time(self, line: str) -> None:
        if "'DRAW BOARD'" in line:
            self._times["total_draw_board"] = self._get_time(line)
        elif "'DRAW BOARD WITH PINS'" in line:
            self._times["draw_board_with_pins"].append(self._get_time(line))
        elif "'DRAW IVC FOR PIN'" in line:
            self._times["ivcs"].append(self._get_time(line))
        elif "'DRAW PIN'" in line:
            self._times["pins"].append(self._get_time(line))

    @staticmethod
    def _get_datetime(line: str) -> Optional[datetime]:
        result = re.match(r"^\[(?P<time>\d+-\d+-\d+ \d+:\d+:\d+) INFO\] .*$", line)
        if result:
            return datetime.strptime(result["time"], "%Y-%m-%d %H:%M:%S")
        return None

    @staticmethod
    def _get_time(line: str) -> Optional[float]:
        result = re.match(r"^.*: (?P<time>\d+\.\d+) sec$", line)
        if result:
            return float(result["time"])
        return None

    def _plot(self) -> None:
        fig, ax = plt.subplots()
        values = []
        labels = []
        total = sum(value for key, value in self._times.items() if "total" in key)
        for key, value in self._times.items():
            if "total" in key:
                values.append(value)
                if key == "total_draw_board":
                    label = "Плата"
                elif key == "total_board_with_pins":
                    label = f"Плата с пинами ({len(self._times['draw_board_with_pins'])} шт.)"
                elif key == "total_ivcs":
                    label = f"ВАХи на пинах ({len(self._times['ivcs'])} шт.)"
                else:
                    label = f"Пины ({len(self._times['pins'])} шт.)"
                labels.append(label)
        ax.pie(values, labels=labels, autopct=lambda x: f"{x * total / 100:.1f}")
        plt.show()

    @staticmethod
    def _read_log_file(file_name: str) -> List[str]:
        with open(file_name, "r", encoding="utf-8") as file:
            content = file.read()
        return content.split("\n")

    def _sum_times(self) -> None:
        self._times["total_ivcs"] = sum(self._times["ivcs"])
        self._times["total_pins"] = sum(self._times["pins"])
        self._times["total_board_with_pins"] = sum(self._times["draw_board_with_pins"])

    def run(self, log_file: str) -> None:
        lines = self._read_log_file(log_file)
        self._analyze(lines)
        self._plot()


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.run("log.txt")
