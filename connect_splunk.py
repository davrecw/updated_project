"""
Custom :mod:`connect_splunk` module implements :class:`ConnectToSplunk` class and static method connect.
"""
import sys
from time import sleep
import splunklib.client as client
import splunklib.results as results


class ConnectToSplunk(object):
    """
    :class:`ConnectToSplunk` declares the following constants.

    - HOST.
    - PORT.
    - USERNAME.
    - PASSWORD.

    Implements static method :func:`connect` which creates and returns a service instance.
    """

    HOST="splunk.fetchtv.com.au"
    PORT="8089"
    USERNAME="davidb"
    PASSWORD="3Bugcftf35"

    @staticmethod
    def connect():
        # Create a service instance to login into splunk server

        service=client.connect(
            host=ConnectToSplunk.HOST,
            port=ConnectToSplunk.PORT,
            username=ConnectToSplunk.USERNAME,
            password=ConnectToSplunk.PASSWORD)

        return service

