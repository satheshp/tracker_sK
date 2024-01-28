const sheetName = 'Sheet1';
const scriptProp = PropertiesService.getScriptProperties();

function intialSetup() {
  const activeSpreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  scriptProp.setProperty('key', activeSpreadsheet.getId());
}

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.tryLock(10000);

  try {
    const doc = SpreadsheetApp.openById(scriptProp.getProperty('key'));
    const sheet = doc.getSheetByName(sheetName);

    // Access form values
    const category = e.parameter['Category'];
    const amount = e.parameter['Amount'];
    const note = e.parameter['Note'];
    const incomeCheckbox = e.parameter['Income'];

    // Check if the "Income" checkbox is checked
    const isIncome = incomeCheckbox === 'on'; // The checkbox value for a checked box

    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var income_records = ss.getSheetByName("Income Records");
    var expense_records = ss.getSheetByName("Expense Records");

    var values = [
      [
        new Date(),    // Date
        category,       // Category (get from HTML form)
        amount,         // Amount (get from HTML form)
        note            // Note (get from HTML form)
      ]
    ];

    // Set value to "Income" if income checkbox is checked
    if (isIncome) {
      income_records.insertRows(2, 1);
      income_records.getRange(2, 1, 1, 4).setValues(values);
    } else {
      expense_records.insertRows(2, 1);
      expense_records.getRange(2, 1, 1, 4).setValues(values);
    }

    // Return a JSON response
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'success', 'row': nextRow }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (e) {
    // Handle errors and return a JSON response
    return ContentService
      .createTextOutput(JSON.stringify({ 'result': 'error', 'error': e }))
      .setMimeType(ContentService.MimeType.JSON);

  } finally {
    lock.releaseLock();
  }
}

