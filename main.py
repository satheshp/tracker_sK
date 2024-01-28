import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import requests
import os


class ExpenseIncomeReportGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense and Income Report Generator")
        
        self.success_label = ttk.Label(root, text="", foreground="green")
        self.success_label.pack(pady=10)
        
        self.month_label = ttk.Label(root, text="Select Month:")
        self.month_var = tk.StringVar()
        self.month_dropdown = ttk.Combobox(root, textvariable=self.month_var, values=self.get_months())

        self.year_label = ttk.Label(root, text="Select Year:")
        self.year_var = tk.StringVar()
        self.year_dropdown = ttk.Combobox(root, textvariable=self.year_var, values=self.get_years())

        self.generate_button = ttk.Button(root, text="Generate Report", command=self.generate_report)

        self.month_label.pack(pady=10)
        self.month_dropdown.pack(pady=10)
        self.year_label.pack(pady=10)
        self.year_dropdown.pack(pady=10)
        self.generate_button.pack(pady=10)

        # Set the CSV file path
        self.csv_file_path = "EITK.csv"

    def get_months(self, selected_year=None):
        # Customize this function to populate months dynamically based on available data and selected year
        # For now, returning all months
        return ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    def get_years(self):
        # Customize this function to populate years dynamically based on available data
        # For now, returning a range of years
        return [str(year) for year in range(2020, 2030)]

    def download_csv(self, csv_url):
        response = requests.get(csv_url)
        with open(self.csv_file_path, 'wb') as file:
            file.write(response.content)

    def generate_report(self):
        selected_month = self.month_var.get()
        selected_year = self.year_var.get()

        if not selected_month or not selected_year:
            return

        # Check if the PDF file already exists
        pdf_file_path = f"Report_{selected_month}_{selected_year}.pdf"
        if os.path.exists(pdf_file_path):
            # Ask for confirmation before replacing the existing PDF
            confirm_replace = messagebox.askyesno("Confirmation", f"The report file '{pdf_file_path}' already exists. Do you want to replace it?")
            if not confirm_replace:
                return

        # Download CSV file from the given link
        csv_url = "<CSV.csv>"
        self.download_csv(csv_url)

        # Read data from downloaded CSV file
        df = pd.read_csv(self.csv_file_path, parse_dates=["DATE"], dayfirst=True)

        # Filter data for the selected month and year
        selected_month_data = df[(df['DATE'].dt.strftime('%B') == selected_month) & (df['DATE'].dt.strftime('%Y') == selected_year)]
        
        # Calculate sum of income and expense for the selected month
        income_sum = selected_month_data.loc[selected_month_data['TYPE'].str.upper() == 'INCOME', 'AMOUNT'].sum()
        expense_sum = selected_month_data.loc[selected_month_data['TYPE'].str.upper() == 'EXPENSE', 'AMOUNT'].sum()

        # Generate PDF report
        pdf_file_path = f"Report_{selected_month}_{selected_year}.pdf"
        with PdfPages(pdf_file_path) as pdf:
                    self.add_summary_to_pdf(pdf, selected_month, selected_year, income_sum, expense_sum)
                    self.create_table(pdf, selected_month_data[selected_month_data['TYPE'] == 'EXPENSE'], "Expense", "CATEGORIES")
                    self.create_table(pdf, selected_month_data[selected_month_data['TYPE'] == 'INCOME'], "Income", "CATEGORIES")
                    self.create_pie_chart(pdf, selected_month_data[selected_month_data['TYPE'] == 'INCOME'], "Income", "CATEGORIES")
                   
                    self.create_pie_chart(pdf, selected_month_data[selected_month_data['TYPE'] == 'EXPENSE'], "Expense", "CATEGORIES")# Add summary to the PDF report
            
        self.success_label.config(text=f"Report generated successfully: {pdf_file_path}")
        print(f"Report generated successfully: {pdf_file_path}")

        # Delete the downloaded CSV file
        os.remove(self.csv_file_path)

    def add_summary_to_pdf(self, pdf, selected_month, selected_year, income_sum, expense_sum):
        # Create a summary page in the PDF
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.axis('off')
        ax.text(0.5, 0.8, f"Summary for {selected_month} {selected_year}", fontsize=14, ha='center', va='center', weight='bold')
        ax.text(0.5, 0.6, f"Income: ₹{income_sum:.2f}", fontsize=12, ha='center', va='center')
        ax.text(0.5, 0.4, f"Expense: ₹{expense_sum:.2f}", fontsize=12, ha='center', va='center')
        ax.text(0.5, 0.2, f"Net Income: ₹{income_sum - expense_sum:.2f}", fontsize=12, ha='center', va='center')

        pdf.savefig(fig)
        plt.close()

    def create_table(self, pdf, data, title, category_column):
        fig, ax = plt.subplots(figsize=(8, 4))  # Create a figure here
        ax.axis('tight')
        ax.axis('off')
        ax.set_title(f"{title} Table")

        table_data = [data.columns.tolist()] + data.values.tolist()
        table = ax.table(cellText=table_data, colLabels=None, cellLoc='center', loc='center')

        for i, key in enumerate(table_data[0]):
            table[(0, i)].set_fontsize(10)
            table[(0, i)].set_text_props(weight='bold')

        pdf.savefig(fig)  # Pass the figure to savefig
        plt.close()

    def create_pie_chart(self, pdf, data, title, category_column):
        fig, ax = plt.subplots()  # Create a figure here
        ax.set_title(f"{title} Pie Chart")
        
        if category_column in data.columns:
            grouped_data = data.groupby(category_column)['AMOUNT'].sum()
            labels = grouped_data.index
            values = grouped_data.values

            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
            pdf.savefig(fig)  # Pass the figure to savefig
            plt.close()
        else:
            print(f"No data for {title} categories in the selected month.")



if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("800x600")  # Set the initial size to 800x600 (adjust as needed)
    app = ExpenseIncomeReportGenerator(root)
    root.mainloop()
