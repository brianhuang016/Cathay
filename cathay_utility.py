from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import traceback


def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--headless")  # 如需無頭模式可取消註解
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def click_dropdown_option(driver, option_name, screenshot_name, dropdown_class=".transformSelectDropdown"):
    """通用的下拉選單點擊函數"""
    dropdown = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, dropdown_class))
    )
    items = dropdown.find_elements(By.TAG_NAME, "li")
    print(f"在下拉選單中尋找: {option_name}")
    print(f"找到 {len(items)} 個 li 元素")
    found = False
    
    for i, item in enumerate(items):
        try:
            # 打印每個 li 的完整 HTML 結構
            print(f"li {i} HTML: {item.get_attribute('outerHTML')}")
            
            # 嘗試多種方式獲取文本
            text = ""
            try:
                # 方法1: 直接獲取 li 的文本
                text = item.text.strip()
                print(f"li {i} 直接文本: '{text}'")
            except:
                pass
            
            if not text:
                try:
                    # 方法2: 查找 span 標籤
                    span = item.find_element(By.TAG_NAME, "span")
                    text = span.text.strip()
                    print(f"li {i} span 文本: '{text}'")
                except:
                    pass
            
            if not text:
                try:
                    # 方法3: 查找 div 標籤
                    div = item.find_element(By.TAG_NAME, "div")
                    text = div.text.strip()
                    print(f"li {i} div 文本: '{text}'")
                except:
                    pass
            
            if text == option_name:
                print(f"找到匹配項: {option_name}")
                # 滾動到元素可見
                driver.execute_script("arguments[0].scrollIntoView(true);", item)
                time.sleep(0.5)
                
                # 嘗試多種點擊方式
                try:
                    # 方法1: 直接點擊 li
                    item.click()
                    print(f"直接點擊 li 成功")
                except Exception as e:
                    print(f"直接點擊失敗: {e}")
                    try:
                        # 方法2: JavaScript 點擊
                        driver.execute_script("arguments[0].click();", item)
                        print(f"JavaScript 點擊成功")
                    except Exception as e2:
                        print(f"JavaScript 點擊也失敗: {e2}")
                        # 方法3: 點擊子元素
                        try:
                            clickable_element = item.find_element(By.CSS_SELECTOR, "*")
                            driver.execute_script("arguments[0].click();", clickable_element)
                            print(f"點擊子元素成功")
                        except Exception as e3:
                            print(f"所有點擊方式都失敗: {e3}")
                            continue
                
                found = True
                time.sleep(1)
                break
                
        except Exception as e:
            print(f"處理 li {i} 時發生錯誤: {e}")
    
    if not found:
        print(f"找不到 {option_name}")
    
    return found


def click_county(driver, county_name, screenshot_name):
    """點擊縣市選項（保持向後兼容）"""
    return click_dropdown_option(driver, county_name, screenshot_name)


def find_and_click_dropdown_trigger(driver, trigger_selectors):
    """查找並點擊下拉選單觸發器"""
    for selector_type, selector in trigger_selectors:
        try:
            print(f"嘗試 {selector_type}: {selector}")
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((selector_type, selector))
            )
            trigger = driver.find_element(selector_type, selector)
            print(f"用 {selector_type} 找到觸發器")
            print("觸發器 outerHTML:", trigger.get_attribute("outerHTML")[:300])
            driver.execute_script("arguments[0].click();", trigger)
            time.sleep(1)
            return True
        except Exception as e:
            print(f"{selector_type} 找不到觸發器: {e}")
    
    return False


def input_field_value(driver, field_xpath, value, field_name="欄位"):
    """
    在指定欄位輸入數值
    
    Args:
        driver: WebDriver 實例
        field_xpath (str): 欄位的 XPath
        value (str): 要輸入的數值
        field_name (str): 欄位名稱，用於日誌輸出
    """
    try:
        print(f"=== 開始輸入{field_name}: {value} ===")
        
        # 等待欄位出現並可點擊
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, field_xpath))
        )
        
        # 找到欄位元素
        field_element = driver.find_element(By.XPATH, field_xpath)
        print(f"找到{field_name}元素")
        
        # 清除現有內容
        field_element.clear()
        time.sleep(0.5)
        
        # 輸入新數值
        field_element.send_keys(value)
        print(f"已輸入{field_name}: {value}")
        
        # 驗證輸入是否成功
        actual_value = field_element.get_attribute("value")
        if actual_value == value:
            print(f"{field_name}輸入成功，驗證通過")
            return True
        else:
            print(f"{field_name}輸入可能失敗，期望值: {value}，實際值: {actual_value}")
            return False
            
    except Exception as e:
        print(f"輸入{field_name}時發生錯誤: {e}")
        return False


