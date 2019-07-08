#! /user/bin/env python3.5
"""
Middleware splunk command line tool.
Imported the custom :mod:`connect_splunk` and :mod:`splunk_search` modules.
"""
import argparse
import time
import sys
import re
import socket
import dateutil.parser
from time import sleep
import splunklib.client as client
import splunklib.results as results
import connect_splunk
import splunk_search


def main():
    """ 
    Command line tool accepts three positional and five optional arguments.
    The positional argument execmode only accepts the values in the given choices list.
    """
    parser = argparse.ArgumentParser()
    choices_list=['story', 'api_errors']
    parser.add_argument("execmode", help="setting the execution mode", choices=choices_list)
    parser.add_argument("startdate", help="add the start date", type=str)
    parser.add_argument("enddate", help="add the end date", type=str)
    parser.add_argument("--household", help="add household uuid", type=str)
    parser.add_argument("--api", help="add the api name", type=str)
    parser.add_argument("--splunkindex", help="add splunk index", type=str)
    parser.add_argument("--mwenv", help="add splunk mw env", type=str)
    parser.add_argument("--couchurl", help="add couch url", type=str)

    args = parser.parse_args()

    # Date parse and validation.
    try:
        start=dateutil.parser.parse(args.startdate)
        start=start.isoformat()
        end=dateutil.parser.parse(args.enddate)
        end=end.isoformat()
    except ValueError as e:
        print("Error on trying to parse start and end dates")
        print(e)
        start,end=None

    # Evaluating conditional statement. 
    if bool(start) and bool(end):

        try:
            splunk_service=connect_splunk.ConnectToSplunk.connect()  # Connect to splunk server.

            splk_search=splunk_search.SplunkSearchJob(splunk_service,start,
                                                      end,args.execmode,
                                                      args.household,args.api)  # Instantiate new object.
            search_results=splk_search.search_job(args.splunkindex,args.mwenv,
                                                  args.couchurl)  # Call the search_job method and store the results.

            if search_results:
                splk_search.print_output(search_results)  # Call the  print_output method to display the results.
            else:
                print("No results returned..!!")

        except socket.gaierror as e:
            print("Socket error on trying to connect to splunk server..!!")
            print(e)

if __name__ == "__main__":
    main()


