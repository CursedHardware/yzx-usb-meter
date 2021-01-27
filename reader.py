#!/usr/bin/env python
import csv
import curses
import math
import struct
import sys
from argparse import ArgumentParser, Namespace
from dataclasses import dataclass, asdict
from datetime import timedelta
from decimal import Decimal
from typing import Union, BinaryIO, Iterator

from serial import Serial


@dataclass
class Report:
    volt: Decimal
    amp: Decimal
    watt: Decimal
    a_h: Decimal
    w_h: Decimal
    delta: timedelta
    data_n: Decimal
    data_p: Decimal

    # noinspection SpellCheckingInspection
    def __init__(self, block: bytes):
        values = struct.unpack_from("<iiIIIHH", block, 3)
        values = [
            Decimal(value) / base
            for value, base in zip(
                values, [10000, 10000, 10000, 10000, 100, 1000, 1000]
            )
        ]
        self.volt = Decimal(values[0])
        self.amp = Decimal(values[1])
        self.watt = self.volt * self.amp
        self.a_h = Decimal(values[2])
        self.w_h = Decimal(values[3])
        self.delta = timedelta(seconds=float(values[4]))
        self.data_n = Decimal(values[5])
        self.data_p = Decimal(values[6])


def trace_report(session: BinaryIO) -> Iterator[Report]:
    header = bytes.fromhex("AB0006")
    while True:
        block = session.read(28)
        if block[:3] != header:
            continue
        yield Report(block)


def open_port(space: Namespace) -> Union[Serial, Serial, Serial, Serial]:
    baud_rate = 115200
    if space.bluetooth:
        baud_rate = 9600
    return Serial(space.device, baud_rate)


def make_report(port: BinaryIO):
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=["volt", "amp", "watt", "a_h", "w_h", "delta", "data_n", "data_p",],
    )
    writer.writeheader()
    for report in trace_report(port):
        row = asdict(report)
        row["delta"] = math.ceil(row["delta"].total_seconds())
        writer.writerow(row)


# noinspection PyUnusedLocal,PyProtectedMember,SpellCheckingInspection
def make_curses(stdscr, port: BinaryIO):
    def add_unit(value: Decimal, suffix: str) -> str:
        for unit in ["", "k"]:
            if abs(value) < 1000:
                return "{} {}{}".format(value, unit, suffix)
            value /= 1000

    for report in trace_report(port):
        stdscr.clear()
        stdscr.addstr(0, 0, f" Volt: {add_unit(report.volt, 'V')}")
        stdscr.addstr(1, 0, f"  Amp: {add_unit(report.amp, 'A')}")
        stdscr.addstr(2, 0, f" Watt: {add_unit(report.watt, 'W')}")
        stdscr.addstr(3, 0, f"  A·h: {add_unit(report.a_h, 'A·h')}")
        stdscr.addstr(4, 0, f"  W·h: {add_unit(report.w_h, 'W·h')}")
        stdscr.addstr(5, 0, f"Delta: {report.delta}")
        stdscr.addstr(6, 0, f"   D-: {add_unit(report.data_n, 'V')}")
        stdscr.addstr(7, 0, f"   D+: {add_unit(report.data_p, 'V')}")
        stdscr.refresh()


# noinspection SpellCheckingInspection
def main():
    parser = ArgumentParser()
    parser.add_argument("--device", dest="device", type=str)
    parser.add_argument("--bluetooth", dest="bluetooth", action="store_true")
    parser.add_argument("--curses", dest="curses", action="store_true")
    args = parser.parse_args()
    with open_port(args) as port:
        if args.curses:
            curses.wrapper(make_curses, port=port)
        else:
            make_report(port)


if __name__ == "__main__":
    main()