def select_loan_period(driver, period_text, other_period=None):
    """
    選擇貸款年限
    
    Args:
        driver: WebDriver 實例
        period_text (str): 要選擇的年限，例如 "20年", "其他"
        other_period (str): 當選擇"其他"時，要輸入的指定年限，例如 "25"
    
    Returns:
        bool: 選擇是否成功
    """
    try:
        print(f"=== 開始選擇貸款年限: {period_text} ===")
        
        # 貸款年限的 XPath
        loan_period_xpath = '//*[@id="mainform"]/div[4]/main/div/div[3]/section/div/div[4]/div[2]/div[1]/div/ul'
        
        # 等待貸款年限選項出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, loan_period_xpath))
        )
        
        # 找到貸款年限容器
        period_container = driver.find_element(By.XPATH, loan_period_xpath)
        
        # 嘗試多種方式找到選項
        period_items = []
        
        # 方法1: 查找 li 元素
        try:
            period_items = period_container.find_elements(By.TAG_NAME, "li")
            print(f"方法1 - 找到 {len(period_items)} 個 li 選項")
        except:
            print("方法1 - 找不到 li 元素")
        
        # 方法2: 如果沒有 li，嘗試查找其他元素
        if len(period_items) == 0:
            try:
                period_items = period_container.find_elements(By.CSS_SELECTOR, "*")
                print(f"方法2 - 找到 {len(period_items)} 個子元素")
            except:
                print("方法2 - 找不到子元素")
        
        print(f"總共找到 {len(period_items)} 個貸款年限選項")
        
        # 遍歷所有選項尋找匹配的年限
        found_period = False
        for i, item in enumerate(period_items):
            try:
                # 獲取選項的完整 HTML
                item_html = item.get_attribute('outerHTML')
                print(f"貸款年限選項 {i} HTML: {item_html}")
                
                # 獲取選項的文本內容
                item_text = item.text.strip()
                print(f"貸款年限選項 {i} 文本: '{item_text}'")
                
                # 檢查是否包含目標年限
                if period_text in item_text:
                    print(f"找到匹配的貸款年限: {item_text}")
                    
                    # 嘗試多種點擊方式
                    try:
                        # 方法1: 直接點擊
                        print("嘗試直接點擊")
                        item.click()
                        print("直接點擊成功")
                        found_period = True
                        break
                    except Exception as e1:
                        print(f"直接點擊失敗: {e1}")
                        try:
                            # 方法2: JavaScript 點擊
                            print("嘗試 JavaScript 點擊")
                            driver.execute_script("arguments[0].click();", item)
                            print("JavaScript 點擊成功")
                            found_period = True
                            break
                        except Exception as e2:
                            print(f"JavaScript 點擊失敗: {e2}")
                            try:
                                # 方法3: 點擊子元素
                                print("嘗試點擊子元素")
                                child_elements = item.find_elements(By.CSS_SELECTOR, "*")
                                if child_elements:
                                    driver.execute_script("arguments[0].click();", child_elements[0])
                                    print("點擊子元素成功")
                                    found_period = True
                                    break
                            except Exception as e3:
                                print(f"點擊子元素失敗: {e3}")
                                continue
                    
            except Exception as e:
                print(f"處理貸款年限選項 {i} 時發生錯誤: {e}")
                continue
        
        if found_period:
            print(f"貸款年限 {period_text} 選擇成功")
            
            # 如果選擇的是"其他"，需要額外輸入指定年限
            if period_text == "其他" and other_period:
                print(f"=== 開始輸入指定年限: {other_period} ===")
                other_period_xpath = '//*[@id="txtLoanTermOtherYear"]'
                
                try:
                    # 等待其他年限輸入欄位出現
                    WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, other_period_xpath))
                    )
                    
                    # 輸入指定年限
                    if input_field_value(driver, other_period_xpath, other_period, "指定年限"):
                        print(f"指定年限 {other_period} 輸入成功")
                        return True
                    else:
                        print(f"指定年限 {other_period} 輸入失敗")
                        return False
                        
                except Exception as e:
                    print(f"輸入指定年限時發生錯誤: {e}")
                    return False
            else:
                return True
        else:
            print(f"找不到或無法點擊貸款年限: {period_text}")
            return False
            
    except Exception as e:
        print(f"選擇貸款年限時發生錯誤: {e}")
        traceback.print_exc()
        return False


