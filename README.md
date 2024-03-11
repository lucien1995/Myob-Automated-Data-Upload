The functional code for this project comes from functional testing  https://github.com/lucien1995/QCT-MYOB-Automated-Data-Upload
it's the starting point of everything 
Thanks to Tom and Quinlan Consulting for giving me the internship opportunity to realize this project！


# How to use the sandbox version

The executable file is in the **dist** folder. You just need to download **app.exe** and run it on your computer. Please use **Time sheet.xlsx** for dragging data into the table.

If you are just uploading a Timesheet, you must at least ensure that the column format is consistent with the example, and the four data of **Date**, **Name**, **Start time**, and **End time** must be complete, and the data in other columns can be filled in as you like.

***Currently, only the data of employees that already exist in the MYOB database can be uploaded, and creating a new payroll category for an employee is not supported.***


The subscription version of MYOB will provide API keys and necessary cf-tokens. If you link to the subscription version, just modify the parameters in app.py.

Documentation on the use of MYOB API:   https://developer.myob.com/api/myob-business-api/
