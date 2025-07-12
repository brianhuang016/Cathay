import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import the functions from the main file
from cathay_utility import (
    setup_driver,
    click_county_and_district_with_driver,
    input_field_value,
    select_loan_period,
    input_loan_interest_rate,
    click_calculate_button,
    extract_calculation_results,
    click_consultation_button,
    click_monthly_payment_calculation,
    click_loan_ratio_calculation,
    click_top_page_link
)


class TestCathayMortgageCalculation:
    """Test class for Cathay mortgage calculation functionality"""
    
    def test_extract_calculation_results_case_5(self):
        """Test the complete calculation flow and result extraction"""
        # 設定參數 (從 main function 複製)
        county_name = "台北市"
        district_name = "萬華區"
        loan_amount = "1000"
        loan_period = "30年"
        other_period = "25"  # 當選擇"其他"時，要輸入的指定年限
        interest_rate = "2.5"  # 貸款利率
        calculate_button = "calculate"  # "calculate" 為開始試算，"reset" 為重新試算
        loan_amount_xpath = '//*[@id="txtAmount"]'

        loan_ratio = "7～7.5成"
        total_loan = "337,449"
        prepare_fund = "84,362"
        house_loan = "253,087"

        result_1 = f'在您所挑選的區域，本行估計最高可貸款成數為 {loan_ratio}'
        result_2 = f'建議您在所選區域購買 {total_loan}萬 型態以內的房屋（包含自備款{prepare_fund}萬及房貸{house_loan}萬）'

        # 建立 driver (從 main function 複製)
        driver = setup_driver()
        
        try:
            # 第一步：選擇縣市和行政區 (從 main function 複製)
            if click_county_and_district_with_driver(driver, county_name, district_name):
                print("縣市和行政區選擇成功")
                
                # 第二步：輸入房貸金額 (從 main function 複製)
                print("=== 開始輸入房貸金額 ===")
                if input_field_value(driver, loan_amount_xpath, loan_amount, "房貸金額"):
                    print("房貸金額輸入成功")
                    
                    # 第三步：選擇貸款年限 (從 main function 複製)
                    if select_loan_period(driver, loan_period, other_period):
                        print("貸款年限選擇成功")
                        
                        # 第四步：輸入貸款利率 (從 main function 複製)
                        if input_loan_interest_rate(driver, interest_rate):
                            print("貸款利率輸入成功")
                            
                            # 第五步：點擊試算按鈕 (從 main function 複製)
                            if click_calculate_button(driver, calculate_button):
                                print("試算按鈕點擊成功")
                                time.sleep(5)
                                
                                # 第六步：提取試算結果 (從 main function 複製)
                                calculation_results = extract_calculation_results(driver)
                                if calculation_results:
                                    print("試算結果提取成功")
                                    print("=== 試算結果摘要 ===")
                                    for i, result in enumerate(calculation_results):
                                        print(f"結果 {i+1}: {result}")
                                    
                                    # 驗證試算結果內容
                                    assert len(calculation_results) == 2, f"期望有2個結果，實際有{len(calculation_results)}個"
                                    
                                    # 驗證第一個結果包含貸款成數資訊
                                    first_result = calculation_results[0]
                                    print(f"第一個結果: {first_result}")
                                    assert result_1 == first_result
                                    
                                    # 驗證第二個結果包含購買建議
                                    second_result = calculation_results[1]
                                    print(f"第二個結果: {second_result}")
                                    assert result_2 == second_result
                                                                        
                                    print("✅ 試算結果驗證通過")
                                    
                                    # 第七步：點擊馬上諮詢按鈕並驗證重定向
                                    print("=== 開始點擊馬上諮詢按鈕 ===")
                                    time.sleep(2)  # 等待頁面穩定
                                    
                                    if click_consultation_button(driver):
                                        print("馬上諮詢按鈕點擊成功")
                                        
                                        # 等待頁面重定向
                                        time.sleep(3)
                                        
                                        # 驗證是否重定向到預約房貸諮詢頁面
                                        current_url = driver.current_url
                                        expected_url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/reserve/mortgage/"
                                        
                                        print(f"當前頁面 URL: {current_url}")
                                        print(f"期望重定向 URL: {expected_url}")
                                        
                                        if expected_url in current_url:
                                            print("✅ 重定向驗證成功 - 已正確跳轉到房貸諮詢預約頁面")
                                        else:
                                            print(f"❌ 重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}")
                                            assert False, f"重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}"
                                    else:
                                        print("馬上諮詢按鈕點擊失敗")
                                        assert False, "馬上諮詢按鈕點擊失敗"
                                else:
                                    print("試算結果提取失敗")
                                    assert False, "試算結果提取失敗"
                            else:
                                print("試算按鈕點擊失敗")
                                assert False, "試算按鈕點擊失敗"
                        else:
                            print("貸款利率輸入失敗，跳過試算按鈕點擊")
                            assert False, "貸款利率輸入失敗"
                    else:
                        print("貸款年限選擇失敗，跳過後續步驟")
                        assert False, "貸款年限選擇失敗"
                else:
                    print("房貸金額輸入失敗，跳過後續步驟")
                    assert False, "房貸金額輸入失敗"
            else:
                print("縣市和行政區選擇失敗，跳過後續步驟")
                assert False, "縣市和行政區選擇失敗"
                
        except Exception as e:
            print(f"執行過程中發生錯誤: {e}")
            assert False, f"執行過程中發生錯誤: {e}"
        finally:
            if driver:
                driver.quit()

    def test_extract_calculation_results_other_period_case_12(self):
        """Test the complete calculation flow and result extraction with other period"""
        # 設定參數 (從 main function 複製)
        county_name = "高雄市"
        district_name = "苓雅區"
        loan_amount = "1000"
        loan_period = "其他"
        other_period = "25"  # 當選擇"其他"時，要輸入的指定年限
        interest_rate = "2.5"  # 貸款利率
        calculate_button = "calculate"  # "calculate" 為開始試算，"reset" 為重新試算
        loan_amount_xpath = '//*[@id="txtAmount"]'

        loan_ratio = "7～7.5成"
        total_loan = "297,209"
        prepare_fund = "74,302"
        house_loan = "222,907"

        result_1 = f'在您所挑選的區域，本行估計最高可貸款成數為 {loan_ratio}'
        result_2 = f'建議您在所選區域購買 {total_loan}萬 型態以內的房屋（包含自備款{prepare_fund}萬及房貸{house_loan}萬）'

        # 建立 driver (從 main function 複製)
        driver = setup_driver()
        
        try:
            # 第一步：選擇縣市和行政區 (從 main function 複製)
            if click_county_and_district_with_driver(driver, county_name, district_name):
                print("縣市和行政區選擇成功")
                
                # 第二步：輸入房貸金額 (從 main function 複製)
                print("=== 開始輸入房貸金額 ===")
                if input_field_value(driver, loan_amount_xpath, loan_amount, "房貸金額"):
                    print("房貸金額輸入成功")
                    
                    # 第三步：選擇貸款年限 (從 main function 複製)
                    if select_loan_period(driver, loan_period, other_period):
                        print("貸款年限選擇成功")
                        
                        # 第四步：輸入貸款利率 (從 main function 複製)
                        if input_loan_interest_rate(driver, interest_rate):
                            print("貸款利率輸入成功")
                            
                            # 第五步：點擊試算按鈕 (從 main function 複製)
                            if click_calculate_button(driver, calculate_button):
                                print("試算按鈕點擊成功")
                                time.sleep(5)
                                
                                # 第六步：提取試算結果 (從 main function 複製)
                                calculation_results = extract_calculation_results(driver)
                                if calculation_results:
                                    print("試算結果提取成功")
                                    print("=== 試算結果摘要 ===")
                                    for i, result in enumerate(calculation_results):
                                        print(f"結果 {i+1}: {result}")
                                    
                                    # 驗證試算結果內容
                                    assert len(calculation_results) == 2, f"期望有2個結果，實際有{len(calculation_results)}個"
                                    
                                    # 驗證第一個結果包含貸款成數資訊
                                    first_result = calculation_results[0]
                                    print(f"第一個結果: {first_result}")
                                    assert result_1 == first_result
                                    
                                    # 驗證第二個結果包含購買建議
                                    second_result = calculation_results[1]
                                    print(f"第二個結果: {second_result}")
                                    assert result_2 == second_result
                                                                        
                                    print("✅ 試算結果驗證通過")
                                    
                                    # 第七步：點擊馬上諮詢按鈕並驗證重定向
                                    print("=== 開始點擊馬上諮詢按鈕 ===")
                                    time.sleep(2)  # 等待頁面穩定
                                    
                                    if click_consultation_button(driver):
                                        print("馬上諮詢按鈕點擊成功")
                                        
                                        # 等待頁面重定向
                                        time.sleep(3)
                                        
                                        # 驗證是否重定向到預約房貸諮詢頁面
                                        current_url = driver.current_url
                                        expected_url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/reserve/mortgage/"
                                        
                                        print(f"當前頁面 URL: {current_url}")
                                        print(f"期望重定向 URL: {expected_url}")
                                        
                                        if expected_url in current_url:
                                            print("✅ 重定向驗證成功 - 已正確跳轉到房貸諮詢預約頁面")
                                        else:
                                            print(f"❌ 重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}")
                                            assert False, f"重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}"
                                    else:
                                        print("馬上諮詢按鈕點擊失敗")
                                        assert False, "馬上諮詢按鈕點擊失敗"
                                else:
                                    print("試算結果提取失敗")
                                    assert False, "試算結果提取失敗"
                            else:
                                print("試算按鈕點擊失敗")
                                assert False, "試算按鈕點擊失敗"
                        else:
                            print("貸款利率輸入失敗，跳過試算按鈕點擊")
                            assert False, "貸款利率輸入失敗"
                    else:
                        print("貸款年限選擇失敗，跳過後續步驟")
                        assert False, "貸款年限選擇失敗"
                else:
                    print("房貸金額輸入失敗，跳過後續步驟")
                    assert False, "房貸金額輸入失敗"
            else:
                print("縣市和行政區選擇失敗，跳過後續步驟")
                assert False, "縣市和行政區選擇失敗"
                
        except Exception as e:
            print(f"執行過程中發生錯誤: {e}")
            assert False, f"執行過程中發生錯誤: {e}"
        finally:
            if driver:
                driver.quit()

    def test_monthly_payment_calculation_redirect_case_22(self):
        """測試每月還款試算按鈕點擊和重定向"""
        print("=== 開始測試每月還款試算按鈕 ===")
        
        # 建立 driver
        driver = setup_driver()
        
        try:
            # 直接導航到房貸試算頁面
            url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/calculator/mortgage-budget/"
            driver.get(url)
            
            # 等待頁面載入
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
            )
            print("頁面載入完成")
            
            # 點擊每月還款試算按鈕
            if click_monthly_payment_calculation(driver):
                print("每月還款試算按鈕點擊成功")
                
                # 等待頁面重定向
                time.sleep(3)
                
                # 驗證是否重定向到每月還款試算頁面
                current_url = driver.current_url
                expected_url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/calculator/mortgage-monthly-payments/"
                
                print(f"當前頁面 URL: {current_url}")
                print(f"期望重定向 URL: {expected_url}")
                
                if expected_url in current_url:
                    print("✅ 每月還款試算重定向驗證成功")
                else:
                    print(f"❌ 每月還款試算重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}")
                    assert False, f"每月還款試算重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}"
            else:
                print("每月還款試算按鈕點擊失敗")
                assert False, "每月還款試算按鈕點擊失敗"
                
        except Exception as e:
            print(f"測試每月還款試算時發生錯誤: {e}")
            assert False, f"測試每月還款試算時發生錯誤: {e}"
        finally:
            if driver:
                driver.quit()

    def test_loan_ratio_calculation_redirect_case_23(self):
        """測試貸款成數試算按鈕點擊和重定向"""
        print("=== 開始測試貸款成數試算按鈕 ===")
        
        # 建立 driver
        driver = setup_driver()
        
        try:
            # 直接導航到房貸試算頁面
            url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/calculator/mortgage-budget/"
            driver.get(url)
            
            # 等待頁面載入
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
            )
            print("頁面載入完成")
            
            # 點擊貸款成數試算按鈕
            if click_loan_ratio_calculation(driver):
                print("貸款成數試算按鈕點擊成功")
                
                # 等待頁面重定向
                time.sleep(3)
                
                # 驗證是否重定向到貸款成數試算頁面
                current_url = driver.current_url
                expected_url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/calculator/mortgage-to-value/"
                
                print(f"當前頁面 URL: {current_url}")
                print(f"期望重定向 URL: {expected_url}")
                
                if expected_url in current_url:
                    print("✅ 貸款成數試算重定向驗證成功")
                else:
                    print(f"❌ 貸款成數試算重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}")
                    assert False, f"貸款成數試算重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}"
            else:
                print("貸款成數試算按鈕點擊失敗")
                assert False, "貸款成數試算按鈕點擊失敗"
                
        except Exception as e:
            print(f"測試貸款成數試算時發生錯誤: {e}")
            assert False, f"測試貸款成數試算時發生錯誤: {e}"
        finally:
            if driver:
                driver.quit()

    def test_top_page_link_redirect_case_20(self):
        """測試主頁上方連結點擊和重定向"""
        print("=== 開始測試主頁上方連結 ===")
        
        # 建立 driver
        driver = setup_driver()
        
        try:
            # 直接導航到房貸試算頁面
            url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/calculator/mortgage-budget/"
            driver.get(url)
            
            # 等待頁面載入
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "main"))
            )
            print("頁面載入完成")
            
            # 點擊主頁上方連結
            if click_top_page_link(driver):
                print("主頁上方連結點擊成功")
                
                # 等待頁面重定向
                time.sleep(3)
                
                # 驗證是否重定向到房貸產品頁面
                current_url = driver.current_url
                expected_url = "https://www.cathaybk.com.tw/cathaybk/personal/loan/product/mortgage/"
                
                print(f"當前頁面 URL: {current_url}")
                print(f"期望重定向 URL: {expected_url}")
                
                if expected_url in current_url:
                    print("✅ 主頁上方連結重定向驗證成功")
                else:
                    print(f"❌ 主頁上方連結重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}")
                    assert False, f"主頁上方連結重定向驗證失敗 - 期望: {expected_url}, 實際: {current_url}"
            else:
                print("主頁上方連結點擊失敗")
                assert False, "主頁上方連結點擊失敗"
                
        except Exception as e:
            print(f"測試主頁上方連結時發生錯誤: {e}")
            assert False, f"測試主頁上方連結時發生錯誤: {e}"
        finally:
            if driver:
                driver.quit()

if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 