def input_loan_interest_rate(driver, interest_rate):
    """
    輸入貸款利率
    
    Args:
        driver: WebDriver 實例
        interest_rate (str): 要輸入的貸款利率，例如 "2.5"
    
    Returns:
        bool: 輸入是否成功
    """
    try:
        print(f"=== 開始輸入貸款利率: {interest_rate} ===")
        
        # 貸款利率欄位的 XPath
        interest_rate_xpath = '//*[@id="txtInterestRate"]'
        
        # 使用現有的 input_field_value 方法
        if input_field_value(driver, interest_rate_xpath, interest_rate, "貸款利率"):
            print(f"貸款利率 {interest_rate}% 輸入成功")
            return True
        else:
            print(f"貸款利率 {interest_rate}% 輸入失敗")
            return False
            
    except Exception as e:
        print(f"輸入貸款利率時發生錯誤: {e}")
        traceback.print_exc()
        return False


def click_calculate_button(driver, button_type="calculate"):
    """
    點擊試算按鈕
    
    Args:
        driver: WebDriver 實例
        button_type (str): 按鈕類型，"calculate" 為開始試算，"reset" 為重新試算
    
    Returns:
        bool: 點擊是否成功
    """
    try:
        if button_type == "calculate":
            print("=== 開始點擊開始試算按鈕 ===")
            button_id = "btnCalculate"
            button_name = "開始試算"
        elif button_type == "reset":
            print("=== 開始點擊重新試算按鈕 ===")
            button_id = "btnReset"
            button_name = "重新試算"
        else:
            print(f"不支援的按鈕類型: {button_type}")
            return False
        
        # 按鈕的 XPath
        button_xpath = f'//*[@id="{button_id}"]'
        
        # 等待按鈕出現並可點擊
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, button_xpath))
        )
        
        # 找到按鈕元素
        button_element = driver.find_element(By.XPATH, button_xpath)
        print(f"找到{button_name}按鈕")
        
        # 獲取按鈕文本
        button_text = button_element.text.strip()
        print(f"{button_name}按鈕文本: '{button_text}'")
        
        # 嘗試多種點擊方式
        try:
            # 方法1: 直接點擊
            print(f"嘗試直接點擊{button_name}按鈕")
            button_element.click()
            print(f"{button_name}按鈕點擊成功")
            return True
        except Exception as e1:
            print(f"直接點擊{button_name}按鈕失敗: {e1}")
            try:
                # 方法2: JavaScript 點擊
                print(f"嘗試 JavaScript 點擊{button_name}按鈕")
                driver.execute_script("arguments[0].click();", button_element)
                print(f"{button_name}按鈕 JavaScript 點擊成功")
                return True
            except Exception as e2:
                print(f"JavaScript 點擊{button_name}按鈕失敗: {e2}")
                return False
                
    except Exception as e:
        print(f"點擊{button_name}按鈕時發生錯誤: {e}")
        traceback.print_exc()
        return False


