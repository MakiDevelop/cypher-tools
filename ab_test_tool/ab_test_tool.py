import numpy as np
from scipy.stats import ttest_ind

def ab_test_ttest(a_conversion, a_size, b_conversion, b_size):
    """
    進行 A/B 測試的 T 檢定
    :param a_conversion: A 組轉換率（0.12 = 12%）
    :param a_size: A 組樣本數
    :param b_conversion: B 組轉換率（0.16 = 16%）
    :param b_size: B 組樣本數
    :return: T 值, p 值, 結論
    """

    # 🚀 設定樣本數
    a_size = 1000  # A 組用戶數
    b_size = 1000  # B 組用戶數

    # 🚀 設定轉換率
    a_conversion = 0.12  # A 組轉換率 12%
    b_conversion = 0.16  # B 組轉換率 16%

    # 🚀 生成 A/B 測試數據
    np.random.seed(42)  # 設定隨機種子，確保每次執行結果相同
    A_group = np.random.choice([0, 1], size=a_size, p=[1 - a_conversion, a_conversion])
    B_group = np.random.choice([0, 1], size=b_size, p=[1 - b_conversion, b_conversion])

    
    # 寫死數據，方便驗證
    # A_group = [1, 0, 1, 1, 0, 1, 0, 0, 1, 1]  # A 組用戶行為
    # B_group = [0, 1, 1, 1, 1, 1, 0, 1, 1, 1]  # B 組用戶行為

    # 計算 T 檢定
    t_stat, p_value = ttest_ind(A_group, B_group, equal_var=False)

    print("="*40)
    print(f"A 組轉換率: {a_conversion*100:.2f}% (樣本數: {a_size})")
    print(f"B 組轉換率: {b_conversion*100:.2f}% (樣本數: {b_size})")
    print(f"T 統計值: {t_stat:.3f}")
    print(f"P 值: {p_value:.5f}")

    # 自動判斷結果
    if p_value < 0.05:
        print("✅ 結論：B 組的轉換率顯著高於 A 組，可以考慮使用 B 組方案！")
    else:
        print("❌ 結論：沒有顯著差異，可能只是隨機波動，繼續觀察或增加樣本數！")
    print("="*40)

# 🚀 **開始測試 A/B 測試**
# 你可以改變這裡的數據
ab_test_ttest(a_conversion=0.12, a_size=1000, b_conversion=0.16, b_size=1000)
