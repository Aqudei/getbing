import re
import os
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Bing:

    def __init__(self, search):

        if os.path.exists(search):
            print('Loading search terms from: ' + search)
            with open(search, 'rt') as fp:
                lines = [line.replace('\r', '').replace('\n', '').replace(
                    '\t', '').strip() for line in fp.readlines()]
                self.search_terms = [l for l in lines if l != '']
        else:
            self.search_terms = [search, ]
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(30)
        self.output_folder = './output'

        self.current_search = ''

    def __perform_search(self):
        print('Searching for: ' + self.current_search)
        search_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'q')))
        search_field.send_keys(self.current_search)
        go_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'go')))
        go_button.click()
        print('Waiting for result...')

    def __write_output(self, page_num, text):
        out_file = os.path.join(
            self.output_folder, self.current_search + '_' + str(page_num) + '.txt')
        print('Writing text file <{}>'.format(out_file))
        with open(out_file, 'wb') as fp:
            fp.write(text.encode('utf-8'))

    def __concat_text(self, results):
        print('Preparing page result for writing...')
        text = ''
        for r in results:
            text = text + r.get_attribute('innerText')

        return text

    def __read_result_write_file(self):
        page_num = 1

        while True:
            try:
                print('Reading result page number: {} of search term: {}'.format(
                    page_num, self.current_search))
                element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//a[contains(@title,"Next page")]')))

                results = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located(
                    (By.XPATH, '//li[@class="b_algo"]')))

                self.__write_output(page_num, self.__concat_text(results))
                page_num = page_num + 1
                element.click()

                time.sleep(4)

            except Exception as ex:
                print('Exiting Loop\nReason: ' + str(ex))
                break

    def __ensure_folder(self, folder):
        try:
            os.makedirs(folder)
        except OSError:
            pass

    def execute_search(self):
        print('Creating output folder...')
        self.__ensure_folder(self.output_folder)

        for s in self.search_terms:
            self.driver.get('https://bing.com')

            self.current_search = s

            self.__perform_search()
            self.__read_result_write_file()

    def terminate(self):
        self.driver.quit()


if __name__ == '__main__':
    try:
        bing = Bing('./search_terms_input.txt')
        bing.execute_search()
    except Exception as ex:
        print('Main Program exited with error: ' + str(ex))
        bing.terminate()