def extract_calculation_results(driver):
    """
    提取試算結果內容
    
    Args:
        driver: WebDriver 實例
    
    Returns:
        list: 包含 div_1 和 div_2 的文本內容列表
    """
    try:
        print("=== 開始提取試算結果 ===")
        
        # 等待結果出現
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".cubinvest-l-cols__8.cubinvest-l-cols__12\\@t"))
        )
        
        result_list = []
        
        # 找到指定 class 下的 div
        container = driver.find_element(By.CSS_SELECTOR, ".cubinvest-l-cols__8.cubinvest-l-cols__12\\@t")
        result_divs = container.find_elements(By.CSS_SELECTOR, ".cubinvest-normal-p")
        
        for i, div in enumerate(result_divs):
            try:
                # print(f"處理第 {i+1} 個 div")
                
                # 獲取 div 的完整 HTML
                div_html = div.get_attribute('outerHTML')
                
                # 檢查是否有 <h5> 標籤（div_3 的情況）- 跳過
                try:
                    h5_element = div.find_element(By.TAG_NAME, "h5")
                    # print(f"Div {i+1} 是通知內容，跳過")
                    continue
                    
                except Exception as e:
                    pass
                
                # 處理有 <b> 和 <span> 的情況（div_1 和 div_2）
                try:
                    b_element = div.find_element(By.TAG_NAME, "b")
                    b_full_text = b_element.text.strip()
                    
                    # 提取 <span> 標籤的文本
                    span_text = ""
                    try:
                        span_element = b_element.find_element(By.TAG_NAME, "span")
                        span_text = span_element.text.strip()
                    except Exception as e:
                        print(f"Div {i+1} 找不到 <span> 標籤: {e}")
                    
                    # 組合完整文本
                    if span_text and span_text in b_full_text:
                        # span 文本已經包含在 b_full_text 中，直接使用
                        full_text = b_full_text
                    else:
                        # 手動組合文本
                        full_text = f"{b_full_text} {span_text}".strip()
                    
                    # 只添加 div_1 和 div_2 的內容到結果列表
                    result_list.append(full_text)
                    print(f"Div {i+1} 完整文本: '{full_text}'")
                    
                except Exception as e:
                    print(f"Div {i+1} 找不到 <b> 標籤: {e}")
                
            except Exception as e:
                print(f"處理第 {i+1} 個 div 時發生錯誤: {e}")
        
        print("=== 試算結果提取完成 ===")
        print(f"提取到 {len(result_list)} 個結果:")
        for i, text in enumerate(result_list):
            print(f"結果 {i+1}: {text}")
        
        return result_list
        
    except Exception as e:
        print(f"提取試算結果時發生錯誤: {e}")
        traceback.print_exc()
        return {}


def click_consultation_button(driver):
    """
    點擊馬上諮詢按鈕
    
    Args:
        driver: WebDriver 實例
    
    Returns:
        bool: 點擊是否成功
    """
    try:
        print("=== 開始點擊馬上諮詢按鈕 ===")
        
        # 馬上諮詢按鈕的 XPath
        consultation_button_xpath = '//*[@id="divResult"]/section/div/div/div[2]/div/a'
        
        # 等待按鈕出現並可點擊
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, consultation_button_xpath))
        )
        
        # 找到按鈕元素
        consultation_button = driver.find_element(By.XPATH, consultation_button_xpath)
        print("找到馬上諮詢按鈕")
        
        # 滾動到按鈕可見
        driver.execute_script("arguments[0].scrollIntoView(true);", consultation_button)
        time.sleep(0.5)
        
        # 嘗試多種點擊方式
        try:
            # 方法1: 直接點擊
            consultation_button.click()
            print("直接點擊馬上諮詢按鈕成功")
            return True
        except Exception as e:
            print(f"直接點擊失敗: {e}")
            try:
                # 方法2: JavaScript 點擊
                driver.execute_script("arguments[0].click();", consultation_button)
                print("JavaScript 點擊馬上諮詢按鈕成功")
                return True
            except Exception as e2:
                print(f"JavaScript 點擊也失敗: {e2}")
                return False
                
    except Exception as e:
        print(f"點擊馬上諮詢按鈕時發生錯誤: {e}")
        traceback.print_exc()
        return False


