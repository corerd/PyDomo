#!/usr/bin/env python3
'''
Reading and Writing CSV Files in Python
Link: https://realpython.com/python-csv/

Plotting multiple Y values against multiple X values which are different timestamps
Link: https://stackoverflow.com/a/24815396

How to show date and time on x axis in matplotlib
Link: https://stackoverflow.com/a/32973263
'''
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from os import path
from datetime import datetime
from csv import DictReader as csv_dict


def templot(log_file_name, plot_file_path, plot_day=None):
    plot_title = 'Temperature plot'
    if plot_day is not None:
        print('Plot temperature of {} from file {}'.format(plot_day, log_file_name))
        search_date = datetime.strptime(plot_day, '%Y-%m-%d').date()
        plot_file_path, plot_file_ext = path.splitext(plot_file_path)
        plot_file_path = '{root}_{day}{ext}'.format( root=plot_file_path,
                                                     ext=plot_file_ext,
                                                     day=plot_day )
        plot_title = plot_title + ' of {}'.format(plot_day)
    else:
        # Plot full temperature history
        print('Plot temperature from file {}'.format(log_file_name))
    tempBySvc = {}
    with open(log_file_name, mode='r') as csv_file:
        csv_fields = ['date_time', 'log_type', 'desc', 'service', 'temp']
        for log_item in csv_dict(csv_file, fieldnames=csv_fields, delimiter=';'):
            if log_item['desc'] != 'ext temp':
                continue
            date_time = datetime.strptime(log_item["date_time"], '%Y-%m-%d %H:%M:%S,%f')
            if plot_day is not None:
                if date_time.date() != search_date:
                    continue
            svc = log_item["service"]
            if svc not in tempBySvc:
                # service doesn't exist
                # create a new item
                tempBySvc[svc] = ([], [])  # (date_time_list, temp_list)
            if log_item["temp"] == '-':
                # get last temperature from service list
                try:
                    current_temp = tempBySvc[svc][1][-1]
                except IndexError:
                    # the list is empty
                    current_temp = 0.0
            else:
                current_temp = float(log_item["temp"])
            tempBySvc[svc][0].append(date_time)
            tempBySvc[svc][1].append(current_temp)

    fig, ax = plt.subplots()
    fig.autofmt_xdate()
    xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
    ax.xaxis.set_major_formatter(xfmt)

    color_idx = 0
    for svc_name in tempBySvc:
        color_str = 'C{}'.format(color_idx)
        color_idx = (color_idx + 1) % 9
        ax.plot( tempBySvc[svc_name][0], tempBySvc[svc_name][1],
                    color_str, label=svc_name )

    ax.set(ylabel='C degrees', title=plot_title)
    ax.grid()
    ax.legend()
    fig.savefig(plot_file_path)
    print('Temperature plot saved in', plot_file_path)


def main():
    log_file_name = 'boilerctrl-log.txt'
    plot_file_name = 'templot.png'
    working_dir = path.dirname(path.abspath(__file__))
    log_file_path = path.join(working_dir, log_file_name)
    plot_file_path = path.join(working_dir, plot_file_name)
    templot(log_file_path, plot_file_path)
    templot(log_file_path, plot_file_path, plot_day='2019-01-10')
    return 0


if __name__ == "__main__":
    exit(main())
