"""
Custom :mod:`splunk_search` module implements :class:`SplunkSearch` and :class:`SplunkSearchJob` classes.
"""
import sys
import splunklib.client as client
import splunklib.results as results
import splunklib.binding as slib
from collections import Counter
from time import sleep


class SplunkSearch(object):
    """
    :class:'SplunkSearch' class initializes the attributes service, start_date and end_date.
    Implements search method which accepts the search_query parameter.
    """

    def __init__(self,service,start_date,end_date):
        self.service=service
        self.start_date=start_date
        self.end_date=end_date
        self.job=service.jobs

    def search(self,search_query):
        """
        Trigger search job based on the search_query argument passed.
        """

        kwargs_normal_search = {"exec_mode": "blocking", "earliest_time": self.start_date, "latest_time": self.end_date}
        self.job = self.job.create(search_query, **kwargs_normal_search)

        # Return search results.
        search_results=[]
        for result in results.ResultsReader(self.job.results()):
            search_results.append(result)

        self.job.cancel()
        sys.stdout.write('\n')

        return search_results

class SplunkSearchJob(SplunkSearch):
    """ 
    :class:`SplunkSearchJob` class inherits from :class:`SplunkSearch`.
    Class attributes splunk_index,mw_env and couch_url are declared.  Initializes attributes story_mode,
    household_id and select_api.
    """

    # Declaring class attributes.
    splunk_index='mw'
    mw_env='prod_no_couchdb'
    couch_url='http://sv425-mwpp1.eq.i.fetchtv.com.au:5984'
    
    def __init__(self,service,start_date,end_date,story_mode,household_id,select_api):

        super(SplunkSearchJob,self).__init__(service,start_date,end_date)
        self.story_mode=story_mode
        self.household_id=household_id
        self.select_api=select_api
        self.search_query={}
        self.search_job_results=[]

    def search_job(self,splunk_index,mw_env,couch_url):
        """
        Method search_job accepts the parameters splunk_index,mw_env and couch_url.
        Calls the search method of parent class based on the conditional statement.
        """

        # Assign a dictionary with exec_mode as key and search query as value.
        self.search_query={"story":"search index={} env={} household_id={} api!=\"\"|table api,log_level,"\
                           "request_id,duration".format(SplunkSearchJob.splunk_index,SplunkSearchJob.mw_env,\
                           self.household_id),
                           "api_errors":"search index={} env={} log_level=ERROR api={}|table household_id".\
                           format(SplunkSearchJob.splunk_index,SplunkSearchJob.mw_env,self.select_api)}
        try:
            # Update class attributes when a new value is supplied through optional arguments.
            if splunk_index:
                SplunkSearchJob.splunk_index=splunk_index
            if mw_env:
                SplunkSearchJob.mw_env=mw_env
            if couch_url:
                SplunkSearchJob.couch_url=couch_url

            # Call search method of parent class based on the conditional statement.    
            if self.story_mode=="story" and self.household_id:
                self.search_job_results=self.search(self.search_query['story'])
            elif self.story_mode=="api_errors" and self.select_api:
                self.search_job_results=self.search(self.search_query['api_errors'])
            else:
                print("Missing optional parameter..!!")

            # Call process_results method if search results are returned from search method of parent class.    
            if self.search_job_results:
                processed_results=self.process_results(self.search_job_results)
                return processed_results               

        except slib.HTTPError as e:
            print("HTTPError on trying to do a splunk search..!!")
            print(e)

    def process_results(self,search_results):
        """
        Method process_results accepts the parameter search_results and returns the processed results.
        """

        if search_results:
            try:
                # Process and return the results for story mode.
                if self.story_mode=="story":
                    api_list = []
                    log_level_list = []
                    request_id_list = []
                    story_list = []
                    temp=[]

                    for result in search_results:
                        temp = list(result.items())
                        if temp[0][1] != "WSMessage":
                            temp_tuple = (temp[2][1], temp[1][1], temp[0][1], temp[3][1])
                            story_list.append(temp_tuple)

                            api_list.append(temp[0][1])
                            log_level_list.append(temp[1][1])
                            request_id_list.append(temp[2][1])

                    api_list = Counter(api_list)
                    log_level_list = Counter(log_level_list)
                    request_id_list = Counter(request_id_list)

                    return api_list,log_level_list,request_id_list,story_list

                # Process and return the results for api_errors mode.
                elif self.story_mode=="api_errors":
                    api_error_list=[]
                    for result in search_results:
                        temp=list(result.items())
                        api_error_list.append(temp[0][1])
                    return api_error_list

            except AttributeError as e:
                print("AttributeError on trying to process the results..!!")
                print(e)

    def print_output(self,processed_results):
        """
        Method print_output accepts the parameter processed_results and prints results onto the console.
        """       

        if processed_results:
            try:
                # Prints processed results for story mode to console.
                if self.story_mode=="story":
                    api_list,log_level_list,request_id_list,story_list=processed_results

                    print("Household: ", self.household_id)
                    print("Requests: ", len(request_id_list))
                    print()

                    for x, y in log_level_list.items():
                        print(x, y, sep=": ")
                    print()

                    for x, y in api_list.items():
                        print(x, y, sep=": ")
                    print()

                    for i in story_list:
                        for j in i:
                            print(j, end=" ")
                        print()
                    print()

                # Prints processed results for api_errors mode to console.
                if self.story_mode=="api_errors":
                    api_error_list=processed_results

                    print()
                    print("API: ",self.select_api)
                    print("Households: ",len(api_error_list))
                    print()
                    for x in api_error_list:
                        print(f"{SplunkSearchJob.couch_url}/households/{x}")

            except ValueError as e:
                print("Value error on trying to print output")
                print(e)   