def click_monthly_payment_calculation(driver):
    """
    點擊每月還款試算按鈕
    
    Args:
        driver: WebDriver 實例
    
    Returns:
        bool: 點擊是否成功
    """
    try:
        print("=== 開始點擊每月還款試算按鈕 ===")
        
        # 每月還款試算按鈕的 XPath
        monthly_payment_xpath = '/html/body/form/div[4]/main/div/section/div/div/a[1]/div'
        
        # 等待按鈕出現並可點擊
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, monthly_payment_xpath))
        )
        
        # 找到按鈕元素
        monthly_payment_button = driver.find_element(By.XPATH, monthly_payment_xpath)
        print("找到每月還款試算按鈕")
        
        # 滾動到按鈕可見
        driver.execute_script("arguments[0].scrollIntoView(true);", monthly_payment_button)
        time.sleep(0.5)
        
        # 嘗試多種點擊方式
        try:
            # 方法1: 直接點擊
            monthly_payment_button.click()
            print("直接點擊每月還款試算按鈕成功")
            return True
        except Exception as e:
            print(f"直接點擊失敗: {e}")
            try:
                # 方法2: JavaScript 點擊
                driver.execute_script("arguments[0].click();", monthly_payment_button)
                print("JavaScript 點擊每月還款試算按鈕成功")
                return True
            except Exception as e2:
                print(f"JavaScript 點擊也失敗: {e2}")
                return False
                
    except Exception as e:
        print(f"點擊每月還款試算按鈕時發生錯誤: {e}")
        traceback.print_exc()
        return False


def click_loan_ratio_calculation(driver):
    """
    點擊貸款成數試算按鈕
    
    Args:
        driver: WebDriver 實例
    
    Returns:
        bool: 點擊是否成功
    """
    try:
        print("=== 開始點擊貸款成數試算按鈕 ===")
        
        # 貸款成數試算按鈕的 XPath
        loan_ratio_xpath = '/html/body/form/div[4]/main/div/section/div/div/a[2]/div'
        
        # 等待按鈕出現並可點擊
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, loan_ratio_xpath))
        )
        
        # 找到按鈕元素
        loan_ratio_button = driver.find_element(By.XPATH, loan_ratio_xpath)
        print("找到貸款成數試算按鈕")
        
        # 滾動到按鈕可見
        driver.execute_script("arguments[0].scrollIntoView(true);", loan_ratio_button)
        time.sleep(0.5)
        
        # 嘗試多種點擊方式
        try:
            # 方法1: 直接點擊
            loan_ratio_button.click()
            print("直接點擊貸款成數試算按鈕成功")
            return True
        except Exception as e:
            print(f"直接點擊失敗: {e}")
            try:
                # 方法2: JavaScript 點擊
                driver.execute_script("arguments[0].click();", loan_ratio_button)
                print("JavaScript 點擊貸款成數試算按鈕成功")
                return True
            except Exception as e2:
                print(f"JavaScript 點擊也失敗: {e2}")
                return False
                
    except Exception as e:
        print(f"點擊貸款成數試算按鈕時發生錯誤: {e}")
        traceback.print_exc()
        return False


def click_top_page_link(driver):
    """
    點擊主頁上方的指定連結
    
    Args:
        driver: WebDriver 實例
    
    Returns:
        bool: 點擊是否成功
    """
    try:
        print("=== 開始點擊主頁上方連結 ===")
        link_xpath = '/html/body/form/div[4]/main/div/div[2]/p/a'
        
        # 等待連結可點擊
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, link_xpath))
        )
        
        link_element = driver.find_element(By.XPATH, link_xpath)
        print("找到主頁上方連結")
        
        # 滾動到連結可見
        driver.execute_script("arguments[0].scrollIntoView(true);", link_element)
        time.sleep(0.5)
        
        # 嘗試多種點擊方式
        try:
            link_element.click()
            print("直接點擊主頁上方連結成功")
            return True
        except Exception as e:
            print(f"直接點擊失敗: {e}")
            try:
                driver.execute_script("arguments[0].click();", link_element)
                print("JavaScript 點擊主頁上方連結成功")
                return True
            except Exception as e2:
                print(f"JavaScript 點擊也失敗: {e2}")
                return False
    except Exception as e:
        print(f"點擊主頁上方連結時發生錯誤: {e}")
        traceback.print_exc()
        return False


