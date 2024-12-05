"""
This module analyses log file and create a report in the form of csv file.
"""

import os
import pandas as pd

def read_file(path: str) -> pd.DataFrame: # pylint: disable=too-many-branches
    """Access the log file to create structured representation of dataframe."""

    with open(path, "r", encoding="utf8") as f:
        file = f.readlines()

    f.close()

    log_file = [row.split("\"") for row in file]

    for entry in log_file:
        for idx, val in enumerate(entry):
            if idx == 0:
                entry[idx] = entry[idx].split(" ")[0]
            elif idx == 1:
                entry.extend(entry[idx].split(" "))
            elif idx == 2:
                entry[idx] = [
                    int(status_code)
                    for status_code in entry[idx].split(" ")
                    if status_code != ''
                ][0]
                if entry[idx] != 401:
                    entry.insert(idx + 1, "Valid credentials")
                entry.pop(1)
            elif val == '\n':
                entry.pop(idx)

    ip_address = []
    req_method = []
    endpoint = []
    http = []
    status_code = []
    credentials = []

    for entry in log_file:
        for idx, val in enumerate(entry):
            if idx == 0:
                ip_address.append(val)
            elif idx == 1:
                status_code.append(val)
            elif idx == 2:
                credentials.append(val)
            elif idx == 3:
                req_method.append(val)
            elif idx == 4:
                endpoint.append(val)
            elif idx == 5:
                http.append(val)

    df = {
        'IP address': ip_address,
        'Request Method': req_method,
        'Endpoint': endpoint,
        'HTTP': http, 
        'Status Code': status_code,
        'Credentials': credentials,
    } # dictionary to make pandas dataframe

    df = pd.DataFrame(df)

    return df


def count_ip_address_freq(ip_address: pd.Series) -> pd.DataFrame:
    """Function to count the frequencies of the ip addresses."""

    freq = ip_address.value_counts()

    ip_address_freq = {
        'IP address': list(freq.keys()),
        'Request Count': list(freq)
    }

    return pd.DataFrame(ip_address_freq, index=None)


def count_endpoint_freq(endpoints: pd.Series) -> tuple:
    """Function to find most frequently accessed endpoint."""

    endpoint_freq = endpoints.value_counts()

    # # Uncomment below code to save all the endpoint frequencies
    # # Perform below changes:
    # # 1) Change the return type of the function to pd.DataFrame
    # # 2) Comment the current return statement
    # endpoint_freq = endpoint_freq.reset_index()
    # endpoint_freq.columns = ["Endpoint", "Frequency"]
    # return endpoint_freq

    return (list(endpoint_freq.keys())[0], list(endpoint_freq)[0])


def count_failed_login_attempts(data: pd.DataFrame) -> pd.DataFrame:
    """Function to find ip addresses with suspecious activity."""

    failed_log_in_data = data[
        (data["Status Code"] == 401)
        | (data["Credentials"] == "Invalid Credentials")
    ]

    failed_freq = failed_log_in_data["IP address"].value_counts()
    failed_freq_above_threshold = failed_freq[failed_freq > 10].reset_index()
    failed_freq_above_threshold.columns = ["IP address", "Failed Login Count"]

    return failed_freq_above_threshold


if __name__ == "__main__":

    log = read_file(os.getcwd() + os.path.sep + 'sample.log')

    ip_address_count = count_ip_address_freq(log["IP address"])
    endpoint_count = count_endpoint_freq(log["Endpoint"])
    suspicious_activity_count = count_failed_login_attempts(log)

    print("\n---------- \033[1;32mAnalysis Report\033[0m ----------\n")

    print("\033[1;33mRequest counts per IP address:\033[0m")
    print(ip_address_count.to_string(index=False))
    print("\n")

    print('\033[1;33mMost Frequently Accessed Endpoint:\033[0m')
    print('\033[1;34m',
          endpoint_count[0],
          '\033[0m(Accessed\033[1;34m',
          endpoint_count[1],
          '\033[0mtimes)'
        )
    print("\n")
    endpoint_count = pd.DataFrame({
        'Most Frequently Accessed Endpoint': [endpoint_count[0]],
        'Frequency': [endpoint_count[1]]
    })

    # # If accessing all the endpoints frequency counts
    # # Perform below changes:
    # # 1) Comment above print statement of endpoint frequency
    # # 2) Uncomment below print statements
    # print('\033[1;33mMost Frequently Accessed Endpoint:\033[0m')
    # print('\033[1;34m', endpoint_count.to_string(index=False), '\033[0m')
    # print("\n")

    print('\033[1;33mSuspicious Activity Detected:\033[0m')
    if suspicious_activity_count.empty:
        print('\033[1;32mNo suspicious activity :)\033[0m')
    else:
        print('\033[1;31m', suspicious_activity_count.to_string(index=False), '\033[0m')


    # Save analysis in xlsx file
    OUTPUT_FILE = "log_analysis_results.xlsx"

    with pd.ExcelWriter(OUTPUT_FILE, engine='xlsxwriter') as writer:
        ip_address_count.to_excel(
            writer,
            sheet_name='Sheet1',
            startrow=0,
            startcol=0,
            index=False
        )

        endpoint_count.to_excel(
            writer,
            sheet_name='Sheet1',
            startrow=0,
            startcol=ip_address_count.shape[1] + 2,
            index=False
        )

        suspicious_activity_count.to_excel(
            writer,
            sheet_name='Sheet1',
            startrow=0,
            startcol=ip_address_count.shape[1] + endpoint_count.shape[1] + 4,
            index=False
        )

    print("\n", "-"*37)
    print(f"\n\n\033[1;32mAnalysis report have been saved to: {OUTPUT_FILE}\033[0m\n\n")
