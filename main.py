import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os
from ttkthemes import ThemedStyle


class ExpenseIncomeReportGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense and Income Report Generator")

        self.style = ThemedStyle(self.root)
        self.style.set_theme("arc")  # Choose a theme (e.g., "arc", "clearlooks", "equilux", etc.)

        

        self.month_label = ttk.Label(root, text="Select Month:", font=("Helvetica", 12))
        self.month_var = tk.StringVar()
        self.month_dropdown = ttk.Combobox(root, textvariable=self.month_var, values=self.get_months(), font=("Helvetica", 12))

        self.year_label = ttk.Label(root, text="Select Year:", font=("Helvetica", 12))
        self.year_var = tk.StringVar()
        self.year_dropdown = ttk.Combobox(root, textvariable=self.year_var, values=self.get_years(), font=("Helvetica", 12))

        self.browse_button = ttk.Button(root, text="Browse CSV", command=self.browse_csv, style="Accent.TButton")
        self.generate_button = ttk.Button(root, text="Generate Report", command=self.generate_report, style="Accent.TButton")

        self.success_label = ttk.Label(root, text="", foreground="green", font=("Helvetica", 12))
        self.success_label.pack(pady=10)
        
        self.month_label.pack(pady=10)
        self.month_dropdown.pack(pady=10)
        self.year_label.pack(pady=10)
        self.year_dropdown.pack(pady=10)
        self.browse_button.pack(pady=10)
        self.generate_button.pack(pady=10)

        # Set the CSV file path
        self.csv_file_path = None

    def get_months(self, selected_year=None):
        # Customize this function to populate months dynamically based on available data and selected year
        # For now, returning all months
        return ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    def get_years(self):
        # Customize this function to populate years dynamically based on available data
        # For now, returning a range of years
        return [str(year) for year in range(2020, 2030)]

    def browse_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.csv_file_path = file_path
            self.success_label.config(text=f"Selected CSV file: {self.csv_file_path}")

    def generate_report(self):
        selected_month = self.month_var.get()
        selected_year = self.year_var.get()

        if not selected_month or not selected_year or not self.csv_file_path:
            messagebox.showerror("Error", "Please select month, year, and CSV file.")
            return

        # Check if the PDF file already exists
        pdf_file_path = f"Report_{selected_month}_{selected_year}.pdf"
        if os.path.exists(pdf_file_path):
            # Ask for confirmation before replacing the existing PDF
            confirm_replace = messagebox.askyesno("Confirmation", f"The report file '{pdf_file_path}' already exists. Do you want to replace it?")
            if not confirm_replace:
                return

        # Read data from selected CSV file
        df = pd.read_csv(self.csv_file_path, parse_dates=["TIME"], dayfirst=True)

        # Filter data for the selected month and year
        selected_month_data = df[
            (df['TIME'].dt.strftime('%B') == selected_month) & 
            (df['TIME'].dt.strftime('%Y') == selected_year)
        ]

        # Calculate sum of income and expense for the selected month
        income_sum = selected_month_data.loc[
            selected_month_data['TYPE'].str.contains('Income', case=False), 
            'AMOUNT'
        ].sum()

        expense_sum = selected_month_data.loc[
            selected_month_data['TYPE'].str.contains('Expense', case=False), 
            'AMOUNT'
        ].sum()

        # Generate PDF report
        pdf_file_path = f"Report_{selected_month}_{selected_year}.pdf"
        with PdfPages(pdf_file_path) as pdf:
            self.add_summary_to_pdf(pdf, selected_month, selected_year, income_sum, expense_sum)
            self.create_table(pdf, selected_month_data[selected_month_data['TYPE'].str.contains('Expense', case=False)], "Expense", "CATEGORY")
            self.create_table(pdf, selected_month_data[selected_month_data['TYPE'].str.contains('Income', case=False)], "Income", "CATEGORY")
            self.create_pie_chart(pdf, selected_month_data[selected_month_data['TYPE'].str.contains('Income', case=False)], "Income", "CATEGORY")
            self.create_pie_chart(pdf, selected_month_data[selected_month_data['TYPE'].str.contains('Expense', case=False)], "Expense", "CATEGORY")

        self.success_label.config(text=f"Report generated successfully: {pdf_file_path}")
        

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