def click_county_and_district_with_driver(driver, county_name="台北市", district_name="萬華區"):
    """
    選擇縣市和行政區的通用函數（使用傳入的 driver）
    
    Args:
        driver: WebDriver 實例
        county_name (str): 要選擇的縣市名稱，預設為"台北市"
        district_name (str): 要選擇的行政區名稱，預設為"萬華區"
    """
    url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/calculator/mortgage-budget/"
    
    # 縣市選擇器的配置
    county_trigger_selectors = [
        (By.XPATH, "/html/body/form/div[4]/main/div/div[3]/section/div/div[2]/div[2]/div/div/div/div[1]/div/ul/li/span"),
        (By.CSS_SELECTOR, ".cubinvest-o-select__trigger")
    ]
    
    # 行政區選擇器的配置（需要根據實際頁面調整）
    district_trigger_selectors = [
        (By.CSS_SELECTOR, ".cubinvest-o-select__trigger"),  # 可能需要調整
        (By.XPATH, "//span[contains(text(), '選擇行政區')]"),
        (By.XPATH, "//span[contains(text(), '行政區')]")
    ]
    
    dropdown_class = ".transformSelectDropdown"
    try:
        driver.get(url)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
        )
        
        # 第一步：選擇縣市
        print(f"=== 開始選擇縣市: {county_name} ===")
        if find_and_click_dropdown_trigger(driver, county_trigger_selectors):
            # 等待下拉選單出現並選擇指定縣市
            dropdown_found = False
            dropdown_selectors = [
                ".transformSelectDropdown",
                ".cubinvest-o-select__dropdown",
                ".select-dropdown",
                "[class*='dropdown']",
                "[class*='select']"
            ]
            
            for selector in dropdown_selectors:
                try:
                    dropdowns = driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if len(dropdowns) > 0:
                        dropdown_class = selector
                        dropdown_found = True
                        break
                except Exception as e:
                    print(f"選擇器 {selector} 失敗: {e}")
            
            if dropdown_found:
                # 點擊指定縣市
                if click_county(driver, county_name, f"{county_name}_selected.png"):
                    print(f"{county_name}選擇成功")
                    
                    # 第二步：選擇行政區
                    print(f"=== 開始選擇行政區: {district_name} ===")
                    time.sleep(2)  # 等待頁面更新
                    
                    # 嘗試多種方式找到行政區觸發器
                    district_trigger_found = False
                    district_trigger_selectors = [
                        (By.CSS_SELECTOR, ".cubinvest-o-select__trigger"),
                        (By.XPATH, "//span[contains(text(), '選擇行政區')]"),
                        (By.XPATH, "//span[contains(text(), '行政區')]"),
                        (By.XPATH, "//div[contains(@class, 'select')]//span[contains(text(), '選擇')]"),
                        (By.CSS_SELECTOR, "[class*='select'] span"),
                        (By.XPATH, "//span[text()='選擇行政區']"),
                        (By.XPATH, "//span[text()='行政區']")
                    ]
                    
                    for selector_type, selector in district_trigger_selectors:
                        try:
                            triggers = driver.find_elements(selector_type, selector)
                            
                            for trigger in triggers:
                                try:
                                    trigger_text = trigger.text.strip()
                                    if "行政區" in trigger_text or "選擇" in trigger_text:
                                        driver.execute_script("arguments[0].click();", trigger)
                                        time.sleep(1)
                                        district_trigger_found = True
                                        break
                                except Exception as e:
                                    continue
                            
                            if district_trigger_found:
                                break
                        except Exception as e:
                            print(f"行政區選擇失敗: {e}")
                    
                    if district_trigger_found:
                        # 等待特定的行政區下拉選單元素出現
                        district_dropdown_xpath = '//*[@id="mainform"]/div[4]/main/div/div[3]/section/div/div[2]/div[2]/div/div/div/div[2]/div/ul/li/ul'
                        try:
                            WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.XPATH, district_dropdown_xpath))
                            )
                        except Exception as e:
                            print(f"等待行政區下拉選單元素超時: {e}")
                            return False
                        
                        # 等待下拉選單內容載入
                        found_district = False
                        for wait_sec in range(10):
                            time.sleep(1)
                            try:
                                # 使用 XPath 找到行政區下拉選單
                                district_dropdown = driver.find_element(By.XPATH, district_dropdown_xpath)
                                items = district_dropdown.find_elements(By.TAG_NAME, "li")
                                
                                
                                for i, item in enumerate(items):
                                    try:
                                        html = item.get_attribute('outerHTML')
                                        
                                        
                                        # 直接從 span 元素獲取文本
                                        span = item.find_element(By.TAG_NAME, "span")
                                        text = span.get_attribute("innerText").strip() or span.get_attribute("textContent").strip()
                                        
                                        
                                        if district_name in text:
                                            
                                            driver.execute_script("arguments[0].scrollIntoView(true);", item)
                                            time.sleep(0.5)
                                            driver.execute_script("arguments[0].click();", item)
                                            # driver.save_screenshot(f"{district_name}_selected.png")
                                            
                                            found_district = True
                                            break
                                    except Exception as e:
                                        print(f"行政區 li {i} 解析失敗: {e}")
                                
                                if found_district:
                                    break
                            except Exception as e:
                                print(f"第{wait_sec+1}秒，無法找到行政區下拉選單: {e}")
                        
                        if not found_district:
                            print(f"10秒內未找到{district_name}，請檢查下拉選單內容")
                            # driver.save_screenshot(f"not_found_{district_name}.png")
                            return False
                        else:
                            return True
                    else:
                        print("無法找到行政區觸發器")
                        # driver.save_screenshot("no_district_trigger.png")
                        return False
                else:
                    print(f"{county_name}選擇失敗")
                    return False
            else:
                print("無法找到縣市下拉選單")
                # driver.save_screenshot("no_county_dropdown.png")
                return False
        else:
            print("無法找到縣市觸發器")
            # driver.save_screenshot("no_county_trigger.png")
            return False
            
    except Exception as e:
        print(f"發生錯誤: {e}")
        traceback.print_exc()
        return False


