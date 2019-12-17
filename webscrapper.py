from selenium import webdriver
import time
import getpass
import csv

def divide_chunks(list_to_be_chunked, size_of_chunk):
    for i in range(0,len(list_to_be_chunked),size_of_chunk):
        yield list_to_be_chunked[i:i + size_of_chunk]

def record_transaction_in_excel(transactions=None,add_header=False,calculate_total=False):
        if add_header:
            with open('/Users/sinatesa/Desktop/RemitlyTransfers.csv', 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                data = [line for line in csv_reader]
            with open('/Users/sinatesa/Desktop/RemitlyTransfers.csv', 'w') as csvfile:
                csv_writer = csv.writer(csvfile)
                csvfile.seek(0)
                csv_writer.writerow(['Date','Method','Sender','USD','INR'])
                csv_writer.writerows(data)

        elif calculate_total:
            with open('/Users/sinatesa/Desktop/RemitlyTransfers.csv', 'r') as csvfile:
                csv_reader = csv.reader(csvfile)
                data = [line for line in csv_reader]
                usd_total = 0
                inr_total = 0
                for line in data:
                    usd_total += float(''.join(line[3].split()[0].split(',')))
                    inr_total += float(''.join(line[4].split()[0].split(',')))
            with open('/Users/sinatesa/Desktop/RemitlyTransfers.csv', 'a') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['','','','',''])
                csv_writer.writerow(['Total Sent', '', '', str(usd_total), str(inr_total)])
        else:
            with open('/Users/sinatesa/Desktop/RemitlyTransfers.csv', 'w+') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerows(transactions)


def login_to_remitly(driver,username,password):
    email = driver.find_element_by_id('loginEmailField')
    email.send_keys(username)
    passw = driver.find_element_by_id('loginPasswordField')
    passw.send_keys(password)
    signin = driver.find_element_by_xpath("//button[@type='submit' and @class='btn btn-cta btn-success']")
    signin.click()
    return driver

def check_for_transfer_history_and_update_excel(driver):
    # Check for transfer history
    driver.find_element_by_link_text("Transfer history").click()
    # collect data for this page
    next_page_enabled = True
    transactions = list()
    while next_page_enabled:
        time.sleep(10)
        all_combinations = driver.find_elements_by_xpath("//dd[@class='text-ellipsis']")
        all_combinations = [element.text for element in all_combinations]
        sub_combinations = list(divide_chunks(list_to_be_chunked=all_combinations,size_of_chunk=5))
        for sub_element in sub_combinations:
            transactions.append(sub_element)
        next_page_enabled = driver.find_element_by_xpath("//button[@type='button' and @class='btn next-button btn-subdued btn-md btn-outline']").is_enabled()
        if next_page_enabled:
            driver.find_element_by_xpath("//button[@type='button' and @class='btn next-button btn-subdued btn-md btn-outline']").click()
    record_transaction_in_excel(transactions=transactions)
    record_transaction_in_excel(calculate_total=True)
    record_transaction_in_excel(add_header=True)


def main():

    # 1. Obtain Username and Password from user
    myemail = input("Enter Username/Email: ")
    mypassword = getpass.getpass("Enter Password: ")

    # 2. Create Driver Object for chrome web browser which will be used for scrapping
    login_url = "https://www.remitly.com/us/en/users/login"
    driver = webdriver.Chrome(executable_path="/Users/sinatesa/Downloads/chromedriver")
    driver.get(login_url)

    # 3. Login to remitly page
    driver = login_to_remitly(driver=driver, username=myemail, password= mypassword)

    # 4. Check Mobile for OTP code for verification
    time.sleep(60)

    # 5. Check for transfer history and update excel sheet
    check_for_transfer_history_and_update_excel(driver=driver)

    # 6. Close chrome driver
    driver.quit()

if __name__ == "__main__":
    main()