import os
import pandas as pd
import glob
import tkinter as tk
from tkinter import filedialog, messagebox

def excel_automation():
    """Excel自动化处理工具"""
    # 创建GUI界面
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    # 1. 选择输入文件夹
    input_dir = filedialog.askdirectory(title="选择包含Excel文件的文件夹")
    if not input_dir:
        print("操作取消")
        return
    
    # 2. 选择输出位置
    output_path = filedialog.asksaveasfilename(
        title="保存合并后的文件",
        defaultextension=".xlsx",
        filetypes=[("Excel文件", "*.xlsx"), ("所有文件", "*.*")]
    )
    if not output_path:
        print("操作取消")
        return
    
    try:
        # 3. 查找所有Excel文件
        excel_files = glob.glob(os.path.join(input_dir, "*.xlsx")) + \
                     glob.glob(os.path.join(input_dir, "*.xls")) + \
                     glob.glob(os.path.join(input_dir, "*.xlsm"))
        
        if not excel_files:
            messagebox.showerror("错误", "文件夹中没有找到Excel文件")
            return
        
        # 4. 合并文件
        all_dfs = []
        for file in excel_files:
            # 根据文件扩展名选择合适的引擎
            if file.endswith('.xlsx') or file.endswith('.xlsm'):
                engine = 'openpyxl'
            elif file.endswith('.xls'):
                engine = 'xlrd'
            else:
                # 跳过非Excel文件
                continue
                
            # 读取文件并添加来源标记
            df = pd.read_excel(file, engine=engine)
            df['来源文件'] = os.path.basename(file)
            all_dfs.append(df)
        
        combined_df = pd.concat(all_dfs, ignore_index=True)
        
        # 5. 数据清洗
        # 删除完全空白的行
        cleaned_df = combined_df.dropna(how='all')
        # 删除完全空白的列
        cleaned_df = cleaned_df.dropna(axis=1, how='all')
        # 填充部分空值
        cleaned_df = cleaned_df.fillna('N/A')
        
        # 6. 保存结果
        cleaned_df.to_excel(output_path, index=False, engine='openpyxl')
        
        # 7. 生成处理报告
        report = f"""
        Excel文件处理报告
        =================
        处理时间: {pd.Timestamp.now()}
        输入文件夹: {input_dir}
        找到文件数: {len(excel_files)}
        合并前总行数: {len(combined_df)}
        清理后总行数: {len(cleaned_df)}
        删除空行数: {len(combined_df) - len(cleaned_df)}
        输出文件: {output_path}
        """
        
        # 保存报告
        report_dir = os.path.dirname(output_path)
        report_path = os.path.join(report_dir, "处理报告.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 显示结果
        messagebox.showinfo("处理完成", 
                           f"成功处理 {len(excel_files)} 个文件\n"
                           f"输出文件: {output_path}\n"
                           f"处理报告: {report_path}")
        
        print(report)
        return output_path
    
    except Exception as e:
        messagebox.showerror("处理失败", f"发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

# 执行自动化脚本
if __name__ == "__main__":
    excel_automation()