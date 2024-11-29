import traceback
from selenium import webdriver
from selenium.common import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re
import os 
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

# Chrome settings
chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
chrome_options.add_argument("--incognito") #don't want cache
chrome_options.add_argument("--headless")

#use driver_version as given in README
driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version='131.0.6778.86').install()), options=chrome_options)

def get_courses(value ="all"):
    try:
        # service = Service(ChromeDriverManager(version='114.0.5735.90').install())
        # driver = webdriver.Chrome(service=service, options=chrome_options)
        # service = Service()
        # driver = webdriver.Chrome(service=service, options=chrome_options)

        url = "https://campus.icu.ac.jp/icumap/ehb/SearchCO.aspx"

        # Open site (will be sent to SSO login)
        driver.get(url)
        driver.implicitly_wait(3)

        # Login to ICU SSO
        driver.find_element(By.ID,"username_input").send_keys(os.environ['ICU_SSO_ADDRESS'])
        driver.find_element(By.ID,"password_input").send_keys(os.environ['ICU_SSO_PASSWORD'])
        driver.find_element(By.ID,"login_button").click()
        driver.implicitly_wait(3)
        
        # Select Academic Year
        select_element = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_ddl_year")
        select_object = Select(select_element)
        select_object.select_by_visible_text(os.environ['ACADEMIC_YEAR'])
        

        # Select show ALL results to get full course list
        select_element = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_ddlPageSize")
        select_object = Select(select_element)
        select_object.select_by_visible_text("ALL")
        # select_object.select_by_visible_text("50")

        if value == "all":
            pass
        else:
            term_element = driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_ddl_term")
            term_object = Select(term_element)
            term_object.select_by_visible_text(value)
        
        driver.find_element(By.ID,"ctl00_ContentPlaceHolder1_btn_search").click()
        driver.implicitly_wait(3)

        # Find course table
        tables = driver.find_elements(By.TAG_NAME,"table")
        course_table = tables[3].get_attribute('innerHTML')
        return course_table
    except KeyError as ke:
        print(f"Environment variable error: {ke}")
    except NoSuchElementException as nse:
        print(f"Element not found error: {nse}")
    except WebDriverException as wde:
        print(f"WebDriver error: {wde}")
    except Exception as e:  # Catch-all for unexpected errors
        print(f"Unexpected error: {e}")
    finally:
        if driver:  # Ensure driver is not None
            driver.quit()
        
def get_syllabus(year, rgno):
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version='131.0.6778.86').install()), options=chrome_options)
            extract_tag = re.compile('lbl_[^\"]+')
            res_list = []
            for i in tqdm(range(len(rgno))):
                url = "https://campus.icu.ac.jp/public/ehandbook/PreviewSyllabus.aspx?year="+year+"&rgno="+str(rgno[i])+"&term="+str(rgno[i])[0]
                # Open site
                # print(url)
                driver.get(url)
                driver.implicitly_wait(1)
                # Find course table (get page -> get main table -> find td with contents inside it -> )
                form = driver.find_elements(By.TAG_NAME,"form")
                content_table = BeautifulSoup(form[0].get_attribute('innerHTML'),'lxml')
                raw_text = content_table.find_all('span')
                syllabus_dict = {'rgno':rgno[i]}
                for x in raw_text:

                    # Process Tag and content
                    tag = extract_tag.findall(str(x))
                    if tag == []:
                        continue
                    tag = tag[0].replace('lbl_','')
                    if tag == 'references':
                        tag = 'ref'

                    content = str(x).replace("<br/>",'\n')
                    content = re.sub('<[^>]+>','',content)
                    # Add to Dict
                    syllabus_dict.update({tag:content.strip('\n')})
                res_list.append(syllabus_dict)

            return res_list
        except:
            traceback.print_exc()
        finally:
            driver.quit()
            
def get_ela():
    try: 
        driver = webdriver.Chrome(service=Service(ChromeDriverManager(driver_version='123.0.6312.58').install()), options=chrome_options)

        url = "https://course-reg.icu.ac.jp/ela/stsch/show_schedule.shtml"
        # Open site (will be sent to SSO login)
        driver.get(url)
        driver.implicitly_wait(3)

        # Login to ICU SSO
        driver.find_element(By.NAME,"uname").send_keys(os.environ['ICU_ELA_ADDRESS'])
        driver.find_element(By.NAME,"pass").send_keys(os.environ['ICU_SSO_PASSWORD'])
        driver.find_element(By.XPATH,"/html/body/form/center/table/tbody/tr[4]/td[2]/input").click() 
        driver.implicitly_wait(3)

        table_list = []
        # TODO
        # update tags based on selected term
        section_list = ["20233_FR3","20233_FR4","20233_AS3","20233_AS4","20233_RW12","20233_RW34"]
        for section in section_list:
            tables = driver.find_elements(By.XPATH,'//*[@id="{}"]/table'.format(section))
            for i in tables:
                i = i.get_attribute('outerHTML')
                table_list.append(i)
        return table_list
    except:
        traceback.print_exc()
    finally:
        driver.quit()