# if __name__ == "__main__":
#     # 設定參數
#     county_name = "台北市"
#     district_name = "萬華區"
#     loan_amount = "1000"
#     loan_period = "30年"
#     other_period = "25"  # 當選擇"其他"時，要輸入的指定年限
#     interest_rate = "2.5"  # 貸款利率
#     calculate_button = "calculate"  # "calculate" 為開始試算，"reset" 為重新試算
#     loan_amount_xpath = '//*[@id="txtAmount"]'
    
#     # 建立 driver
#     driver = setup_driver()
    
#     try:
#         # 第一步：選擇縣市和行政區
#         if click_county_and_district_with_driver(driver, county_name, district_name):
#             print("縣市和行政區選擇成功")
            
#             # 第二步：輸入房貸金額
#             print("=== 開始輸入房貸金額 ===")
#             if input_field_value(driver, loan_amount_xpath, loan_amount, "房貸金額"):
#                 print("房貸金額輸入成功")
                
#                 # 第三步：選擇貸款年限
#                 if select_loan_period(driver, loan_period, other_period):
#                     print("貸款年限選擇成功")
                    
#                     # 第四步：輸入貸款利率
#                     if input_loan_interest_rate(driver, interest_rate):
#                         print("貸款利率輸入成功")
                        
#                         # 第五步：點擊試算按鈕
#                         if click_calculate_button(driver, calculate_button):
#                             print("試算按鈕點擊成功")
#                             time.sleep(5)
                            
#                             # 第六步：提取試算結果
#                             calculation_results = extract_calculation_results(driver)
#                             if calculation_results:
#                                 print("試算結果提取成功")
#                                 print("=== 試算結果摘要 ===")
#                                 for i, result in enumerate(calculation_results):
#                                     print(f"結果 {i+1}: {result}")
                                
#                                 # 第七步：點擊馬上諮詢按鈕
#                                 time.sleep(2)
                                
#                                 if click_top_page_link(driver):
#                                     print("購屋貸款方案點擊成功")
#                                 else:
#                                     print("購屋貸款方案點擊失敗")
                                
#                             else:
#                                 print("試算結果提取失敗")
#                         else:
#                             print("試算按鈕點擊失敗")
#                     else:
#                         print("貸款利率輸入失敗，跳過試算按鈕點擊")
#                 else:
#                     print("貸款年限選擇失敗，跳過後續步驟")
#             else:
#                 print("房貸金額輸入失敗，跳過後續步驟")
#         else:
#             print("縣市和行政區選擇失敗，跳過後續步驟")
            
#     except Exception as e:
#         print(f"執行過程中發生錯誤: {e}")
#         traceback.print_exc()
#     finally:
#         if driver:
#             time.sleep(10)
#             driver.quit()